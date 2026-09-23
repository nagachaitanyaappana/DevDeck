"""
Process Manager for DevDeck.
Handles spawning, monitoring, streaming logs, resource metrics, 
URL auto-detection, and clean tree termination for developer projects.
"""

import os
import signal
import re
import socket
from typing import Dict, Optional, Tuple, List
from PyQt6.QtCore import QObject, pyqtSignal, QProcess, QTimer
import psutil

def is_port_open(port: int) -> bool:
    """Checks whether a local TCP port is currently listening."""
    if not port or port <= 0 or port > 65535:
        return False
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.12)
            return s.connect_ex(("127.0.0.1", port)) == 0
    except Exception:
        return False

URL_REGEX = re.compile(
    r'(https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])(?::\d+)?(?:/[^\s"\'\`\<\>)]*)?)',
    re.IGNORECASE
)
PORT_REGEX = re.compile(
    r'(?:port|listening on|running at|server at|started on)\s*(?:port)?\s*:?\s*(\d{2,5})',
    re.IGNORECASE
)

class ProjectProcess(QObject):
    """Encapsulates a running QProcess for a specific project."""
    log_appended = pyqtSignal(str, str, bool)     # project_id, text, is_stderr
    url_detected = pyqtSignal(str, str)           # project_id, url
    status_changed = pyqtSignal(str, str)         # project_id, status ("running", "stopped", "error")
    finished = pyqtSignal(str, int)               # project_id, exit_code

    def __init__(self, project_id: str, command: str, cwd: str, env: Optional[Dict[str, str]] = None):
        super().__init__()
        self.project_id = project_id
        self.command = command
        self.cwd = cwd
        self.custom_env = env or {}
        self.detected_url: Optional[str] = None
        self.log_history: List[Tuple[str, bool]] = []  # (text, is_stderr)
        self.max_log_lines = 1500

        self.process = QProcess()
        self.process.setWorkingDirectory(self.cwd)
        
        # Setup environment
        system_env = self.process.processEnvironment().systemEnvironment()
        for k, v in self.custom_env.items():
            system_env.insert(k, v)
        # Ensure colored outputs in node/python/etc.
        system_env.insert("FORCE_COLOR", "1")
        system_env.insert("TERM", "xterm-256color")
        self.process.setProcessEnvironment(system_env)

        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_error)

    def start(self):
        self.status_changed.emit(self.project_id, "starting")
        self._append_log(f"⚡ Starting command: {self.command}\n📁 In directory: {self.cwd}\n" + "─" * 50 + "\n", False)
        
        # Use shell to execute commands properly (handles npm, gradle, pipes, args)
        self.process.start("/bin/bash", ["-c", self.command])
        if self.process.waitForStarted(1500):
            self.status_changed.emit(self.project_id, "running")
        else:
            self.status_changed.emit(self.project_id, "error")

    def stop(self):
        pid = self.process.processId()
        if not pid or self.process.state() == QProcess.ProcessState.NotRunning:
            self.status_changed.emit(self.project_id, "stopped")
            return

        self._append_log("\n⏹ Stopping process tree...\n", False)
        self._kill_process_tree(pid)
        self.process.terminate()
        if not self.process.waitForFinished(1000):
            self.process.kill()
        self.status_changed.emit(self.project_id, "stopped")

    def _kill_process_tree(self, pid: int):
        """Recursively terminates all child processes of pid."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    child.terminate()
                except (psutil.NoSuchProcess, ProcessLookupError):
                    pass
            parent.terminate()
            
            # Wait briefly, then kill any survivors
            gone, alive = psutil.wait_procs(children + [parent], timeout=0.8)
            for p in alive:
                try:
                    p.kill()
                except (psutil.NoSuchProcess, ProcessLookupError):
                    pass
        except (psutil.NoSuchProcess, ProcessLookupError):
            pass

    def get_metrics(self) -> Tuple[float, float]:
        """Returns (cpu_percent, memory_mb) for the process and its children."""
        pid = self.process.processId()
        if not pid or self.process.state() != QProcess.ProcessState.Running:
            return 0.0, 0.0

        total_cpu = 0.0
        total_mem_bytes = 0
        try:
            parent = psutil.Process(pid)
            total_cpu += parent.cpu_percent(interval=None)
            total_mem_bytes += parent.memory_info().rss
            for child in parent.children(recursive=True):
                try:
                    total_cpu += child.cpu_percent(interval=None)
                    total_mem_bytes += child.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0, 0.0

        return total_cpu, round(total_mem_bytes / (1024 * 1024), 1)

    def _on_stdout(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self._append_log(data, False)
        self._inspect_for_urls(data)

    def _on_stderr(self):
        data = self.process.readAllStandardError().data().decode("utf-8", errors="replace")
        self._append_log(data, True)
        self._inspect_for_urls(data)

    def _inspect_for_urls(self, text: str):
        # Look for explicit URL
        matches = URL_REGEX.findall(text)
        if matches:
            url = matches[0].strip()
            # Clean up trailing punctuation
            url = url.rstrip(",.;)>]")
            url = url.replace("0.0.0.0", "localhost").replace("127.0.0.1", "localhost")
            if not self.detected_url or self.detected_url != url:
                self.detected_url = url
                self.url_detected.emit(self.project_id, url)
            return

        # Look for port mention if no URL yet
        if not self.detected_url:
            port_matches = PORT_REGEX.findall(text)
            if port_matches:
                port = port_matches[0].strip()
                if port.isdigit() and 1000 <= int(port) <= 65535:
                    url = f"http://localhost:{port}"
                    self.detected_url = url
                    self.url_detected.emit(self.project_id, url)

    def _append_log(self, text: str, is_stderr: bool):
        self.log_history.append((text, is_stderr))
        if len(self.log_history) > self.max_log_lines:
            self.log_history = self.log_history[-self.max_log_lines:]
        self.log_appended.emit(self.project_id, text, is_stderr)

    def _on_finished(self, exit_code: int, exit_status: QProcess.ExitStatus):
        status = "stopped" if exit_code == 0 else "error"
        self._append_log(f"\n⏹ Process finished with exit code {exit_code}\n", exit_code != 0)
        self.status_changed.emit(self.project_id, status)
        self.finished.emit(self.project_id, exit_code)

    def _on_error(self, error: QProcess.ProcessError):
        self._append_log(f"\n⚠️ Process error: {error}\n", True)
        self.status_changed.emit(self.project_id, "error")


class ProcessManager(QObject):
    """Manages active processes for all projects."""
    log_appended = pyqtSignal(str, str, bool)        # project_id, text, is_stderr
    url_detected = pyqtSignal(str, str)              # project_id, url
    status_changed = pyqtSignal(str, str)            # project_id, status
    metrics_updated = pyqtSignal(str, float, float)  # project_id, cpu_pct, mem_mb

    def __init__(self):
        super().__init__()
        self.active_processes: Dict[str, ProjectProcess] = {}

        # Resource monitoring timer
        self.metrics_timer = QTimer(self)
        self.metrics_timer.setInterval(1500)
        self.metrics_timer.timeout.connect(self._update_all_metrics)
        self.metrics_timer.start()

    def start_project(self, project: Dict) -> bool:
        p_id = project["id"]
        if self.is_running(p_id):
            return True

        cwd = project["path"]
        cmd = project.get("command", "")
        if not cmd:
            return False

        # Prepare environment with port injection if port is assigned
        env = dict(project.get("env") or {})
        port = project.get("port")
        if port:
            env["PORT"] = str(port)
            env["SERVER_PORT"] = str(port)
            env["VITE_PORT"] = str(port)

        proc = ProjectProcess(p_id, cmd, cwd, env)
        proc.log_appended.connect(self.log_appended)
        proc.url_detected.connect(self.url_detected)
        proc.status_changed.connect(self.status_changed)
        self.active_processes[p_id] = proc
        proc.start()
        return True

    def stop_project(self, project_id: str):
        if project_id in self.active_processes:
            proc = self.active_processes[project_id]
            proc.stop()

    def restart_project(self, project: Dict):
        p_id = project["id"]
        self.stop_project(p_id)
        # Small delay before starting again
        QTimer.singleShot(600, lambda: self.start_project(project))

    def stop_all(self):
        for p_id in list(self.active_processes.keys()):
            self.stop_project(p_id)

    def is_running(self, project_id: str) -> bool:
        proc = self.active_processes.get(project_id)
        if not proc:
            return False
        return proc.process.state() == QProcess.ProcessState.Running

    def get_status(self, project_id: str) -> str:
        proc = self.active_processes.get(project_id)
        if not proc:
            return "stopped"
        state = proc.process.state()
        if state == QProcess.ProcessState.Running:
            return "running"
        elif state == QProcess.ProcessState.Starting:
            return "starting"
        return "stopped"

    def get_detected_url(self, project_id: str) -> Optional[str]:
        proc = self.active_processes.get(project_id)
        return proc.detected_url if proc else None

    def is_port_listening(self, port: Optional[int]) -> bool:
        if not port:
            return False
        return is_port_open(port)

    def get_logs(self, project_id: str) -> List[Tuple[str, bool]]:
        proc = self.active_processes.get(project_id)
        return proc.log_history if proc else []

    def _update_all_metrics(self):
        for p_id, proc in list(self.active_processes.items()):
            if proc.process.state() == QProcess.ProcessState.Running:
                cpu, mem = proc.get_metrics()
                self.metrics_updated.emit(p_id, cpu, mem)
            elif proc.process.state() == QProcess.ProcessState.NotRunning:
                self.metrics_updated.emit(p_id, 0.0, 0.0)

"""
Quick Actions for DevDeck.
Handles opening projects in VS Code, Terminal, File Manager, and Web Browser.
"""

import os
import sys
import shutil
import subprocess
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

def open_url(url: str):
    """Opens a URL in the user's default browser."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    QDesktopServices.openUrl(QUrl(url))

def open_in_vscode(path: str):
    """Opens the directory in Visual Studio Code."""
    code_bin = shutil.which("code") or shutil.which("codium") or shutil.which("code.cmd")
    if code_bin:
        subprocess.Popen([code_bin, path], start_new_session=True)
    else:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path], start_new_session=True)
        else:
            subprocess.Popen(["xdg-open", path], start_new_session=True)

def open_in_terminal(path: str):
    """Opens an interactive terminal in the specified directory."""
    if sys.platform == "win32":
        if shutil.which("wt"):
            subprocess.Popen(["wt", "-d", path], start_new_session=True)
        else:
            subprocess.Popen(f'start cmd /k "cd /d {path}"', shell=True)
        return
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-a", "Terminal", path], start_new_session=True)
        return

    terminals = [
        ("xfce4-terminal", ["xfce4-terminal", f"--working-directory={path}"]),
        ("gnome-terminal", ["gnome-terminal", f"--working-directory={path}"]),
        ("kitty", ["kitty", f"--directory={path}"]),
        ("alacritty", ["alacritty", f"--working-directory={path}"]),
        ("xterm", ["xterm", "-e", f"cd '{path}' && bash"]),
    ]
    for term, cmd in terminals:
        if shutil.which(term):
            subprocess.Popen(cmd, start_new_session=True)
            return
    # Fallback
    subprocess.Popen(["x-terminal-emulator"], cwd=path, start_new_session=True)

def open_in_file_manager(path: str):
    """Opens the directory in the default file manager."""
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path], start_new_session=True)
    else:
        fm = shutil.which("thunar") or shutil.which("nautilus") or shutil.which("dolphin") or "xdg-open"
        subprocess.Popen([fm, path], start_new_session=True)

def get_process_on_port(port: int):
    """Finds which PID, process, and working directory is holding a TCP port."""
    if not port:
        return None
    import psutil
    try:
        for conn in psutil.net_connections(kind="inet"):
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                pid = conn.pid
                if pid:
                    try:
                        p = psutil.Process(pid)
                        cwd = None
                        try:
                            cwd = p.cwd()
                        except Exception:
                            pass
                        return {
                            "pid": pid,
                            "name": p.name(),
                            "cwd": cwd,
                            "cmdline": " ".join(p.cmdline())
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        return {"pid": pid, "name": "unknown", "cwd": None, "cmdline": ""}
    except Exception:
        pass
    return None

def is_project_running(project: dict, process_manager) -> bool:
    """
    Accurately checks if a project/service is running.
    Prevents false positives when multiple projects share the same port.
    """
    p_id = project.get("id")
    if p_id and process_manager.get_status(p_id) in ["running", "starting"]:
        return True

    port = project.get("port")
    if not port or not process_manager.is_port_listening(port):
        return False

    info = get_process_on_port(port)
    if not info:
        return False

    proj_path = project.get("path")
    if proj_path:
        norm_proj = os.path.normpath(proj_path)
        proc_cwd = info.get("cwd")
        if proc_cwd:
            norm_cwd = os.path.normpath(proc_cwd)
            # True match if the process is running in this directory or a child/parent
            if norm_cwd == norm_proj or norm_cwd.startswith(norm_proj + os.sep) or norm_proj.startswith(norm_cwd + os.sep):
                return True
        cmdline = info.get("cmdline", "")
        if norm_proj in cmdline:
            return True
        # A process is listening on this port, but it belongs to a DIFFERENT directory / project!
        return False

    return True

def kill_process_on_port(port: int) -> bool:
    """Safely kills whatever process is holding the specified port."""
    info = get_process_on_port(port)
    if not info or not info.get("pid"):
        return False
    import psutil
    try:
        proc = psutil.Process(info["pid"])
        # Kill children first
        for child in proc.children(recursive=True):
            try:
                child.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        proc.kill()
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


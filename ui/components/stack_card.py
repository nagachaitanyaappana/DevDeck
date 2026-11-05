"""
Stack Card Component for DevDeck.
Displays a multi-project group (e.g. ITIAP Backend + Frontend) as a single
floating card with 1-click simultaneous launching, stopping, and port routing.
Styled with Figma theme (purple/violet color scheme).
"""

import os
from typing import Dict
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QWidget, QStyleOption, QStyle, QInputDialog, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt6.QtGui import QPainter, QAction, QCursor
from PyQt6.QtGui import QPainter, QAction, QCursor

from ui.icons import (
    glyph_for, ICO_BROWSER, ICO_CODE, ICO_CLOSE, ICO_FAV_OFF, ICO_FAV_ON,
    ICO_FOLDER, ICO_LOGS, ICO_RESTART, ICO_STACK, ICO_START, ICO_STOP,
    ICO_TERMINAL,
)


class ElidedTitleLabel(QLabel):
    """A label that elides its text instead of forcing the card to grow."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._full_text = text
        self.setToolTip(text)

    def setText(self, text):
        self._full_text = text
        self.setToolTip(text)
        super().setText(text)
        self.update()

    def minimumSizeHint(self):
        h = super().minimumSizeHint().height()
        return QSize(60, max(h, 16))

    def paintEvent(self, event):
        painter = QPainter(self)
        fm = self.fontMetrics()
        elided = fm.elidedText(self._full_text, Qt.TextElideMode.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)


class ServiceMiniRow(QFrame):
    """Sub-row representing one service inside the stack card."""
    logs_clicked = pyqtSignal(dict)
    restart_clicked = pyqtSignal(dict)
    port_changed = pyqtSignal(dict, int)
    start_clicked = pyqtSignal(dict)
    stop_clicked = pyqtSignal(str)
    open_url_clicked = pyqtSignal(str)
    open_code_clicked = pyqtSignal(str)
    open_terminal_clicked = pyqtSignal(str)
    open_folder_clicked = pyqtSignal(str)

    def __init__(self, service: Dict, parent=None):
        super().__init__(parent)
        self.service = service
        self.status = "stopped"
        self.detected_url = ""
        self.setObjectName("ServiceMiniRow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(8)

        # Service tech icon & name
        icon = glyph_for(service.get("stack", ""))
        name = service.get("name", "Service")
        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setObjectName("ServiceIcon")
        layout.addWidget(self.icon_lbl)

        self.name_label = QLabel(name)
        self.name_label.setObjectName("ServiceName")
        self.name_label.setToolTip(f"{name}\n{service.get('command', '')}")
        # The name must never be squeezed out by the command snippet next to it.
        self.name_label.setMinimumWidth(72)
        self.name_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.name_label)

        # Port control: the number is the content, so no pictogram.
        port = service.get("port")
        self.port_btn = QPushButton(f":{port}" if port else "port")
        self.port_btn.setToolTip(f"Assigned port for {name}: :{port or 'none'}\nClick to change")
        self.port_btn.setObjectName("PortTag")
        self.port_btn.clicked.connect(self._quick_edit_port)
        layout.addWidget(self.port_btn)

        # Command snippet
        cmd = service.get("command", "")
        if len(cmd) > 20:
            cmd_snippet = cmd[:18] + "..."
        else:
            cmd_snippet = cmd
        self.cmd_lbl = QLabel(f"$ {cmd_snippet}")
        self.cmd_lbl.setToolTip(cmd)
        self.cmd_lbl.setObjectName("ServiceCmd")
        # Command text is the first thing to give up space when the row is tight.
        self.cmd_lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        layout.addWidget(self.cmd_lbl, 1)

        layout.addStretch()

        # Service Quick IDE / Terminal / Folder Shortcuts (sleek 24x24 buttons)
        self.code_btn = QPushButton("Code")
        self.code_btn.setVisible(False)
        self.code_btn.setToolTip(f"Open {name} in VS Code")
        self.code_btn.setObjectName("IconBtn")
        self.code_btn.clicked.connect(lambda: self.open_code_clicked.emit(self.service.get("path", "")))
        layout.addWidget(self.code_btn)

        self.term_btn = QPushButton("Terminal")
        self.term_btn.setVisible(False)
        self.term_btn.setToolTip(f"Open {name} in Terminal")
        self.term_btn.setObjectName("IconBtn")
        self.term_btn.clicked.connect(lambda: self.open_terminal_clicked.emit(self.service.get("path", "")))
        layout.addWidget(self.term_btn)

        self.folder_btn = QPushButton("Folder")
        self.folder_btn.setVisible(False)
        self.folder_btn.setToolTip(f"Open {name} in File Manager")
        self.folder_btn.setObjectName("IconBtn")
        self.folder_btn.clicked.connect(lambda: self.open_folder_clicked.emit(self.service.get("path", "")))
        layout.addWidget(self.folder_btn)

        # Service Open URL button
        self.url_btn = QPushButton("Open")
        self.url_btn.setVisible(False)
        self.url_btn.setToolTip(f"Open {name} in Browser")
        self.url_btn.setObjectName("IconBtn")
        self.url_btn.clicked.connect(self._on_open_single_url)
        layout.addWidget(self.url_btn)

        # Service Logs button
        self.logs_btn = QPushButton("Logs")
        self.logs_btn.setVisible(False)
        self.logs_btn.setToolTip(f"View logs for {name}")
        self.logs_btn.setObjectName("IconBtn")
        self.logs_btn.clicked.connect(lambda: self.logs_clicked.emit(self.service))
        layout.addWidget(self.logs_btn)

        # Service Restart button
        self.restart_btn = QPushButton("Restart")
        self.restart_btn.setVisible(False)
        self.restart_btn.setToolTip(f"Restart {name}")
        self.restart_btn.setObjectName("IconBtn")
        self.restart_btn.clicked.connect(lambda: self.restart_clicked.emit(self.service))
        layout.addWidget(self.restart_btn)

        # Status indicator
        self.status_lbl = QLabel("Stopped")
        self.status_lbl.setMinimumWidth(68)
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.setObjectName("StatusBadge")
        self.status_lbl.setProperty("status", "stopped")
        layout.addWidget(self.status_lbl)

    def _on_open_single_url(self):
        u = self.detected_url
        if not u or u in ["http://localhost", "http://localhost/", "https://localhost", "https://localhost/"]:
            if self.service.get("port"):
                u = f"http://localhost:{self.service['port']}"
        if u:
            self.open_url_clicked.emit(u)

    def _quick_edit_port(self):
        curr_port = self.service.get("port") or 8080
        name = self.service.get("name", "Service")
        port, ok = QInputDialog.getInt(
            self, f"Change Port - {name}",
            f"Set assigned port for '{name}':\n(DevDeck will export PORT={curr_port} and update routing)",
            value=int(curr_port), min=1000, max=65535, step=1
        )
        if ok:
            self.service["port"] = port
            self.port_btn.setText(f":{port}" if port else "port")
            self.port_changed.emit(self.service, port)

    def resizeEvent(self, event):
        """Collapse the optional bits when the row gets narrow.

        The command snippet and the two least-used shortcuts are the first to
        go; the name, port, status and primary actions always stay.
        """
        super().resizeEvent(event)
        compact = self.width() < 460
        self.cmd_lbl.setVisible(not compact)
        for btn in (self.folder_btn, self.restart_btn):
            btn.setVisible(not compact)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        name = self.service.get("name", "Service")

        if self.status in ["running", "starting"]:
            act_start_stop = QAction(f"{ICO_STOP}  Stop {name}", self)
            act_start_stop.triggered.connect(lambda: self.stop_clicked.emit(self.service["id"]))
        else:
            act_start_stop = QAction(f"{ICO_START}  Start {name}", self)
            act_start_stop.triggered.connect(lambda: self.start_clicked.emit(self.service))
        menu.addAction(act_start_stop)

        act_restart = QAction(f"{ICO_RESTART}  Restart {name}", self)
        act_restart.triggered.connect(lambda: self.restart_clicked.emit(self.service))
        menu.addAction(act_restart)

        act_port = QAction(f"Change Port  ·  :{self.service.get('port') or 'none'}", self)
        act_port.triggered.connect(self._quick_edit_port)
        menu.addAction(act_port)

        menu.addSeparator()

        act_logs = QAction(f"{ICO_LOGS}  View Logs for {name}", self)
        act_logs.triggered.connect(lambda: self.logs_clicked.emit(self.service))
        menu.addAction(act_logs)

        menu.addSeparator()
        code_act = QAction("Open in VS Code", self)
        code_act.triggered.connect(lambda: self.open_code_clicked.emit(self.service.get("path", "")))
        menu.addAction(code_act)
        terminal_act = QAction("Open in Terminal", self)
        terminal_act.triggered.connect(lambda: self.open_terminal_clicked.emit(self.service.get("path", "")))
        menu.addAction(terminal_act)
        folder_act = QAction("Open service folder", self)
        folder_act.triggered.connect(lambda: self.open_folder_clicked.emit(self.service.get("path", "")))
        menu.addAction(folder_act)
        browser_act = QAction("Open in browser", self)
        browser_act.triggered.connect(self._on_open_single_url)
        menu.addAction(browser_act)

        menu.exec(event.globalPos())

    def set_status(self, status: str):
        self.status = status
        self.status_lbl.setProperty("status", status)
        self.setProperty("status", status)
        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)
        self.style().unpolish(self)
        self.style().polish(self)

        if status == "running":
            self.status_lbl.setText("Running")
        elif status == "starting":
            self.status_lbl.setText("Starting…")
        elif status == "error":
            self.status_lbl.setText("Error")
        else:
            self.status_lbl.setText("Stopped")


class StackCard(QFrame):
    """Card representing an entire grouped stack of projects."""
    start_stack_clicked = pyqtSignal(dict)
    stop_stack_clicked = pyqtSignal(dict)
    restart_stack_clicked = pyqtSignal(dict)
    edit_stack_clicked = pyqtSignal(dict)
    remove_stack_clicked = pyqtSignal(str)
    open_urls_clicked = pyqtSignal(list)
    view_service_logs_clicked = pyqtSignal(dict)
    restart_service_clicked = pyqtSignal(dict)
    service_port_changed = pyqtSignal(dict, dict, int)
    start_service_clicked = pyqtSignal(dict)
    stop_service_clicked = pyqtSignal(str)
    open_code_clicked = pyqtSignal(str)
    open_terminal_clicked = pyqtSignal(str)
    open_folder_clicked = pyqtSignal(str)

    def __init__(self, stack: Dict, parent=None):
        super().__init__(parent)
        self.stack = dict(stack)
        self.service_rows: Dict[str, ServiceMiniRow] = {}
        self.setObjectName("StackCard")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        super().paintEvent(event)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # ─── Top Row: Icon, Title, Stack Tag, Status Badge, Close ───
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # Icon squircle (Figma style: soft purple with border)
        icon_box = QFrame()
        icon_box.setObjectName("StackCardIconBox")
        icon_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        ib_layout = QHBoxLayout(icon_box)
        ib_layout.setContentsMargins(0, 0, 0, 0)
        ib_lbl = QLabel(ICO_STACK)
        ib_lbl.setObjectName("StackCardIcon")
        ib_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ib_layout.addWidget(ib_lbl)
        top_row.addWidget(icon_box)

        # Title & Subtitle
        t_box = QVBoxLayout()
        t_box.setSpacing(2)
        self.title_lbl = ElidedTitleLabel(self.stack.get("name", "Project Stack"))
        self.title_lbl.setObjectName("StackCardTitle")
        self.sub_lbl = QLabel(f"{len(self.stack.get('services', []))} services")
        self.sub_lbl.setObjectName("StackCardSub")
        t_box.addWidget(self.title_lbl)
        t_box.addWidget(self.sub_lbl)
        top_row.addLayout(t_box, 1)

        top_row.addStretch()

        # Overall Status Badge
        self.overall_status_badge = QLabel("Stopped")
        self.overall_status_badge.setObjectName("StatusBadge")
        self.overall_status_badge.setProperty("status", "stopped")
        top_row.addWidget(self.overall_status_badge)

        # Edit button
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setMinimumHeight(28)
        self.edit_btn.setToolTip("Edit Stack Settings")
        self.edit_btn.setObjectName("IconBtn")
        self.edit_btn.clicked.connect(lambda: self.edit_stack_clicked.emit(self.stack))
        top_row.addWidget(self.edit_btn)

        # Delete button
        self.close_btn = QPushButton("Remove")
        self.close_btn.setMinimumHeight(28)
        self.close_btn.setToolTip("Remove Stack from Deck")
        self.close_btn.setObjectName("IconBtn")
        self.close_btn.clicked.connect(lambda: self.remove_stack_clicked.emit(self.stack["id"]))
        top_row.addWidget(self.close_btn)

        layout.addLayout(top_row)

        # ─── Middle Section: List of member services ───
        self.services_box = QVBoxLayout()
        self.services_box.setSpacing(6)

        for s in self.stack.get("services", []):
            s_id = s["id"]
            row = ServiceMiniRow(s, self)
            row.logs_clicked.connect(self.view_service_logs_clicked.emit)
            row.restart_clicked.connect(self.restart_service_clicked.emit)
            row.port_changed.connect(lambda srv, p: self._on_row_port_changed(srv, p))
            row.start_clicked.connect(self.start_service_clicked.emit)
            row.stop_clicked.connect(self.stop_service_clicked.emit)
            row.open_url_clicked.connect(lambda u: self.open_urls_clicked.emit([u]))
            row.open_code_clicked.connect(self.open_code_clicked.emit)
            row.open_terminal_clicked.connect(self.open_terminal_clicked.emit)
            row.open_folder_clicked.connect(self.open_folder_clicked.emit)
            self.service_rows[s_id] = row
            self.services_box.addWidget(row)

        layout.addLayout(self.services_box)

        # ─── Bottom Row: Launch & URL Actions ───
        bot_row = QHBoxLayout()
        bot_row.setSpacing(6)

        # Start / Stop All Button
        self.main_btn = QPushButton("Start stack")
        self.main_btn.setObjectName("StartBtn")
        self.main_btn.clicked.connect(self._on_toggle_stack)
        bot_row.addWidget(self.main_btn)

        # Restart Stack Button
        self.restart_stack_btn = QPushButton("Restart")
        self.restart_stack_btn.setToolTip("Restart all services in this stack")
        self.restart_stack_btn.setObjectName("IconBtn")
        self.restart_stack_btn.clicked.connect(lambda: self.restart_stack_clicked.emit(self.stack))
        bot_row.addWidget(self.restart_stack_btn)

        # Open URLs Button
        self.open_urls_btn = QPushButton("Open URLs")
        self.open_urls_btn.setEnabled(False)
        self.open_urls_btn.setObjectName("BrowserBtn")
        self.open_urls_btn.clicked.connect(self._on_open_urls)
        bot_row.addWidget(self.open_urls_btn)

        bot_row.addStretch()

        # Quick IDE / Terminal / Folder Shortcuts for Stack
        for btn, tip, handler, icon_name in [
            (QPushButton("Code"), "Open Stack in VS Code", self._on_open_code, "code_btn"),
            (QPushButton("Terminal"), "Open Stack in Terminal", self._on_open_terminal, "term_btn"),
            (QPushButton("Folder"), "Open Stack in File Manager", self._on_open_folder, "folder_btn"),
        ]:
            setattr(self, icon_name, btn)
            btn.setVisible(False)
            btn.setToolTip(tip)
            btn.setObjectName("IconBtn")
            btn.clicked.connect(handler)
            bot_row.addWidget(btn)

        layout.addLayout(bot_row)

    def _get_stack_path(self) -> str:
        paths = [s.get("path") for s in self.stack.get("services", []) if s.get("path") and os.path.exists(s.get("path"))]
        if not paths:
            return ""
        if len(paths) == 1:
            return paths[0]
        try:
            common = os.path.commonpath(paths)
            if common and os.path.isdir(common):
                return common
        except Exception:
            pass
        return paths[0]

    def _on_open_code(self):
        p = self._get_stack_path()
        if p:
            self.open_code_clicked.emit(p)

    def _on_open_terminal(self):
        p = self._get_stack_path()
        if p:
            self.open_terminal_clicked.emit(p)

    def _on_open_folder(self):
        p = self._get_stack_path()
        if p:
            self.open_folder_clicked.emit(p)

    def _on_row_port_changed(self, srv: dict, new_port: int):
        for s in self.stack.get("services", []):
            if s.get("id") == srv.get("id"):
                s["port"] = new_port
                s["url"] = f"http://localhost:{new_port}"
                break
        self.service_port_changed.emit(self.stack, srv, new_port)

    def set_service_status(self, service_id: str, status: str):
        if service_id in self.service_rows:
            self.service_rows[service_id].set_status(status)
            self._update_overall_state()

    def set_service_url(self, service_id: str, url: str):
        if service_id in self.service_rows:
            self.service_rows[service_id].detected_url = url
            self._update_overall_state()

    def _update_overall_state(self):
        total = len(self.service_rows)
        running = sum(1 for r in self.service_rows.values() if r.status == "running")
        starting = sum(1 for r in self.service_rows.values() if r.status == "starting")

        self.setProperty("running", "true" if running == total and total > 0 else "false")
        self.style().unpolish(self)
        self.style().polish(self)

        if total == 0:
            self.overall_status_badge.setText("Empty")
        elif running == total:
            self.overall_status_badge.setText(f"{running}/{total} running")
        elif running > 0 or starting > 0:
            self.overall_status_badge.setText(f"{running}/{total} running")
        else:
            self.overall_status_badge.setText("Stopped")

        if running > 0 or starting > 0:
            self.main_btn.setText("Stop stack")
            self.main_btn.setObjectName("StopBtn")
        else:
            self.main_btn.setText(f"Start stack ({total})")
            self.main_btn.setObjectName("StartBtn")
        self.main_btn.style().unpolish(self.main_btn)
        self.main_btn.style().polish(self.main_btn)

        # Enable Open URLs button if any service has a URL or port to open
        has_any_url = any(
            bool(r.detected_url) or (r.status == "running" and bool(r.service.get("port")))
            for r in self.service_rows.values()
        )
        self.open_urls_btn.setEnabled(has_any_url)

    def _on_toggle_stack(self):
        running = sum(1 for r in self.service_rows.values() if r.status == "running")
        if running > 0:
            self.stop_stack_clicked.emit(self.stack)
        else:
            self.start_stack_clicked.emit(self.stack)

    def _on_open_urls(self):
        urls = []
        for r in self.service_rows.values():
            u = r.detected_url
            if not u or u in ["http://localhost", "http://localhost/", "https://localhost", "https://localhost/"]:
                if r.service.get("port"):
                    u = f"http://localhost:{r.service['port']}"
            if u:
                urls.append(u)
        if urls:
            self.open_urls_clicked.emit(urls)
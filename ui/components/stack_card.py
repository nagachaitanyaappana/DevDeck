"""
Stack Card Component for DevDeck.
Displays a multi-project group (e.g. ITIAP Backend + Frontend) as a single
floating card with 1-click simultaneous launching, stopping, and port routing.
"""

from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QWidget, QStyleOption, QStyle, QInputDialog, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QAction, QCursor

STACK_ICONS = {
    "Vite / React": "⚛️",
    "Vite": "⚡",
    "Next.js": "▲",
    "Node.js": "🟢",
    "Express": "🚂",
    "Spring Boot (Gradle)": "🍃",
    "Spring Boot (Maven)": "🍃",
    "Gradle": "🐘",
    "Python App": "🐍",
    "Python CLI": "🐍",
    "Django": "🎸",
    "Flask / FastAPI": "🌶️",
    "Docker Compose": "🐳",
}

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
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame {
                background-color: #1a2234;
                border: 1px solid #2a3852;
                border-radius: 10px;
                padding: 4px 8px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Service tech icon & name
        self.theme = "dark"
        icon = STACK_ICONS.get(service.get("stack", ""), "💻")
        name = service.get("name", "Service")
        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setStyleSheet("font-size: 16px; background: transparent;")
        layout.addWidget(self.icon_lbl)

        self.name_label = QLabel(name)
        self.name_label.setStyleSheet("font-weight: 800; font-size: 13px; color: #f1f5f9; background: transparent;")
        layout.addWidget(self.name_label)

        # Port Button (Clickable to change port!)
        port = service.get("port")
        self.port_btn = QPushButton(f"🔌 :{port}" if port else "🔌 Port")
        self.port_btn.setToolTip(f"Click to change port for {name} (currently :{port or 'None'})")
        self.port_btn.clicked.connect(self._quick_edit_port)
        layout.addWidget(self.port_btn)

        # Command snippet
        cmd = service.get("command", "")
        if len(cmd) > 28:
            cmd_snippet = cmd[:25] + "..."
        else:
            cmd_snippet = cmd
        self.cmd_lbl = QLabel(f"$ {cmd_snippet}")
        self.cmd_lbl.setToolTip(cmd)
        self.cmd_lbl.setStyleSheet("font-family: monospace; font-size: 11px; color: #4B5563; background: transparent;")
        layout.addWidget(self.cmd_lbl)

        layout.addStretch()

        # Service Quick IDE / Terminal / Folder Shortcuts
        self.code_btn = QPushButton("💻")
        self.code_btn.setFixedSize(34, 34)
        self.code_btn.setToolTip(f"Open {name} in VS Code")
        self.code_btn.clicked.connect(lambda: self.open_code_clicked.emit(self.service.get("path", "")))
        layout.addWidget(self.code_btn)

        self.term_btn = QPushButton("📟")
        self.term_btn.setFixedSize(34, 34)
        self.term_btn.setToolTip(f"Open {name} in Terminal")
        self.term_btn.clicked.connect(lambda: self.open_terminal_clicked.emit(self.service.get("path", "")))
        layout.addWidget(self.term_btn)

        self.folder_btn = QPushButton("📁")
        self.folder_btn.setFixedSize(34, 34)
        self.folder_btn.setToolTip(f"Open {name} in File Manager")
        self.folder_btn.clicked.connect(lambda: self.open_folder_clicked.emit(self.service.get("path", "")))
        layout.addWidget(self.folder_btn)

        # Service Open URL button
        self.url_btn = QPushButton("🌐")
        self.url_btn.setFixedSize(34, 34)
        self.url_btn.setToolTip(f"Open {name} in Browser")
        self.url_btn.clicked.connect(self._on_open_single_url)
        layout.addWidget(self.url_btn)

        # Service Logs button
        self.logs_btn = QPushButton("📋")
        self.logs_btn.setFixedSize(34, 34)
        self.logs_btn.setToolTip(f"View logs for {name}")
        self.logs_btn.clicked.connect(lambda: self.logs_clicked.emit(self.service))
        layout.addWidget(self.logs_btn)

        # Service Restart button
        self.restart_btn = QPushButton("🔄")
        self.restart_btn.setFixedSize(34, 34)
        self.restart_btn.setToolTip(f"Restart {name}")
        self.restart_btn.clicked.connect(lambda: self.restart_clicked.emit(self.service))
        layout.addWidget(self.restart_btn)

        # Status indicator
        self.status_lbl = QLabel("● Stopped")
        self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #6B7280; background: transparent;")
        layout.addWidget(self.status_lbl)

        self._update_port_btn_style()

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
            self._update_port_btn_style()
            self.port_changed.emit(self.service, port)

    def _update_port_btn_style(self):
        port = self.service.get("port")
        name = self.service.get("name", "Service")
        self.port_btn.setText(f"🔌 :{port}" if port else "🔌 Port")
        self.port_btn.setToolTip(f"Click to change port for {name} (currently :{port or 'None'})")
        if port:
            self.port_btn.setStyleSheet("color: #60a5fa; background-color: #1e3a5f; border: 1px solid #2563eb; border-radius: 8px; font-family: monospace; font-size: 12px; font-weight: 800; padding: 4px 8px;")
        else:
            self.port_btn.setStyleSheet("color: #94a3b8; background-color: #1e2638; border: 1px solid #2e3c54; border-radius: 8px; font-size: 12px; font-weight: 700; padding: 4px 8px;")

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #151b27;
                border: 1px solid #2e3c54;
                border-radius: 8px;
                padding: 6px;
                color: #f1f5f9;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 6px;
                color: #f1f5f9;
                background-color: transparent;
                font-weight: 600;
                font-size: 12px;
            }
            QMenu::item:hover, QMenu::item:selected {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: 800;
            }
            QMenu::item:disabled {
                color: #64748b;
                background-color: transparent;
            }
            QMenu::separator {
                height: 1px;
                background-color: #242f44;
                margin: 4px 8px;
            }
        """)
        name = self.service.get("name", "Service")
        
        if self.status in ["running", "starting"]:
            act_start_stop = QAction(f"⏹ Stop {name}", self)
            act_start_stop.triggered.connect(lambda: self.stop_clicked.emit(self.service["id"]))
        else:
            act_start_stop = QAction(f"▶ Start {name}", self)
            act_start_stop.triggered.connect(lambda: self.start_clicked.emit(self.service))
        menu.addAction(act_start_stop)

        act_restart = QAction(f"🔄 Restart {name}", self)
        act_restart.triggered.connect(lambda: self.restart_clicked.emit(self.service))
        menu.addAction(act_restart)

        act_port = QAction(f"🔌 Change Port (currently :{self.service.get('port') or 'None'})", self)
        act_port.triggered.connect(self._quick_edit_port)
        menu.addAction(act_port)

        menu.addSeparator()

        act_logs = QAction(f"📋 View Logs for {name}", self)
        act_logs.triggered.connect(lambda: self.logs_clicked.emit(self.service))
        menu.addAction(act_logs)

        menu.exec(event.globalPos())

    def update_row_style(self, theme: str = "dark"):
        self.theme = "dark"
        self.name_label.setStyleSheet("font-weight: 800; font-size: 13px; color: #f1f5f9; background: transparent;")
        self.cmd_lbl.setStyleSheet("font-family: monospace; font-size: 11px; color: #94a3b8; background: transparent;")
        for btn in [self.code_btn, self.term_btn, self.folder_btn, self.logs_btn, self.url_btn, self.restart_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e2638;
                    border: 1px solid #2e3c54;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    color: #f1f5f9;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #2e3c54;
                }
            """)
        self._update_port_btn_style()
        self.set_status(self.status, "dark")

    def set_status(self, status: str, theme: Optional[str] = None):
        self.status = status
        self.theme = "dark"
        if status == "running":
            self.status_lbl.setText("● Running")
            self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 800; color: #34d399; background: transparent;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #064e3b;
                    border: 1px solid #059669;
                    border-radius: 10px;
                    padding: 4px 8px;
                }
            """)
        elif status == "starting":
            self.status_lbl.setText("⏳ Starting...")
            self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 800; color: #fbbf24; background: transparent;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #451a03;
                    border: 1px solid #d97706;
                    border-radius: 10px;
                    padding: 4px 8px;
                }
            """)
        elif status == "error":
            self.status_lbl.setText("⚠️ Error")
            self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 800; color: #f87171; background: transparent;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #4c0519;
                    border: 1px solid #e11d48;
                    border-radius: 10px;
                    padding: 4px 8px;
                }
            """)
        else:
            self.status_lbl.setText("● Stopped")
            self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #94a3b8; background: transparent;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #1a2234;
                    border: 1px solid #2a3852;
                    border-radius: 10px;
                    padding: 4px 8px;
                }
            """)


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

        # Icon squircle (pastel blue/dark circle)
        icon_box = QFrame()
        icon_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        icon_box.setStyleSheet("background-color: #1e2638; border: 1px solid #2d3952; border-radius: 20px; min-width: 40px; max-width: 40px; min-height: 40px; max-height: 40px;")
        ib_layout = QHBoxLayout(icon_box)
        ib_layout.setContentsMargins(0, 0, 0, 0)
        ib_lbl = QLabel("⚡")
        ib_lbl.setStyleSheet("font-size: 20px; color: #38bdf8; background: transparent;")
        ib_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ib_layout.addWidget(ib_lbl)
        top_row.addWidget(icon_box)

        # Title & Subtitle
        t_box = QVBoxLayout()
        t_box.setSpacing(2)
        self.title_lbl = QLabel(self.stack.get("name", "Project Stack"))
        self.title_lbl.setStyleSheet("font-size: 15px; font-weight: 900; color: #f1f5f9; background: transparent;")
        self.sub_lbl = QLabel(f"MULTI-PROJECT STACK ({len(self.stack.get('services', []))} SERVICES)")
        self.sub_lbl.setStyleSheet("font-size: 10px; font-weight: 800; color: #94a3b8; letter-spacing: 0.5px; background: transparent;")
        t_box.addWidget(self.title_lbl)
        t_box.addWidget(self.sub_lbl)
        top_row.addLayout(t_box)

        top_row.addStretch()

        # Overall Status Badge
        self.overall_status_badge = QLabel("● Stopped")
        self.overall_status_badge.setStyleSheet("font-size: 11px; font-weight: 800; border: 1px solid #2e3c54; border-radius: 10px; padding: 4px 10px; background-color: #1e2430; color: #94a3b8;")
        top_row.addWidget(self.overall_status_badge)

        # Edit button
        self.edit_btn = QPushButton("⚙")
        self.edit_btn.setFixedSize(34, 34)
        self.edit_btn.setToolTip("Edit Stack Settings")
        self.edit_btn.clicked.connect(lambda: self.edit_stack_clicked.emit(self.stack))
        top_row.addWidget(self.edit_btn)

        # Delete button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(34, 34)
        self.close_btn.setToolTip("Remove Stack from Deck")
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
        bot_row.setSpacing(10)

        # Start / Stop All Button
        self.main_btn = QPushButton(f"▶ Start Stack ({len(self.stack.get('services', []))})")
        self.main_btn.setStyleSheet("background-color: #065f46; color: #ecfdf5; font-weight: 900; font-size: 12px; border: 1.5px solid #10b981; border-radius: 12px; padding: 7px 18px;")
        self.main_btn.clicked.connect(self._on_toggle_stack)
        bot_row.addWidget(self.main_btn)

        # Restart Stack Button
        self.restart_stack_btn = QPushButton("🔄 Restart Stack")
        self.restart_stack_btn.setToolTip("Restart all services in this stack")
        self.restart_stack_btn.clicked.connect(lambda: self.restart_stack_clicked.emit(self.stack))
        bot_row.addWidget(self.restart_stack_btn)

        # Open URLs Button
        self.open_urls_btn = QPushButton("🌐 Open All URLs")
        self.open_urls_btn.setEnabled(False)
        self.open_urls_btn.setStyleSheet("background-color: #1e2638; color: #f1f5f9; font-weight: 800; font-size: 12px; border: 1px solid #2e3c54; border-radius: 12px; padding: 7px 14px;")
        self.open_urls_btn.clicked.connect(self._on_open_urls)
        bot_row.addWidget(self.open_urls_btn)

        bot_row.addStretch()

        # Quick IDE / Terminal / Folder Shortcuts for Stack
        self.code_btn = QPushButton("💻")
        self.code_btn.setFixedSize(34, 34)
        self.code_btn.setToolTip("Open Stack in VS Code")
        self.code_btn.clicked.connect(self._on_open_code)
        bot_row.addWidget(self.code_btn)

        self.term_btn = QPushButton("📟")
        self.term_btn.setFixedSize(34, 34)
        self.term_btn.setToolTip("Open Stack in Terminal")
        self.term_btn.clicked.connect(self._on_open_terminal)
        bot_row.addWidget(self.term_btn)

        self.folder_btn = QPushButton("📁")
        self.folder_btn.setFixedSize(34, 34)
        self.folder_btn.setToolTip("Open Stack in File Manager")
        self.folder_btn.clicked.connect(self._on_open_folder)
        bot_row.addWidget(self.folder_btn)

        layout.addLayout(bot_row)

        self.update_card_style("dark")

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

    def update_card_style(self, theme: str = "dark"):
        self.theme = "dark"
        any_running = any(r.status == "running" for r in self.service_rows.values())
        border = "2px solid #10b981" if any_running else "1.5px solid #283449"
        self.setStyleSheet(f"""
            QFrame#StackCard {{
                background-color: #151b27;
                border: {border};
                border-radius: 14px;
            }}
        """)
        self.title_lbl.setStyleSheet("font-size: 15px; font-weight: 900; color: #f1f5f9; background: transparent;")
        if hasattr(self, "sub_lbl"):
            self.sub_lbl.setStyleSheet("font-size: 10px; font-weight: 800; color: #94a3b8; letter-spacing: 0.5px; background: transparent;")
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e2638;
                border: 1px solid #2e3c54;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                color: #f1f5f9;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #2e3c54;
            }
        """)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e2638;
                border: 1px solid #2e3c54;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 900;
                color: #f1f5f9;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #4c0519;
                color: #f87171;
            }
        """)
        self.restart_stack_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e2638;
                color: #f1f5f9;
                font-weight: 800;
                font-size: 13px;
                border: 1px solid #2e3c54;
                border-radius: 12px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #2e3c54;
            }
        """)
        self.open_urls_btn.setStyleSheet("background-color: #1e2638; color: #f1f5f9; font-weight: 800; font-size: 13px; border: 1px solid #2e3c54; border-radius: 12px; padding: 8px 16px;")
        for btn in [self.code_btn, self.term_btn, self.folder_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e2638;
                    border: 1px solid #2e3c54;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    color: #f1f5f9;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #2e3c54;
                }
            """)

        for row in self.service_rows.values():
            row.update_row_style("dark")

    def set_service_status(self, service_id: str, status: str):
        if service_id in self.service_rows:
            self.service_rows[service_id].set_status(status, "dark")
            self._update_overall_state()

    def set_service_url(self, service_id: str, url: str):
        if service_id in self.service_rows:
            self.service_rows[service_id].detected_url = url
            self._update_overall_state()

    def _update_overall_state(self):
        total = len(self.service_rows)
        running = sum(1 for r in self.service_rows.values() if r.status == "running")
        starting = sum(1 for r in self.service_rows.values() if r.status == "starting")

        if running == total and total > 0:
            self.overall_status_badge.setText(f"● {running}/{total} Running")
            self.overall_status_badge.setStyleSheet("font-size: 11px; font-weight: 800; border: 1.5px solid #059669; border-radius: 10px; padding: 4px 10px; background-color: #064e3b; color: #34d399;")
            self.main_btn.setText("⏹ Stop Stack")
            self.main_btn.setStyleSheet("background-color: #881337; color: #fff1f2; font-weight: 900; font-size: 12px; border: 1.5px solid #f43f5e; border-radius: 12px; padding: 7px 18px;")
        elif running > 0 or starting > 0:
            self.overall_status_badge.setText(f"⏳ {running}/{total} Running")
            self.overall_status_badge.setStyleSheet("font-size: 11px; font-weight: 800; border: 1.5px solid #d97706; border-radius: 10px; padding: 4px 10px; background-color: #451a03; color: #fbbf24;")
            self.main_btn.setText("⏹ Stop Stack")
            self.main_btn.setStyleSheet("background-color: #881337; color: #fff1f2; font-weight: 900; font-size: 12px; border: 1.5px solid #f43f5e; border-radius: 12px; padding: 7px 18px;")
        else:
            self.overall_status_badge.setText("● Stopped")
            self.overall_status_badge.setStyleSheet("font-size: 11px; font-weight: 800; border: 1.5px solid #2e3c54; border-radius: 10px; padding: 4px 10px; background-color: #1e2430; color: #94a3b8;")
            self.main_btn.setText(f"▶ Start Stack ({total})")
            self.main_btn.setStyleSheet("background-color: #065f46; color: #ecfdf5; font-weight: 900; font-size: 12px; border: 1.5px solid #10b981; border-radius: 12px; padding: 7px 18px;")

        # Enable Open URLs button if any service has URL or port
        has_any_url = any(bool(r.detected_url) or (r.status == "running" and bool(r.service.get("port"))) for r in self.service_rows.values())
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

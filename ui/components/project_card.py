"""
Project Card Component for DevDeck.
Provides 1-click Start/Stop, Browser launch, Logs toggle, and developer shortcuts.
"""

import os
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMenu, QMessageBox, QWidget, QStyleOption, QStyle
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QCursor, QPainter

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

class ElidedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._full_text = text
        self.setStyleSheet("background: transparent;")
        if text:
            self.setToolTip(text)

    def setText(self, text):
        self._full_text = text
        if text:
            self.setToolTip(text)
        super().setText(text)
        self.update()

    def minimumSizeHint(self):
        h = super().minimumSizeHint().height()
        return QSize(40, max(h, 16))

    def paintEvent(self, event):
        painter = QPainter(self)
        fm = self.fontMetrics()
        elided = fm.elidedText(self._full_text, Qt.TextElideMode.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

class ProjectCard(QFrame):
    start_clicked = pyqtSignal(dict)
    stop_clicked = pyqtSignal(str)
    restart_clicked = pyqtSignal(dict)
    open_url_clicked = pyqtSignal(str)
    view_logs_clicked = pyqtSignal(dict)
    open_code_clicked = pyqtSignal(str)
    open_terminal_clicked = pyqtSignal(str)
    open_folder_clicked = pyqtSignal(str)
    favorite_toggled = pyqtSignal(str)
    edit_clicked = pyqtSignal(dict)
    remove_clicked = pyqtSignal(str)
    port_changed = pyqtSignal(dict, int)
    kill_port_requested = pyqtSignal(int)

    def __init__(self, project: dict, parent=None):
        super().__init__(parent)
        self.project = dict(project)
        self.status = "stopped"
        self.detected_url = self.project.get("url", "")
        self.setObjectName("ProjectCard")
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

        # ─── Top Row: Icon Squircle, Title, Stack Badge, Port Badge, Favorite, More, Close ───
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Stack Icon Squircle (Soft pastel circle like in Figma design)
        icon_squircle = QFrame()
        icon_squircle.setObjectName("IconSquircle")
        icon_squircle.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sq_layout = QHBoxLayout(icon_squircle)
        sq_layout.setContentsMargins(0, 0, 0, 0)
        sq_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        stack = self.project.get("stack", "Custom")
        icon = STACK_ICONS.get(stack, "💻")
        self.icon_label = QLabel(icon)
        self.icon_label.setObjectName("SquircleIcon")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sq_layout.addWidget(self.icon_label)
        top_row.addWidget(icon_squircle)

        # Title & Path container
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        self.title_label = ElidedLabel(self.project.get("name", "Unnamed"))
        self.title_label.setObjectName("CardTitle")
        title_box.addWidget(self.title_label)

        # Display relative or shortened path
        path_str = self.project.get("path", "")
        home = os.path.expanduser("~")
        display_path = path_str.replace(home, "~")
        self.path_label = ElidedLabel(display_path)
        self.path_label.setObjectName("CardPath")
        self.path_label.setToolTip(path_str)
        title_box.addWidget(self.path_label)

        top_row.addLayout(title_box)
        top_row.addStretch()

        # Stack Badge
        self.stack_badge = QLabel(stack)
        self.stack_badge.setObjectName("StackBadge")
        top_row.addWidget(self.stack_badge)

        # Favorite Star Button
        # Favorite Star Button
        is_fav = self.project.get("favorite", False)
        self.fav_btn = QPushButton("★" if is_fav else "☆")
        self.fav_btn.setToolTip("Pin to Favorites")
        self.fav_btn.setFixedSize(34, 34)
        self.fav_btn.clicked.connect(self._toggle_favorite)
        top_row.addWidget(self.fav_btn)

        # More Options Menu Button
        self.more_btn = QPushButton("⋮")
        self.more_btn.setToolTip("More Options")
        self.more_btn.setFixedSize(34, 34)
        self.more_btn.clicked.connect(self._show_context_menu)
        top_row.addWidget(self.more_btn)

        # Close button (like top-right in Figma modal)
        self.close_btn = QPushButton("✕")
        self.close_btn.setToolTip("Remove from Deck")
        self.close_btn.setFixedSize(34, 34)
        self.close_btn.clicked.connect(lambda: self.remove_clicked.emit(self.project["id"]))
        top_row.addWidget(self.close_btn)

        layout.addLayout(top_row)

        # ─── Middle Row: Command line display, Port badge & live metrics ───
        mid_row = QHBoxLayout()
        mid_row.setSpacing(8)

        cmd_text = self.project.get("command", "")
        if len(cmd_text) > 30:
            display_cmd = cmd_text[:27] + "..."
        else:
            display_cmd = cmd_text
        self.cmd_label = QLabel(f"$ {display_cmd}")
        self.cmd_label.setObjectName("CardCmd")
        self.cmd_label.setToolTip(f"Full command: {cmd_text}")
        mid_row.addWidget(self.cmd_label)

        # Port Badge (Clickable to quick-edit port!)
        self.port_btn = QPushButton()
        self.port_btn.setObjectName("IconBtn")
        self._update_port_btn_label()
        self.port_btn.setToolTip("Click to change assigned port")
        self.port_btn.clicked.connect(self._quick_edit_port)
        mid_row.addWidget(self.port_btn)

        mid_row.addStretch()

        # Live CPU & RAM Metrics
        self.metrics_label = QLabel("")
        self.metrics_label.setObjectName("MetricsLabel")
        self.metrics_label.setVisible(False)
        mid_row.addWidget(self.metrics_label)

        # Status Badge Pill
        self.status_badge = QLabel("● Stopped")
        self.status_badge.setObjectName("StatusBadge")
        self.status_badge.setProperty("status", "stopped")
        mid_row.addWidget(self.status_badge)

        layout.addLayout(mid_row)

        # ─── Bottom Row: Action Buttons ───
        bot_row = QHBoxLayout()
        bot_row.setSpacing(8)

        # 1. Start / Stop Main Button
        self.main_btn = QPushButton("▶ Start")
        self.main_btn.setObjectName("StartBtn")
        self.main_btn.clicked.connect(self._on_main_action)
        bot_row.addWidget(self.main_btn)

        # 2. Open in Browser Button
        self.browser_btn = QPushButton("🌐 Open URL")
        self.browser_btn.setObjectName("BrowserBtn")
        self.browser_btn.setEnabled(False)
        self.browser_btn.clicked.connect(self._on_open_browser)
        bot_row.addWidget(self.browser_btn)

        # Update browser button state based on initial url
        self._update_browser_button()

        # 3. View Logs Button
        self.logs_btn = QPushButton("📋 Logs")
        self.logs_btn.setObjectName("IconBtn")
        self.logs_btn.clicked.connect(lambda: self.view_logs_clicked.emit(self.project))
        bot_row.addWidget(self.logs_btn)

        bot_row.addStretch()

        # 4. Quick IDE / Terminal / Folder Shortcuts
        self.code_btn = QPushButton("💻")
        self.code_btn.setFixedSize(34, 34)
        self.code_btn.setToolTip("Open in VS Code")
        self.code_btn.clicked.connect(lambda: self.open_code_clicked.emit(self.project["path"]))
        bot_row.addWidget(self.code_btn)

        self.term_btn = QPushButton("📟")
        self.term_btn.setFixedSize(34, 34)
        self.term_btn.setToolTip("Open in Terminal")
        self.term_btn.clicked.connect(lambda: self.open_terminal_clicked.emit(self.project["path"]))
        bot_row.addWidget(self.term_btn)

        self.folder_btn = QPushButton("📁")
        self.folder_btn.setFixedSize(34, 34)
        self.folder_btn.setToolTip("Open in File Manager")
        self.folder_btn.clicked.connect(lambda: self.open_folder_clicked.emit(self.project["path"]))
        bot_row.addWidget(self.folder_btn)

        layout.addLayout(bot_row)
        self.update_card_style("figma")

    def update_card_style(self, theme: str = "figma"):
        self.theme = theme
        is_running = (self.status == "running")
        if theme == "figma":
            border = "3px solid #16A34A" if is_running else "2px solid #111111"
            self.setStyleSheet(f"""
                QFrame#ProjectCard {{
                    background-color: #FFFFFF;
                    border: {border};
                    border-radius: 18px;
                }}
            """)
            self.title_label.setStyleSheet("background: transparent; color: #111111; font-weight: 900; font-size: 15px;")
            self.path_label.setStyleSheet("background: transparent; color: #666666; font-size: 11px;")
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1.5px solid #111111;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: 900;
                    color: #111111;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #FEE2E2;
                    color: #DC2626;
                }
            """)
            for btn in [self.more_btn, self.code_btn, self.term_btn, self.folder_btn]:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #FFFFFF;
                        border: 1.5px solid #111111;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: bold;
                        color: #111111;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: #FFF9C4;
                    }
                """)
            is_fav = self.project.get("favorite", False)
            fav_col = "#F59E0B" if is_fav else "#111111"
            self.fav_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #FFFFFF;
                    border: 1.5px solid #111111;
                    border-radius: 8px;
                    font-size: 17px;
                    font-weight: bold;
                    color: {fav_col};
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: #FFF9C4;
                }}
            """)
        else:
            border = "2px solid #10b981" if is_running else "1.5px solid #283449"
            self.setStyleSheet(f"""
                QFrame#ProjectCard {{
                    background-color: #151b27;
                    border: {border};
                    border-radius: 14px;
                }}
            """)
            self.title_label.setStyleSheet("background: transparent; color: #f1f5f9; font-weight: 800; font-size: 14px;")
            self.path_label.setStyleSheet("background: transparent; color: #64748b; font-size: 11px;")
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
            for btn in [self.more_btn, self.code_btn, self.term_btn, self.folder_btn]:
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
            is_fav = self.project.get("favorite", False)
            fav_col = "#F59E0B" if is_fav else "#f1f5f9"
            self.fav_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e2638;
                    border: 1px solid #2e3c54;
                    border-radius: 8px;
                    font-size: 17px;
                    font-weight: bold;
                    color: {fav_col};
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: #2e3c54;
                }}
            """)
        self._update_port_btn_label()

    def set_status(self, status: str):
        self.status = status
        self.status_badge.setProperty("status", status)
        self.status_badge.style().unpolish(self.status_badge)
        self.status_badge.style().polish(self.status_badge)

        self.setProperty("running", "true" if status == "running" else "false")
        self.style().unpolish(self)
        self.style().polish(self)

        theme = getattr(self, "theme", "figma")
        self.update_card_style(theme)

        if status == "running":
            self.status_badge.setText("● Running")
            self.main_btn.setText("⏹ Stop")
            self.main_btn.setObjectName("StopBtn")
            self._update_browser_button()
        elif status == "starting":
            self.status_badge.setText("⏳ Starting...")
            self.main_btn.setText("⏹ Stop")
            self.main_btn.setObjectName("StopBtn")
        elif status == "error":
            self.status_badge.setText("⚠️ Error")
            self.main_btn.setText("▶ Start")
            self.main_btn.setObjectName("StartBtn")
            self.metrics_label.setVisible(False)
        else:
            self.status_badge.setText("● Stopped")
            self.main_btn.setText("▶ Start")
            self.main_btn.setObjectName("StartBtn")
            self.metrics_label.setVisible(False)

        self.main_btn.style().unpolish(self.main_btn)
        self.main_btn.style().polish(self.main_btn)

    def set_detected_url(self, url: str):
        self.detected_url = url
        self._update_browser_button()

    def set_metrics(self, cpu_pct: float, mem_mb: float):
        if self.status == "running" and (cpu_pct > 0 or mem_mb > 0):
            self.metrics_label.setText(f"{cpu_pct:.1f}% CPU • {mem_mb:.0f} MB")
            self.metrics_label.setVisible(True)
        else:
            self.metrics_label.setVisible(False)

    def _update_browser_button(self):
        url = self.detected_url or self.project.get("url")
        if not url or url in ["http://localhost", "http://localhost/", "https://localhost", "https://localhost/"]:
            if self.project.get("port"):
                url = f"http://localhost:{self.project['port']}"
        if url:
            # Shorten display for button (e.g. :5173 or localhost:5173)
            display = url.replace("http://", "").replace("https://", "").rstrip("/")
            self.browser_btn.setText(f"🌐 {display}")
            self.browser_btn.setEnabled(True)
            self.browser_btn.setToolTip(f"Open {url} in Browser")
        else:
            self.browser_btn.setText("🌐 Open URL")
            self.browser_btn.setEnabled(False)
            self.browser_btn.setToolTip("No active URL detected")

    def _on_main_action(self):
        if self.status in ["running", "starting"]:
            self.stop_clicked.emit(self.project["id"])
        else:
            self.start_clicked.emit(self.project)

    def _update_port_btn_label(self):
        port = self.project.get("port")
        theme = getattr(self, "theme", "figma")
        if theme == "figma":
            if port:
                self.port_btn.setText(f"🔌 :{port}")
                self.port_btn.setStyleSheet("color: #0369A1; background-color: #E0F2FE; border: 1.5px solid #BAE6FD; border-radius: 8px; font-family: monospace; font-weight: 700; padding: 3px 8px;")
            else:
                self.port_btn.setText("🔌 Port")
                self.port_btn.setStyleSheet("color: #4B5563; background-color: #F3F4F6; border: 1px solid #CBD5E1; border-radius: 8px; font-size: 11px; font-weight: 600; padding: 3px 8px;")
        else:
            if port:
                self.port_btn.setText(f"🔌 :{port}")
                self.port_btn.setStyleSheet("color: #60a5fa; background-color: #1e3a5f; border: 1.5px solid #2563eb; border-radius: 8px; font-family: monospace; font-weight: 700; padding: 3px 8px;")
            else:
                self.port_btn.setText("🔌 Port")
                self.port_btn.setStyleSheet("color: #94a3b8; background-color: #1e2638; border: 1px solid #2e3c54; border-radius: 8px; font-size: 11px; font-weight: 600; padding: 3px 8px;")

    def _quick_edit_port(self):
        from PyQt6.QtWidgets import QInputDialog
        curr_port = self.project.get("port") or 5173
        port, ok = QInputDialog.getInt(
            self, "Manage Assigned Port", 
            f"Set assigned port for '{self.project.get('name')}':\n(DevDeck will export PORT={curr_port} and update browser URL)",
            value=int(curr_port), min=1000, max=65535, step=1
        )
        if ok:
            self.project["port"] = port
            self.project["url"] = f"http://localhost:{port}"
            self._update_port_btn_label()
            self._update_browser_button()
            self.port_changed.emit(self.project, port)

    def _on_open_browser(self):
        url = self.detected_url or self.project.get("url")
        if url:
            self.open_url_clicked.emit(url)

    def _toggle_favorite(self):
        fav = not self.project.get("favorite", False)
        self.project["favorite"] = fav
        self.fav_btn.setText("★" if fav else "☆")
        theme = getattr(self, "theme", "figma")
        fav_col = "#F59E0B" if fav else ("#111111" if theme == "figma" else "#f1f5f9")
        bg_col = "#FFFFFF" if theme == "figma" else "#1e2638"
        border_col = "1.5px solid #111111" if theme == "figma" else "1px solid #2e3c54"
        hover_col = "#FFF9C4" if theme == "figma" else "#2e3c54"
        self.fav_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_col};
                border: {border_col};
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: {fav_col};
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {hover_col};
            }}
        """)
        self.favorite_toggled.emit(self.project["id"])

    def _show_context_menu(self):
        from core.actions import get_process_on_port

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #111111;
                border: 2px solid #333333;
                border-radius: 10px;
                padding: 6px;
                color: #FFFFFF;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 6px;
                color: #FFFFFF;
                background-color: transparent;
                font-weight: 600;
                font-size: 12px;
            }
            QMenu::item:hover, QMenu::item:selected {
                background-color: #FFC107;
                color: #111111;
                font-weight: 800;
            }
            QMenu::item:disabled {
                color: #666666;
                background-color: transparent;
            }
            QMenu::separator {
                height: 1px;
                background-color: #2E2E2E;
                margin: 4px 8px;
            }
        """)

        # Start / Stop Action
        if self.status in ["running", "starting"]:
            start_stop_act = QAction("⏹ Stop Process", self)
            start_stop_act.triggered.connect(lambda: self.stop_clicked.emit(self.project["id"]))
        else:
            start_stop_act = QAction("▶ Start Process", self)
            start_stop_act.triggered.connect(lambda: self.start_clicked.emit(self.project))
        menu.addAction(start_stop_act)

        restart_act = QAction("🔄 Restart Process", self)
        restart_act.triggered.connect(lambda: self.restart_clicked.emit(self.project))
        menu.addAction(restart_act)

        # Port management in context menu
        port = self.project.get("port")
        port_act = QAction(f"🔌 Change Port (currently :{port or 'None'})", self)
        port_act.triggered.connect(self._quick_edit_port)
        menu.addAction(port_act)

        if port:
            holder = get_process_on_port(port)
            if holder:
                p_desc = f"{holder.get('name', 'process')} (PID {holder.get('pid')})"
                kill_port_act = QAction(f"⚡ Kill Port :{port} holder [{p_desc}]", self)
                kill_port_act.triggered.connect(lambda: self.kill_port_requested.emit(port))
                menu.addAction(kill_port_act)

        menu.addSeparator()

        edit_act = QAction("⚙ Edit Project Settings", self)
        edit_act.triggered.connect(lambda: self.edit_clicked.emit(self.project))
        menu.addAction(edit_act)

        remove_act = QAction("🗑 Remove from Deck", self)
        remove_act.triggered.connect(lambda: self.remove_clicked.emit(self.project["id"]))
        menu.addAction(remove_act)

        menu.exec(QCursor.pos())

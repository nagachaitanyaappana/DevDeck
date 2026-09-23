"""
Stack Card Component for DevDeck.
Displays a multi-project group (e.g. ITIAP Backend + Frontend) as a single
floating card with 1-click simultaneous launching, stopping, and port routing.
"""

from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QWidget, QStyleOption, QStyle
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPainter

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
    def __init__(self, service: Dict, parent=None):
        super().__init__(parent)
        self.service = service
        self.status = "stopped"
        self.detected_url = ""
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QFrame {
                background-color: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 10px;
                padding: 4px 8px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        # Service tech icon & name
        self.theme = "figma"
        icon = STACK_ICONS.get(service.get("stack", ""), "💻")
        name = service.get("name", "Service")
        self.name_label = QLabel(f"{icon} {name}")
        self.name_label.setStyleSheet("font-weight: 800; font-size: 12px; color: #111111; background: transparent;")
        layout.addWidget(self.name_label)

        # Port badge if configured
        port = service.get("port")
        self.port_lbl = None
        if port:
            self.port_lbl = QLabel(f":{port}")
            self.port_lbl.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #2563EB; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; padding: 2px 6px;")
            layout.addWidget(self.port_lbl)

        # Command snippet
        cmd = service.get("command", "")
        if len(cmd) > 28:
            cmd_snippet = cmd[:25] + "..."
        else:
            cmd_snippet = cmd
        self.cmd_lbl = QLabel(f"$ {cmd_snippet}")
        self.cmd_lbl.setToolTip(cmd)
        self.cmd_lbl.setStyleSheet("font-family: monospace; font-size: 10px; color: #4B5563; background: transparent;")
        layout.addWidget(self.cmd_lbl)

        layout.addStretch()

        # Service Logs button
        self.logs_btn = QPushButton("📋")
        self.logs_btn.setFixedSize(24, 24)
        self.logs_btn.setToolTip(f"View logs for {name}")
        self.logs_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #111111;
                border-radius: 6px;
                font-size: 11px;
                color: #111111;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #F3F4F6;
            }
        """)
        layout.addWidget(self.logs_btn)

        # Status indicator
        self.status_lbl = QLabel("● Stopped")
        self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #6B7280; background: transparent;")
        layout.addWidget(self.status_lbl)

    def update_row_style(self, theme: str):
        self.theme = theme
        if theme == "figma":
            self.name_label.setStyleSheet("font-weight: 800; font-size: 12px; color: #111111; background: transparent;")
            self.cmd_lbl.setStyleSheet("font-family: monospace; font-size: 10px; color: #4B5563; background: transparent;")
            if self.port_lbl:
                self.port_lbl.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #2563EB; background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 6px; padding: 2px 6px;")
            self.logs_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #111111;
                    border-radius: 6px;
                    font-size: 11px;
                    color: #111111;
                    padding: 0;
                }
                QPushButton:hover {
                    background-color: #F3F4F6;
                }
            """)
        else:
            self.name_label.setStyleSheet("font-weight: 800; font-size: 12px; color: #f1f5f9; background: transparent;")
            self.cmd_lbl.setStyleSheet("font-family: monospace; font-size: 10px; color: #94a3b8; background: transparent;")
            if self.port_lbl:
                self.port_lbl.setStyleSheet("font-family: monospace; font-size: 11px; font-weight: 700; color: #60a5fa; background: #1e3a5f; border: 1px solid #2563eb; border-radius: 6px; padding: 2px 6px;")
            self.logs_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e2638;
                    border: 1px solid #2e3c54;
                    border-radius: 6px;
                    font-size: 11px;
                    color: #f1f5f9;
                    padding: 0;
                }
                QPushButton:hover {
                    background-color: #2e3c54;
                }
            """)
        self.set_status(self.status, theme)

    def set_status(self, status: str, theme: Optional[str] = None):
        self.status = status
        if theme:
            self.theme = theme
        th = getattr(self, "theme", "figma")
        if th == "figma":
            if status == "running":
                self.status_lbl.setText("● Running")
                self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 800; color: #15803D; background: transparent;")
                self.setStyleSheet("""
                    QFrame {
                        background-color: #F0FDF4;
                        border: 1px solid #BBF7D0;
                        border-radius: 10px;
                        padding: 4px 8px;
                    }
                """)
            elif status == "starting":
                self.status_lbl.setText("⏳ Starting...")
                self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 800; color: #D97706; background: transparent;")
                self.setStyleSheet("""
                    QFrame {
                        background-color: #FFFBEB;
                        border: 1px solid #FDE68A;
                        border-radius: 10px;
                        padding: 4px 8px;
                    }
                """)
            elif status == "error":
                self.status_lbl.setText("⚠️ Error")
                self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 800; color: #DC2626; background: transparent;")
                self.setStyleSheet("""
                    QFrame {
                        background-color: #FEF2F2;
                        border: 1px solid #FECACA;
                        border-radius: 10px;
                        padding: 4px 8px;
                    }
                """)
            else:
                self.status_lbl.setText("● Stopped")
                self.status_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #6B7280; background: transparent;")
                self.setStyleSheet("""
                    QFrame {
                        background-color: #F9FAFB;
                        border: 1px solid #E5E7EB;
                        border-radius: 10px;
                        padding: 4px 8px;
                    }
                """)
        else:
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
    edit_stack_clicked = pyqtSignal(dict)
    remove_stack_clicked = pyqtSignal(str)
    open_urls_clicked = pyqtSignal(list)
    view_service_logs_clicked = pyqtSignal(dict)

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

        # Icon squircle (pastel orange/yellow circle)
        icon_box = QFrame()
        icon_box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        icon_box.setStyleSheet("background-color: #FEF08A; border: 2px solid #111111; border-radius: 20px; min-width: 40px; max-width: 40px; min-height: 40px; max-height: 40px;")
        ib_layout = QHBoxLayout(icon_box)
        ib_layout.setContentsMargins(0, 0, 0, 0)
        ib_lbl = QLabel("⚡")
        ib_lbl.setStyleSheet("font-size: 20px; background: transparent;")
        ib_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ib_layout.addWidget(ib_lbl)
        top_row.addWidget(icon_box)

        # Title & Subtitle
        t_box = QVBoxLayout()
        t_box.setSpacing(2)
        self.title_lbl = QLabel(self.stack.get("name", "Project Stack"))
        self.title_lbl.setStyleSheet("font-size: 15px; font-weight: 900; color: #111111; background: transparent;")
        self.sub_lbl = QLabel(f"MULTI-PROJECT STACK ({len(self.stack.get('services', []))} SERVICES)")
        self.sub_lbl.setStyleSheet("font-size: 10px; font-weight: 800; color: #6B7280; letter-spacing: 0.5px; background: transparent;")
        t_box.addWidget(self.title_lbl)
        t_box.addWidget(self.sub_lbl)
        top_row.addLayout(t_box)

        top_row.addStretch()

        # Overall Status Badge
        self.overall_status_badge = QLabel("● Stopped")
        self.overall_status_badge.setStyleSheet("font-size: 11px; font-weight: 800; border: 1.5px solid #111111; border-radius: 10px; padding: 4px 10px; background-color: #F3F4F6; color: #4B5563;")
        top_row.addWidget(self.overall_status_badge)

        # Edit button
        self.edit_btn = QPushButton("⚙")
        self.edit_btn.setFixedSize(30, 30)
        self.edit_btn.setToolTip("Edit Stack Settings")
        self.edit_btn.clicked.connect(lambda: self.edit_stack_clicked.emit(self.stack))
        top_row.addWidget(self.edit_btn)

        # Delete button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
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
            row.logs_btn.clicked.connect(lambda checked, s_item=s: self.view_service_logs_clicked.emit(s_item))
            self.service_rows[s_id] = row
            self.services_box.addWidget(row)

        layout.addLayout(self.services_box)

        # ─── Bottom Row: Launch & URL Actions ───
        bot_row = QHBoxLayout()
        bot_row.setSpacing(10)

        # Start / Stop All Button
        self.main_btn = QPushButton(f"▶ Start Stack ({len(self.stack.get('services', []))})")
        self.main_btn.setStyleSheet("background-color: #111111; color: #FFFFFF; font-weight: 900; font-size: 12px; border: 2px solid #111111; border-radius: 12px; padding: 7px 18px;")
        self.main_btn.clicked.connect(self._on_toggle_stack)
        bot_row.addWidget(self.main_btn)

        # Open URLs Button
        self.open_urls_btn = QPushButton("🌐 Open All URLs")
        self.open_urls_btn.setEnabled(False)
        self.open_urls_btn.setStyleSheet("background-color: #FFFFFF; color: #111111; font-weight: 800; font-size: 12px; border: 2px solid #111111; border-radius: 12px; padding: 7px 14px;")
        self.open_urls_btn.clicked.connect(self._on_open_urls)
        bot_row.addWidget(self.open_urls_btn)

        bot_row.addStretch()
        layout.addLayout(bot_row)

        self.update_card_style("figma")

    def update_card_style(self, theme: str = "figma"):
        self.theme = theme
        any_running = any(r.status == "running" for r in self.service_rows.values())
        if theme == "figma":
            border = "3px solid #16A34A" if any_running else "2px solid #111111"
            self.setStyleSheet(f"""
                QFrame#StackCard {{
                    background-color: #FFFFFF;
                    border: {border};
                    border-radius: 18px;
                }}
            """)
            self.title_lbl.setStyleSheet("font-size: 15px; font-weight: 900; color: #111111; background: transparent;")
            if hasattr(self, "sub_lbl"):
                self.sub_lbl.setStyleSheet("font-size: 10px; font-weight: 800; color: #6B7280; letter-spacing: 0.5px; background: transparent;")
            self.edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1.5px solid #111111;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    color: #111111;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #FFF9C4;
                }
            """)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1.5px solid #111111;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 900;
                    color: #111111;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #FEE2E2;
                    color: #DC2626;
                }
            """)
            self.open_urls_btn.setStyleSheet("background-color: #FFFFFF; color: #111111; font-weight: 800; font-size: 12px; border: 2px solid #111111; border-radius: 12px; padding: 7px 14px;")
        else:
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
                    font-size: 14px;
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
                    font-size: 13px;
                    font-weight: 900;
                    color: #f1f5f9;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #4c0519;
                    color: #f87171;
                }
            """)
            self.open_urls_btn.setStyleSheet("background-color: #1e2638; color: #f1f5f9; font-weight: 800; font-size: 12px; border: 1px solid #2e3c54; border-radius: 12px; padding: 7px 14px;")

        for row in self.service_rows.values():
            row.update_row_style(theme)

    def set_service_status(self, service_id: str, status: str):
        if service_id in self.service_rows:
            self.service_rows[service_id].set_status(status, getattr(self, "theme", "figma"))
            self._update_overall_state()

    def set_service_url(self, service_id: str, url: str):
        if service_id in self.service_rows:
            self.service_rows[service_id].detected_url = url
            self._update_overall_state()

    def _update_overall_state(self):
        total = len(self.service_rows)
        running = sum(1 for r in self.service_rows.values() if r.status == "running")
        starting = sum(1 for r in self.service_rows.values() if r.status == "starting")

        theme = getattr(self, "theme", "figma")
        if theme == "figma":
            if running == total and total > 0:
                self.overall_status_badge.setText(f"● {running}/{total} Running")
                self.overall_status_badge.setStyleSheet("font-size: 11px; font-weight: 800; border: 1.5px solid #16A34A; border-radius: 10px; padding: 4px 10px; background-color: #DCFCE7; color: #15803D;")
                self.main_btn.setText("⏹ Stop Stack")
                self.main_btn.setStyleSheet("background-color: #DC2626; color: #FFFFFF; font-weight: 900; font-size: 12px; border: 2px solid #111111; border-radius: 12px; padding: 7px 18px;")
            elif running > 0 or starting > 0:
                self.overall_status_badge.setText(f"⏳ {running}/{total} Running")
                self.overall_status_badge.setStyleSheet("font-size: 11px; font-weight: 800; border: 1.5px solid #D97706; border-radius: 10px; padding: 4px 10px; background-color: #FEF3C7; color: #B45309;")
                self.main_btn.setText("⏹ Stop Stack")
                self.main_btn.setStyleSheet("background-color: #DC2626; color: #FFFFFF; font-weight: 900; font-size: 12px; border: 2px solid #111111; border-radius: 12px; padding: 7px 18px;")
            else:
                self.overall_status_badge.setText("● Stopped")
                self.overall_status_badge.setStyleSheet("font-size: 11px; font-weight: 800; border: 1.5px solid #111111; border-radius: 10px; padding: 4px 10px; background-color: #F3F4F6; color: #4B5563;")
                self.main_btn.setText(f"▶ Start Stack ({total})")
                self.main_btn.setStyleSheet("background-color: #111111; color: #FFFFFF; font-weight: 900; font-size: 12px; border: 2px solid #111111; border-radius: 12px; padding: 7px 18px;")
        else:
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
            if not u and r.service.get("port"):
                u = f"http://localhost:{r.service['port']}"
            if u:
                urls.append(u)
        if urls:
            self.open_urls_clicked.emit(urls)

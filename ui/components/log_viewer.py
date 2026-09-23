"""
Live Log Viewer component for DevDeck.
Handles streaming stdout/stderr, ANSI color parsing, auto-scroll, searching, and filtering.
"""

import re
import html
from PyQt6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QCheckBox, QToolButton, QStyleOption, QStyle
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QPainter

# ANSI Color Map to Hex
ANSI_COLORS = {
    30: "#94a3b8", 31: "#f87171", 32: "#4ade80", 33: "#fde047",
    34: "#60a5fa", 35: "#c084fc", 36: "#2dd4bf", 37: "#f1f5f9",
    90: "#64748b", 91: "#ef4444", 92: "#22c55e", 93: "#eab308",
    94: "#3b82f6", 95: "#a855f7", 96: "#06b6d4", 97: "#ffffff",
}

ANSI_PATTERN = re.compile(r'\x1b\[([0-9;]*)m')

def ansi_to_html(text: str) -> str:
    """Converts ANSI terminal color escapes to HTML spans."""
    escaped = html.escape(text)
    
    def replace_ansi(match):
        codes = match.group(1).split(';')
        if not codes or codes == [''] or codes == ['0']:
            return '</span>'
        
        styles = []
        for code in codes:
            if not code.isdigit():
                continue
            c = int(code)
            if c in ANSI_COLORS:
                styles.append(f"color: {ANSI_COLORS[c]};")
            elif c == 1:
                styles.append("font-weight: bold;")
            elif c == 4:
                styles.append("text-decoration: underline;")
            elif c == 0:
                return '</span>'
        
        if styles:
            return f'<span style="{" ".join(styles)}">'
        return ''

    formatted = ANSI_PATTERN.sub(replace_ansi, escaped)
    # Convert newlines to breaks
    formatted = formatted.replace('\n', '<br>')
    return formatted

class LogViewer(QFrame):
    """Integrated Console Log Viewer with live streaming and ANSI support."""
    close_requested = pyqtSignal()
    open_url_requested = pyqtSignal(str)
    fullscreen_toggled = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_project_id = None
        self.current_project_name = ""
        self.current_url = ""
        self.auto_scroll = True
        self._is_fullscreen = False
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)
        super().paintEvent(event)

    def _init_ui(self):
        self.setObjectName("LogDrawer")
        self.setStyleSheet("""
            QFrame#LogDrawer {
                background-color: #0A0A0A;
                border: 2px solid #111111;
                border-radius: 16px;
            }
            QTextEdit#LogViewer {
                background-color: #000000;
                color: #00FF66;
                border: 1px solid #222222;
                border-radius: 10px;
                font-family: 'JetBrains Mono', 'Fira Code', 'DejaVu Sans Mono', monospace;
                font-size: 12px;
                padding: 10px;
                selection-background-color: #2563EB;
            }
            QLineEdit#LogSearch {
                background-color: #1A1A1A;
                color: #FFFFFF;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QLineEdit#LogSearch:focus {
                border: 1px solid #FFC107;
            }
            QCheckBox#LogAutoScroll {
                color: #FFFFFF;
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }
            QCheckBox#LogAutoScroll::indicator {
                width: 14px;
                height: 14px;
                border: 1.5px solid #666666;
                border-radius: 4px;
                background-color: #1A1A1A;
            }
            QCheckBox#LogAutoScroll::indicator:checked {
                background-color: #FFC107;
                border: 1.5px solid #FFC107;
            }
            QPushButton#LogBtn {
                background-color: #1A1A1A;
                color: #E5E7EB;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#LogBtn:hover {
                background-color: #2A2A2A;
                color: #FFFFFF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 12)
        layout.setSpacing(8)

        # Top Control Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Project Info Header
        self.title_label = QLabel("📋 Console Logs: No project selected")
        self.title_label.setStyleSheet("font-weight: 800; font-size: 12px; color: #FFFFFF; background: transparent;")
        toolbar.addWidget(self.title_label)

        # URL button if detected
        self.url_btn = QPushButton("🌐 Open URL")
        self.url_btn.setObjectName("BrowserBtn")
        self.url_btn.setVisible(False)
        self.url_btn.setStyleSheet("""
            QPushButton#BrowserBtn {
                background-color: #2563EB;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#BrowserBtn:hover {
                background-color: #1D4ED8;
            }
        """)
        self.url_btn.clicked.connect(self._on_open_url_clicked)
        toolbar.addWidget(self.url_btn)

        toolbar.addStretch()

        # Search / Filter
        self.search_input = QLineEdit()
        self.search_input.setObjectName("LogSearch")
        self.search_input.setPlaceholderText("Filter logs...")
        self.search_input.setStyleSheet("max-width: 180px; padding: 4px 8px; font-size: 11px; background-color: #1A1A1A; color: #FFFFFF; border: 1px solid #333333; border-radius: 8px;")
        self.search_input.textChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.search_input)

        # Auto-scroll checkbox
        self.scroll_cb = QCheckBox("Autoscroll")
        self.scroll_cb.setObjectName("LogAutoScroll")
        self.scroll_cb.setChecked(True)
        self.scroll_cb.setStyleSheet("color: #A3A3A3; font-size: 11px; font-weight: 600; background: transparent;")
        self.scroll_cb.toggled.connect(self._on_scroll_toggled)
        toolbar.addWidget(self.scroll_cb)

        # Clear Logs Button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("LogBtn")
        self.clear_btn.setStyleSheet("background-color: #1A1A1A; color: #E5E7EB; border: 1px solid #333333; border-radius: 8px; padding: 4px 10px; font-size: 11px; font-weight: 700;")
        self.clear_btn.clicked.connect(self.clear_logs)
        toolbar.addWidget(self.clear_btn)

        # Copy Logs Button
        self.copy_btn = QPushButton("Copy All")
        self.copy_btn.setObjectName("LogBtn")
        self.copy_btn.setStyleSheet("background-color: #1A1A1A; color: #E5E7EB; border: 1px solid #333333; border-radius: 8px; padding: 4px 10px; font-size: 11px; font-weight: 700;")
        self.copy_btn.clicked.connect(self._copy_all)
        toolbar.addWidget(self.copy_btn)

        # Fullscreen / Maximize Button
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setFixedSize(32, 32)
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A1A1A;
                color: #A3A3A3;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 0px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border-color: #555555;
            }
        """)
        self.fullscreen_btn.setToolTip("Toggle Fullscreen Console (Ctrl+Shift+L)")
        self.fullscreen_btn.clicked.connect(self._toggle_fullscreen)
        toolbar.addWidget(self.fullscreen_btn)

        # Close / Minimize Button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1A1A1A;
                color: #888888;
                border: 1px solid #333333;
                border-radius: 8px;
                padding: 0px;
                font-size: 15px;
                font-weight: 900;
            }
            QPushButton:hover {
                background-color: #7F1D1D;
                color: #F87171;
                border-color: #DC2626;
            }
        """)
        self.close_btn.setToolTip("Close Console Drawer (Ctrl+L)")
        self.close_btn.clicked.connect(self.close_requested.emit)
        toolbar.addWidget(self.close_btn)

        layout.addLayout(toolbar)

        # Text Console
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("LogViewer")
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setStyleSheet("background-color: #000000; color: #E5E7EB; border: 1px solid #222222; border-radius: 10px; font-family: monospace; font-size: 12px; padding: 10px;")
        layout.addWidget(self.text_edit)

    def _toggle_fullscreen(self):
        self._is_fullscreen = not getattr(self, "_is_fullscreen", False)
        self.set_fullscreen_state(self._is_fullscreen)
        self.fullscreen_toggled.emit(self._is_fullscreen)

    def set_fullscreen_state(self, is_fs: bool):
        self._is_fullscreen = is_fs
        if is_fs:
            self.fullscreen_btn.setText("🗗")
            self.fullscreen_btn.setToolTip("Restore Console Size (Ctrl+Shift+L)")
        else:
            self.fullscreen_btn.setText("⛶")
            self.fullscreen_btn.setToolTip("Maximize Console Fullscreen (Ctrl+Shift+L)")

    def set_active_project(self, project_id: str, project_name: str, url: str = ""):
        self.current_project_id = project_id
        self.current_project_name = project_name
        self.title_label.setText(f"📋 Console Logs: {project_name}")
        self.set_url(url)

    def set_url(self, url: str):
        self.current_url = url or ""
        if self.current_url:
            self.url_btn.setText(f"🌐 {self.current_url}")
            self.url_btn.setVisible(True)
        else:
            self.url_btn.setVisible(False)

    def append_log(self, text: str, is_stderr: bool = False):
        formatted = ansi_to_html(text)
        if is_stderr and "<span" not in formatted:
            formatted = f'<span style="color: #f87171;">{formatted}</span>'

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(formatted)

        if self.auto_scroll:
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def clear_logs(self):
        self.text_edit.clear()

    def _copy_all(self):
        self.text_edit.selectAll()
        self.text_edit.copy()
        cursor = self.text_edit.textCursor()
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)

    def _on_scroll_toggled(self, checked: bool):
        self.auto_scroll = checked
        if checked:
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def _on_filter_changed(self, text: str):
        # Basic find in text edit
        if not text:
            return
        cursor = self.text_edit.document().find(text)
        if not cursor.isNull():
            self.text_edit.setTextCursor(cursor)

    def _on_open_url_clicked(self):
        if self.current_url:
            self.open_url_requested.emit(self.current_url)

"""
Live Log Viewer component for DevDeck.
Handles streaming stdout/stderr, ANSI color parsing, auto-scroll, searching, and filtering.
Styled with Figma theme (purple/violet color scheme).
"""

import re
import html
from PyQt6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QLineEdit, QCheckBox, QToolButton, QStyleOption, QStyle
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QPainter

# ANSI Color Map to Hex (adjusted for dark terminal on purple theme)
ANSI_COLORS = {
    30: "#9070a0", 31: "#f87171", 32: "#4ade80", 33: "#fde047",
    34: "#60a5fa", 35: "#c084fc", 36: "#2dd4bf", 37: "#e0d0f0",
    90: "#705080", 91: "#ef4444", 92: "#22c55e", 93: "#eab308",
    94: "#3b82f6", 95: "#a855f7", 96: "#06b6d4", 97: "#ffffff",
}

ANSI_PATTERN = re.compile(r'\x1b\[([0-9;]*)m')

def ansi_to_html(text: str) -> str:
    """Converts ANSI terminal color escapes to HTML spans.

    The style attribute value must be quoted or Qt discards the color
    entirely, and any span left open at a chunk boundary is closed so the
    console output stays well-formed.
    """
    escaped = html.escape(text)
    state = {"open": 0}

    def replace_ansi(match):
        codes = match.group(1).split(";")
        if not codes or codes == [""] or codes == ["0"]:
            if state["open"]:
                state["open"] -= 1
            return "</span>" if state["open"] >= 0 else ""

        styles = []
        for code in codes:
            if not code.isdigit():
                continue
            c = int(code)
            if c in ANSI_COLORS:
                styles.append("color: %s;" % ANSI_COLORS[c])
            elif c == 1:
                styles.append("font-weight: bold;")
            elif c == 4:
                styles.append("text-decoration: underline;")
            elif c == 0:
                if state["open"]:
                    state["open"] -= 1
                return "</span>" if state["open"] >= 0 else ""

        if not styles:
            return ""
        state["open"] += 1
        joined = " ".join(styles)
        return '<span style="' + joined + '">'

    formatted = ANSI_PATTERN.sub(replace_ansi, escaped)
    formatted += "</span>" * state["open"]
    # Convert newlines to breaks
    formatted = formatted.replace("\n", "<br>")
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 12)
        layout.setSpacing(8)

        # Top Control Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Project Info Header
        self.title_label = QLabel("Console  ·  no project selected")
        self.title_label.setObjectName("LogTitle")
        toolbar.addWidget(self.title_label)

        # URL button if detected
        self.url_btn = QPushButton("Open URL")
        self.url_btn.setObjectName("LogBtn")
        self.url_btn.setVisible(False)
        self.url_btn.clicked.connect(self._on_open_url_clicked)
        toolbar.addWidget(self.url_btn)

        toolbar.addStretch()

        # Search / Filter
        self.search_input = QLineEdit()
        self.search_input.setObjectName("LogSearch")
        self.search_input.setPlaceholderText("Find in logs…")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(150)
        self.search_input.textChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self.search_input)

        # Auto-scroll checkbox
        self.scroll_cb = QCheckBox("Autoscroll")
        self.scroll_cb.setObjectName("LogAutoScroll")
        self.scroll_cb.setChecked(True)
        self.scroll_cb.toggled.connect(self._on_scroll_toggled)
        toolbar.addWidget(self.scroll_cb)

        # Clear Logs Button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("LogBtn")
        self.clear_btn.clicked.connect(self.clear_logs)
        toolbar.addWidget(self.clear_btn)

        # Copy Logs Button
        self.copy_btn = QPushButton("Copy All")
        self.copy_btn.setObjectName("LogBtn")
        self.copy_btn.clicked.connect(self._copy_all)
        toolbar.addWidget(self.copy_btn)

        # Fullscreen / Maximize Button. Uses text rather than an arrow glyph:
        # the geometric arrows (U+2922 etc.) are missing from common Linux
        # UI fonts and render as tofu boxes.
        self.fullscreen_btn = QPushButton("Max")
        self.fullscreen_btn.setFixedWidth(42)
        self.fullscreen_btn.setObjectName("LogBtn")
        self.fullscreen_btn.setToolTip("Maximize Console (Ctrl+Shift+L)")
        self.fullscreen_btn.clicked.connect(self._toggle_fullscreen)
        toolbar.addWidget(self.fullscreen_btn)

        # Close / Minimize Button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(26, 26)
        self.close_btn.setToolTip("Close Console Drawer (Ctrl+L)")
        self.close_btn.clicked.connect(self.close_requested.emit)
        toolbar.addWidget(self.close_btn)

        layout.addLayout(toolbar)

        # Text Console
        self.text_edit = QTextEdit()
        self.text_edit.setObjectName("LogViewer")
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.text_edit)

    def _toggle_fullscreen(self):
        self._is_fullscreen = not getattr(self, "_is_fullscreen", False)
        self.set_fullscreen_state(self._is_fullscreen)
        self.fullscreen_toggled.emit(self._is_fullscreen)

    def set_fullscreen_state(self, is_fs: bool):
        self._is_fullscreen = is_fs
        if is_fs:
            self.fullscreen_btn.setText("Restore")
            self.fullscreen_btn.setToolTip("Restore Console Size (Ctrl+Shift+L)")
        else:
            self.fullscreen_btn.setText("Max")
            self.fullscreen_btn.setToolTip("Maximize Console (Ctrl+Shift+L)")

    def set_active_project(self, project_id: str, project_name: str, url: str = ""):
        self.current_project_id = project_id
        self.current_project_name = project_name
        self.title_label.setText(f"Console  ·  {project_name}")
        self.set_url(url)

    def set_url(self, url: str):
        self.current_url = url or ""
        if self.current_url:
            label = self.current_url.replace("http://", "").replace("https://", "").rstrip("/")
            if len(label) > 22:
                label = label[:20] + "…"
            self.url_btn.setText(label if len(label) <= 20 else label[:18] + "…")
            self.url_btn.setToolTip(f"Open {self.current_url} in Browser")
            self.url_btn.setVisible(True)
        else:
            self.url_btn.setVisible(False)

    def append_log(self, text: str, is_stderr: bool = False):
        if not text:
            return
        formatted = ansi_to_html(text)
        if is_stderr and "<span" not in formatted:
            formatted = f'<span style="color: {ANSI_COLORS[31]};">{formatted}</span>'

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(formatted)

        if self.auto_scroll:
            self.text_edit.moveCursor(QTextCursor.MoveOperation.End)

    def clear_logs(self):
        self.text_edit.clear()
        self._log_line_count = 0

    def _on_filter_changed(self, text: str):
        # Highlight the next match; the console itself is never rewritten.
        if not text:
            return
        cursor = self.text_edit.document().find(text)
        if not cursor.isNull():
            self.text_edit.setTextCursor(cursor)
            self.text_edit.ensureCursorVisible()

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

    def _on_open_url_clicked(self):
        if self.current_url:
            self.open_url_requested.emit(self.current_url)
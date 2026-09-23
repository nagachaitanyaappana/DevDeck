"""
Modern Dark Theme and Styles for DevDeck.
Carefully designed for high contrast, clean typography, and sleek developer aesthetics.
"""

DARK_THEME_QSS = """
/* Global Window & Fonts */
QWidget {
    background-color: #0f141c;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif;
    font-size: 13px;
    outline: none;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0f141c;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #273349;
    min-height: 25px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #3b4d6e;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    border: none;
    background: #0f141c;
    height: 8px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #273349;
    min-width: 25px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #3b4d6e;
}

/* Header & Toolbars */
QFrame#HeaderBar {
    background-color: #151b27;
    border-bottom: 1px solid #222c3e;
    padding: 12px 20px;
}

QLabel#AppTitle {
    font-size: 19px;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: 0.5px;
}

QLabel#AppSubtitle {
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
}

/* Stats Badges */
QFrame#StatBadge {
    background-color: #1e2638;
    border: 1px solid #2d3952;
    border-radius: 6px;
    padding: 4px 10px;
}
QLabel#StatValue {
    font-weight: 700;
    font-size: 13px;
    color: #60a5fa;
}
QLabel#StatLabel {
    font-size: 11px;
    color: #94a3b8;
}

/* Search & Input Fields */
QLineEdit#SearchBar {
    background-color: #182030;
    border: 1px solid #2a374e;
    border-radius: 8px;
    padding: 7px 14px;
    color: #f1f5f9;
    font-size: 13px;
    min-width: 220px;
}
QLineEdit#SearchBar:focus {
    border: 1px solid #6366f1;
    background-color: #1d273a;
}

/* Buttons */
QPushButton {
    background-color: #1e2638;
    border: 1px solid #2e3a50;
    border-radius: 7px;
    padding: 6px 14px;
    color: #e2e8f0;
    font-weight: 600;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #27334b;
    border-color: #40506e;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #171d2b;
}

QPushButton#PrimaryBtn {
    background-color: #4f46e5;
    border: 1px solid #6366f1;
    color: #ffffff;
}
QPushButton#PrimaryBtn:hover {
    background-color: #4338ca;
    border-color: #818cf8;
}

QPushButton#StartBtn {
    background-color: #065f46;
    border: 1px solid #059669;
    color: #ecfdf5;
    font-weight: 700;
    border-radius: 6px;
    padding: 6px 14px;
}
QPushButton#StartBtn:hover {
    background-color: #047857;
    border-color: #10b981;
}

QPushButton#StopBtn {
    background-color: #881337;
    border: 1px solid #e11d48;
    color: #fff1f2;
    font-weight: 700;
    border-radius: 6px;
    padding: 6px 14px;
}
QPushButton#StopBtn:hover {
    background-color: #9f1239;
    border-color: #f43f5e;
}

QPushButton#BrowserBtn {
    background-color: #1e1b4b;
    border: 1px solid #4338ca;
    color: #a5b4fc;
    font-weight: 600;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton#BrowserBtn:hover {
    background-color: #312e81;
    border-color: #6366f1;
    color: #ffffff;
}
QPushButton#BrowserBtn:disabled {
    background-color: #161b24;
    border-color: #232b38;
    color: #475569;
}

QPushButton#IconBtn {
    background-color: #182030;
    border: 1px solid #283449;
    border-radius: 6px;
    padding: 5px 8px;
    color: #94a3b8;
}
QPushButton#IconBtn:hover {
    background-color: #232e44;
    border-color: #3f5172;
    color: #ffffff;
}

/* Filter Pill Buttons */
QPushButton#FilterPill {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 16px;
    padding: 5px 12px;
    color: #94a3b8;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#FilterPill:hover {
    background-color: #1a2232;
    color: #e2e8f0;
}
QPushButton#FilterPill[checked="true"] {
    background-color: #312e81;
    border: 1px solid #4f46e5;
    color: #c7d2fe;
}

/* Project Card */
QFrame#ProjectCard {
    background-color: #151b27;
    border: 1px solid #222d40;
    border-radius: 10px;
    padding: 12px;
}
QFrame#ProjectCard:hover {
    border-color: #384866;
    background-color: #171e2c;
}
QFrame#ProjectCard[running="true"] {
    border: 1px solid #059669;
    background-color: #14202a;
}

QLabel#CardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #f1f5f9;
}

QLabel#CardPath {
    font-size: 11px;
    color: #64748b;
    font-family: monospace;
}

QLabel#CardCmd {
    font-size: 11px;
    color: #94a3b8;
    background-color: #0d121a;
    border: 1px solid #1f2838;
    border-radius: 4px;
    padding: 3px 6px;
    font-family: monospace;
}

/* Badges */
QLabel#StackBadge {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 11px;
    font-weight: 600;
    color: #cbd5e1;
}

QLabel#StatusBadge {
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#StatusBadge[status="running"] {
    background-color: #064e3b;
    color: #34d399;
    border: 1px solid #059669;
}
QLabel#StatusBadge[status="starting"] {
    background-color: #451a03;
    color: #fbbf24;
    border: 1px solid #d97706;
}
QLabel#StatusBadge[status="stopped"] {
    background-color: #1e2430;
    color: #64748b;
    border: 1px solid #2b3545;
}
QLabel#StatusBadge[status="error"] {
    background-color: #4c0519;
    color: #f87171;
    border: 1px solid #e11d48;
}

QLabel#MetricsLabel {
    font-size: 11px;
    color: #38bdf8;
    font-family: monospace;
    font-weight: 600;
}

/* Log Console Drawer */
QFrame#LogDrawer {
    background-color: #0c0f16;
    border-top: 1px solid #222d40;
}
QTextEdit#LogViewer {
    background-color: #080a0f;
    border: 1px solid #1b2230;
    border-radius: 6px;
    color: #d1d5db;
    font-family: "JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "Courier New", monospace;
    font-size: 12px;
    padding: 8px;
    line-height: 1.4;
}

/* Modal Dialogs */
QDialog {
    background-color: #151b27;
    border: 1px solid #2c3850;
    border-radius: 10px;
}
QLabel#DialogHeader {
    font-size: 16px;
    font-weight: 700;
    color: #f8fafc;
}
QLineEdit, QComboBox {
    background-color: #1b2332;
    border: 1px solid #2e3c54;
    border-radius: 6px;
    padding: 7px 10px;
    color: #f1f5f9;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #6366f1;
}
"""

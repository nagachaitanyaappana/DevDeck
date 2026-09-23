"""
Neo-Clean Figma UI Theme for DevDeck.
Inspired by modern card, modal, and alert design systems:
- Pure white floating cards with 18px rounded corners
- Bold typography and high contrast black action buttons
- Punchy amber/yellow accents
- Soft pill tags and pastel icon squircle containers
"""

FIGMA_THEME_QSS = """
/* Global Window & Fonts */
QWidget {
    background-color: #F8F9FB;
    color: #111827;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif;
    font-size: 13px;
    outline: none;
}

QLabel {
    background-color: transparent;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #F8F9FB;
    width: 8px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #D1D5DB;
    min-height: 25px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #9CA3AF;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    border: none;
    background: #F8F9FB;
    height: 8px;
    margin: 0px;
}
QScrollBar::handle:horizontal {
    background: #D1D5DB;
    min-width: 25px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal:hover {
    background: #9CA3AF;
}

/* ─── Header Bar ─── */
QFrame#HeaderBar {
    background-color: #FFFFFF;
    border-bottom: 2px solid #E5E7EB;
    padding: 14px 24px;
}

QLabel#AppTitle {
    font-size: 20px;
    font-weight: 900;
    color: #111827;
    letter-spacing: -0.5px;
}

QLabel#AppSubtitle {
    font-size: 11px;
    color: #6B7280;
    font-weight: 600;
    letter-spacing: 0.2px;
}

/* Stats Badges: Inspired by the "30K+ downloads" black pill badge */
QFrame#StatBadge {
    background-color: #111827;
    border: 1.5px solid #111827;
    border-radius: 14px;
    padding: 3px 12px;
}
QFrame#StatBadge QLabel {
    background-color: transparent;
}
QFrame#StatBadge QLabel#StatValue {
    font-weight: 800;
    font-size: 13px;
    color: #FCD34D;  /* Punchy Figma Yellow */
    background-color: transparent;
}
QFrame#StatBadge QLabel#StatLabel {
    font-size: 10px;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: 0.5px;
    background-color: transparent;
}

QFrame#FilterBar {
    background-color: #FFFFFF;
    border-bottom: 1.5px solid #E5E7EB;
    padding: 10px 20px;
}

/* ─── Search & Inputs ─── */
QLineEdit#SearchBar {
    background-color: #FFFFFF;
    border: 1.5px solid #E5E7EB;
    border-radius: 12px;
    padding: 8px 16px;
    color: #111827;
    font-size: 13px;
    font-weight: 500;
    min-width: 250px;
}
QLineEdit#SearchBar:focus {
    border: 2px solid #111827;
    background-color: #FFFFFF;
}

/* ─── Filter Pills ─── */
QPushButton#FilterPill {
    background-color: #F3F4F6;
    border: 1.5px solid transparent;
    border-radius: 20px;
    padding: 6px 14px;
    color: #4B5563;
    font-weight: 700;
    font-size: 12px;
}
QPushButton#FilterPill:hover {
    background-color: #E5E7EB;
    color: #111827;
}
QPushButton#FilterPill[checked="true"] {
    background-color: #111827;
    border: 1.5px solid #111827;
    color: #FFFFFF;
}

/* ─── Buttons: Based on the Figma Modal Button Styles ─── */
QPushButton {
    background-color: #F3F4F6;
    border: 1.5px solid #E5E7EB;
    border-radius: 10px;
    padding: 7px 16px;
    color: #111827;
    font-weight: 700;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #E5E7EB;
    border-color: #D1D5DB;
}
QPushButton:pressed {
    background-color: #D1D5DB;
}

/* Solid Black Primary Action (like "Thanks!" button in Figma) */
QPushButton#PrimaryBtn {
    background-color: #111827;
    border: 1.5px solid #111827;
    color: #FFFFFF;
    border-radius: 10px;
    padding: 7px 18px;
    font-weight: 800;
}
QPushButton#PrimaryBtn:hover {
    background-color: #000000;
    border-color: #000000;
}
QPushButton#PrimaryBtn:pressed {
    background-color: #374151;
}

/* Solid Black Start Button */
QPushButton#StartBtn {
    background-color: #111827;
    border: 1.5px solid #111827;
    color: #FFFFFF;
    font-weight: 800;
    border-radius: 10px;
    padding: 7px 18px;
}
QPushButton#StartBtn:hover {
    background-color: #059669;
    border-color: #059669;
}

/* Red Stop Button */
QPushButton#StopBtn {
    background-color: #DC2626;
    border: 1.5px solid #DC2626;
    color: #FFFFFF;
    font-weight: 800;
    border-radius: 10px;
    padding: 7px 18px;
}
QPushButton#StopBtn:hover {
    background-color: #B91C1C;
    border-color: #B91C1C;
}

/* Outline Browser Button (like "Undo" outline button in Figma) */
QPushButton#BrowserBtn {
    background-color: #FFFFFF;
    border: 1.5px solid #111827;
    color: #111827;
    font-weight: 700;
    border-radius: 10px;
    padding: 7px 14px;
}
QPushButton#BrowserBtn:hover {
    background-color: #FEF3C7;
    border-color: #F59E0B;
    color: #92400E;
}
QPushButton#BrowserBtn:disabled {
    background-color: #F9FAFB;
    border-color: #E5E7EB;
    color: #9CA3AF;
}

/* Soft Icon Buttons (like "Undo" soft grey button in Figma) */
QPushButton#IconBtn {
    background-color: #F3F4F6;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 5px 10px;
    color: #374151;
    font-weight: 600;
}
QPushButton#IconBtn:hover {
    background-color: #E5E7EB;
    color: #111827;
}

/* ─── Project Card (Figma Modal / Card Aesthetic) ─── */
QFrame#ProjectCard {
    background-color: #FFFFFF;
    border: 1.5px solid #E5E7EB;
    border-radius: 18px;
    padding: 16px;
}
QFrame#ProjectCard:hover {
    border: 1.5px solid #111827;
    background-color: #FFFFFF;
}
QFrame#ProjectCard[running="true"] {
    border: 2px solid #10B981;
    background-color: #F0FDF4;
}

QLabel#CardTitle {
    font-size: 15px;
    font-weight: 800;
    color: #111827;
    letter-spacing: -0.3px;
}

QLabel#CardPath {
    font-size: 11px;
    color: #6B7280;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-weight: 500;
}

QLabel#CardCmd {
    font-size: 11px;
    color: #374151;
    background-color: #F3F4F6;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 4px 8px;
    font-family: monospace;
    font-weight: 600;
}

/* Icon Squircle (Soft Yellow / Pastel Circle like in Figma design) */
QFrame#IconSquircle {
    background-color: #FEF3C7;
    border: 1px solid #FDE68A;
    border-radius: 20px;
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
}
QLabel#SquircleIcon {
    font-size: 20px;
    background: transparent;
}

/* Badges */
QLabel#StackBadge {
    background-color: #F3F4F6;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 700;
    color: #4B5563;
}

QLabel#StatusBadge {
    border-radius: 8px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 800;
}
QLabel#StatusBadge[status="running"] {
    background-color: #D1FAE5;
    color: #065F46;
    border: 1px solid #A7F3D0;
}
QLabel#StatusBadge[status="starting"] {
    background-color: #FEF3C7;
    color: #92400E;
    border: 1px solid #FDE68A;
}
QLabel#StatusBadge[status="stopped"] {
    background-color: #F3F4F6;
    color: #6B7280;
    border: 1px solid #E5E7EB;
}
QLabel#StatusBadge[status="error"] {
    background-color: #FEE2E2;
    color: #991B1B;
    border: 1px solid #FECACA;
}

QLabel#MetricsLabel {
    font-size: 11px;
    color: #0284C7;
    font-family: monospace;
    font-weight: 700;
}

/* ─── Log Console Drawer (Sleek Dark Terminal) ─── */
QFrame#LogDrawer {
    background-color: #111827;
    border-top: 2px solid #1F2937;
}
QTextEdit#LogViewer {
    background-color: #0B0F19;
    border: 1px solid #1F2937;
    border-radius: 10px;
    color: #F3F4F6;
    font-family: "JetBrains Mono", "Fira Code", "DejaVu Sans Mono", monospace;
    font-size: 12px;
    padding: 10px;
    line-height: 1.5;
}

/* ─── Dialogs & Modals (Matching Figma Popups) ─── */
QDialog {
    background-color: #FFFFFF;
    border: 2px solid #111827;
    border-radius: 20px;
}
QLabel#DialogHeader {
    font-size: 18px;
    font-weight: 900;
    color: #111827;
    letter-spacing: -0.4px;
}
QLineEdit, QComboBox {
    background-color: #F9FAFB;
    border: 1.5px solid #E5E7EB;
    border-radius: 10px;
    padding: 8px 12px;
    color: #111827;
    font-size: 13px;
    font-weight: 500;
}
QLineEdit:focus, QComboBox:focus {
    border: 2px solid #111827;
    background-color: #FFFFFF;
}
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
QPushButton#PrimaryBtn {
    background-color: #4f46e5;
    border: 1px solid #6366f1;
    color: #ffffff;
}
QPushButton#StartBtn {
    background-color: #065f46;
    border: 1px solid #059669;
    color: #ecfdf5;
    font-weight: 700;
}
QPushButton#StopBtn {
    background-color: #881337;
    border: 1px solid #e11d48;
    color: #fff1f2;
    font-weight: 700;
}
QPushButton#BrowserBtn {
    background-color: #1e1b4b;
    border: 1px solid #4338ca;
    color: #a5b4fc;
    font-weight: 600;
}
QPushButton#IconBtn {
    background-color: #182030;
    border: 1px solid #283449;
    border-radius: 6px;
    padding: 5px 8px;
    color: #94a3b8;
}
QPushButton#FilterPill {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 16px;
    padding: 5px 12px;
    color: #94a3b8;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#FilterPill[checked="true"] {
    background-color: #312e81;
    border: 1px solid #4f46e5;
    color: #c7d2fe;
}
QFrame#ProjectCard {
    background-color: #151b27;
    border: 1px solid #222d40;
    border-radius: 12px;
    padding: 12px;
}
QFrame#ProjectCard:hover {
    border-color: #384866;
}
QFrame#ProjectCard[running="true"] {
    border: 1px solid #059669;
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
QFrame#IconSquircle {
    background-color: #1e2638;
    border: 1px solid #2d3952;
    border-radius: 18px;
    min-width: 38px;
    max-width: 38px;
    min-height: 38px;
    max-height: 38px;
}
QLabel#SquircleIcon {
    font-size: 18px;
    background: transparent;
}
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
}
QLabel#StatusBadge[status="starting"] {
    background-color: #451a03;
    color: #fbbf24;
}
QLabel#StatusBadge[status="stopped"] {
    background-color: #1e2430;
    color: #64748b;
}
QLabel#StatusBadge[status="error"] {
    background-color: #4c0519;
    color: #f87171;
}
QFrame#LogDrawer {
    background-color: #0c0f16;
    border-top: 1px solid #222d40;
}
QTextEdit#LogViewer {
    background-color: #080a0f;
    border: 1px solid #1b2230;
    border-radius: 6px;
    color: #d1d5db;
    font-family: monospace;
    font-size: 12px;
    padding: 8px;
}
QDialog {
    background-color: #151b27;
    border: 1px solid #2c3850;
    border-radius: 10px;
}
QLineEdit, QComboBox {
    background-color: #1b2332;
    border: 1px solid #2e3c54;
    border-radius: 6px;
    padding: 7px 10px;
    color: #f1f5f9;
}
"""


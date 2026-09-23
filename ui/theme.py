"""
Figma-Inspired Theme for DevDeck.

Design language from reference:
- Bright warm yellow/amber background (#FFC107 / #FFCC00)
- Pure white floating cards with generous border-radius (16-20px) and soft box shadows
- Very bold black typography (900 weight)
- Soft pastel yellow circular icon containers behind emoji
- Solid black pill buttons, grey outline buttons
- Grey ✕ close icons top-right on cards
- Toast-style notification bars
"""

FIGMA_THEME_QSS = """
/* ─── Global ─── */
QWidget {
    background-color: #FFC107;
    color: #111111;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif;
    font-size: 13px;
    outline: none;
}

QLabel {
    background-color: transparent;
}

/* ─── App Shell (Rounded floating container) ─── */
QFrame#AppShell {
    background-color: #FFC107;
    border-radius: 22px;
    border: none;
}

/* ─── Window Control Buttons ─── */
QPushButton#WinCtrlBtn {
    background-color: rgba(0, 0, 0, 0.08);
    border: none;
    border-radius: 8px;
    color: #555555;
    font-weight: 800;
    font-size: 13px;
    padding: 2px;
}
QPushButton#WinCtrlBtn:hover {
    background-color: rgba(0, 0, 0, 0.15);
    color: #111111;
}
QPushButton#WinCloseBtn {
    background-color: rgba(0, 0, 0, 0.08);
    border: none;
    border-radius: 8px;
    color: #555555;
    font-weight: 800;
    font-size: 13px;
    padding: 2px;
}
QPushButton#WinCloseBtn:hover {
    background-color: #D32F2F;
    color: #FFFFFF;
}

/* ─── Scrollbars ─── */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: rgba(0, 0, 0, 0.15);
    min-height: 30px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(0, 0, 0, 0.3);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: rgba(0, 0, 0, 0.15);
    min-width: 30px;
    border-radius: 4px;
}

/* ─── Hero Left Sidebar (Figma Reference Style) ─── */
QFrame#HeroPanel {
    background: transparent;
    border: none;
}

QLabel#HeroTitle {
    font-size: 32px;
    font-weight: 900;
    color: #111111;
    letter-spacing: -1.2px;
}

QLabel#HeroSubtitle {
    font-size: 13px;
    font-weight: 700;
    color: #444444;
}

/* ─── Header Bar: Floating white card on yellow canvas ─── */
QFrame#HeaderBar {
    background-color: #FFFFFF;
    border: none;
    border-radius: 20px;
    padding: 14px 24px;
}

QLabel#AppTitle {
    font-size: 22px;
    font-weight: 900;
    color: #111111;
    letter-spacing: -0.5px;
}

QLabel#AppSubtitle {
    font-size: 11px;
    color: #888888;
    font-weight: 600;
}

/* ─── Filter Bar ─── */
QFrame#FilterBar {
    background-color: transparent;
    border: none;
    padding: 4px 4px;
}

/* ─── Search ─── */
QLineEdit#SearchBar {
    background-color: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 14px;
    padding: 9px 16px;
    color: #111111;
    font-size: 13px;
    font-weight: 600;
    min-width: 250px;
}
QLineEdit#SearchBar:focus {
    border: 2.5px solid #000000;
}

/* ─── Filter Pills ─── */
QPushButton#FilterPill {
    background-color: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 14px;
    padding: 6px 12px;
    color: #111111;
    font-weight: 800;
    font-size: 11px;
}
QPushButton#FilterPill:hover {
    background-color: #FFF9C4;
}
QPushButton#FilterPill[checked="true"] {
    background-color: #111111;
    color: #FFFFFF;
    border: 2px solid #111111;
}

/* ─── Buttons (default) ─── */
QPushButton {
    background-color: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 12px;
    padding: 7px 16px;
    color: #111111;
    font-weight: 800;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #FFF9C4;
}
QPushButton:pressed {
    background-color: #EEEEEE;
}

/* Solid Black Primary ("Thanks!" style) */
QPushButton#PrimaryBtn {
    background-color: #111111;
    border: 2px solid #111111;
    color: #FFFFFF;
    border-radius: 14px;
    padding: 8px 18px;
    font-weight: 900;
    font-size: 13px;
}
QPushButton#PrimaryBtn:hover {
    background-color: #333333;
}

/* Start = Solid Black */
QPushButton#StartBtn {
    background-color: #111111;
    border: 2px solid #111111;
    color: #FFFFFF;
    font-weight: 900;
    border-radius: 12px;
    padding: 7px 16px;
    font-size: 12px;
}
QPushButton#StartBtn:hover {
    background-color: #16A34A;
    border-color: #16A34A;
}

/* Stop = Red */
QPushButton#StopBtn {
    background-color: #DC2626;
    border: 2px solid #111111;
    color: #FFFFFF;
    font-weight: 900;
    border-radius: 12px;
    padding: 7px 16px;
    font-size: 12px;
}
QPushButton#StopBtn:hover {
    background-color: #B91C1C;
}

/* Browser = Outline ("Undo" style) */
QPushButton#BrowserBtn {
    background-color: #FFFFFF;
    border: 2px solid #111111;
    color: #111111;
    font-weight: 800;
    border-radius: 12px;
    padding: 7px 14px;
    font-size: 12px;
}
QPushButton#BrowserBtn:hover {
    background-color: #FFF9C4;
}
QPushButton#BrowserBtn:disabled {
    background-color: #F3F4F6;
    border-color: #9CA3AF;
    color: #9CA3AF;
}

/* Soft grey icon buttons */
QPushButton#IconBtn {
    background-color: #FFFFFF;
    border: 1.5px solid #111111;
    border-radius: 10px;
    padding: 5px 8px;
    color: #111111;
    font-weight: 700;
}
QPushButton#IconBtn:hover {
    background-color: #FFF9C4;
    border-color: #000000;
}

/* ─── Project Card (White floating modal with crisp black border) ─── */
QFrame#ProjectCard {
    background-color: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 18px;
    padding: 14px;
}
QFrame#ProjectCard:hover {
    background-color: #FFFFFF;
    border: 2.5px solid #000000;
}
QFrame#ProjectCard[running="true"] {
    border: 3px solid #16A34A;
    background-color: #FFFFFF;
}

QLabel#CardTitle {
    font-size: 15px;
    font-weight: 900;
    color: #111111;
    letter-spacing: -0.3px;
}

QLabel#CardPath {
    font-size: 11px;
    color: #666666;
    font-weight: 600;
}

QLabel#CardCmd {
    font-size: 11px;
    color: #111111;
    background-color: #F9FAFB;
    border: 1.5px solid #111111;
    border-radius: 8px;
    padding: 4px 8px;
    font-family: monospace;
    font-weight: 700;
}

/* Icon Squircle (soft pastel yellow circle with black border) */
QFrame#IconSquircle {
    background-color: #FFF3CD;
    border: 2px solid #111111;
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
    background-color: #FFFFFF;
    border: 1.5px solid #111111;
    border-radius: 8px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 800;
    color: #111111;
}

QLabel#StatusBadge {
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 800;
    border: 1.5px solid #111111;
}
QLabel#StatusBadge[status="running"] {
    background-color: #DCFCE7;
    color: #15803D;
    border: 1.5px solid #16A34A;
}
QLabel#StatusBadge[status="starting"] {
    background-color: #FEF3C7;
    color: #B45309;
    border: 1.5px solid #D97706;
}
QLabel#StatusBadge[status="stopped"] {
    background-color: #F3F4F6;
    color: #4B5563;
    border: 1.5px solid #111111;
}
QLabel#StatusBadge[status="error"] {
    background-color: #FEE2E2;
    color: #B91C1C;
    border: 1.5px solid #DC2626;
}

QLabel#MetricsLabel {
    font-size: 11px;
    color: #0284C7;
    font-family: monospace;
    font-weight: 700;
}

/* ─── Log Console (Dark terminal feel with clean black border) ─── */
QFrame#LogDrawer {
    background-color: #0A0A0A;
    border: 2px solid #111111;
    border-radius: 16px;
}
QTextEdit#LogViewer {
    background-color: #000000;
    border: 1px solid #222222;
    border-radius: 10px;
    color: #E5E7EB;
    font-family: "JetBrains Mono", "Fira Code", "DejaVu Sans Mono", monospace;
    font-size: 12px;
    padding: 10px;
}

/* ─── Dialogs ─── */
QDialog {
    background-color: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 18px;
}
QLabel#DialogHeader {
    font-size: 20px;
    font-weight: 900;
    color: #111111;
}
QLineEdit {
    background-color: #F9FAFB;
    border: 2px solid #111111;
    border-radius: 10px;
    padding: 8px 12px;
    color: #111111;
    font-size: 13px;
    font-weight: 600;
}
QLineEdit:focus {
    border: 2px solid #000000;
    background-color: #FFFFFF;
}

/* ─── Combo Boxes & Dropdown Menus (High-Contrast Fix) ─── */
QComboBox {
    background-color: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 10px;
    padding: 7px 12px;
    color: #111111;
    font-size: 12px;
    font-weight: 700;
}
QComboBox:hover {
    background-color: #FFFDE7;
    border-color: #000000;
}
QComboBox:focus {
    border: 2px solid #111111;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    border-left: 1.5px solid #111111;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    background-color: #F3F4F6;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #111111;
    width: 0;
    height: 0;
}
QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #111111;
    border: 2px solid #111111;
    border-radius: 10px;
    padding: 4px;
    outline: none;
    selection-background-color: #FFC107;
    selection-color: #111111;
}
QComboBox QAbstractItemView::item {
    color: #111111;
    background-color: #FFFFFF;
    padding: 8px 12px;
    min-height: 24px;
    border-radius: 6px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #FFF3C4;
    color: #111111;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #FFC107;
    color: #111111;
    font-weight: 800;
}

/* ─── Context Menus (High-Contrast Fix) ─── */
QMenu {
    background-color: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 12px;
    padding: 6px;
    color: #111111;
}
QMenu::item {
    padding: 8px 20px;
    border-radius: 8px;
    color: #111111;
    background-color: transparent;
    font-weight: 600;
}
QMenu::item:hover, QMenu::item:selected {
    background-color: #FFF8E1;
    color: #111111;
    font-weight: 800;
}
QMenu::separator {
    height: 1px;
    background-color: #E5E7EB;
    margin: 4px 8px;
}

/* ─── Message Boxes & Input Dialogs ─── */
QMessageBox, QInputDialog {
    background-color: #FFFFFF;
    color: #111111;
    border: 2px solid #111111;
    border-radius: 16px;
}
QMessageBox QLabel, QInputDialog QLabel {
    color: #111111;
    font-size: 13px;
    font-weight: 700;
    background: transparent;
}
QMessageBox QPushButton, QInputDialog QPushButton {
    background-color: #FFFFFF;
    color: #111111;
    border: 2px solid #111111;
    border-radius: 10px;
    padding: 6px 18px;
    font-weight: 800;
    font-size: 12px;
    min-width: 70px;
}
QMessageBox QPushButton:hover, QInputDialog QPushButton:hover {
    background-color: #FFF9C4;
}
"""

DARK_THEME_QSS = """
/* ─── Global ─── */
QWidget {
    background-color: #0f141c;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif;
    font-size: 13px;
    outline: none;
}

QLabel {
    background-color: transparent;
}

QFrame#AppShell {
    background-color: #0f141c;
    border-radius: 22px;
    border: 1px solid #1e2638;
}

QPushButton#WinCtrlBtn {
    background-color: #1e2638;
    border: none;
    border-radius: 8px;
    color: #94a3b8;
    font-weight: 800;
    font-size: 13px;
    padding: 2px;
}
QPushButton#WinCtrlBtn:hover {
    background-color: #273349;
    color: #ffffff;
}
QPushButton#WinCloseBtn {
    background-color: #1e2638;
    border: none;
    border-radius: 8px;
    color: #94a3b8;
    font-weight: 800;
    font-size: 13px;
    padding: 2px;
}
QPushButton#WinCloseBtn:hover {
    background-color: #e11d48;
    color: #ffffff;
}

QScrollBar:vertical {
    border: none;
    background: #0f141c;
    width: 8px;
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
}
QScrollBar::handle:horizontal {
    background: #273349;
    min-width: 25px;
    border-radius: 4px;
}

/* ─── Hero Left Sidebar (Figma Reference Style) ─── */
QFrame#HeroPanel {
    background: transparent;
    border: none;
}

QLabel#HeroTitle {
    font-size: 32px;
    font-weight: 900;
    color: #f8fafc;
    letter-spacing: -1.2px;
}

QLabel#HeroSubtitle {
    font-size: 13px;
    font-weight: 700;
    color: #94a3b8;
}

QFrame#HeaderBar {
    background-color: #151b27;
    border-bottom: 1px solid #222c3e;
    border-radius: 16px;
    padding: 12px 20px;
}
QLabel#AppTitle {
    font-size: 19px;
    font-weight: 800;
    color: #f8fafc;
}
QLabel#AppSubtitle {
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
}

QFrame#FilterBar {
    background-color: #121824;
    border-bottom: 1px solid #1e2638;
    padding: 8px 20px;
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
QLabel#MetricsLabel {
    font-size: 11px;
    color: #38bdf8;
    font-family: monospace;
    font-weight: 600;
}

QFrame#LogDrawer {
    background-color: #0c0f16;
    border-top: 1px solid #222d40;
    border-bottom-left-radius: 22px;
    border-bottom-right-radius: 22px;
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
    border-radius: 12px;
}
QLineEdit {
    background-color: #1b2332;
    border: 1px solid #2e3c54;
    border-radius: 6px;
    padding: 7px 10px;
    color: #f1f5f9;
}
QLineEdit:focus {
    border: 1px solid #3b82f6;
}

QComboBox {
    background-color: #1b2332;
    border: 1.5px solid #2e3c54;
    border-radius: 6px;
    padding: 7px 10px;
    color: #f1f5f9;
    font-weight: 600;
}
QComboBox:hover {
    border-color: #3b82f6;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #2e3c54;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
    background-color: #242f44;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #94a3b8;
    width: 0;
    height: 0;
}
QComboBox QAbstractItemView {
    background-color: #151b27;
    color: #f1f5f9;
    border: 1px solid #2e3c54;
    border-radius: 6px;
    padding: 4px;
    outline: none;
    selection-background-color: #2563EB;
    selection-color: #ffffff;
}
QComboBox QAbstractItemView::item {
    color: #f1f5f9;
    background-color: #151b27;
    padding: 6px 10px;
    min-height: 22px;
    border-radius: 4px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #1e2638;
    color: #ffffff;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #2563EB;
    color: #ffffff;
    font-weight: bold;
}

QMenu {
    background-color: #1e2638;
    border: 1px solid #2e3c54;
    border-radius: 8px;
    padding: 4px;
    color: #f1f5f9;
}
QMenu::item {
    padding: 6px 16px;
    border-radius: 4px;
    color: #f1f5f9;
    background-color: transparent;
}
QMenu::item:hover, QMenu::item:selected {
    background-color: #2563EB;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background-color: #2e3c54;
    margin: 4px 6px;
}

QMessageBox, QInputDialog {
    background-color: #151b27;
    color: #f1f5f9;
    border: 1px solid #2e3c54;
    border-radius: 12px;
}
QMessageBox QLabel, QInputDialog QLabel {
    color: #f1f5f9;
    font-size: 13px;
    font-weight: 600;
    background: transparent;
}
QMessageBox QPushButton, QInputDialog QPushButton {
    background-color: #1e2638;
    color: #f1f5f9;
    border: 1px solid #2e3c54;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    min-width: 60px;
}
QMessageBox QPushButton:hover, QInputDialog QPushButton:hover {
    background-color: #2563EB;
    color: #ffffff;
}
"""

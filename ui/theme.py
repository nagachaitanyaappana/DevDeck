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
    border: 2px solid #111111;
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
    border-radius: 12px;
    padding: 7px 12px;
    font-size: 13px;
    color: #111111;
    font-weight: 800;
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

QSpinBox {
    background-color: #FFFFFF;
    border: 2px solid #111111;
    border-radius: 10px;
    padding: 6px 10px;
    color: #111111;
    font-weight: 700;
    font-size: 13px;
}
QSpinBox:focus {
    border: 2px solid #000000;
}

QToolTip {
    background-color: #111111;
    color: #FFFFFF;
    border: 1px solid #333333;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 600;
}
"""

DARK_THEME_QSS = """
/* ─── Global ─── */
QWidget {
    background-color: #030712;
    color: #f9fafb;
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "Helvetica Neue", Ubuntu, sans-serif;
    font-size: 13px;
    outline: none;
}

QLabel {
    background-color: transparent;
}

QFrame#AppShell {
    background-color: #030712;
    border-radius: 16px;
    border: 1px solid #1f2937;
}

QPushButton#WinCtrlBtn {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 6px;
    color: #9ca3af;
    font-weight: 700;
    font-size: 12px;
    padding: 2px;
}
QPushButton#WinCtrlBtn:hover {
    background-color: #1f2937;
    color: #ffffff;
}
QPushButton#WinCloseBtn {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 6px;
    color: #9ca3af;
    font-weight: 700;
    font-size: 12px;
    padding: 2px;
}
QPushButton#WinCloseBtn:hover {
    background-color: #dc2626;
    border-color: #dc2626;
    color: #ffffff;
}

/* ─── Modern Minimal Scrollbars ─── */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #1f2937;
    min-height: 28px;
    border-radius: 3px;
}
QScrollBar::handle:vertical:hover {
    background: #374151;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    border: none;
    background: transparent;
    height: 6px;
    margin: 0;
}
QScrollBar::handle:horizontal {
    background: #1f2937;
    min-width: 28px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal:hover {
    background: #374151;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ─── Splitter ─── */
QSplitter::handle {
    background: #1f2937;
    image: none;
    border: none;
}
QSplitter::handle:vertical {
    height: 3px;
    background: #1f2937;
    margin: 2px 0;
    image: none;
    border: none;
}
QSplitter::handle:vertical:hover {
    background: #10b981;
    image: none;
}

/* ─── Hero Left Sidebar ─── */
QFrame#HeroPanel {
    background-color: #0b0f17;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 16px;
}

QLabel#HeroTitle {
    font-size: 18px;
    font-weight: 800;
    color: #f9fafb;
    letter-spacing: -0.3px;
}

QLabel#HeroSubtitle {
    font-size: 11px;
    font-weight: 500;
    color: #9ca3af;
}

/* ─── Search ─── */
QLineEdit#SearchBar {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 8px 12px;
    color: #f9fafb;
    font-size: 12px;
}
QLineEdit#SearchBar:focus {
    border: 1px solid #10b981;
    background-color: #111827;
}

/* ─── Buttons ─── */
QPushButton {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 7px 14px;
    color: #f9fafb;
    font-weight: 600;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #1f2937;
    border-color: #374151;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #0b0f17;
}

QPushButton#PrimaryBtn {
    background-color: #10b981;
    border: 1px solid #10b981;
    color: #ffffff;
    font-weight: 700;
}
QPushButton#PrimaryBtn:hover {
    background-color: #059669;
    border-color: #059669;
}

QPushButton#StartBtn {
    background-color: #10b981;
    border: 1px solid #10b981;
    color: #ffffff;
    font-weight: 700;
}
QPushButton#StartBtn:hover {
    background-color: #059669;
    border-color: #059669;
}

QPushButton#StopBtn {
    background-color: #271418;
    border: 1px solid #7f1d1d;
    color: #f87171;
    font-weight: 700;
}
QPushButton#StopBtn:hover {
    background-color: #3b1419;
    border-color: #ef4444;
}

QPushButton#BrowserBtn {
    background-color: #111827;
    border: 1px solid #1f2937;
    color: #38bdf8;
    font-weight: 600;
}
QPushButton#BrowserBtn:hover {
    background-color: #1f2937;
    border-color: #0284c7;
}
QPushButton#BrowserBtn:disabled {
    background-color: #0b0f17;
    border-color: #1f2937;
    color: #6b7280;
}

QPushButton#IconBtn {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 12px;
    color: #9ca3af;
    font-weight: 700;
}
QPushButton#IconBtn:hover {
    background-color: #1f2937;
    border-color: #374151;
    color: #f9fafb;
}

/* ─── Navigation Item (Linear / Modern Dashboard style) ─── */
QPushButton#NavItem {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 7px 10px;
    color: #9ca3af;
    font-weight: 600;
    font-size: 12px;
    text-align: left;
}
QPushButton#NavItem:hover {
    background-color: #111827;
    color: #f9fafb;
}
QPushButton#NavItem[checked="true"] {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-left: 3px solid #10b981;
    color: #34d399;
    font-weight: 700;
}

/* ─── Project & Stack Cards ─── */
QFrame#ProjectCard, QFrame#StackCard {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 16px;
    padding: 14px;
}
QFrame#ProjectCard:hover, QFrame#StackCard:hover {
    border-color: #374151;
}
QFrame#ProjectCard[running="true"], QFrame#StackCard[running="true"] {
    border: 1.5px solid #10b981;
}

QLabel#SectionHeader {
    background-color: #1f2937;
    color: #e5e7eb;
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 4px 14px;
    font-size: 11px;
    font-weight: 700;
}

QLabel#CardTitle {
    font-size: 14px;
    font-weight: 700;
    color: #f9fafb;
}
QLabel#CardPath {
    font-size: 11px;
    color: #9ca3af;
    font-family: monospace;
}
QLabel#CardCmd {
    font-size: 11px;
    color: #9ca3af;
    background-color: #030712;
    border: 1px solid #1f2937;
    border-radius: 6px;
    padding: 3px 8px;
    font-family: monospace;
}

QFrame#IconSquircle {
    background-color: #1f2937;
    border: 1px solid #374151;
    border-radius: 10px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
}
QLabel#SquircleIcon {
    font-size: 18px;
    background: transparent;
}

QLabel#StackBadge {
    background-color: #1f2937;
    border: 1px solid #374151;
    border-radius: 10px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 600;
    color: #e5e7eb;
}

QLabel#StatusBadge {
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 700;
}
QLabel#StatusBadge[status="running"] {
    background-color: #052e16;
    border: 1px solid #10b981;
    color: #34d399;
}
QLabel#StatusBadge[status="starting"] {
    background-color: #451a03;
    border: 1px solid #d97706;
    color: #fbbf24;
}
QLabel#StatusBadge[status="stopped"] {
    background-color: #1f2937;
    border: 1px solid #374151;
    color: #9ca3af;
}
QLabel#StatusBadge[status="error"] {
    background-color: #450a0a;
    border: 1px solid #dc2626;
    color: #f87171;
}

QLabel#MetricsLabel {
    font-size: 11px;
    color: #38bdf8;
    font-family: monospace;
    font-weight: 600;
}

/* ─── Log Drawer ─── */
QFrame#LogDrawer {
    background-color: #0b0f17;
    border-top: 1px solid #1f2937;
    border-radius: 12px;
}
QTextEdit#LogViewer {
    background-color: #030712;
    border: 1px solid #1f2937;
    border-radius: 8px;
    color: #e5e7eb;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 12px;
    padding: 10px;
}

/* ─── Dialogs ─── */
QDialog {
    background-color: #0b0f17;
    border: 1px solid #1f2937;
    border-radius: 14px;
}
QLabel#DialogHeader {
    font-size: 18px;
    font-weight: 800;
    color: #f9fafb;
}

QLineEdit {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 8px 12px;
    color: #f9fafb;
}
QLineEdit:focus {
    border: 1px solid #10b981;
    background-color: #111827;
}

QComboBox {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 7px 12px;
    color: #f9fafb;
    font-weight: 600;
}
QComboBox:hover {
    border-color: #10b981;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #1f2937;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
    background-color: #111827;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #9ca3af;
    width: 0;
    height: 0;
}
QComboBox QAbstractItemView {
    background-color: #0b0f17;
    color: #f9fafb;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 4px;
    outline: none;
    selection-background-color: #1f2937;
    selection-color: #34d399;
}
QComboBox QAbstractItemView::item {
    color: #f9fafb;
    background-color: #0b0f17;
    padding: 6px 10px;
    min-height: 22px;
    border-radius: 4px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #1f2937;
    color: #ffffff;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #1f2937;
    color: #34d399;
    font-weight: bold;
}

QMenu {
    background-color: #0b0f17;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 6px;
    color: #f9fafb;
}
QMenu::item {
    padding: 8px 18px;
    border-radius: 6px;
    color: #f9fafb;
    background-color: transparent;
    font-weight: 600;
    font-size: 12px;
}
QMenu::item:hover, QMenu::item:selected {
    background-color: #1f2937;
    color: #34d399;
    font-weight: 700;
}
QMenu::item:disabled {
    color: #6b7280;
    background-color: transparent;
}
QMenu::separator {
    height: 1px;
    background-color: #1f2937;
    margin: 4px 6px;
}

QMessageBox, QInputDialog {
    background-color: #0b0f17;
    color: #f9fafb;
    border: 1px solid #1f2937;
    border-radius: 14px;
}
QMessageBox QLabel, QInputDialog QLabel {
    color: #f9fafb;
    font-size: 13px;
    font-weight: 600;
    background: transparent;
}
QMessageBox QPushButton, QInputDialog QPushButton {
    background-color: #111827;
    color: #f9fafb;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 7px 16px;
    font-weight: 600;
    min-width: 60px;
}
QMessageBox QPushButton:hover, QInputDialog QPushButton:hover {
    background-color: #1f2937;
    border-color: #10b981;
    color: #ffffff;
}

QSpinBox {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 6px 10px;
    color: #f9fafb;
    font-weight: 700;
    font-size: 13px;
}
QSpinBox:focus {
    border: 1px solid #10b981;
}

QToolTip {
    background-color: #0b0f17;
    color: #f9fafb;
    border: 1px solid #1f2937;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 11px;
    font-weight: 600;
}
"""

# Universal dark theme
FIGMA_THEME_QSS = DARK_THEME_QSS




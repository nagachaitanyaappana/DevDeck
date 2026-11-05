"""
Main Window for DevDeck.
Integrates project cards, search, filtering, process lifecycle, logs drawer, and system tray.
"""

import os
import sys
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QScrollArea, QSplitter, QFrame,
    QSystemTrayIcon, QMenu, QMessageBox, QApplication,
    QGraphicsDropShadowEffect, QSizeGrip, QGridLayout
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QShortcut, QColor

from core.config_manager import ConfigManager
from core.process_manager import ProcessManager
from core.actions import open_url, open_in_vscode, open_in_terminal, open_in_file_manager, kill_process_on_port, is_project_running, get_process_on_port
from ui.theme import apply_theme, stylesheet_for
from ui.icons import ICO_FAV_OFF, ICO_LOGS, ICO_STACK, ICO_STOP
from version import __version__
from .components.project_card import ProjectCard
from .components.log_viewer import LogViewer
from .components.project_dialog import ProjectDialog
from .components.stack_card import StackCard
from .components.stack_dialog import StackDialog

# ── Ecosystem keyword groups used for the sidebar category filters ──────────
ECOSYSTEM_KEYWORDS = {
    "Node / Web": ["node", "npm", "vite", "react", "next", "angular", "express", "vue"],
    "Java / Spring": ["java", "spring", "gradle", "maven", "kotlin"],
    "Python": ["python", "django", "fastapi", "flask", "uvicorn"],
}


def matches_ecosystem(stack_name: str, ecosystem: str) -> bool:
    """True when a project's declared stack belongs to the given ecosystem."""
    haystack = (stack_name or "").lower()
    return any(k in haystack for k in ECOSYSTEM_KEYWORDS.get(ecosystem, []))


class SectionHeaderWidget(QWidget):
    """Title + count pill used to introduce a group of cards."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("CardSectionHeader")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 8, 2, 2)
        layout.setSpacing(8)

        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("CardSectionTitle")
        layout.addWidget(self.title_lbl)

        self.count_lbl = QLabel("0")
        self.count_lbl.setObjectName("CardSectionCount")
        self.count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.count_lbl)

        layout.addStretch()

    def set_count(self, count: int):
        self.count_lbl.setText(str(count))


class NavItem(QPushButton):
    """Linear / modern dashboard navigation item with left icon and right-aligned count."""
    def __init__(self, filter_id: str, label: str, icon_str: str, parent=None):
        super().__init__(parent)
        self.filter_id = filter_id
        self.label_text = label
        self.icon_str = icon_str
        self.count = 0
        self.setObjectName("NavItem")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(9)

        self.icon_lbl = QLabel(icon_str)
        self.icon_lbl.setObjectName("NavIcon")
        self.icon_lbl.setVisible(bool(icon_str))
        layout.addWidget(self.icon_lbl)

        self.title_lbl = QLabel(label)
        self.title_lbl.setObjectName("NavTitle")
        layout.addWidget(self.title_lbl)

        layout.addStretch()

        self.count_badge = QLabel("0")
        self.count_badge.setObjectName("NavBadge")
        self.count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.count_badge)

    def set_count(self, count: int):
        self.count = count
        self.count_badge.setText(str(count))
        # A zero count is noise — hide the badge so the row stays aligned.
        self.count_badge.setVisible(count > 0)


class MainWindow(QMainWindow):
    def __init__(self, config_manager: ConfigManager, process_manager: ProcessManager, app_icon: QIcon = None):
        super().__init__()
        self.config = config_manager
        self.process_manager = process_manager

        if app_icon and not app_icon.isNull():
            self.app_icon = app_icon
        else:
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_path = os.path.join(base_dir, "assets", "icon.png")
            self.app_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

        self.cards: Dict[str, ProjectCard] = {}
        self.stack_cards: Dict[str, StackCard] = {}
        self.active_filter = "All"
        self.search_query = ""
        self.theme = self.config.data.get("theme", "light")
        if self.theme not in ("light", "dark"):
            self.theme = "light"
        self._force_quit = False

        self.setWindowTitle("DevDeck — Project Control Center")
        self.resize(1280, 800)
        self.setMinimumSize(980, 620)
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)

        self._init_ui()
        self._init_tray()
        self._init_shortcuts()
        self._connect_process_signals()
        self._set_theme(self.theme, persist=False)

        # Initial load: render saved projects and stacks (manual workflow, no auto-scan)
        saved_projects = self.config.get_projects()
        self._render_projects(saved_projects.values())
        self._render_stacks()
        self._apply_filters()
        self._update_stats()

        # Background Port and Process Live Reconciler Timer (polls every 3s)
        self.port_poll_timer = QTimer(self)
        self.port_poll_timer.setInterval(3000)
        self.port_poll_timer.timeout.connect(self._sync_all_statuses)
        self.port_poll_timer.start()

    def _init_ui(self):
        """Build the DevDeck workspace with a calm, editor-inspired hierarchy."""
        self.setObjectName("MainWindow")
        central = QWidget()
        central.setObjectName("CentralRoot")
        central.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(16)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("HeroPanel")
        sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        sidebar.setFixedWidth(250)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 18, 16, 16)
        side.setSpacing(14)

        brand = QHBoxLayout()
        brand.setSpacing(11)
        brand_icon = QLabel()
        if not self.app_icon.isNull():
            brand_icon.setPixmap(self.app_icon.pixmap(34, 34))
        brand_icon.setFixedSize(34, 34)
        brand.addWidget(brand_icon)
        brand_copy = QVBoxLayout()
        brand_copy.setSpacing(1)
        app_title = QLabel("DevDeck")
        app_title.setObjectName("HeroTitle")
        app_sub = QLabel("PROJECT WORKSPACE")
        app_sub.setObjectName("HeroSubtitle")
        brand_copy.addWidget(app_title)
        brand_copy.addWidget(app_sub)
        brand.addLayout(brand_copy, 1)
        side.addLayout(brand)

        # Search stays close to navigation and is keyboard accessible.
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBar")
        self.search_input.setPlaceholderText("Search projects…  Ctrl+F")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_changed)
        side.addWidget(self.search_input)

        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        nav_scroll.setObjectName("NavScroll")
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        nav_container = QWidget()
        nav_container.setObjectName("NavContainer")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 4, 0, 4)
        nav_layout.setSpacing(5)

        workspace_label = QLabel("WORKSPACE")
        workspace_label.setObjectName("SectionHeader")
        nav_layout.addWidget(workspace_label)

        self.filter_buttons: Dict[str, NavItem] = {}
        workspace_items = [
            ("All", "All projects", ""),
            ("Stacks", "Stacks", ""),
            ("Running", "Running", ""),
            ("Favorites", "Favorites", ""),
        ]
        for filter_id, label, icon in workspace_items:
            item = NavItem(filter_id, label, icon)
            item.setFixedHeight(40)
            if filter_id == "All":
                item.setChecked(True)
                item.setProperty("checked", "true")
            item.clicked.connect(lambda _checked, name=filter_id: self._set_filter(name))
            nav_layout.addWidget(item)
            self.filter_buttons[filter_id] = item

        nav_layout.addSpacing(18)
        eco_label = QLabel("BY TECHNOLOGY")
        eco_label.setObjectName("SectionHeader")
        nav_layout.addWidget(eco_label)
        for filter_id, label in [
            ("Node / Web", "Node & Web"),
            ("Java / Spring", "Java & Spring"),
            ("Python", "Python"),
        ]:
            item = NavItem(filter_id, label, "")
            item.setFixedHeight(40)
            item.clicked.connect(lambda _checked, name=filter_id: self._set_filter(name))
            nav_layout.addWidget(item)
            self.filter_buttons[filter_id] = item

        nav_layout.addStretch(1)
        nav_scroll.setWidget(nav_container)
        side.addWidget(nav_scroll, 1)

        # Small live overview, not a large decorative dashboard widget.
        overview = QFrame()
        overview.setObjectName("StatsCard")
        overview_layout = QHBoxLayout(overview)
        overview_layout.setContentsMargins(10, 10, 10, 10)
        overview_layout.setSpacing(4)
        self.total_badge = self._create_mini_stat("0", "PROJECTS", "TOTAL")
        self.running_badge = self._create_mini_stat("0", "RUNNING", "ACTIVE")
        self.ports_badge = self._create_mini_stat("0", "PORTS", "PORTS")
        overview_layout.addWidget(self.total_badge)
        overview_layout.addWidget(self._create_vdivider())
        overview_layout.addWidget(self.running_badge)
        overview_layout.addWidget(self._create_vdivider())
        overview_layout.addWidget(self.ports_badge)
        side.addWidget(overview)

        # Actions are grouped and labelled; no tiny mystery buttons.
        add_project = QPushButton("Add project")
        add_project.setObjectName("PrimaryBtn")
        add_project.setMinimumHeight(40)
        add_project.clicked.connect(self._open_add_dialog)
        side.addWidget(add_project)

        new_stack = QPushButton("Create stack")
        new_stack.setObjectName("SecondaryBtn")
        new_stack.setMinimumHeight(38)
        new_stack.clicked.connect(self._open_new_stack_dialog)
        side.addWidget(new_stack)

        self.stop_all_btn = QPushButton("Stop all services")
        self.stop_all_btn.setObjectName("StopBtn")
        self.stop_all_btn.setMinimumHeight(36)
        self.stop_all_btn.setToolTip("Stop every running server DevDeck manages")
        self.stop_all_btn.clicked.connect(self._stop_all)
        side.addWidget(self.stop_all_btn)

        utility_row = QHBoxLayout()
        utility_row.setSpacing(8)
        self.toggle_logs_btn = QPushButton("Console")
        self.toggle_logs_btn.setObjectName("UtilityBtn")
        self.toggle_logs_btn.setMinimumHeight(34)
        self.toggle_logs_btn.setToolTip("Toggle console logs (Ctrl+L)")
        self.toggle_logs_btn.clicked.connect(self._toggle_logs)
        utility_row.addWidget(self.toggle_logs_btn, 1)
        self.theme_toggle_btn = QPushButton("Light theme" if self.theme == "dark" else "Dark theme")
        self.theme_toggle_btn.setObjectName("UtilityBtn")
        self.theme_toggle_btn.setMinimumHeight(34)
        self.theme_toggle_btn.clicked.connect(self._toggle_theme)
        utility_row.addWidget(self.theme_toggle_btn, 1)
        side.addLayout(utility_row)
        root.addWidget(sidebar)

        # Main workspace
        right = QWidget()
        right.setObjectName("RightContainer")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)

        header = QFrame()
        header.setObjectName("WorkspaceHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(4, 2, 4, 8)
        header_layout.setSpacing(12)
        heading_box = QVBoxLayout()
        heading_box.setSpacing(3)
        self.page_title = QLabel("Your workspace")
        self.page_title.setObjectName("PageTitle")
        page_subtitle = QLabel("Manage local projects and the services that power them.")
        page_subtitle.setObjectName("PageSubtitle")
        heading_box.addWidget(self.page_title)
        heading_box.addWidget(page_subtitle)
        header_layout.addLayout(heading_box, 1)

        self.header_add_btn = QPushButton("＋  Add project")
        self.header_add_btn.setObjectName("PrimaryBtn")
        self.header_add_btn.setMinimumHeight(38)
        self.header_add_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(self.header_add_btn)
        right_layout.addWidget(header)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(5)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setObjectName("CardsScroll")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.cards_container.setObjectName("CardsContainer")
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 2, 8, 12)
        self.cards_layout.setHorizontalSpacing(14)
        self.cards_layout.setVerticalSpacing(14)
        self.cards_layout.setColumnStretch(0, 1)
        self.cards_layout.setColumnStretch(1, 1)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._grid_cols = 2

        self.stacks_header = SectionHeaderWidget("Stacks")
        self.projects_header = SectionHeaderWidget("Projects")

        self.empty_state_frame = QFrame(self.cards_container)
        self.empty_state_frame.setObjectName("EmptyStateFrame")
        self.empty_state_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        empty_layout = QVBoxLayout(self.empty_state_frame)
        empty_layout.setContentsMargins(32, 54, 32, 54)
        empty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.setSpacing(12)
        self.es_icon = QLabel("DEVDECK")
        self.es_icon.setObjectName("EmptyIcon")
        self.es_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self.es_icon)
        self.es_title = QLabel("Your workspace is ready")
        self.es_title.setObjectName("EmptyTitle")
        self.es_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(self.es_title)
        self.es_sub = QLabel("Add a project to start managing your development environment.")
        self.es_sub.setObjectName("EmptySubtitle")
        self.es_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.es_sub.setWordWrap(True)
        empty_layout.addWidget(self.es_sub)

        self.es_btns_widget = QWidget()
        self.es_btns_widget.setObjectName("EmptyBtns")
        empty_buttons = QHBoxLayout(self.es_btns_widget)
        empty_buttons.setContentsMargins(0, 8, 0, 0)
        empty_buttons.setSpacing(10)
        empty_buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_add = QPushButton("Add your first project")
        empty_add.setObjectName("PrimaryBtn")
        empty_add.clicked.connect(self._open_add_dialog)
        empty_buttons.addWidget(empty_add)
        empty_stack = QPushButton("Create a stack")
        empty_stack.setObjectName("SecondaryBtn")
        empty_stack.clicked.connect(self._open_new_stack_dialog)
        empty_buttons.addWidget(empty_stack)
        empty_layout.addWidget(self.es_btns_widget)
        self.empty_state_frame.setVisible(False)

        self.scroll_area.setWidget(self.cards_container)
        self.splitter.addWidget(self.scroll_area)

        self.log_viewer = LogViewer()
        self.log_viewer.close_requested.connect(self._on_console_closed)
        self.log_viewer.fullscreen_toggled.connect(self._on_console_fullscreen_toggled)
        self.log_viewer.open_url_requested.connect(open_url)
        self.splitter.addWidget(self.log_viewer)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        self._prev_splitter_sizes = [720, 0]
        self.splitter.setSizes([720, 0])
        self._logs_open = False
        right_layout.addWidget(self.splitter, 1)
        root.addWidget(right, 1)

    def _create_mini_stat(self, initial_val: str, label_text: str, stat_kind: str) -> QFrame:
        badge = QFrame()
        badge.setObjectName("StatBadge")
        badge.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        ly = QVBoxLayout(badge)
        ly.setContentsMargins(2, 0, 2, 0)
        ly.setSpacing(1)
        ly.setAlignment(Qt.AlignmentFlag.AlignCenter)

        val_label = QLabel(initial_val)
        val_label.setObjectName("StatValue")
        # Colour comes from the stylesheet via this property, so it adapts to
        # the active theme instead of being hard-coded to a light-mode hex.
        val_label.setProperty("statKind", stat_kind)
        val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ly.addWidget(val_label)

        sub_label = QLabel(label_text)
        sub_label.setObjectName("StatLabel")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ly.addWidget(sub_label)

        badge.val_label = val_label
        badge.sub_label = sub_label
        return badge

    def _create_vdivider(self) -> QFrame:
        divider = QFrame()
        divider.setObjectName("VDivider")
        divider.setFrameShape(QFrame.Shape.VLine)
        return divider

    def _init_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self._focus_search)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self._toggle_logs)
        QShortcut(QKeySequence("Ctrl+Shift+L"), self, activated=self.log_viewer._toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+N"), self, activated=self._open_add_dialog)
        QShortcut(QKeySequence("Escape"), self, activated=self._clear_search)

    def _focus_search(self):
        self.search_input.setFocus()
        self.search_input.selectAll()

    def _clear_search(self):
        if self.search_input.text():
            self.search_input.clear()
        else:
            self.search_input.clearFocus()

    def _init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self)
        if not self.app_icon.isNull():
            self.tray.setIcon(self.app_icon)

        tray_menu = QMenu()
        # Uses global QMenu theme from FIGMA_THEME_QSS

        show_act = QAction("Open DevDeck", self)
        show_act.triggered.connect(self._show_window)
        tray_menu.addAction(show_act)

        stop_all_act = QAction("⏹ Stop All Running", self)
        stop_all_act.triggered.connect(self._stop_all)
        tray_menu.addAction(stop_all_act)

        tray_menu.addSeparator()

        quit_act = QAction("Quit DevDeck", self)
        quit_act.triggered.connect(self._quit_app)
        tray_menu.addAction(quit_act)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self._on_tray_activated)
        self.tray.show()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window()

    def _show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self._sync_all_statuses()

    def _quit_app(self):
        """Cleanly stop all background servers and exit DevDeck."""
        self._force_quit = True
        self._stop_all()
        QApplication.instance().quit()

    def closeEvent(self, event):
        """Minimize to system tray when window is closed, keeping all servers active."""
        if getattr(self, "_force_quit", False):
            self._stop_all()
            event.accept()
            return

        if hasattr(self, "tray") and self.tray is not None:
            event.ignore()
            self.hide()
            if self.tray.isVisible():
                self.tray.showMessage(
                    "DevDeck Running in Background",
                    "DevDeck is minimized to the system tray. Your servers and multi-stacks continue running.\nClick tray icon to reopen.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2500
                )
            return

        self._stop_all()
        event.accept()

    def _on_console_fullscreen_toggled(self, is_fullscreen: bool):
        sizes = self.splitter.sizes()
        total = sum(sizes) if sum(sizes) > 0 else 800
        if is_fullscreen:
            if sizes[0] > 30 and sizes[1] > 30:
                self._prev_splitter_sizes = list(sizes)
            else:
                self._prev_splitter_sizes = [int(total * 0.65), int(total * 0.35)]
            self.splitter.setSizes([0, total])
            self._logs_open = True
        else:
            prev = getattr(self, "_prev_splitter_sizes", [int(total * 0.65), int(total * 0.35)])
            if prev[0] == 0 or prev[1] == 0:
                prev = [int(total * 0.65), int(total * 0.35)]
            self.splitter.setSizes(prev)
            self._logs_open = prev[1] > 0

    def _on_console_closed(self):
        sizes = self.splitter.sizes()
        total = sum(sizes) if sum(sizes) > 0 else 800
        if sizes[0] > 30 and sizes[1] > 30:
            self._prev_splitter_sizes = list(sizes)
        self.splitter.setSizes([total, 0])
        self._logs_open = False
        self.log_viewer.set_fullscreen_state(False)

    def _toggle_logs(self):
        sizes = self.splitter.sizes()
        total = sum(sizes) if sum(sizes) > 0 else 800
        if sizes[1] > 30:
            if sizes[0] > 30:
                self._prev_splitter_sizes = list(sizes)
            self.splitter.setSizes([total, 0])
            self._logs_open = False
            self.log_viewer.set_fullscreen_state(False)
        else:
            prev = getattr(self, "_prev_splitter_sizes", [int(total * 0.65), int(total * 0.35)])
            if prev[0] == 0 or prev[1] == 0:
                prev = [int(total * 0.65), int(total * 0.35)]
            self.splitter.setSizes(prev)
            self._logs_open = True
            self.log_viewer.set_fullscreen_state(False)

    def _toggle_theme(self):
        self._set_theme("dark" if self.theme == "light" else "light")

    def _set_theme(self, theme: str, persist: bool = True):
        """Switch the whole app between the light and dark sheets.

        The two sheets are distinct rather than one sheet full of
        ``[theme="dark"]`` overrides: Qt does not re-evaluate property
        selectors reliably for every widget, and swapping the sheet guarantees
        every widget, including dialogs, is restyled.
        """
        if theme not in ("light", "dark"):
            return
        self.theme = theme

        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(stylesheet_for(theme))
        # Dialogs are top-level windows and do not inherit an app stylesheet
        # change while they are already built, so refresh what we can.
        self._refresh_all_styles()

        if hasattr(self, "theme_toggle_btn"):
            self.theme_toggle_btn.setText("Light mode" if theme == "dark" else "Dark mode")

        if persist:
            self.config.data["theme"] = theme
            self.config.save()

    def _refresh_all_styles(self):
        """Repolish every widget so property-selector rules re-evaluate."""
        for widget in [self] + self.findChildren(QWidget):
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()
        self.update()

    def _render_projects(self, projects: List[dict]):
        # Clear existing cards
        for card in self.cards.values():
            card.setParent(None)
            card.deleteLater()
        self.cards.clear()

        # Sort: favorites first, then name
        sorted_projects = sorted(
            projects,
            key=lambda p: (not p.get("favorite", False), p.get("name", "").lower())
        )

        for p in sorted_projects:
            card = ProjectCard(p)
            card.start_clicked.connect(self._start_project)
            card.stop_clicked.connect(self._stop_project)
            card.restart_clicked.connect(self._restart_project)
            card.open_url_clicked.connect(open_url)
            card.view_logs_clicked.connect(self._view_logs)
            card.project_selected.connect(self._view_logs)
            card.open_code_clicked.connect(open_in_vscode)
            card.open_terminal_clicked.connect(open_in_terminal)
            card.open_folder_clicked.connect(open_in_file_manager)
            card.favorite_toggled.connect(self._toggle_favorite)
            card.edit_clicked.connect(self._open_edit_dialog)
            card.remove_clicked.connect(self._remove_project)
            card.port_changed.connect(self._on_port_changed)
            card.kill_port_requested.connect(self._on_kill_port_requested)

            # Check if already running in process manager or accurately matching on port
            p_id = p["id"]
            is_running = is_project_running(p, self.process_manager)
            pm_status = self.process_manager.get_status(p_id)
            if pm_status in ["running", "starting"]:
                card.set_status(pm_status)
            else:
                card.set_status("running" if is_running else "stopped")

            url = self.process_manager.get_detected_url(p_id)
            if not url and is_running and p.get("port"):
                url = p.get("url") or f"http://localhost:{p['port']}"
            if url:
                card.set_detected_url(url)

            self.cards[p_id] = card

        self._apply_filters()
        self._update_stats()

    def _connect_process_signals(self):
        self.process_manager.status_changed.connect(self._on_process_status)
        self.process_manager.url_detected.connect(self._on_url_detected)
        self.process_manager.metrics_updated.connect(self._on_metrics_updated)
        self.process_manager.log_appended.connect(self._on_log_appended)

    def _start_project(self, project: dict):
        p_id = project["id"]
        # Make logs drawer visible and select this project
        self._view_logs(project)
        self.process_manager.start_project(project)
        self._update_stats()

    def _stop_project(self, project_id: str):
        if self.process_manager.get_status(project_id) in ["running", "starting"]:
            self.process_manager.stop_project(project_id)
        else:
            # Check if listening on configured port externally
            proj = self.config.get_project(project_id)
            if not proj:
                for s in self.config.get_stacks().values():
                    for srv in s.get("services", []):
                        if srv["id"] == project_id:
                            proj = srv
                            break
            if proj and proj.get("port") and self.process_manager.is_port_listening(proj["port"]):
                kill_process_on_port(proj["port"])
        self._sync_all_statuses()
        self._update_stats()

    def _restart_project(self, project: dict):
        self._view_logs(project)
        self.process_manager.restart_project(project)
        self._update_stats()

    def _stop_all(self):
        self.process_manager.stop_all()
        # Also terminate external processes on configured ports
        for p in self.config.get_projects().values():
            if p.get("port") and self.process_manager.is_port_listening(p["port"]):
                kill_process_on_port(p["port"])
        for s in self.config.get_stacks().values():
            for srv in s.get("services", []):
                if srv.get("port") and self.process_manager.is_port_listening(srv["port"]):
                    kill_process_on_port(srv["port"])
        self._sync_all_statuses()
        self._update_stats()

    def _view_logs(self, project: dict):
        p_id = project["id"]
        # Ensure log viewer is visible
        sizes = self.splitter.sizes()
        if sizes[1] < 50:
            total = sum(sizes) if sum(sizes) > 0 else 800
            prev = getattr(self, "_prev_splitter_sizes", [int(total * 0.65), int(total * 0.35)])
            if prev[0] == 0 or prev[1] == 0:
                prev = [int(total * 0.65), int(total * 0.35)]
            self.splitter.setSizes(prev)
            self._logs_open = True
            self.log_viewer.set_fullscreen_state(False)

        url = self.process_manager.get_detected_url(p_id) or project.get("url", "")
        self.log_viewer.set_active_project(p_id, project.get("name", "Unnamed"), url)
        self.log_viewer.clear_logs()

        # Backfill history
        logs = self.process_manager.get_logs(p_id)
        if logs:
            for text, is_stderr in logs:
                self.log_viewer.append_log(text, is_stderr)
        else:
            self.log_viewer.append_log(
                "No output yet. Start this project to stream its terminal logs here.\n",
                False,
            )

    def _on_process_status(self, project_id: str, status: str):
        if project_id in self.cards:
            self.cards[project_id].set_status(status)
        for s_card in self.stack_cards.values():
            s_card.set_service_status(project_id, status)
        self._update_stats()

    def _on_url_detected(self, project_id: str, url: str):
        if project_id in self.cards:
            self.cards[project_id].set_detected_url(url)
        for s_card in self.stack_cards.values():
            s_card.set_service_url(project_id, url)
        if self.log_viewer.current_project_id == project_id:
            self.log_viewer.set_url(url)
        self._update_stats()

    def _on_metrics_updated(self, project_id: str, cpu: float, mem: float):
        if project_id in self.cards:
            self.cards[project_id].set_metrics(cpu, mem)

    def _on_log_appended(self, project_id: str, text: str, is_stderr: bool):
        if self.log_viewer.current_project_id == project_id:
            self.log_viewer.append_log(text, is_stderr)

    def _toggle_favorite(self, project_id: str):
        self.config.toggle_favorite(project_id)
        # Keep the card's own state in sync with what was persisted, then
        # re-evaluate filters and counts.
        card = self.cards.get(project_id)
        if card:
            card.project["favorite"] = self.config.get_project(project_id).get("favorite", False)
            card._sync_favorite_button()
        self._apply_filters()
        self._update_stats()

    def _open_add_dialog(self):
        dialog = ProjectDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            self.config.save_project(data)
            self._render_projects(self.config.get_projects().values())

    def _open_edit_dialog(self, project: dict):
        dialog = ProjectDialog(self, project_data=project)
        if dialog.exec():
            data = dialog.get_data()
            self.config.save_project(data)
            self._render_projects(self.config.get_projects().values())

    def _on_port_changed(self, project: dict, new_port: int):
        self.config.save_project(project)
        self._update_stats()

    def _on_kill_port_requested(self, port: int):
        holder = get_process_on_port(port)
        if not holder:
            QMessageBox.information(self, "Port Free", f"Nothing is listening on port :{port}.")
            return

        desc = holder.get("name", "process")
        pid = holder.get("pid")
        cwd = holder.get("cwd") or "unknown directory"
        confirm = QMessageBox.question(
            self,
            "Free Port",
            f"Terminate the process holding port :{port}?\n\n"
            f"Process: {desc} (PID {pid})\n"
            f"Location: {cwd}\n\n"
            "This kills the process immediately, regardless of which project "
            "started it.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        if kill_process_on_port(port):
            QMessageBox.information(self, "Port Released", f"Process on port :{port} was terminated.")
        else:
            QMessageBox.warning(self, "Failed", f"Could not terminate process on port :{port}.")
        self._sync_all_statuses()
        self._update_stats()


    def _remove_project(self, project_id: str):
        confirm = QMessageBox.question(
            self, "Remove Project",
            "Remove this project from DevDeck? (No files on disk will be deleted)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self._stop_project(project_id)
            self.config.remove_project(project_id)
            self._render_projects(self.config.get_projects().values())

    def _render_stacks(self):
        """Render all configured multi-project stacks as StackCards."""
        for card in self.stack_cards.values():
            card.setParent(None)
            card.deleteLater()
        self.stack_cards.clear()

        stacks = self.config.get_stacks()
        for s_id, stack in stacks.items():
            card = StackCard(stack, self.cards_container)
            card.start_stack_clicked.connect(self._start_stack)
            card.stop_stack_clicked.connect(self._stop_stack)
            card.restart_stack_clicked.connect(self._restart_stack)
            card.edit_stack_clicked.connect(self._edit_stack)
            card.remove_stack_clicked.connect(self._remove_stack)
            card.open_urls_clicked.connect(self._open_multiple_urls)
            card.view_service_logs_clicked.connect(self._view_logs)
            card.restart_service_clicked.connect(self._restart_service)
            card.service_port_changed.connect(self._on_stack_service_port_changed)
            card.start_service_clicked.connect(self._start_project)
            card.stop_service_clicked.connect(self._stop_project)
            card.open_code_clicked.connect(open_in_vscode)
            card.open_terminal_clicked.connect(open_in_terminal)
            card.open_folder_clicked.connect(open_in_file_manager)

            # Reconcile status & detected URL for each member service
            for service in stack.get("services", []):
                srv_id = service["id"]
                is_running = is_project_running(service, self.process_manager)
                pm_status = self.process_manager.get_status(srv_id)
                if pm_status in ["running", "starting"]:
                    card.set_service_status(srv_id, pm_status)
                else:
                    card.set_service_status(srv_id, "running" if is_running else "stopped")

                url = self.process_manager.get_detected_url(srv_id)
                if not url and is_running and service.get("port"):
                    url = f"http://localhost:{service['port']}"
                if url:
                    card.set_service_url(srv_id, url)

            self.stack_cards[s_id] = card

    def _open_new_stack_dialog(self):
        """Open the multi-project stack builder dialog."""
        existing = list(self.config.get_projects().values())
        dialog = StackDialog(existing_projects=existing, parent=self)
        if dialog.exec():
            res = dialog.get_result()
            if res:
                self.config.save_stack(res)
                self._render_stacks()
                self._apply_filters()
                self._update_stats()

    def _edit_stack(self, stack: dict):
        """Open stack builder dialog in edit mode."""
        existing = list(self.config.get_projects().values())
        dialog = StackDialog(stack_data=stack, existing_projects=existing, parent=self)
        if dialog.exec():
            res = dialog.get_result()
            if res:
                self.config.save_stack(res)
                self._render_stacks()
                self._apply_filters()
                self._update_stats()

    def _remove_stack(self, stack_id: str):
        """Safely stops services and removes a stack."""
        stack = self.config.get_stack(stack_id)
        name = stack.get("name", "this stack") if stack else "this stack"
        confirm = QMessageBox.question(
            self, "Remove Stack",
            f"Remove stack '{name}' from DevDeck? (No files on disk will be deleted)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            if stack:
                for s in stack.get("services", []):
                    self.process_manager.stop_project(s["id"])
            self.config.remove_stack(stack_id)
            if stack_id in self.stack_cards:
                c = self.stack_cards.pop(stack_id)
                c.setParent(None)
                c.deleteLater()
            self._apply_filters()
            self._update_stats()

    def _start_stack(self, stack: dict):
        """Starts all services in a stack simultaneously."""
        services = stack.get("services", [])
        if not services:
            return
        # Open log viewer on the first service for instant feedback
        self._view_logs(services[0])
        for s in services:
            self.process_manager.start_project(s)
        self._update_stats()

    def _stop_stack(self, stack: dict):
        """Stops all services in a stack."""
        for s in stack.get("services", []):
            self._stop_project(s["id"])
        self._sync_all_statuses()
        self._update_stats()

    def _restart_stack(self, stack: dict):
        """Restarts all services in a stack simultaneously."""
        services = stack.get("services", [])
        if not services:
            return
        self._view_logs(services[0])
        for s in services:
            self.process_manager.restart_project(s)
        self._update_stats()

    def _restart_service(self, service: dict):
        """Restarts a single service in a stack."""
        self._view_logs(service)
        self.process_manager.restart_project(service)
        self._update_stats()

    def _on_stack_service_port_changed(self, stack: dict, service: dict, new_port: int):
        """Updates and persists the port configuration for a service inside a stack."""
        for s in stack.get("services", []):
            if s.get("id") == service.get("id"):
                s["port"] = new_port
                s["url"] = f"http://localhost:{new_port}"
                break
        self.config.save_stack(stack)
        self._update_stats()

    def _open_multiple_urls(self, urls: List[str]):
        """Opens multiple URLs in the default browser."""
        for u in urls:
            open_url(u)

    def _set_filter(self, filter_name: str):
        self.active_filter = filter_name
        for name, item in self.filter_buttons.items():
            is_active = (name == filter_name)
            item.setChecked(is_active)
            item.setProperty("checked", "true" if is_active else "false")
            item.style().unpolish(item)
            item.style().polish(item)
            # Also update child labels
            item.title_lbl.style().unpolish(item.title_lbl)
            item.title_lbl.style().polish(item.title_lbl)
            item.count_badge.style().unpolish(item.count_badge)
            item.count_badge.style().polish(item.count_badge)
        self._apply_filters()

    def _on_search_changed(self, text: str):
        self.search_query = text.strip().lower()
        self._apply_filters()

    def _apply_filters(self):
        # Detach every card from the grid without destroying it.
        while self.cards_layout.count():
            self.cards_layout.takeAt(0)

        stacks_only = self.active_filter == "Stacks"

        # 1. Stacks
        visible_stacks = []
        for scard in self.stack_cards.values():
            stk = scard.stack
            services = stk.get("services", [])
            haystack = " ".join([
                stk.get("name", "").lower(),
                *[s.get("name", "").lower() for s in services],
                *[s.get("command", "").lower() for s in services],
                *[s.get("stack", "").lower() for s in services],
            ])
            matches_search = not self.search_query or self.search_query in haystack

            if self.active_filter == "All" or stacks_only:
                matches_filter = True
            elif self.active_filter == "Running":
                matches_filter = any(r.status == "running" for r in scard.service_rows.values())
            elif self.active_filter == "Favorites":
                # A stack is a favorite when any of its services is.
                fav_ids = {p["id"] for p in self.config.get_projects().values()
                           if p.get("favorite")}
                matches_filter = any(s.get("id") in fav_ids for s in services)
            elif self.active_filter in ECOSYSTEM_KEYWORDS:
                matches_filter = any(
                    matches_ecosystem(s.get("stack", ""), self.active_filter)
                    for s in services
                )
            else:
                matches_filter = False

            is_visible = matches_search and matches_filter
            scard.setVisible(is_visible)
            if is_visible:
                visible_stacks.append(scard)

        # 2. Individual projects
        visible_projects = []
        for card in self.cards.values():
            if stacks_only:
                card.setVisible(False)
                continue
            proj = card.project
            haystack = " ".join([
                proj.get("name", "").lower(),
                proj.get("path", "").lower(),
                proj.get("command", "").lower(),
                proj.get("stack", "").lower(),
            ])
            matches_search = not self.search_query or self.search_query in haystack

            if self.active_filter == "All":
                matches_filter = True
            elif self.active_filter == "Running":
                matches_filter = card.status == "running"
            elif self.active_filter == "Favorites":
                matches_filter = bool(proj.get("favorite", False))
            elif self.active_filter in ECOSYSTEM_KEYWORDS:
                matches_filter = matches_ecosystem(proj.get("stack", ""), self.active_filter)
            else:
                matches_filter = False

            is_visible = matches_search and matches_filter
            card.setVisible(is_visible)
            if is_visible:
                visible_projects.append(card)

        # 3. Layout placement
        # Column count adapts to the available width. Two columns have a
        # hard minimum (~700px); below that they force the grid wider than
        # the viewport and clip every card, so drop to one.
        cols = 2 if self.scroll_area.viewport().width() >= 720 else 1
        row = 0
        # Park the unused column so it contributes no minimum width.
        self.cards_layout.setColumnStretch(1, 1 if cols == 2 else 0)

        if visible_stacks:
            self.stacks_header.set_count(len(visible_stacks))
            self.stacks_header.setVisible(True)
            self.cards_layout.addWidget(self.stacks_header, row, 0, 1, cols)
            row += 1
            for scard in visible_stacks:
                self.cards_layout.addWidget(scard, row, 0, 1, cols)
                row += 1
        else:
            self.stacks_header.setVisible(False)

        if visible_projects:
            self.projects_header.set_count(len(visible_projects))
            self.projects_header.setVisible(True)
            self.cards_layout.addWidget(self.projects_header, row, 0, 1, cols)
            row += 1
            for idx, pcard in enumerate(visible_projects):
                self.cards_layout.addWidget(pcard, row + idx // cols, idx % cols)
            row += (len(visible_projects) + cols - 1) // cols
        else:
            self.projects_header.setVisible(False)

        # Empty state
        if not visible_stacks and not visible_projects:
            self._update_empty_state_content()
            self.empty_state_frame.setVisible(True)
            self.cards_layout.addWidget(self.empty_state_frame, 0, 0, 1, cols)
        else:
            self.empty_state_frame.setVisible(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Re-flow when the width crosses the 1/2 column threshold.
        cols = 2 if self.scroll_area.viewport().width() >= 720 else 1
        if cols != getattr(self, "_grid_cols", None):
            self._grid_cols = cols
            self._apply_filters()

    def _update_empty_state_content(self):
        filter_name = getattr(self, "active_filter", "All")
        search = getattr(self, "search_query", "").strip()

        if search:
            self.es_icon.setText("⌕")
            self.es_title.setText(f"No Results for '{search}'")
            self.es_sub.setText("No projects or stacks match your search query.")
            if hasattr(self, "es_btns_widget"):
                self.es_btns_widget.setVisible(False)
        elif filter_name == "Running":
            self.es_icon.setText("◌")
            self.es_title.setText("No Projects or Stacks Running")
            self.es_sub.setText("Start a project or stack from 'All' to monitor it here.")
            if hasattr(self, "es_btns_widget"):
                self.es_btns_widget.setVisible(False)
        elif filter_name == "Favorites":
            self.es_icon.setText("☆")
            self.es_title.setText("No Favorite Projects Yet")
            self.es_sub.setText("Click the star icon on any project card to bookmark it here.")
            if hasattr(self, "es_btns_widget"):
                self.es_btns_widget.setVisible(False)
        elif filter_name == "Stacks":
            self.es_icon.setText("▦")
            self.es_title.setText("No Multi-Project Stacks Yet")
            self.es_sub.setText("Create a stack to launch frontend, backend, and services together.")
            if hasattr(self, "es_btns_widget"):
                self.es_btns_widget.setVisible(True)
        else:
            self.es_icon.setText("▤")
            self.es_title.setText("No Projects or Stacks Yet")
            self.es_sub.setText("DevDeck is ready. Add projects manually or create multi-service stacks.")
            if hasattr(self, "es_btns_widget"):
                self.es_btns_widget.setVisible(True)

    def _sync_all_statuses(self):
        """Reconciles live process states and listening TCP ports for all cards & stacks."""
        changed = False

        # 1. Sync Individual Project Cards
        for p_id, card in self.cards.items():
            proj = card.project
            is_running = is_project_running(proj, self.process_manager)
            pm_status = self.process_manager.get_status(p_id)
            if pm_status in ["running", "starting"]:
                new_status = pm_status
            else:
                new_status = "running" if is_running else "stopped"

            if card.status != new_status:
                card.set_status(new_status)
                changed = True

            # URL Sync
            if is_running:
                url = self.process_manager.get_detected_url(p_id) or proj.get("url") or (f"http://localhost:{proj['port']}" if proj.get("port") else None)
                if url and card.detected_url != url:
                    card.set_detected_url(url)
                    changed = True
            elif card.detected_url:
                card.set_detected_url(None)
                changed = True

        # 2. Sync Stack Cards
        for s_id, scard in self.stack_cards.items():
            for service in scard.stack.get("services", []):
                srv_id = service["id"]
                is_running = is_project_running(service, self.process_manager)
                pm_status = self.process_manager.get_status(srv_id)
                if pm_status in ["running", "starting"]:
                    srv_status = pm_status
                else:
                    srv_status = "running" if is_running else "stopped"

                curr_row = scard.service_rows.get(srv_id)
                if curr_row and curr_row.status != srv_status:
                    scard.set_service_status(srv_id, srv_status)
                    changed = True

                if is_running and service.get("port"):
                    srv_url = self.process_manager.get_detected_url(srv_id) or f"http://localhost:{service['port']}"
                    if curr_row and curr_row.detected_url != srv_url:
                        scard.set_service_url(srv_id, srv_url)
                        changed = True
                elif curr_row and curr_row.detected_url:
                    curr_row.detected_url = None
                    changed = True

        if changed:
            self._update_stats()

    def _update_stats(self):
        total = 0
        running = 0
        ports = 0
        counted_ids = set()

        for card in self.cards.values():
            p_id = card.project.get("id")
            if p_id in counted_ids:
                continue
            counted_ids.add(p_id)
            total += 1
            if card.status == "running":
                running += 1
            if card.detected_url:
                ports += 1

        for s_card in self.stack_cards.values():
            for row in s_card.service_rows.values():
                srv_id = row.service.get("id")
                # A service shared with a standalone project is one project.
                if srv_id in counted_ids:
                    continue
                counted_ids.add(srv_id)
                total += 1
                if row.status == "running":
                    running += 1
                if row.detected_url:
                    ports += 1

        self.total_badge.val_label.setText(str(total))
        self.running_badge.val_label.setText(str(running))
        self.ports_badge.val_label.setText(str(ports))

        # Sidebar counts. These are live totals, unaffected by the active
        # filter, so the badge numbers stay stable while browsing.
        fav_ids = {p["id"] for p in self.config.get_projects().values()
                   if p.get("favorite", False)}
        stack_rows = [r for s in self.stack_cards.values() for r in s.service_rows.values()]

        cat_counts = {
            "All": total,
            "Stacks": len(self.stack_cards),
            "Running": sum(
                1 for c in self.cards.values() if c.status == "running"
            ) + sum(
                1 for r in stack_rows
                if r.status == "running" and r.service.get("id") not in self.cards
            ),
            "Favorites": len(fav_ids),
        }
        for eco in ECOSYSTEM_KEYWORDS:
            cat_counts[eco] = (
                sum(1 for c in self.cards.values()
                    if matches_ecosystem(c.project.get("stack", ""), eco))
                + sum(1 for r in stack_rows
                      if r.service.get("id") not in self.cards
                      and matches_ecosystem(r.service.get("stack", ""), eco))
            )

        for cat_name, item in self.filter_buttons.items():
            item.set_count(cat_counts.get(cat_name, 0))

        # Reflect whether anything is actually running in the Stop All button.
        self.stop_all_btn.setEnabled(running > 0)

        if hasattr(self, 'tray'):
            self.tray.setToolTip(f"DevDeck: {running}/{total} running")

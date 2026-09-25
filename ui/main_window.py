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
from core.actions import open_url, open_in_vscode, open_in_terminal, open_in_file_manager, kill_process_on_port, is_project_running
from ui.theme import FIGMA_THEME_QSS, DARK_THEME_QSS
from .components.project_card import ProjectCard
from .components.log_viewer import LogViewer
from .components.project_dialog import ProjectDialog
from .components.stack_card import StackCard
from .components.stack_dialog import StackDialog

class NavItem(QPushButton):
    """Linear / modern dark dashboard navigation item with left icon and right-aligned count."""
    def __init__(self, filter_id: str, label: str, icon_str: str, parent=None):
        super().__init__(parent)
        self.filter_id = filter_id
        self.label_text = label
        self.icon_str = icon_str
        self.count = 0
        self.setObjectName("NavItem")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(34)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(9)

        self.icon_lbl = QLabel(icon_str)
        self.icon_lbl.setStyleSheet("font-size: 13px; background: transparent;")
        layout.addWidget(self.icon_lbl)

        self.title_lbl = QLabel(label)
        self.title_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #94a3b8; background: transparent;")
        layout.addWidget(self.title_lbl)

        layout.addStretch()

        self.count_badge = QLabel("0")
        self.count_badge.setStyleSheet(
            "background-color: #111827; color: #9ca3af; font-size: 10px; font-weight: 700; "
            "border: 1px solid #1f2937; border-radius: 8px; padding: 1px 6px; min-width: 14px;"
        )
        self.count_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.count_badge)

    def set_count(self, count: int):
        self.count = count
        self.count_badge.setText(str(count))


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

        self.setWindowTitle("DevDeck — Project Control Center")
        self.resize(1200, 780)
        self.setMinimumSize(940, 580)
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)

        self._init_ui()
        self._init_tray()
        self._init_shortcuts()
        self._connect_process_signals()

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
        central = QWidget()
        self.setCentralWidget(central)
        
        # Horizontal Split: Left Hero Panel + Right Cards & Logs
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(20, 18, 20, 18)
        root_layout.setSpacing(20)

        # ─── LEFT: Modern Sidebar (Linear / Figma Developer Console Style) ───
        left_panel = QFrame()
        left_panel.setObjectName("HeroPanel")
        left_panel.setFixedWidth(275)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(12)

        # 1. App Brand Header (Icon + Title + Version Badge + Subtitle)
        brand_container = QWidget()
        brand_layout = QHBoxLayout(brand_container)
        brand_layout.setContentsMargins(2, 0, 2, 0)
        brand_layout.setSpacing(10)

        brand_icon = QLabel()
        if not self.app_icon.isNull():
            brand_icon.setPixmap(self.app_icon.pixmap(32, 32))
        brand_icon.setFixedSize(32, 32)
        brand_layout.addWidget(brand_icon)

        brand_text_box = QVBoxLayout()
        brand_text_box.setSpacing(2)

        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        app_title = QLabel("DevDeck")
        app_title.setObjectName("HeroTitle")
        app_title.setStyleSheet("font-size: 17px; font-weight: 800; color: #f9fafb; letter-spacing: -0.4px;")
        title_row.addWidget(app_title)

        version_badge = QLabel("v1.0.2")
        version_badge.setStyleSheet(
            "background-color: #111827; color: #34d399; font-size: 10px; font-weight: 700; "
            "border: 1px solid #1f2937; border-radius: 6px; padding: 1px 6px;"
        )
        title_row.addWidget(version_badge)
        title_row.addStretch()
        brand_text_box.addLayout(title_row)

        app_sub = QLabel("Developer Control Center")
        app_sub.setStyleSheet("font-size: 11px; font-weight: 500; color: #9ca3af;")
        brand_text_box.addWidget(app_sub)

        brand_layout.addLayout(brand_text_box)
        left_layout.addWidget(brand_container)

        # 2. Telemetry Card (3-Column Minimal Stats: TOTAL, ACTIVE, PORTS)
        stats_card = QFrame()
        stats_card.setObjectName("StatsCard")
        stats_card.setStyleSheet(
            "background-color: #111827; border: 1px solid #1f2937; border-radius: 10px; padding: 6px 4px;"
        )
        stats_layout = QHBoxLayout(stats_card)
        stats_layout.setContentsMargins(4, 4, 4, 4)
        stats_layout.setSpacing(2)

        self.total_badge = self._create_mini_stat("0", "TOTAL", "#f9fafb")
        self.running_badge = self._create_mini_stat("0", "ACTIVE", "#10b981")
        self.ports_badge = self._create_mini_stat("0", "PORTS", "#38bdf8")

        stats_layout.addWidget(self.total_badge)
        stats_layout.addWidget(self._create_vdivider())
        stats_layout.addWidget(self.running_badge)
        stats_layout.addWidget(self._create_vdivider())
        stats_layout.addWidget(self.ports_badge)
        left_layout.addWidget(stats_card)

        # 3. Search Bar with Ctrl+F shortcut pill
        search_box = QFrame()
        search_box.setStyleSheet(
            "background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 2px 8px;"
        )
        search_layout = QHBoxLayout(search_box)
        search_layout.setContentsMargins(4, 2, 6, 2)
        search_layout.setSpacing(6)

        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 12px; color: #9ca3af; background: transparent;")
        search_layout.addWidget(search_icon)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBar")
        self.search_input.setPlaceholderText("Search projects or stacks...")
        self.search_input.setStyleSheet(
            "background: transparent; border: none; color: #f9fafb; font-size: 12px; padding: 4px 0;"
        )
        self.search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_input)

        shortcut_pill = QLabel("Ctrl+F")
        shortcut_pill.setStyleSheet(
            "background-color: #0b0f17; color: #9ca3af; font-size: 10px; font-weight: 700; "
            "border: 1px solid #1f2937; border-radius: 4px; padding: 2px 5px;"
        )
        search_layout.addWidget(shortcut_pill)
        left_layout.addWidget(search_box)

        # 4. Navigation Menu (Vertical List with Icons and Count Badges)
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        nav_scroll.setStyleSheet("background: transparent; border: none;")
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        nav_container = QWidget()
        nav_container.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(3)

        # Workspace section
        ws_label = QLabel("WORKSPACE")
        ws_label.setStyleSheet("font-size: 10px; font-weight: 800; color: #6b7280; letter-spacing: 0.8px; margin-top: 2px; margin-bottom: 2px; padding-left: 6px;")
        nav_layout.addWidget(ws_label)

        self.filter_buttons: Dict[str, NavItem] = {}
        workspace_items = [
            ("All", "All Projects", "⚡"),
            ("⚡ Stacks", "Multi-Stacks", "📦"),
            ("Running", "Active Servers", "🟢"),
            ("Favorites", "Favorites", "⭐"),
        ]
        for f_id, label, icon in workspace_items:
            item = NavItem(f_id, label, icon)
            if f_id == "All":
                item.setChecked(True)
                item.setProperty("checked", "true")
                item.title_lbl.setStyleSheet("font-size: 12px; font-weight: 700; color: #34d399; background: transparent;")
                item.count_badge.setStyleSheet(
                    "background-color: #052e16; color: #34d399; font-size: 10px; font-weight: 700; "
                    "border: 1px solid #10b981; border-radius: 8px; padding: 1px 6px; min-width: 14px;"
                )
            item.clicked.connect(lambda checked, name=f_id: self._set_filter(name))
            nav_layout.addWidget(item)
            self.filter_buttons[f_id] = item

        # Ecosystem section
        eco_label = QLabel("ECOSYSTEM")
        eco_label.setStyleSheet("font-size: 10px; font-weight: 800; color: #6b7280; letter-spacing: 0.8px; margin-top: 10px; margin-bottom: 2px; padding-left: 6px;")
        nav_layout.addWidget(eco_label)

        eco_items = [
            ("Node / Web", "Node & Web", "🌐"),
            ("Java / Spring", "Java & Spring", "🍃"),
            ("Python", "Python", "🐍"),
        ]
        for f_id, label, icon in eco_items:
            item = NavItem(f_id, label, icon)
            item.clicked.connect(lambda checked, name=f_id: self._set_filter(name))
            nav_layout.addWidget(item)
            self.filter_buttons[f_id] = item

        nav_layout.addStretch()
        nav_scroll.setWidget(nav_container)
        left_layout.addWidget(nav_scroll, 1)

        # 5. Global Action Buttons
        actions_box = QVBoxLayout()
        actions_box.setSpacing(7)

        add_row = QHBoxLayout()
        add_row.setSpacing(7)

        add_btn = QPushButton("➕ Project")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.setStyleSheet(
            "background-color: #10b981; color: #ffffff; font-weight: 700; "
            "border: 1px solid #10b981; border-radius: 8px; padding: 7px 12px; font-size: 12px;"
        )
        add_btn.setToolTip("Add a single project manually")
        add_btn.clicked.connect(self._open_add_dialog)
        add_row.addWidget(add_btn)

        stack_btn = QPushButton("⚡ Stack")
        stack_btn.setStyleSheet(
            "background-color: #111827; border: 1px solid #1f2937; color: #f9fafb; "
            "font-weight: 700; border-radius: 8px; padding: 7px 12px; font-size: 12px;"
        )
        stack_btn.setToolTip("Create a multi-project stack (e.g. ITIAP Backend + Frontend)")
        stack_btn.clicked.connect(self._open_new_stack_dialog)
        add_row.addWidget(stack_btn)
        actions_box.addLayout(add_row)

        self.stop_all_btn = QPushButton("⏹ Stop All Running")
        self.stop_all_btn.setStyleSheet(
            "background-color: #271418; border: 1px solid #7f1d1d; color: #f87171; "
            "font-weight: 700; border-radius: 8px; padding: 7px 14px; font-size: 12px;"
        )
        self.stop_all_btn.setToolTip("Stop all active servers safely")
        self.stop_all_btn.clicked.connect(self._stop_all)
        actions_box.addWidget(self.stop_all_btn)

        self.toggle_logs_btn = QPushButton("📋 Console Logs")
        self.toggle_logs_btn.setObjectName("IconBtn")
        self.toggle_logs_btn.setStyleSheet(
            "background-color: #111827; border: 1px solid #1f2937; color: #e5e7eb; "
            "font-weight: 600; border-radius: 8px; padding: 7px 14px; font-size: 12px;"
        )
        self.toggle_logs_btn.clicked.connect(self._toggle_logs)
        actions_box.addWidget(self.toggle_logs_btn)

        left_layout.addLayout(actions_box)
        root_layout.addWidget(left_panel)

        # ─── RIGHT: Content Splitter (Cards Grid + Collapsible Log Drawer) ───
        right_container = QWidget()
        right_container.setStyleSheet("background: transparent;")
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(4)

        # Scrollable Cards Container (2-Column Grid of floating cards)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setContentsMargins(4, 4, 4, 4)
        self.cards_layout.setSpacing(14)
        self.cards_layout.setColumnStretch(0, 1)
        self.cards_layout.setColumnStretch(1, 1)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Section Headers for Stacks and Projects (Figma-style pill tags)
        self.traces_header_widget = QWidget()
        th_layout = QHBoxLayout(self.traces_header_widget)
        th_layout.setContentsMargins(2, 6, 2, 2)
        th_layout.setSpacing(8)
        self.traces_header = QLabel("⚡ Multi-Project Stacks")
        self.traces_header.setObjectName("SectionHeader")
        th_layout.addWidget(self.traces_header)
        th_layout.addStretch()

        self.projects_header_widget = QWidget()
        ph_layout = QHBoxLayout(self.projects_header_widget)
        ph_layout.setContentsMargins(2, 10, 2, 2)
        ph_layout.setSpacing(8)
        self.projects_header = QLabel("📦 Individual Projects")
        self.projects_header.setObjectName("SectionHeader")
        ph_layout.addWidget(self.projects_header)
        ph_layout.addStretch()

        self._apply_section_headers_style()

        # Empty State Display when 0 cards match or exist
        self.empty_state_frame = QFrame(self.cards_container)
        self.empty_state_frame.setObjectName("EmptyStateFrame")
        self.empty_state_frame.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.empty_state_frame.setStyleSheet("""
            QFrame#EmptyStateFrame {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 14px;
                padding: 40px 24px;
            }
        """)
        es_layout = QVBoxLayout(self.empty_state_frame)
        es_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        es_layout.setSpacing(10)

        self.es_icon = QLabel("📁✨")
        self.es_icon.setStyleSheet("font-size: 38px; background: transparent;")
        self.es_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        es_layout.addWidget(self.es_icon)

        self.es_title = QLabel("No Projects or Stacks Yet")
        self.es_title.setStyleSheet("font-size: 17px; font-weight: 800; color: #f9fafb; background: transparent;")
        self.es_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        es_layout.addWidget(self.es_title)

        self.es_sub = QLabel("DevDeck is ready. Add projects manually or create multi-service stacks.")
        self.es_sub.setStyleSheet("font-size: 12px; font-weight: 500; color: #9ca3af; background: transparent;")
        self.es_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        es_layout.addWidget(self.es_sub)

        self.es_btns_widget = QWidget()
        self.es_btns_widget.setStyleSheet("background: transparent;")
        es_btns = QHBoxLayout(self.es_btns_widget)
        es_btns.setContentsMargins(0, 4, 0, 0)
        es_btns.setSpacing(10)
        es_btns.setAlignment(Qt.AlignmentFlag.AlignCenter)

        es_add_p = QPushButton("➕ Add Project")
        es_add_p.setStyleSheet("color: #FFFFFF; background-color: #10b981; border: 1px solid #10b981; border-radius: 8px; padding: 7px 16px; font-weight: 700; font-size: 12px;")
        es_add_p.clicked.connect(self._open_add_dialog)
        es_btns.addWidget(es_add_p)

        es_add_s = QPushButton("⚡ New Stack")
        es_add_s.setStyleSheet("color: #f9fafb; background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 7px 16px; font-weight: 700; font-size: 12px;")
        es_add_s.clicked.connect(self._open_new_stack_dialog)
        es_btns.addWidget(es_add_s)
        es_layout.addWidget(self.es_btns_widget)
        self.empty_state_frame.setVisible(False)

        self.scroll_area.setWidget(self.cards_container)
        self.splitter.addWidget(self.scroll_area)

        # Log Viewer Drawer
        self.log_viewer = LogViewer()
        self.log_viewer.close_requested.connect(self._on_console_closed)
        self.log_viewer.fullscreen_toggled.connect(self._on_console_fullscreen_toggled)
        self.log_viewer.open_url_requested.connect(open_url)
        self.splitter.addWidget(self.log_viewer)

        # Start with logs drawer collapsed by default so cards have full room
        self._prev_splitter_sizes = [720, 0]
        self.splitter.setSizes([720, 0])

        right_layout.addWidget(self.splitter)
        root_layout.addWidget(right_container, 1)

    def _create_mini_stat(self, initial_val: str, label_text: str, val_color: str = "#f8fafc") -> QFrame:
        badge = QFrame()
        badge.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        badge.setStyleSheet("background: transparent; border: none;")
        ly = QVBoxLayout(badge)
        ly.setContentsMargins(2, 2, 2, 2)
        ly.setSpacing(2)
        ly.setAlignment(Qt.AlignmentFlag.AlignCenter)

        val_label = QLabel(initial_val)
        val_label.setObjectName("StatValue")
        val_label.setStyleSheet(f"color: {val_color}; font-weight: 800; font-size: 16px; background: transparent;")
        val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ly.addWidget(val_label)

        sub_label = QLabel(label_text)
        sub_label.setObjectName("StatLabel")
        sub_label.setStyleSheet("color: #9ca3af; font-weight: 700; font-size: 9px; background: transparent;")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ly.addWidget(sub_label)

        badge.val_label = val_label
        badge.sub_label = sub_label
        return badge

    def _create_vdivider(self) -> QFrame:
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet("color: #1f2937; background-color: #1f2937; max-width: 1px; min-width: 1px;")
        return divider

    def _create_stat_badge(self, initial_val: str, label_text: str) -> QFrame:
        return self._create_mini_stat(initial_val, label_text)

    def _apply_badge_style(self, badge: QFrame):
        pass

    def _apply_section_headers_style(self):
        style = """
            QLabel#SectionHeader {
                background-color: #1f2937;
                color: #e5e7eb;
                border: 1px solid #374151;
                border-radius: 12px;
                padding: 4px 14px;
                font-size: 11px;
                font-weight: 700;
            }
        """
        if hasattr(self, "traces_header"):
            self.traces_header.setStyleSheet(style)
        if hasattr(self, "projects_header"):
            self.projects_header.setStyleSheet(style)


    def _init_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.search_input.setFocus)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self._toggle_logs)
        QShortcut(QKeySequence("Ctrl+Shift+L"), self, activated=self.log_viewer._toggle_fullscreen)

    def _init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self)
        if not self.app_icon.isNull():
            self.tray.setIcon(self.app_icon)
        
        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu {
                background-color: #0b0f17;
                border: 1px solid #1f2937;
                border-radius: 10px;
                padding: 6px;
                color: #f9fafb;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 6px;
                color: #e5e7eb;
                background-color: transparent;
                font-weight: 600;
                font-size: 12px;
            }
            QMenu::item:hover, QMenu::item:selected {
                background-color: #1f2937;
                color: #10b981;
                font-weight: 700;
            }
            QMenu::item:disabled {
                color: #4b5563;
                background-color: transparent;
            }
            QMenu::separator {
                height: 1px;
                background-color: #1f2937;
                margin: 4px 8px;
            }
        """)
        
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
        else:
            prev = getattr(self, "_prev_splitter_sizes", [int(total * 0.65), int(total * 0.35)])
            if prev[0] == 0:
                prev = [int(total * 0.65), int(total * 0.35)]
            self.splitter.setSizes(prev)

    def _on_console_closed(self):
        sizes = self.splitter.sizes()
        total = sum(sizes) if sum(sizes) > 0 else 800
        if sizes[0] > 30 and sizes[1] > 30:
            self._prev_splitter_sizes = list(sizes)
        self.splitter.setSizes([total, 0])
        self.log_viewer.set_fullscreen_state(False)

    def _toggle_logs(self):
        sizes = self.splitter.sizes()
        total = sum(sizes) if sum(sizes) > 0 else 800
        if sizes[1] > 30:
            if sizes[0] > 30:
                self._prev_splitter_sizes = list(sizes)
            self.splitter.setSizes([total, 0])
            self.log_viewer.set_fullscreen_state(False)
        else:
            prev = getattr(self, "_prev_splitter_sizes", [int(total * 0.65), int(total * 0.35)])
            if prev[0] == 0 or prev[1] == 0:
                prev = [int(total * 0.65), int(total * 0.35)]
            self.splitter.setSizes(prev)
            self.log_viewer.set_fullscreen_state(False)

    def _toggle_theme(self):
        self.config.data["theme"] = "dark"
        self.config.save()
        app = QApplication.instance()
        if app:
            app.setStyleSheet(DARK_THEME_QSS)
        if hasattr(self, "hero_tag"):
            self.hero_tag.setStyleSheet("background-color: #1e2638; color: #60a5fa; border: 1px solid #2d3952; font-weight: 800; font-size: 11px; border-radius: 12px; padding: 4px 12px; max-width: 170px;")
        if hasattr(self, "empty_state_frame"):
            self.empty_state_frame.setStyleSheet("""
                QFrame#EmptyStateFrame {
                    background-color: #111827;
                    border: 1px solid #1f2937;
                    border-radius: 14px;
                    padding: 40px 24px;
                }
            """)
            if hasattr(self, "es_title"):
                self.es_title.setStyleSheet("font-size: 17px; font-weight: 800; color: #f9fafb; background: transparent;")
            if hasattr(self, "es_sub"):
                self.es_sub.setStyleSheet("font-size: 12px; font-weight: 500; color: #9ca3af; background: transparent;")
        self._apply_section_headers_style()
        for card in self.cards.values():
            card.update_card_style("dark")
        for scard in self.stack_cards.values():
            scard.update_card_style("dark")

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

            card.update_card_style("dark")
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
            self.log_viewer.set_fullscreen_state(False)

        url = self.process_manager.get_detected_url(p_id) or project.get("url", "")
        self.log_viewer.set_active_project(p_id, project.get("name", "Unnamed"), url)
        self.log_viewer.clear_logs()

        # Backfill history
        logs = self.process_manager.get_logs(p_id)
        for text, is_stderr in logs:
            self.log_viewer.append_log(text, is_stderr)

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
        self._apply_filters()

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
        confirm = QMessageBox.question(
            self, "Free Port",
            f"Are you sure you want to terminate the process currently listening on port :{port}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            success = kill_process_on_port(port)
            if success:
                QMessageBox.information(self, "Port Released", f"Process on port :{port} was terminated successfully.")
            else:
                QMessageBox.warning(self, "Failed", f"Could not terminate process on port :{port}.")
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

            card.update_card_style("dark")
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
            if is_active:
                item.title_lbl.setStyleSheet("font-size: 12px; font-weight: 700; color: #34d399; background: transparent;")
                item.count_badge.setStyleSheet(
                    "background-color: #052e16; color: #34d399; font-size: 10px; font-weight: 700; "
                    "border: 1px solid #10b981; border-radius: 8px; padding: 1px 6px; min-width: 14px;"
                )
            else:
                item.title_lbl.setStyleSheet("font-size: 12px; font-weight: 600; color: #9ca3af; background: transparent;")
                item.count_badge.setStyleSheet(
                    "background-color: #111827; color: #9ca3af; font-size: 10px; font-weight: 700; "
                    "border: 1px solid #1f2937; border-radius: 8px; padding: 1px 6px; min-width: 14px;"
                )
            item.style().unpolish(item)
            item.style().polish(item)
        self._apply_filters()

    def _on_search_changed(self, text: str):
        self.search_query = text.strip().lower()
        self._apply_filters()

    def _apply_filters(self):
        # Remove cards and headers from grid positions without destroying them
        while self.cards_layout.count():
            self.cards_layout.takeAt(0)

        # 1. Filter Stack Cards
        visible_stacks = []
        for s_id, scard in self.stack_cards.items():
            stk = scard.stack
            name = stk.get("name", "").lower()
            service_names = " ".join([s.get("name", "").lower() for s in stk.get("services", [])])
            service_cmds = " ".join([s.get("command", "").lower() for s in stk.get("services", [])])
            service_stacks = " ".join([s.get("stack", "").lower() for s in stk.get("services", [])])

            matches_search = not self.search_query or (
                self.search_query in name or
                self.search_query in service_names or
                self.search_query in service_cmds or
                self.search_query in service_stacks
            )

            matches_filter = True
            if self.active_filter == "⚡ Stacks":
                matches_filter = True
            elif self.active_filter == "Running":
                matches_filter = any(r.status == "running" for r in scard.service_rows.values())
            elif self.active_filter == "All":
                matches_filter = True
            elif self.active_filter == "Favorites":
                matches_filter = False
            elif self.active_filter == "Node / Web":
                matches_filter = any(any(k in s.get("stack", "").lower() for k in ["node", "vite", "react", "next", "angular", "express"]) for s in stk.get("services", []))
            elif self.active_filter == "Java / Spring":
                matches_filter = any(any(k in s.get("stack", "").lower() for k in ["java", "spring", "gradle", "maven"]) for s in stk.get("services", []))
            elif self.active_filter == "Python":
                matches_filter = any(any(k in s.get("stack", "").lower() for k in ["python", "django", "fastapi"]) for s in stk.get("services", []))
            else:
                matches_filter = False

            is_visible = matches_search and matches_filter
            scard.setVisible(is_visible)
            if is_visible:
                visible_stacks.append(scard)

        # 2. Filter Individual Project Cards
        visible_projects = []
        if self.active_filter != "⚡ Stacks":
            for p_id, card in self.cards.items():
                proj = card.project
                name = proj.get("name", "").lower()
                path = proj.get("path", "").lower()
                cmd = proj.get("command", "").lower()
                stack = proj.get("stack", "").lower()

                # Search match
                matches_search = not self.search_query or (
                    self.search_query in name or 
                    self.search_query in path or 
                    self.search_query in cmd or 
                    self.search_query in stack
                )

                # Category filter match
                matches_filter = True
                if self.active_filter == "Running":
                    matches_filter = (card.status == "running")
                elif self.active_filter == "Favorites":
                    matches_filter = proj.get("favorite", False)
                elif self.active_filter == "Node / Web":
                    matches_filter = any(k in stack for k in ["node", "vite", "react", "next", "angular", "express"])
                elif self.active_filter == "Java / Spring":
                    matches_filter = any(k in stack for k in ["java", "spring", "gradle", "maven"])
                elif self.active_filter == "Python":
                    matches_filter = "python" in stack or "django" in stack or "fastapi" in stack

                is_visible = matches_search and matches_filter
                card.setVisible(is_visible)
                if is_visible:
                    visible_projects.append(card)
        else:
            for card in self.cards.values():
                card.setVisible(False)

        # 3. Dynamic Neo-Brutalist Layout Placement
        current_grid_row = 0

        # Full-width multi-service traces (columns 0 and 1)
        if visible_stacks:
            if visible_projects or self.active_filter == "All":
                self.traces_header.setText(f"⚡ Multi-Project Stacks  ·  {len(visible_stacks)}")
                self.traces_header_widget.setVisible(True)
                self.cards_layout.addWidget(self.traces_header_widget, current_grid_row, 0, 1, 2)
                current_grid_row += 1
            else:
                self.traces_header_widget.setVisible(False)

            for scard in visible_stacks:
                self.cards_layout.addWidget(scard, current_grid_row, 0, 1, 2)
                current_grid_row += 1
        else:
            self.traces_header_widget.setVisible(False)

        # 2-Column Grid for Individual Projects
        if visible_projects:
            if visible_stacks:
                self.projects_header.setText(f"📦 Individual Projects  ·  {len(visible_projects)}")
                self.projects_header_widget.setVisible(True)
                self.cards_layout.addWidget(self.projects_header_widget, current_grid_row, 0, 1, 2)
                current_grid_row += 1
            else:
                self.projects_header_widget.setVisible(False)

            for idx, pcard in enumerate(visible_projects):
                r = current_grid_row + (idx // 2)
                c = idx % 2
                self.cards_layout.addWidget(pcard, r, c)
            current_grid_row += (len(visible_projects) + 1) // 2
        else:
            self.projects_header.setVisible(False)

        # Empty State
        total_visible = len(visible_stacks) + len(visible_projects)
        if total_visible == 0 and hasattr(self, 'empty_state_frame'):
            self._update_empty_state_content()
            self.empty_state_frame.setVisible(True)
            self.cards_layout.addWidget(self.empty_state_frame, 0, 0, 1, 2)
        elif hasattr(self, 'empty_state_frame'):
            self.empty_state_frame.setVisible(False)

    def _update_empty_state_content(self):
        filter_name = getattr(self, "active_filter", "All")
        search = getattr(self, "search_query", "").strip()

        if search:
            self.es_icon.setText("🔍")
            self.es_title.setText(f"No Results for '{search}'")
            self.es_sub.setText("No projects or stacks match your search query.")
            if hasattr(self, "es_btns_widget"):
                self.es_btns_widget.setVisible(False)
        elif filter_name == "Running":
            self.es_icon.setText("⏸️")
            self.es_title.setText("No Projects or Stacks Running")
            self.es_sub.setText("Start a project or stack from 'All' to monitor it here.")
            if hasattr(self, "es_btns_widget"):
                self.es_btns_widget.setVisible(False)
        elif filter_name == "Favorites":
            self.es_icon.setText("⭐")
            self.es_title.setText("No Favorite Projects Yet")
            self.es_sub.setText("Click the star icon on any project card to bookmark it here.")
            if hasattr(self, "es_btns_widget"):
                self.es_btns_widget.setVisible(False)
        elif filter_name == "⚡ Stacks":
            self.es_icon.setText("⚡")
            self.es_title.setText("No Multi-Project Stacks Yet")
            self.es_sub.setText("Create a stack to launch frontend, backend, and services together.")
            if hasattr(self, "es_btns_widget"):
                self.es_btns_widget.setVisible(True)
        else:
            self.es_icon.setText("📁✨")
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
        total = len(self.cards)
        running = sum(1 for c in self.cards.values() if c.status == "running")
        ports = sum(1 for c in self.cards.values() if c.detected_url or (c.status == "running" and c.project.get("url")))

        for s_card in self.stack_cards.values():
            for row in s_card.service_rows.values():
                if row.service["id"] not in self.cards:
                    total += 1
                    if row.status == "running":
                        running += 1
                    if row.detected_url or (row.status == "running" and row.service.get("port")):
                        ports += 1

        self.total_badge.val_label.setText(str(total))
        self.running_badge.val_label.setText(str(running))
        self.ports_badge.val_label.setText(str(ports))

        # Update category counts on filter pills
        stacks_list = list(self.stack_cards.values())
        cards_list = list(self.cards.values())

        c_all = len(stacks_list) + len(cards_list)
        c_stacks = len(stacks_list)
        c_running = sum(1 for s in stacks_list if any(r.status == "running" for r in s.service_rows.values())) + \
                    sum(1 for c in cards_list if c.status == "running")
        c_fav = sum(1 for c in cards_list if c.project.get("favorite", False))
        c_node = sum(1 for s in stacks_list if any(any(k in srv.get("stack", "").lower() for k in ["node", "vite", "react", "next", "angular", "express"]) for srv in s.stack.get("services", []))) + \
                 sum(1 for c in cards_list if any(k in c.project.get("stack", "").lower() for k in ["node", "vite", "react", "next", "angular", "express"]))
        c_java = sum(1 for s in stacks_list if any(any(k in srv.get("stack", "").lower() for k in ["java", "spring", "gradle", "maven"]) for srv in s.stack.get("services", []))) + \
                 sum(1 for c in cards_list if any(k in c.project.get("stack", "").lower() for k in ["java", "spring", "gradle", "maven"]))
        c_py = sum(1 for s in stacks_list if any(any(k in srv.get("stack", "").lower() for k in ["python", "django", "fastapi"]) for srv in s.stack.get("services", []))) + \
               sum(1 for c in cards_list if any(k in c.project.get("stack", "").lower() for k in ["python", "django", "fastapi"]))

        cat_counts = {
            "All": c_all,
            "⚡ Stacks": c_stacks,
            "Running": c_running,
            "Favorites": c_fav,
            "Node / Web": c_node,
            "Java / Spring": c_java,
            "Python": c_py,
        }

        for cat_name, item in self.filter_buttons.items():
            cnt = cat_counts.get(cat_name, 0)
            item.set_count(cnt)

        # Update tray tooltip
        if hasattr(self, 'tray'):
            self.tray.setToolTip(f"DevDeck: {running}/{total} running")

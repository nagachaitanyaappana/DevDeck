"""
Main Window for DevDeck.
Integrates project cards, search, filtering, process lifecycle, logs drawer, and system tray.
"""

import os
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QScrollArea, QSplitter, QFrame,
    QSystemTrayIcon, QMenu, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QKeySequence, QShortcut

from core.config_manager import ConfigManager
from core.scanner import ProjectScanner
from core.process_manager import ProcessManager
from core.actions import open_url, open_in_vscode, open_in_terminal, open_in_file_manager, kill_process_on_port
from ui.theme import FIGMA_THEME_QSS, DARK_THEME_QSS
from .components.project_card import ProjectCard
from .components.log_viewer import LogViewer
from .components.project_dialog import ProjectDialog

class MainWindow(QMainWindow):
    def __init__(self, config_manager: ConfigManager, process_manager: ProcessManager, app_icon: QIcon = None):
        super().__init__()
        self.config = config_manager
        self.process_manager = process_manager
        
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icon.png")
        if app_icon and not app_icon.isNull():
            self.app_icon = app_icon
        elif os.path.exists(icon_path):
            self.app_icon = QIcon(icon_path)
        else:
            self.app_icon = QIcon()
        
        self.cards: Dict[str, ProjectCard] = {}
        self.active_filter = "All"
        self.search_query = ""

        self.setWindowTitle("DevDeck — Project Control Center")
        self.resize(1100, 750)
        self.setMinimumSize(850, 550)
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)

        self._init_ui()
        self._init_tray()
        self._init_shortcuts()
        self._connect_process_signals()

        # Initial load & scan if no projects saved yet
        saved_projects = self.config.get_projects()
        if not saved_projects:
            self._scan_projects(silent=True)
        else:
            self._render_projects(saved_projects.values())

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ─── 1. Header Bar ───
        header = QFrame()
        header.setObjectName("HeaderBar")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)
        header_layout.setSpacing(16)

        # Title & Subtitle
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("⚡ DevDeck")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Project Control Center")
        subtitle.setObjectName("AppSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)

        # Stats Badges
        self.total_badge = self._create_stat_badge("0", "PROJECTS")
        self.running_badge = self._create_stat_badge("0", "RUNNING")
        self.ports_badge = self._create_stat_badge("0", "ACTIVE PORTS")
        header_layout.addWidget(self.total_badge)
        header_layout.addWidget(self.running_badge)
        header_layout.addWidget(self.ports_badge)

        header_layout.addStretch()

        # Global Actions
        scan_btn = QPushButton("🔄 Rescan ~/Projects")
        scan_btn.setToolTip("Scan ~/Projects for new codebases (Ctrl+R)")
        scan_btn.clicked.connect(lambda: self._scan_projects(silent=False))
        header_layout.addWidget(scan_btn)

        self.stop_all_btn = QPushButton("⏹ Stop All")
        self.stop_all_btn.setObjectName("StopBtn")
        self.stop_all_btn.setToolTip("Stop all active servers safely")
        self.stop_all_btn.clicked.connect(self._stop_all)
        header_layout.addWidget(self.stop_all_btn)

        add_btn = QPushButton("➕ Add Project")
        add_btn.setObjectName("PrimaryBtn")
        add_btn.setToolTip("Add a custom project manually")
        add_btn.clicked.connect(self._open_add_dialog)
        header_layout.addWidget(add_btn)

        # Theme Toggle (Figma Neo-Clean / Dark Mode)
        self.theme_btn = QPushButton("🌓")
        self.theme_btn.setObjectName("IconBtn")
        self.theme_btn.setToolTip("Toggle Theme (Figma Neo-Clean / Dark)")
        self.theme_btn.setFixedSize(36, 32)
        self.theme_btn.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self.theme_btn)

        main_layout.addWidget(header)

        # ─── 2. Search & Filter Bar ───
        filter_bar = QFrame()
        filter_bar.setObjectName("FilterBar")
        filter_layout = QHBoxLayout(filter_bar)
        filter_layout.setContentsMargins(16, 8, 16, 8)
        filter_layout.setSpacing(12)

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setObjectName("SearchBar")
        self.search_input.setPlaceholderText("🔍  Search projects by name, path, or command... (Ctrl+F)")
        self.search_input.textChanged.connect(self._on_search_changed)
        filter_layout.addWidget(self.search_input)

        # Filter Pills
        self.filter_buttons = {}
        for f in ["All", "Running", "Favorites", "Node / Web", "Java / Spring", "Python"]:
            btn = QPushButton(f)
            btn.setObjectName("FilterPill")
            btn.setCheckable(True)
            if f == "All":
                btn.setChecked(True)
                btn.setProperty("checked", "true")
            btn.clicked.connect(lambda checked, name=f: self._set_filter(name))
            filter_layout.addWidget(btn)
            self.filter_buttons[f] = btn

        filter_layout.addStretch()

        # Toggle Logs Drawer Button
        self.toggle_logs_btn = QPushButton("📋 Console Logs")
        self.toggle_logs_btn.setObjectName("IconBtn")
        self.toggle_logs_btn.clicked.connect(self._toggle_logs)
        filter_layout.addWidget(self.toggle_logs_btn)

        main_layout.addWidget(filter_bar)

        # ─── 3. Main Splitter: Cards Grid + Collapsible Log Drawer ───
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(4)

        # Scrollable Cards Container
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(20, 16, 20, 20)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.cards_container)
        self.splitter.addWidget(self.scroll_area)

        # Log Viewer Drawer
        self.log_viewer = LogViewer()
        self.log_viewer.close_requested.connect(lambda: self.splitter.setSizes([750, 0]))
        self.log_viewer.open_url_requested.connect(open_url)
        self.splitter.addWidget(self.log_viewer)

        # Start with logs drawer visible but compact
        self.splitter.setSizes([550, 200])

        main_layout.addWidget(self.splitter)

    def _create_stat_badge(self, initial_val: str, label_text: str) -> QFrame:
        badge = QFrame()
        badge.setObjectName("StatBadge")
        badge.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        ly = QHBoxLayout(badge)
        ly.setContentsMargins(12, 4, 12, 4)
        ly.setSpacing(6)

        val_label = QLabel(initial_val)
        val_label.setObjectName("StatValue")
        ly.addWidget(val_label)

        sub_label = QLabel(label_text)
        sub_label.setObjectName("StatLabel")
        ly.addWidget(sub_label)

        badge.val_label = val_label
        badge.sub_label = sub_label
        self._apply_badge_style(badge)
        return badge

    def _apply_badge_style(self, badge: QFrame):
        theme = self.config.data.get("theme", "figma")
        if theme == "figma":
            badge.setStyleSheet("QFrame#StatBadge { background-color: #111827; border: 1.5px solid #111827; border-radius: 14px; padding: 3px 10px; }")
            badge.val_label.setStyleSheet("color: #FCD34D; font-weight: 900; font-size: 13px; background: transparent;")
            badge.sub_label.setStyleSheet("color: #FFFFFF; font-weight: 800; font-size: 10px; letter-spacing: 0.5px; background: transparent;")
        else:
            badge.setStyleSheet("QFrame#StatBadge { background-color: #1e2638; border: 1px solid #2d3952; border-radius: 14px; padding: 3px 10px; }")
            badge.val_label.setStyleSheet("color: #60a5fa; font-weight: 900; font-size: 13px; background: transparent;")
            badge.sub_label.setStyleSheet("color: #94a3b8; font-weight: 700; font-size: 10px; background: transparent;")

    def _init_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+F"), self, activated=self.search_input.setFocus)
        QShortcut(QKeySequence("Ctrl+R"), self, activated=lambda: self._scan_projects(silent=False))
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self._toggle_logs)

    def _init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self)
        if not self.app_icon.isNull():
            self.tray.setIcon(self.app_icon)
        
        tray_menu = QMenu()
        tray_menu.setStyleSheet("background-color: #1a2232; color: #f1f5f9;")
        
        show_act = QAction("Open DevDeck", self)
        show_act.triggered.connect(self._show_window)
        tray_menu.addAction(show_act)

        stop_all_act = QAction("⏹ Stop All Running", self)
        stop_all_act.triggered.connect(self._stop_all)
        tray_menu.addAction(stop_all_act)

        tray_menu.addSeparator()

        quit_act = QAction("Quit DevDeck", self)
        quit_act.triggered.connect(QApplication.instance().quit)
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

    def _toggle_logs(self):
        sizes = self.splitter.sizes()
        if sizes[1] > 20:
            self.splitter.setSizes([sum(sizes), 0])
        else:
            self.splitter.setSizes([int(sum(sizes) * 0.65), int(sum(sizes) * 0.35)])

    def _toggle_theme(self):
        current = self.config.data.get("theme", "figma")
        new_theme = "dark" if current == "figma" else "figma"
        self.config.data["theme"] = new_theme
        self.config.save()
        app = QApplication.instance()
        if app:
            app.setStyleSheet(DARK_THEME_QSS if new_theme == "dark" else FIGMA_THEME_QSS)
        for b in [self.total_badge, self.running_badge, self.ports_badge]:
            self._apply_badge_style(b)

    def _scan_projects(self, silent: bool = False):
        scanner = ProjectScanner(self.config.get_scan_dirs(), max_depth=5)
        found = scanner.scan_all()
        
        # Merge with existing
        existing = self.config.get_projects()
        merged_count = 0
        for p in found:
            pid = p["id"]
            if pid not in existing:
                self.config.save_project(p)
                merged_count += 1
            else:
                # Update detected command/port if unset
                curr = existing[pid]
                if not curr.get("command") and p.get("command"):
                    curr["command"] = p["command"]
                if not curr.get("port") and p.get("port"):
                    curr["port"] = p["port"]
                self.config.save_project(curr)

        self._render_projects(self.config.get_projects().values())
        if not silent:
            QMessageBox.information(
                self, "Scan Complete", 
                f"Scan complete!\nFound {len(found)} total projects ({merged_count} new)."
            )

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

            # Check if already running in process manager or listening on port
            p_id = p["id"]
            card.set_status(self.process_manager.get_status(p_id))
            url = self.process_manager.get_detected_url(p_id)
            if not url and p.get("port") and self.process_manager.is_port_listening(p["port"]):
                url = p.get("url") or f"http://localhost:{p['port']}"
            if url:
                card.set_detected_url(url)

            self.cards[p_id] = card
            self.cards_layout.addWidget(card)

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
        self.process_manager.stop_project(project_id)
        self._update_stats()

    def _restart_project(self, project: dict):
        self._view_logs(project)
        self.process_manager.restart_project(project)
        self._update_stats()

    def _stop_all(self):
        self.process_manager.stop_all()
        self._update_stats()

    def _view_logs(self, project: dict):
        p_id = project["id"]
        # Ensure log viewer is visible
        sizes = self.splitter.sizes()
        if sizes[1] < 50:
            self.splitter.setSizes([int(sum(sizes) * 0.65), int(sum(sizes) * 0.35)])

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
        self._update_stats()

    def _on_url_detected(self, project_id: str, url: str):
        if project_id in self.cards:
            self.cards[project_id].set_detected_url(url)
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

    def _set_filter(self, filter_name: str):
        self.active_filter = filter_name
        for name, btn in self.filter_buttons.items():
            is_active = (name == filter_name)
            btn.setChecked(is_active)
            btn.setProperty("checked", "true" if is_active else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._apply_filters()

    def _on_search_changed(self, text: str):
        self.search_query = text.strip().lower()
        self._apply_filters()

    def _apply_filters(self):
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

            card.setVisible(matches_search and matches_filter)

    def _update_stats(self):
        total = len(self.cards)
        running = sum(1 for c in self.cards.values() if c.status == "running")
        ports = sum(1 for c in self.cards.values() if c.detected_url or (c.status == "running" and c.project.get("url")))

        self.total_badge.val_label.setText(str(total))
        self.running_badge.val_label.setText(str(running))
        self.ports_badge.val_label.setText(str(ports))

        # Update tray tooltip
        if hasattr(self, 'tray'):
            self.tray.setToolTip(f"DevDeck: {running}/{total} running")

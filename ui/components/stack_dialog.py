"""
Stack Creation & Editing Dialog for DevDeck.
Allows users to manually create or configure multi-project stacks (e.g. ITIAP Backend + Frontend)
with individual paths, launch commands, and ports for 1-click simultaneous launching.
Styled with Figma theme (purple/violet color scheme).
"""

import os
import hashlib
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFileDialog, QMessageBox,
    QScrollArea, QWidget, QFrame
)
from PyQt6.QtCore import Qt

STACK_OPTIONS = [
    "Vite / React", "Vite", "Next.js", "Node.js", "Express",
    "Spring Boot (Maven)", "Spring Boot (Gradle)", "Gradle",
    "Python App", "Python CLI", "Django", "Flask / FastAPI",
    "Docker Compose", "Custom"
]

class ServiceRow(QFrame):
    """Row representing a single service within a multi-project stack."""
    def __init__(self, service_data: Optional[Dict] = None, existing_projects: Optional[List[Dict]] = None, parent=None):
        super().__init__(parent)
        self.existing_projects = existing_projects or []
        self.setObjectName("ServiceRow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Header of service row with quick autofill from existing projects
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.service_badge = QLabel("Service / Component")
        self.service_badge.setObjectName("ServiceRowBadge")
        top_bar.addWidget(self.service_badge)

        top_bar.addStretch()

        if self.existing_projects:
            self.autofill_combo = QComboBox()
            self.autofill_combo.addItem("Autofill from project…")
            for p in self.existing_projects:
                self.autofill_combo.addItem(p.get("name", "Project"), p)
            self.autofill_combo.currentIndexChanged.connect(self._on_autofill_selected)
            top_bar.addWidget(self.autofill_combo)

        self.remove_btn = QPushButton("Remove")
        self.remove_btn.setObjectName("StopBtn")
        top_bar.addWidget(self.remove_btn)
        layout.addLayout(top_bar)

        # Grid of fields
        # Row 1: Name and Stack
        r1 = QHBoxLayout()
        r1.setSpacing(10)

        n_box = QVBoxLayout()
        n_box.setSpacing(2)
        n_label = QLabel("Service Name:")
        n_label.setObjectName("DialogFieldLabel")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Backend, Frontend, API")
        n_box.addWidget(n_label)
        n_box.addWidget(self.name_input)
        r1.addLayout(n_box, 2)

        s_box = QVBoxLayout()
        s_box.setSpacing(2)
        s_label = QLabel("Tech Stack:")
        s_label.setObjectName("DialogFieldLabel")
        self.stack_combo = QComboBox()
        self.stack_combo.addItems(STACK_OPTIONS)
        s_box.addWidget(s_label)
        s_box.addWidget(self.stack_combo)
        r1.addLayout(s_box, 1)

        p_box = QVBoxLayout()
        p_box.setSpacing(2)
        p_label = QLabel("Port:")
        p_label.setObjectName("DialogFieldLabel")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("e.g. 8080")
        p_box.addWidget(p_label)
        p_box.addWidget(self.port_input)
        r1.addLayout(p_box, 1)

        layout.addLayout(r1)

        # Row 2: Directory Path with browse button
        path_box = QVBoxLayout()
        path_box.setSpacing(2)
        path_label = QLabel("Directory Path:")
        path_label.setObjectName("DialogFieldLabel")
        
        path_row = QHBoxLayout()
        path_row.setSpacing(6)
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("/home/naga/Projects/...")
        path_row.addWidget(self.path_input)

        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("IconBtn")
        browse_btn.clicked.connect(self._browse_dir)
        path_row.addWidget(browse_btn)

        path_box.addWidget(path_label)
        path_box.addLayout(path_row)
        layout.addLayout(path_box)

        # Row 3: Launch Command
        cmd_box = QVBoxLayout()
        cmd_box.setSpacing(2)
        cmd_label = QLabel("Launch Command:")
        cmd_label.setObjectName("DialogFieldLabel")
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("e.g. ./mvnw spring-boot:run, npm run dev, python app.py")
        cmd_box.addWidget(cmd_label)
        cmd_box.addWidget(self.cmd_input)
        layout.addLayout(cmd_box)

        # Fill if initial data provided
        if service_data:
            self.service_id = service_data.get("id")
            self.name_input.setText(service_data.get("name", ""))
            self.path_input.setText(service_data.get("path", ""))
            self.cmd_input.setText(service_data.get("command", ""))
            port = service_data.get("port")
            if port:
                self.port_input.setText(str(port))
            stack_val = service_data.get("stack", "")
            idx = self.stack_combo.findText(stack_val)
            if idx >= 0:
                self.stack_combo.setCurrentIndex(idx)
        else:
            self.service_id = None

    def _browse_dir(self):
        curr = self.path_input.text().strip() or os.path.expanduser("~/Projects")
        folder = QFileDialog.getExistingDirectory(self, "Select Service Project Directory", curr)
        if folder:
            self.path_input.setText(folder)
            if not self.name_input.text().strip():
                self.name_input.setText(os.path.basename(folder))

    def _on_autofill_selected(self, index: int):
        if index <= 0:
            return
        proj = self.autofill_combo.currentData()
        if proj:
            self.name_input.setText(proj.get("name", ""))
            self.path_input.setText(proj.get("path", ""))
            self.cmd_input.setText(proj.get("command", ""))
            port = proj.get("port")
            if port:
                self.port_input.setText(str(port))
            stack = proj.get("stack", "")
            idx = self.stack_combo.findText(stack)
            if idx >= 0:
                self.stack_combo.setCurrentIndex(idx)

    def get_data(self) -> Optional[Dict]:
        name = self.name_input.text().strip()
        path = self.path_input.text().strip()
        cmd = self.cmd_input.text().strip()
        stack = self.stack_combo.currentText()
        port_txt = self.port_input.text().strip()

        if not name or not path or not cmd:
            return None

        port = int(port_txt) if port_txt.isdigit() else None
        s_id = self.service_id or hashlib.sha256(f"{path}::{name}::{port}".encode()).hexdigest()[:12]

        return {
            "id": s_id,
            "name": name,
            "path": path,
            "command": cmd,
            "port": port,
            "stack": stack,
        }


class StackDialog(QDialog):
    """Dialog to create or edit a multi-project stack."""
    def __init__(self, stack_data: Optional[Dict] = None, existing_projects: Optional[List[Dict]] = None, parent=None):
        super().__init__(parent)
        self.stack_data = stack_data or {}
        self.existing_projects = existing_projects or []
        self.service_rows: List[ServiceRow] = []

        self.setWindowTitle("Multi-Project Stack Builder" if not stack_data else "Edit Stack")
        self.resize(680, 600)
        self.setMinimumSize(580, 480)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # Header Title
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("Multi-Project Stack")
        title.setObjectName("DialogTitle")
        sub = QLabel("Group multiple services (e.g. Backend + Frontend) to launch simultaneously with 1 click.")
        sub.setObjectName("DialogSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        root.addLayout(title_box)

        # Stack Name input
        name_box = QVBoxLayout()
        name_box.setSpacing(4)
        name_label = QLabel("Stack Name:")
        name_label.setObjectName("DialogFieldLabel")
        self.stack_name_input = QLineEdit()
        self.stack_name_input.setPlaceholderText("e.g. ITIAP Fullstack, Minecraft Tools Hub")
        self.stack_name_input.setText(self.stack_data.get("name", ""))
        name_box.addWidget(name_label)
        name_box.addWidget(self.stack_name_input)
        root.addLayout(name_box)

        # Scroll area for services
        services_label = QLabel("Services in this Stack:")
        services_label.setObjectName("DialogFieldLabel")
        root.addWidget(services_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setObjectName("StackDialogScroll")

        self.services_container = QWidget()
        self.services_container.setObjectName("StackDialogContainer")
        self.services_layout = QVBoxLayout(self.services_container)
        self.services_layout.setContentsMargins(0, 0, 0, 0)
        self.services_layout.setSpacing(10)
        self.services_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll.setWidget(self.services_container)
        root.addWidget(self.scroll, 1)

        # Populate existing services or start with 2 empty services
        existing_services = self.stack_data.get("services", [])
        if existing_services:
            for s in existing_services:
                self._add_service_row(s)
        else:
            # Default to 2 services (Backend + Frontend)
            self._add_service_row({"name": "Backend"})
            self._add_service_row({"name": "Frontend"})

        # Button to add another service
        add_service_btn = QPushButton("+  Add Another Service")
        add_service_btn.setObjectName("IconBtn")
        add_service_btn.clicked.connect(lambda: self._add_service_row())
        root.addWidget(add_service_btn)

        # Dialog Buttons
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("IconBtn")
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(cancel_btn)

        btn_box.addStretch()

        save_btn = QPushButton("Save Stack")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self._on_save)
        btn_box.addWidget(save_btn)

        root.addLayout(btn_box)

    def _add_service_row(self, service_data: Optional[Dict] = None):
        row = ServiceRow(service_data, self.existing_projects, self.services_container)
        row.remove_btn.clicked.connect(lambda: self._remove_service_row(row))
        self.service_rows.append(row)
        self.services_layout.addWidget(row)

    def _remove_service_row(self, row: ServiceRow):
        if len(self.service_rows) <= 1:
            QMessageBox.warning(self, "Cannot Remove", "A stack must contain at least 1 service.")
            return
        self.service_rows.remove(row)
        row.setParent(None)
        row.deleteLater()

    def _on_save(self):
        name = self.stack_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a name for this stack (e.g. ITIAP Fullstack).")
            return

        services = []
        seen_ids = set()
        for idx, row in enumerate(self.service_rows):
            data = row.get_data()
            if not data:
                QMessageBox.warning(
                    self, "Incomplete Service", 
                    "Please fill in the Name, Path, and Launch Command for all services in the stack."
                )
                return
            s_id = data.get("id")
            if not s_id or s_id in seen_ids:
                s_id = hashlib.sha256(f"{name}::{idx}::{data['path']}::{data['name']}::{data.get('port')}".encode()).hexdigest()[:12]
                data["id"] = s_id
            seen_ids.add(s_id)
            services.append(data)

        if not services:
            QMessageBox.warning(self, "No Services", "Please add at least one service to the stack.")
            return

        self.result_stack = {
            "id": self.stack_data.get("id"),
            "name": name,
            "services": services
        }
        self.accept()

    def get_result(self) -> Optional[Dict]:
        return getattr(self, "result_stack", None)
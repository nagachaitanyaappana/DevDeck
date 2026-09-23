"""
Project Add/Edit Dialog for DevDeck.
Allows users to add any project manually or modify detected commands and ports.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QComboBox, QFileDialog, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt

class ProjectDialog(QDialog):
    def __init__(self, parent=None, project_data=None):
        super().__init__(parent)
        self.project_data = project_data or {}
        self.setWindowTitle("Edit Project" if project_data else "Add New Project")
        self.setFixedWidth(480)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        header = QLabel("Edit Project" if self.project_data else "Add New Project")
        header.setObjectName("DialogHeader")
        layout.addWidget(header)

        # Name
        layout.addWidget(QLabel("Project Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. My Awesome Web App")
        self.name_input.setText(self.project_data.get("name", ""))
        layout.addWidget(self.name_input)

        # Directory Path
        layout.addWidget(QLabel("Directory Path:"))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("/home/naga/Projects/...")
        self.path_input.setText(self.project_data.get("path", ""))
        path_layout.addWidget(self.path_input)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_dir)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Launch Command
        layout.addWidget(QLabel("Launch Command:"))
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("e.g. npm run dev, gradle bootRun, python3 main.py")
        self.cmd_input.setText(self.project_data.get("command", ""))
        layout.addWidget(self.cmd_input)

        # Stack / Type & Port in a row
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        # Stack Type
        stack_layout = QVBoxLayout()
        stack_layout.addWidget(QLabel("Stack / Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Node / Vite / React", 
            "Next.js", 
            "Spring Boot (Gradle)", 
            "Spring Boot (Maven)", 
            "Python App / CLI", 
            "Docker Compose", 
            "Custom"
        ])
        current_stack = self.project_data.get("stack", "Custom")
        idx = self.type_combo.findText(current_stack, Qt.MatchFlag.MatchContains)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        stack_layout.addWidget(self.type_combo)
        row_layout.addLayout(stack_layout)

        # Port
        port_layout = QVBoxLayout()
        port_layout.addWidget(QLabel("Port (optional):"))
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("e.g. 5173, 8080")
        if self.project_data.get("port"):
            self.port_input.setText(str(self.project_data["port"]))
        port_layout.addWidget(self.port_input)
        row_layout.addLayout(port_layout)

        layout.addLayout(row_layout)

        # Target URL
        layout.addWidget(QLabel("Web URL (optional):"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("e.g. http://localhost:5173")
        self.url_input.setText(self.project_data.get("url", ""))
        layout.addWidget(self.url_input)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Project")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _browse_dir(self):
        start_dir = self.path_input.text() or os.path.expanduser("~/Projects")
        d = QFileDialog.getExistingDirectory(self, "Select Project Directory", start_dir)
        if d:
            self.path_input.setText(d)
            if not self.name_input.text():
                self.name_input.setText(os.path.basename(d))

    def _save(self):
        name = self.name_input.text().strip()
        path = self.path_input.text().strip()
        cmd = self.cmd_input.text().strip()

        if not name or not path or not cmd:
            QMessageBox.warning(self, "Missing Fields", "Please provide a Project Name, Directory Path, and Command.")
            return

        if not os.path.exists(path):
            QMessageBox.warning(self, "Invalid Directory", f"The directory '{path}' does not exist.")
            return

        port = None
        if self.port_input.text().strip().isdigit():
            port = int(self.port_input.text().strip())

        url = self.url_input.text().strip()
        if not url and port:
            url = f"http://localhost:{port}"

        self.result_data = {
            "id": self.project_data.get("id"),
            "name": name,
            "display_name": name,
            "path": path,
            "command": cmd,
            "stack": self.type_combo.currentText(),
            "port": port,
            "url": url,
            "favorite": self.project_data.get("favorite", False),
        }
        self.accept()

    def get_data(self):
        return self.result_data

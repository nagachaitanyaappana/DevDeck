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
        self.setFixedWidth(520)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QDialog {
                background-color: #151b27;
                border: 1.5px solid #2e3c54;
                border-radius: 14px;
            }
        """)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        header = QLabel("⚙ Edit Project" if self.project_data else "➕ Add New Project")
        header.setObjectName("DialogHeader")
        header.setStyleSheet("font-size: 20px; font-weight: 900; color: #f1f5f9; background: transparent;")
        layout.addWidget(header)

        # Name
        lbl_name = QLabel("Project Name:")
        lbl_name.setStyleSheet("font-size: 11px; font-weight: 800; color: #94a3b8; background: transparent;")
        layout.addWidget(lbl_name)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. My Awesome Web App")
        self.name_input.setText(self.project_data.get("name", ""))
        self.name_input.setStyleSheet("color: #f1f5f9; background-color: #1a2234; border: 1.5px solid #2e3c54; border-radius: 8px; padding: 7px 10px; font-weight: 600;")
        layout.addWidget(self.name_input)

        # Directory Path
        lbl_path = QLabel("Directory Path:")
        lbl_path.setStyleSheet("font-size: 11px; font-weight: 800; color: #94a3b8; background: transparent;")
        layout.addWidget(lbl_path)
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("/home/naga/Projects/...")
        self.path_input.setText(self.project_data.get("path", ""))
        self.path_input.setStyleSheet("color: #f1f5f9; background-color: #1a2234; border: 1.5px solid #2e3c54; border-radius: 8px; padding: 7px 10px; font-weight: 500;")
        path_layout.addWidget(self.path_input)

        browse_btn = QPushButton("📁 Browse...")
        browse_btn.setStyleSheet("""
            QPushButton {
                color: #f1f5f9;
                background-color: #1e2638;
                border: 1.5px solid #2e3c54;
                border-radius: 8px;
                padding: 7px 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #2e3c54;
            }
        """)
        browse_btn.clicked.connect(self._browse_dir)
        path_layout.addWidget(browse_btn)
        layout.addLayout(path_layout)

        # Launch Command
        lbl_cmd = QLabel("Launch Command:")
        lbl_cmd.setStyleSheet("font-size: 11px; font-weight: 800; color: #94a3b8; background: transparent;")
        layout.addWidget(lbl_cmd)
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("e.g. npm run dev, gradle bootRun, python3 main.py")
        self.cmd_input.setText(self.project_data.get("command", ""))
        self.cmd_input.setStyleSheet("color: #f1f5f9; background-color: #1a2234; border: 1.5px solid #2e3c54; border-radius: 8px; padding: 7px 10px; font-family: monospace; font-weight: 600;")
        layout.addWidget(self.cmd_input)

        # Stack / Type & Port in a row
        row_layout = QHBoxLayout()
        row_layout.setSpacing(10)

        # Stack Type
        stack_layout = QVBoxLayout()
        lbl_type = QLabel("Stack / Type:")
        lbl_type.setStyleSheet("font-size: 11px; font-weight: 800; color: #94a3b8; background: transparent;")
        stack_layout.addWidget(lbl_type)
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
        self.type_combo.setStyleSheet("""
            QComboBox {
                color: #f1f5f9;
                background-color: #1a2234;
                border: 1.5px solid #2e3c54;
                border-radius: 8px;
                padding: 7px 10px;
                font-weight: 700;
            }
            QComboBox QAbstractItemView {
                background-color: #151b27;
                color: #f1f5f9;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
        """)
        stack_layout.addWidget(self.type_combo)
        row_layout.addLayout(stack_layout, 2)

        # Port
        port_layout = QVBoxLayout()
        lbl_port = QLabel("Port (optional):")
        lbl_port.setStyleSheet("font-size: 11px; font-weight: 800; color: #94a3b8; background: transparent;")
        port_layout.addWidget(lbl_port)
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("e.g. 5173, 8080")
        if self.project_data.get("port"):
            self.port_input.setText(str(self.project_data["port"]))
        self.port_input.setStyleSheet("color: #f1f5f9; background-color: #1a2234; border: 1.5px solid #2e3c54; border-radius: 8px; padding: 7px 10px; font-weight: 600;")
        port_layout.addWidget(self.port_input)
        row_layout.addLayout(port_layout, 1)

        layout.addLayout(row_layout)

        # Target URL
        lbl_url = QLabel("Web URL (optional):")
        lbl_url.setStyleSheet("font-size: 11px; font-weight: 800; color: #94a3b8; background: transparent;")
        layout.addWidget(lbl_url)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("e.g. http://localhost:5173")
        self.url_input.setText(self.project_data.get("url", ""))
        self.url_input.setStyleSheet("color: #f1f5f9; background-color: #1a2234; border: 1.5px solid #2e3c54; border-radius: 8px; padding: 7px 10px; font-weight: 500;")
        layout.addWidget(self.url_input)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                color: #94a3b8;
                background-color: #1e2638;
                border: 1.5px solid #2e3c54;
                border-radius: 12px;
                padding: 8px 20px;
                font-weight: 800;
            }
            QPushButton:hover {
                background-color: #2e3c54;
                color: #f1f5f9;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("💾 Save Project")
        save_btn.setStyleSheet("""
            QPushButton {
                color: #ffffff;
                background-color: #2563eb;
                border: 1.5px solid #3b82f6;
                border-radius: 12px;
                padding: 8px 22px;
                font-weight: 900;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
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

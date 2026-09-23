"""
Configuration Manager for DevDeck.
Handles persistent storage of scanned and custom projects, settings, and favorites.
"""

import json
import os
import hashlib
from typing import Dict, List, Any, Optional

CONFIG_DIR = os.path.expanduser("~/.config/devdeck")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG: Dict[str, Any] = {
    "scan_dirs": [os.path.expanduser("~/Projects")],
    "scan_depth": 3,
    "theme": "dark",
    "terminal_emulator": "xfce4-terminal",
    "editor_command": "code",
    "projects": {},
}

def generate_project_id(path: str, name: str) -> str:
    """Generates a stable unique ID for a project path and name."""
    raw = f"{os.path.abspath(path)}::{name}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

class ConfigManager:
    def __init__(self, config_file: str = CONFIG_FILE):
        self.config_file = config_file
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Loads configuration from JSON file or initializes defaults."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"[ConfigManager] Error reading config: {e}. Resetting to defaults.")
                self.data = dict(DEFAULT_CONFIG)
        else:
            self.data = dict(DEFAULT_CONFIG)
            self.save()

        # Ensure all default keys exist
        for k, v in DEFAULT_CONFIG.items():
            if k not in self.data:
                self.data[k] = v

    def save(self) -> None:
        """Saves current configuration to file."""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"[ConfigManager] Error writing config: {e}")

    def get_projects(self) -> Dict[str, Dict[str, Any]]:
        return self.data.get("projects", {})

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        return self.data.get("projects", {}).get(project_id)

    def save_project(self, project: Dict[str, Any]) -> str:
        """Adds or updates a project."""
        p_id = project.get("id")
        if not p_id:
            p_id = generate_project_id(project["path"], project.get("name", "Unnamed"))
            project["id"] = p_id

        if "projects" not in self.data:
            self.data["projects"] = {}
        self.data["projects"][p_id] = project
        self.save()
        return p_id

    def remove_project(self, project_id: str) -> bool:
        """Removes a project by ID."""
        if project_id in self.data.get("projects", {}):
            del self.data["projects"][project_id]
            self.save()
            return True
        return False

    def toggle_favorite(self, project_id: str) -> bool:
        """Toggles favorite status for a project."""
        proj = self.get_project(project_id)
        if proj:
            proj["favorite"] = not proj.get("favorite", False)
            self.save()
            return proj["favorite"]
        return False

    def get_scan_dirs(self) -> List[str]:
        return self.data.get("scan_dirs", [os.path.expanduser("~/Projects")])

    def set_scan_dirs(self, dirs: List[str]) -> None:
        self.data["scan_dirs"] = dirs
        self.save()

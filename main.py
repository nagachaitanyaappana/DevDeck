#!/usr/bin/env python3
"""
DevDeck — Native Project Control Center
Entry point for launching and managing local developer projects.
"""

import sys
import os
import signal

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from core.config_manager import ConfigManager
from core.process_manager import ProcessManager
from ui.theme import FIGMA_THEME_QSS, DARK_THEME_QSS
from ui.main_window import MainWindow

def main():
    # Allow clean Ctrl+C handling in terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("DevDeck")
    app.setApplicationDisplayName("DevDeck")
    app.setDesktopFileName("devdeck.desktop")

    # Load App Icon
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png")
    app_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    # Initialize Core Subsystems
    config_mgr = ConfigManager()
    process_mgr = ProcessManager()

    # Apply Modern Blue-Black Dark Theme
    app.setStyleSheet(DARK_THEME_QSS)

    # Clean shutdown of all running child servers on app exit
    app.aboutToQuit.connect(process_mgr.stop_all)

    # Create and Show Main Window
    window = MainWindow(config_mgr, process_mgr, app_icon)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

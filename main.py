#!/usr/bin/env python3
"""
DevDeck — Native Project Control Center
Entry point for launching and managing local developer projects.
"""

import sys
import os
import signal
import hashlib

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

from core.config_manager import ConfigManager
from core.process_manager import ProcessManager
from ui.theme import apply_theme
from ui.main_window import MainWindow

def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

def main():
    # Allow clean Ctrl+C handling in terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("DevDeck")

    # Keep one GUI instance per Windows user. A second launch asks the
    # existing instance (including one minimized to the tray) to foreground.
    user_key = hashlib.sha256(os.path.expanduser("~").casefold().encode("utf-8")).hexdigest()[:12]
    server_name = f"DevDeck-{user_key}"
    probe = QLocalSocket()
    probe.connectToServer(server_name)
    if probe.waitForConnected(500):
        probe.write(b"activate")
        probe.flush()
        probe.waitForBytesWritten(500)
        probe.disconnectFromServer()
        return 0

    # Remove a stale local-server endpoint only after no instance accepted
    # the connection.
    QLocalServer.removeServer(server_name)
    instance_server = QLocalServer()
    if not instance_server.listen(server_name):
        print(f"[DevDeck] Single-instance listener unavailable: {instance_server.errorString()}")
    app.setApplicationDisplayName("DevDeck")
    app.setDesktopFileName("devdeck.desktop")
    app.setQuitOnLastWindowClosed(False)

    # Load App Icon
    icon_path = get_resource_path(os.path.join("assets", "icon.png"))
    app_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()
    if not app_icon.isNull():
        app.setWindowIcon(app_icon)

    # Initialize Core Subsystems
    config_mgr = ConfigManager()
    process_mgr = ProcessManager()

    # Apply the saved theme (MainWindow also applies it once built, so that
    # widgets created later pick it up too)
    apply_theme(app, config_mgr.data.get("theme", "light"))

    # Clean shutdown of all running child servers on app exit
    app.aboutToQuit.connect(process_mgr.stop_all)

    # Create and Show Main Window
    window = MainWindow(config_mgr, process_mgr, app_icon)
    window.show()

    def activate_existing_instance():
        while instance_server.hasPendingConnections():
            connection = instance_server.nextPendingConnection()
            if connection:
                connection.waitForReadyRead(250)
                if b"activate" in bytes(connection.readAll()):
                    window._show_window()
                connection.disconnectFromServer()
                connection.deleteLater()

    instance_server.newConnection.connect(activate_existing_instance)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

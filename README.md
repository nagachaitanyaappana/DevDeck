# ⚡ DevDeck — Developer Project & Multi-Stack Control Center

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-orange.svg)](https://github.com/nagachaitanyaappana/DevDeck/releases)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.1.0-a78bfa.svg)](https://github.com/nagachaitanyaappana/DevDeck/releases)

**DevDeck** is a native desktop dashboard built with Python and PyQt6 for Linux and Windows. It centralises your development environment into one workspace — eliminating terminal sprawl, forgotten ports, and multi-service startup headaches.

Everything is under your control: DevDeck never scans your filesystem in the background. You add exactly the projects you want, and it stays out of the way.

---

## 🌟 Key Features

### ⚡ Multi-Project Stacks

- **Simultaneous launch**: group related services (backend API, frontend, microservices) into a single stack and start or stop all of them with one click.
- **Per-service controls**: start, stop, and restart any service independently without disturbing the rest of the stack.
- **Stack-wide shortcuts**: open the whole stack in VS Code, a terminal, or your file manager.
- **Automatic URL detection**: DevDeck parses process output for localhost URLs and port announcements, so a full-stack app is one click from opening in your browser.
- **Status summary** on each stack shows how many of its services are actually running.

### 📦 Deterministic Project Control

- **100% user-controlled**: no automatic filesystem scanning — add, configure, and organise only what you choose.
- **Arbitrary commands and paths**: `npm run dev`, `gradle bootRun`, `python app.py`, `docker compose up`, or anything else.
- **Port management**: click any port to reassign it. DevDeck exports the right environment variables for you — `PORT`, `VITE_PORT`, `FLASK_RUN_PORT`, and `-Dserver.port=` for Spring Boot.

### 📋 Live ANSI Console

- **Non-blocking streaming** of stdout and stderr.
- **Full ANSI colour support**, so banners and coloured output from Vite, Next.js, Spring Boot, and FastAPI render as they do in your terminal.
- **Console utilities**: in-console search, autoscroll toggle, copy all, and full-screen mode.

### 🎨 Light & Dark Themes

- **Two complete, hand-built stylesheets.** The active theme is saved to your config and restored on launch.
- **WCAG AA accessible.** All fifteen text/background pairs in both themes meet or exceed a 4.5:1 contrast ratio.
- **Dark by default**, with a purple-on-near-black palette suited to long sessions.

### 📊 Monitoring & Safety

- **Live CPU and memory** per running project.
- **Clean process teardown**: recursive process-tree termination via `psutil`, so child processes and ports are genuinely released.
- **Port ownership awareness**: DevDeck matches a listening port against a project's directory before reporting it as running, so two projects sharing a port don't produce false positives.
- **Informed port killing**: terminating a port shows the process name, PID, and working directory first, and defaults to *No*.
- **System tray integration**: close to tray, servers keep running, and the tooltip shows the live running count.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + F` | Focus the search bar |
| `Ctrl + N` | Add a new project |
| `Ctrl + L` | Toggle the console drawer |
| `Ctrl + Shift + L` | Toggle full-screen console |
| `Esc` | Clear the search, or dismiss a dialog |

---

## 📦 Download Pre-built Binaries

Ready-to-use standalone executables are on the **[GitHub Releases](https://github.com/nagachaitanyaappana/DevDeck/releases)** page:

| Platform | Package | Description |
| :--- | :--- | :--- |
| **Linux (x86_64)** | `DevDeck-linux-x86_64.tar.gz` | Standalone executable + `.desktop` launcher & icon |
| **Windows (x64)** | `DevDeck-windows-x64.zip` | Standalone `DevDeck.exe` |

The Linux build is a standalone binary alongside a `.desktop` entry and the
app icon. Copy them to your desktop environment and make the binary executable:

```bash
tar -xzf DevDeck-linux-x86_64.tar.gz
sudo cp DevDeck devdeck.desktop ~/.local/bin/ && sudo cp icon.png ~/.local/share/icons/
```

---

## 🚀 Running from Source

### Prerequisites

- **Python 3.10+**
- **Linux or Windows**

```bash
git clone https://github.com/nagachaitanyaappana/DevDeck.git
cd DevDeck

# Create a virtual environment (recommended)
python3 -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
python3 main.py
```

On Linux, `psutil` needs elevated permissions to see every process, so some
port details may be incomplete unless you run with `sudo`:

```bash
sudo python3 main.py
```

---

## 📁 Project Structure

```
DevDeck/
├── main.py                     # Application entry point
├── version.py                  # Single source of truth for the version string
├── core/
│   ├── config_manager.py       # JSON configuration persistence (~/.config/devdeck/)
│   ├── process_manager.py      # Async process lifecycle & telemetry (psutil + QProcess)
│   └── actions.py              # System actions (VS Code, terminal, browser, ports)
├── ui/
│   ├── main_window.py          # Layout, sidebar, filtering, card orchestration
│   ├── theme.py                # Token-driven light & dark stylesheet generation
│   ├── icons.py                # Monochrome icon set
│   └── components/
│       ├── project_card.py     # Individual project card
│       ├── stack_card.py       # Full-width multi-project stack card
│       ├── project_dialog.py   # Add / edit project modal
│       ├── stack_dialog.py     # Multi-project stack builder modal
│       └── log_viewer.py       # Live ANSI console drawer
├── assets/
│   ├── icon.png
│   └── devdeck_current_ui.png
├── devdeck.desktop             # Linux launcher entry
├── devdeck                     # Source-run launcher script
├── devdeck.spec                # PyInstaller configuration
└── requirements.txt
```

---

## ⚙️ How Theming Works

`ui/theme.py` generates both stylesheets from a pair of token dictionaries, so
light and dark can never drift apart:

```python
from ui.theme import LIGHT, DARK, stylesheet_for, apply_theme

apply_theme(app, "dark")        # switch the running app
```

To adjust the palette, edit the token values at the top of `theme.py`. Every
colour in the UI derives from them, so there is a single place to make a change.

---

## 🐛 Reporting Issues

Found something broken? Please open an issue with your OS, Python version, and
the steps that reproduce it. Console output helps a lot for process-related
problems.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

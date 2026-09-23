# ⚡ DevDeck — Developer Project & Multi-Stack Control Center

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![Platform](https://img.shields.io/badge/Platform-Linux-orange.svg)](https://www.linux.org/)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**DevDeck** is a fast, responsive, native Linux desktop dashboard built with Python and PyQt6. It centralizes your entire development environment into a single, clean workspace—eliminating terminal sprawl, forgotten ports, and multi-service startup headaches.

Designed with an aesthetic Neo-Brutalist / Figma-inspired interface, DevDeck gives you manual, deterministic control over your individual projects and complex multi-project traces.

---

## 🌟 Key Features

### ⚡ Multi-Project Traces (Component Stacks)
- **Simultaneous 1-Click Launch**: Group interconnected services (e.g., Backend API, Frontend Web, Microservices) into unified Traces. Start or stop all dependent components with a single click.
- **Per-Service Controls**: Individual `▶ Start`, `⏹ Stop`, `🔄 Restart`, and `📋 Logs` for every service within a trace.
- **Trace-Wide & Component Shortcuts**: Jump right into code with dedicated `💻 VS Code`, `📟 Terminal`, and `📁 File Manager` shortcuts for the overall stack as well as each member component.
- **Smart "Open All URLs"**: DevDeck auto-detects ports and live URLs for all services in the stack, letting you launch full-stack applications in your browser in one tap.

### 📦 Deterministic Manual Project Control
- **100% User-Controlled**: Zero unwanted automatic filesystem background scanning—add, configure, edit, and organize only the projects you choose.
- **Custom Commands & Paths**: Configure arbitrary commands (e.g., `npm run dev`, `gradle bootRun`, `python app.py`, `docker compose up`) with tailored root paths.
- **Port Management & Quick Changing**: Click any port badge to instantly edit assigned ports with automatic `PORT` environment routing and conflict resolution.

### 📋 Real-Time ANSI Live Console Drawer
- **Non-Blocking Streaming**: Asynchronous stdout/stderr capture with zero UI lag.
- **Full ANSI Color Formatting**: Preserves terminal output styling, colors, and banners from modern toolchains (Vite, Next.js, Spring Boot, FastAPI, etc.).
- **Console Utilities**: Instant log filtering/search, toggleable autoscroll, one-click copy, and full-screen maximization (`Ctrl + Shift + L`).

### 🎨 Dual Theme: Neo-Brutalist Figma & Modern Dark
- **Figma Neo-Brutalist Theme**: High-contrast, clean lines, vibrant amber/yellow canvas, bold typography, and tactile pill buttons.
- **Modern Slate Dark Theme**: Deep slate-blue/charcoal palette optimized for low-light coding sessions.
- **High-Contrast Context Menus**: Crisp white text on dark menus with vibrant yellow highlights for seamless readability.

### 📊 Live Resource Monitoring & Safety
- **Per-Project Telemetry**: Real-time CPU % and memory (RAM) usage tracking for active processes.
- **Clean Process Termination**: Recursive process tree teardown via `psutil`, ensuring lingering child processes and ports are completely freed.
- **System Tray Integration**: Dock DevDeck neatly into your system tray with quick status counts and a global "Stop All Running" fail-safe.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + F` | Focus project search bar |
| `Ctrl + L` | Toggle Live Console drawer |
| `Ctrl + Shift + L` | Toggle Fullscreen console mode |
| `Escape` | Close console drawer / dialogs |

---

## 🚀 Getting Started

### Prerequisites

- **Linux** (Tested on Ubuntu, Debian, Arch Linux, XFCE, GNOME, KDE)
- **Python 3.10+**
- **PyQt6** and **psutil**

```bash
# Clone the repository
git clone https://github.com/nagachaitanyaappana/DevDeck.git
cd DevDeck

# Install Python dependencies
pip install PyQt6 psutil
```

### Running DevDeck

```bash
# Direct Python execution
python3 main.py

# Or if installed to PATH / Desktop entry:
devdeck
```

---

## 📁 Project Structure

```
DevDeck/
├── main.py                     # Application entry point
├── core/
│   ├── config_manager.py       # JSON configuration persistence (~/.config/devdeck/)
│   ├── process_manager.py      # Async process lifecycle & telemetry (psutil + QProcess)
│   └── actions.py              # System actions (VS Code, terminal, browser, ports)
├── ui/
│   ├── main_window.py          # Primary layout, header, search & card orchestration
│   ├── theme.py                # Figma Neo-Brutalist & Dark QSS stylesheets
│   └── components/
│       ├── project_card.py     # Individual project card widget
│       ├── stack_card.py       # Full-width Multi-Project Trace card widget
│       ├── project_dialog.py   # Add / Edit project modal
│       ├── stack_dialog.py     # Multi-project stack builder modal
│       └── log_viewer.py       # Real-time ANSI log console drawer
└── assets/
    └── icon.png                # Application icon
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

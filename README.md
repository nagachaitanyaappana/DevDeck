# ⚡ DevDeck — Project Control Center

**DevDeck** is a fast, native Linux desktop application built with Python and PyQt6 designed to streamline managing, starting, stopping, and accessing your local developer projects without opening multiple terminals or remembering commands.

---

## 🌟 Key Features

- 🔍 **Intelligent Auto-Discovery**:
  - Automatically scans `~/Projects` and subprojects.
  - Recognizes **Vite**, **React**, **Next.js**, **Node/Express**, **Spring Boot (Gradle & Maven)**, **Python CLI/Web (FastAPI/Django/Flask)**, **Docker Compose**, and more.
- ⚡ **One-Click Start & Stop**:
  - Run or terminate services with a single click.
  - Recursively terminates child processes (`psutil` tree management) so ports never stay locked.
- 🌐 **Auto Port & URL Detection**:
  - Automatically captures URLs (e.g. `http://localhost:5173`, `http://localhost:8080`, `http://localhost:3000`) from stdout/stderr.
  - Glowing **Open URL** button launches the project directly in your default browser.
- 📋 **Integrated Live Console**:
  - Streaming stdout/stderr with real-time ANSI terminal colors.
  - Search/filter logs, toggle autoscroll, and one-click copy.
- 💻 **Developer Shortcuts**:
  - One-click **Open in VS Code** (`code <dir>`)
  - One-click **Open in Terminal** (`xfce4-terminal`)
  - One-click **Open in File Manager** (`thunar`)
- 📊 **Live Resource Monitoring**:
  - Real-time CPU % and RAM usage per running project.
- 📌 **Favorites & Categories**:
  - Star your active daily drivers to keep them pinned at the top.
  - Instant category filtering: `All`, `Running`, `Favorites`, `Node / Web`, `Java / Spring`, `Python`.
- 🗔 **System Tray**:
  - Minimizes neatly to the XFCE system tray with quick stop-all and status count.

---

## 🚀 How to Run

### From Desktop:
Double-click the **DevDeck** icon on your Desktop.

### From Command Line:
```bash
devdeck
# or
python3 ~/Projects/DevDeck/main.py
```

### Hotkeys:
- `Ctrl + F`: Jump to Search
- `Ctrl + R`: Rescan `~/Projects`
- `Ctrl + L`: Toggle Live Console Drawer

---

## 🛠 Tech Stack
- **GUI Framework**: PyQt6 (Native Qt widgets, High DPI support)
- **Process & Resource Engine**: `psutil` + `QProcess` asynchronous event loops
- **Theme**: Custom modern slate/dark developer styling with responsive layouts

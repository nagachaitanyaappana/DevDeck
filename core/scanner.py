"""
Project Scanner for DevDeck.
Auto-detects runnable projects, frameworks, ports, and default scripts.
"""

import os
import json
import re
from typing import List, Dict, Any
from .config_manager import generate_project_id

IGNORE_DIRS = {
    ".git", "node_modules", ".gradle", "build", "dist", ".idea", 
    ".vscode", ".kilo", "__pycache__", "venv", ".venv", "target", 
    ".next", ".cache", "bin", "obj", ".angular"
}

class ProjectScanner:
    def __init__(self, roots: List[str] = None, max_depth: int = 3):
        self.roots = roots or [os.path.expanduser("~/Projects")]
        self.max_depth = max_depth

    def scan_all(self) -> List[Dict[str, Any]]:
        """Scans all root directories and returns a list of detected projects."""
        discovered: Dict[str, Dict[str, Any]] = {}
        for root in self.roots:
            abs_root = os.path.abspath(os.path.expanduser(root))
            if os.path.exists(abs_root) and os.path.isdir(abs_root):
                self._scan_directory(abs_root, abs_root, 0, discovered)

        return list(discovered.values())

    def _scan_directory(self, current_dir: str, root_dir: str, depth: int, results: Dict[str, Dict[str, Any]]):
        if depth > self.max_depth:
            return

        try:
            entries = os.listdir(current_dir)
        except (PermissionError, FileNotFoundError):
            return

        # Check for runnable project definitions in current_dir
        detected_projects = self._inspect_directory(current_dir, root_dir, entries)
        for proj in detected_projects:
            pid = proj["id"]
            if pid not in results:
                results[pid] = proj

        # Recurse into subdirectories
        for entry in entries:
            if entry in IGNORE_DIRS or entry.startswith('.'):
                continue
            full_path = os.path.join(current_dir, entry)
            if os.path.isdir(full_path):
                self._scan_directory(full_path, root_dir, depth + 1, results)

    def _inspect_directory(self, path: str, root_dir: str, entries: List[str]) -> List[Dict[str, Any]]:
        projects = []
        rel_to_root = os.path.relpath(path, root_dir)
        display_name = os.path.basename(path) if rel_to_root != "." else os.path.basename(root_dir)
        
        # Better name for nested projects
        if rel_to_root != ".":
            display_name = rel_to_root.replace("/", " ➔ ")

        # 1. Check Node / Package.json
        if "package.json" in entries:
            pkg_path = os.path.join(path, "package.json")
            try:
                with open(pkg_path, "r", encoding="utf-8") as f:
                    pkg_data = json.load(f)
                
                scripts = pkg_data.get("scripts", {})
                dependencies = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                
                # Determine package manager
                pm = "npm"
                if "pnpm-lock.yaml" in entries:
                    pm = "pnpm"
                elif "yarn.lock" in entries:
                    pm = "yarn"
                elif "bun.lockb" in entries:
                    pm = "bun"

                # Determine tech stack & default command
                cmd = None
                port = None
                stack = "Node.js"
                
                if "vite" in dependencies:
                    stack = "Vite / React" if "react" in dependencies else "Vite"
                    port = 5173
                elif "next" in dependencies:
                    stack = "Next.js"
                    port = 3000
                elif "@angular/core" in dependencies:
                    stack = "Angular"
                    port = 4200
                elif "express" in dependencies or "@nestjs/core" in dependencies:
                    stack = "NestJS" if "@nestjs/core" in dependencies else "Express"
                    port = 3000

                # Select best script
                for s in ["dev", "start", "serve", "preview"]:
                    if s in scripts:
                        cmd = f"{pm} run {s}" if pm != "yarn" or s not in ["start", "test"] else f"{pm} {s}"
                        break
                
                if not cmd and scripts:
                    first_script = list(scripts.keys())[0]
                    cmd = f"{pm} run {first_script}"
                elif not cmd:
                    if "main" in pkg_data:
                        cmd = f"node {pkg_data['main']}"
                    else:
                        cmd = f"{pm} start"

                url = f"http://localhost:{port}" if port else ""
                proj_name = pkg_data.get("name") or display_name

                projects.append({
                    "id": generate_project_id(path, proj_name),
                    "name": proj_name,
                    "display_name": display_name,
                    "path": path,
                    "type": "node",
                    "stack": stack,
                    "command": cmd,
                    "port": port,
                    "url": url,
                    "auto_detect_url": True,
                    "favorite": False,
                    "category": "Frontend" if port in [5173, 3000, 4200] else "Fullstack",
                })
            except Exception as e:
                print(f"[Scanner] Error parsing {pkg_path}: {e}")

        # 2. Check Gradle
        has_gradle = "build.gradle" in entries or "build.gradle.kts" in entries
        if has_gradle:
            gradle_cmd = "./gradlew" if "./gradlew" in entries or "gradlew" in entries else "gradle"
            cmd = f"{gradle_cmd} bootRun"
            # Read build.gradle to see if spring boot or standard application
            is_spring = False
            for gf in ["build.gradle", "build.gradle.kts"]:
                if gf in entries:
                    try:
                        with open(os.path.join(path, gf), "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            if "spring" in content.lower():
                                is_spring = True
                                break
                    except Exception:
                        pass
            if not is_spring:
                cmd = f"{gradle_cmd} run"

            port = 8080 if is_spring else None
            projects.append({
                "id": generate_project_id(path, f"{display_name}-gradle"),
                "name": display_name,
                "display_name": display_name,
                "path": path,
                "type": "gradle",
                "stack": "Spring Boot (Gradle)" if is_spring else "Gradle",
                "command": cmd,
                "port": port,
                "url": f"http://localhost:{port}" if port else "",
                "auto_detect_url": True,
                "favorite": False,
                "category": "Backend",
            })

        # 3. Check Maven
        if "pom.xml" in entries:
            mvn_cmd = "./mvnw" if "mvnw" in entries else "mvn"
            cmd = f"{mvn_cmd} spring-boot:run"
            projects.append({
                "id": generate_project_id(path, f"{display_name}-maven"),
                "name": display_name,
                "display_name": display_name,
                "path": path,
                "type": "maven",
                "stack": "Spring Boot (Maven)",
                "command": cmd,
                "port": 8080,
                "url": "http://localhost:8080",
                "auto_detect_url": True,
                "favorite": False,
                "category": "Backend",
            })

        # 4. Check Python
        py_scripts = [f for f in entries if f in ["main.py", "app.py", "cli.py", "manage.py", "server.py"]]
        if py_scripts and not projects:  # Only if not already identified as a higher-level Node/Java project
            py_bin = "python3"
            if ".venv" in entries and os.path.exists(os.path.join(path, ".venv", "bin", "python3")):
                py_bin = "./.venv/bin/python3"
            elif "venv" in entries and os.path.exists(os.path.join(path, "venv", "bin", "python3")):
                py_bin = "./venv/bin/python3"

            cmd = f"{py_bin} main.py"
            stack = "Python"
            port = None

            if "manage.py" in py_scripts:
                cmd = f"{py_bin} manage.py runserver"
                stack = "Django"
                port = 8000
            elif "app.py" in py_scripts:
                cmd = f"{py_bin} app.py"
                stack = "Flask / FastAPI"
                port = 5000
            elif "main.py" in py_scripts:
                cmd = f"{py_bin} main.py"
                stack = "Python App"
            elif "cli.py" in py_scripts:
                cmd = f"{py_bin} cli.py"
                stack = "Python CLI"

            projects.append({
                "id": generate_project_id(path, display_name),
                "name": display_name,
                "display_name": display_name,
                "path": path,
                "type": "python",
                "stack": stack,
                "command": cmd,
                "port": port,
                "url": f"http://localhost:{port}" if port else "",
                "auto_detect_url": True,
                "favorite": False,
                "category": "Backend" if port else "Tools",
            })

        # 5. Check Docker Compose
        if "docker-compose.yml" in entries or "docker-compose.yaml" in entries or "compose.yaml" in entries:
            # Add docker compose as a dedicated service runner if appropriate
            projects.append({
                "id": generate_project_id(path, f"{display_name}-docker"),
                "name": f"{display_name} (Docker)",
                "display_name": f"{display_name} (Docker)",
                "path": path,
                "type": "docker",
                "stack": "Docker Compose",
                "command": "docker compose up",
                "port": None,
                "url": "",
                "auto_detect_url": True,
                "favorite": False,
                "category": "Services",
            })

        return projects

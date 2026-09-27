"""
DevDeck icon set.

One consistent, monochrome set instead of a mix of colour emoji and symbols.
Emoji rendered inconsistently across platforms and read as "prototype"; these
are drawn in the widget's own text colour, so they inherit the active theme
and stay legible in both light and dark.

The port control is deliberately plain — a port is a number, not a concept,
so it gets no pictogram at all.
"""

# ── Tech marks: single glyph per ecosystem, used in cards and nav ───────────
STACK_GLYPH = {
    "vite / react": "▲",
    "vite":         "▲",
    "next.js":      "▲",
    "react":        "⚛",
    "node.js":      "◈",
    "node":         "◈",
    "express":      "◈",
    "javascript":   "◈",
    "typescript":   "◈",
    "spring boot (gradle)": "J",
    "spring boot (maven)":  "J",
    "spring":       "J",
    "gradle":       "J",
    "maven":        "J",
    "java":         "J",
    "kotlin":       "K",
    "python app":   "P",
    "python cli":   "P",
    "python":       "P",
    "django":       "D",
    "flask / fastapi": "F",
    "fastapi":      "F",
    "flask":        "F",
    "docker compose": "D",
    "docker":       "D",
}
DEFAULT_GLYPH = "•"


def glyph_for(stack: str) -> str:
    """Return the tech mark for a stack name, case-insensitively."""
    return STACK_GLYPH.get((stack or "").strip().lower(), DEFAULT_GLYPH)


# ── Action glyphs ───────────────────────────────────────────────────────────
ICO_START = "▶"
ICO_STOP = "■"
ICO_RESTART = "↻"
ICO_BROWSER = "○"          # hollow circle = "go to site"
ICO_LOGS = "≡"
ICO_CODE = "⌘"            # generic "editor"
ICO_TERMINAL = ">_"
ICO_FOLDER = "▤"
ICO_SETTINGS = "⚙"
ICO_CLOSE = "✕"
ICO_PORT = ":#d"           # the port number; the '#' is the only glyph
ICO_MORE = "⋯"
ICO_FAV_ON = "★"
ICO_FAV_OFF = "☆"
ICO_STACK = "▦"           # stacked layers = a multi-project stack

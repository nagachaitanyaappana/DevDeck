"""
Single source of truth for the DevDeck version.

Previously the version string lived inside a QLabel in main_window.py, which
meant it could not be read by the build scripts, the changelog, or any
packaging metadata. Keep it here and import it wherever it is needed.
"""

__version__ = "1.1.0"

"""Application entry point for PSPlot."""

import logging
import sys
from typing import NoReturn

# Silence matplotlib debug spam BEFORE any matplotlib imports
logging.basicConfig(level=logging.INFO)
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)

from PyQt5.QtWidgets import QApplication

from psplot.core.config import APP_NAME, setup_logging
from psplot.gui.main_window import MainWindow


def main() -> NoReturn:
    """Main application entry point."""
    setup_logging()
    log = logging.getLogger(__name__)
    log.info(f"Starting {APP_NAME}")
    
    app = QApplication(sys.argv)
    
    # Try to set the process name for macOS Dock/Task Manager
    if sys.platform == 'darwin':
        try:
            import ctypes
            libc = ctypes.CDLL(None)
            libc.setprogname(b"PSPlot")
        except Exception:
            pass

    # Set application identity
    app.setApplicationName("PSPlot")
    app.setApplicationDisplayName("PSPlot")
    app.setOrganizationName("UGM")
    
     # Set global application icon
    import os
    from PyQt5.QtGui import QIcon
    
     # Resolve icon path for cross-platform support (macOS, Windows, Linux)
    if hasattr(sys, '_MEIPASS'):
         # PyInstaller bundled mode
        icon_path = os.path.join(sys._MEIPASS, "PSPlot_icon.png")
    else:
         # Always use importlib.resources for package-installed mode; fallback for dev
        try:
            import importlib.resources
            res = importlib.resources.files("psplot").joinpath("assets", "PSPlot_icon.png")
            icon_path = str(res)
        except Exception:
             # Dev fallback: look relative to this file
            icon_path = os.path.join(os.path.dirname(__file__), "psplot", "assets", "PSPlot_icon.png")
    
     # For Windows: importlib.resources may return a Traversable path that QIcon can't read directly
     # If file doesn't exist as-is, extract to a temp location
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        try:
             # Try reading via resources API (handles zip/pyz bundles)
            import importlib.resources
            res = importlib.resources.files("psplot").joinpath("assets", "PSPlot_icon.png")
            with res.open("rb") as f:
                icon_data = f.read()
            from PyQt5.QtGui import QPixmap
            pixmap = QPixmap()
            pixmap.loadFromData(icon_data, format="PNG")
            if pixmap.width() > 0:
                app.setWindowIcon(QIcon(pixmap))
        except Exception:
            pass  # Run without icon if loading fails
    
    window = MainWindow()
    window.show()
    
    log.info(f"{APP_NAME} started successfully")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

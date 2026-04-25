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

from core.config import APP_NAME, setup_logging
from gui.main_window import MainWindow


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
    if hasattr(sys, '_MEIPASS'):
        icon_path = os.path.join(sys._MEIPASS, "PSPlot_icon.png")
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "PSPlot_icon.png")
        
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    window = MainWindow()
    window.show()
    
    log.info(f"{APP_NAME} started successfully")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

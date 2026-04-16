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

from config import APP_NAME, setup_logging
from main_window import MainWindow


def main() -> NoReturn:
    """Main application entry point."""
    setup_logging()
    log = logging.getLogger(__name__)
    log.info(f"Starting {APP_NAME}")
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    log.info(f"{APP_NAME} started successfully")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

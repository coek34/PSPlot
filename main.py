"""Application entry point for PSPlot."""

import sys
import logging
from typing import NoReturn

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

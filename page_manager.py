# page_manager.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QDialog, QPushButton, QScrollArea,
                             QMessageBox, QInputDialog)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from page_widget import PageWidget
from settings import PageState
from theme import get_theme


class RenameDialog(QDialog):
    """Custom themed dialog for renaming pages."""

    def __init__(self, parent, current_name):
        super().__init__(parent)
        self.setWindowTitle("Rename Page")
        self.setModal(True)
        self.setFixedSize(350, 140)
        self.current_name = current_name
        self.result_text = ""

        self._build_ui()
        self._apply_theme()
        # Focus the QLineEdit
        self.line_edit.setFocus()
        self.line_edit.selectAll()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel("Enter new page name:")
        layout.addWidget(lbl)

        self.line_edit = QLineEdit(self)
        self.line_edit.setText(self.current_name)
        layout.addWidget(self.line_edit)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.setObjectName("ok_btn")
        self.ok_btn.setMinimumHeight(35)
        self.ok_btn.clicked.connect(self._on_ok)

        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # Support Enter/Return key
        self.line_edit.returnPressed.connect(self._on_ok)

    def _on_ok(self):
        text = self.line_edit.text().strip()
        if text:
            self.result_text = text
            self.accept()
        else:
            self.line_edit.setStyleSheet(
                "QLineEdit { border: 2px solid #f44336; "
                "border-radius: 4px; background-color: #ffe6e6; }}"
            )

    def _apply_theme(self):
        theme = get_theme()
        c = theme.colors
        hover_bg = "#555" if theme.is_dark else "#e0e0e0"
        sheet = f"""
            QDialog, QWidget {{
                background-color: {c.base};
                color: {c.text};
                font-size: 13px;
            }}
            QLabel {{
                color: {c.text};
                background: transparent;
            }}
            QLineEdit {{
                background-color: {c.alt};
                color: {c.text};
                border: 1px solid {c.border};
                border-radius: 4px;
                padding: 8px;
            }}
            QPushButton#ok_btn {{
                background-color: {c.success};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton#ok_btn:hover {{
                background-color: {theme._darken(c.success)};
            }}
            QPushButton#cancel_btn {{
                background-color: {c.alt};
                color: {c.text};
                border: 1px solid {c.border};
                border-radius: 4px;
            }}
            QPushButton#cancel_btn:hover {{
                background-color: {hover_bg};
            }}
        """
        self.setStyleSheet(sheet)


class PageManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.pages = []
        self.current_page_index = 0
    
    def get_all_pages_state(self):
        """Get state for all pages for persistence"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Getting state for {len(self.pages)} pages...")
        
        states = []
        for idx, page in enumerate(self.pages):
            try:
                state = page.get_state()
                states.append(state)
                logger.info(f"  Got state for page {idx}: {state.name}")
            except Exception as e:
                logger.error(f"  ERROR getting state for page {idx}: {e}", exc_info=True)
        
        logger.info(f"Total {len(states)} page states collected")
        return states
    
    def add_new_page(self, width=8.27, height=11.69):
        """Add a new page to the tab widget"""
        page_index = len(self.pages)
        page_widget = PageWidget(page_index, width, height)
        
        # Give page_widget and its canvas a reference to main_window
        page_widget.main_window = self.main_window
        if page_widget.plot_canvas:
            page_widget.plot_canvas.main_window = self.main_window
        
        self.pages.append(page_widget)

        # Add to tab widget
        tab_name = f"Page {page_index + 1}"
        self.main_window.tab_widget.addTab(page_widget, tab_name)
        self.main_window.tab_widget.setCurrentIndex(page_index)
        
        # Update current page index
        self.current_page_index = page_index
        
        # Update status bar
        self.main_window.update_status_bar()
        
        return page_widget
    
    def close_page(self, index):
        """Close a page"""
        if len(self.pages) <= 1:
            return  # Don't close the last page
            
        # Remove page
        self.pages.pop(index)
        self.main_window.tab_widget.removeTab(index)
        
        # Update page indices
        for i, page in enumerate(self.pages):
            page.page_index = i
            self.main_window.tab_widget.setTabText(i, f"Page {i + 1}")
        
        # Update current page index
        if index < len(self.pages):
            self.current_page_index = index
        else:
            self.current_page_index = max(0, len(self.pages) - 1)
            
        self.main_window.tab_widget.setCurrentIndex(self.current_page_index)
        self.main_window.update_status_bar()
    
    def get_current_page(self):
        """Get the currently active page"""
        if self.current_page_index < len(self.pages):
            return self.pages[self.current_page_index]
        return None
    
    def get_current_page_widget(self):
        """Get the currently active page widget"""
        return self.main_window.tab_widget.currentWidget()
    
    def update_status_bar(self):
        """Update the status bar with page information"""
        total_pages = len(self.pages)
        current_page = self.current_page_index + 1
        self.main_window.status_label.setText(f"Keys: 1-6 (plots) | A/D (pan) | R (res x) | Y (res y) | X (grid) | T (cursors) | E (export) | M (margins) | Page {current_page}/{total_pages}")

    def on_page_changed(self, index):
        """Handle page change event"""
        self.current_page_index = index
        self.main_window.update_status_bar()
    
    def rename_page(self, index):
        """Rename a page using a themed custom dialog."""
        if index < 0 or index >= len(self.pages):
            return

        page = self.pages[index]
        old_name = page.page_name
        dialog = RenameDialog(self.main_window, old_name)
        if dialog.exec():
            new_name = dialog.result_text
            page.page_name = new_name
            self.main_window.tab_widget.setTabText(index, new_name)

# page_manager.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
from page_widget import PageWidget
from settings import PageState

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
        
        # Give page_widget a reference to main_window
        page_widget.main_window = self.main_window
        
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
        self.main_window.status_label.setText(f"Keys: 1-6 (plots) | A/D (pan) | R (reset x) | Y (reset y) | X (grid) | E (export) | M (margins) | Double-click tabs to rename pages | Page {current_page}/{total_pages}")
    
    def on_page_changed(self, index):
        """Handle page change event"""
        self.current_page_index = index
        self.main_window.update_status_bar()
    
    def rename_page(self, index):
        """Rename a page"""
        if index < 0 or index >= len(self.pages):
            return
            
        page = self.pages[index]
        old_name = page.page_name
        new_name, ok = QInputDialog.getText(self.main_window, "Rename Page", "Enter new page name:", text=old_name)
        
        if ok and new_name:
            page.page_name = new_name
            self.main_window.tab_widget.setTabText(index, new_name)

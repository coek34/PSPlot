import sys, os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QMenuBar, QMenu, QAction, QFileDialog, QDialog, QFormLayout, 
                            QLineEdit, QPushButton, QComboBox, QSpinBox, QMessageBox, 
                            QDoubleSpinBox, QTabWidget, QTabBar, QToolBar, QToolButton, 
                            QInputDialog, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal

# Import from separate modules
from canvas_size_dialog import CanvasSizeDialog
from margin_dialog import MarginDialog
from page_widget import PageWidget
from plot_canvas import InteractivePlotCanvas
from data_import import DataImportDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PSPlotter - Power System Results Plotter")
        self.setGeometry(100, 100, 1200, 900)
        
        # Store all pages
        self.pages = []
        self.current_page_index = 0
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget for pages
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_page)
        self.tab_widget.currentChanged.connect(self.on_page_changed)
        # Connect tab bar double-click to rename function
        self.tab_widget.tabBar().tabBarDoubleClicked.connect(self.rename_page)
        main_layout.addWidget(self.tab_widget)
        
        # Status bar for instructions
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Keys: 1-6 (plots) | A/D (pan) | R (reset x) | Y (reset y) | X (grid) | E (export) | M (margins) | Double-click tabs to rename pages")
        self.status_label.setStyleSheet("QLabel { background-color : #e0e0e0; padding : 5px; }")
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)
        
        # Plot count label
        self.plot_count_label = QLabel("Plots: 1")
        self.plot_count_label.setStyleSheet("QLabel { font-weight: bold; padding: 5px; }")
        main_layout.addWidget(self.plot_count_label)
        
        # Add initial page
        self.add_new_page()
        
        # Make sure window can receive focus
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
        # Add a flag to track if we're in data import mode
        self.data_import_mode = False
        self.imported_data = []
    
    def create_menu_bar(self):
        """Create menu bar with action items"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_plot_action = QAction('New Plot (N)', self)
        new_plot_action.setShortcut('N')
        new_plot_action.triggered.connect(self.new_canvas)
        file_menu.addAction(new_plot_action)
        
        # Add data import action
        import_data_action = QAction('Import Data (C)', self)
        import_data_action.setShortcut('C')
        import_data_action.triggered.connect(self.import_pscad_data)
        file_menu.addAction(import_data_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('Export All Pages (E)', self)
        export_action.setShortcut('E')
        export_action.triggered.connect(self.on_export_clicked)
        file_menu.addAction(export_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        reset_x_action = QAction('Reset X-Zoom (R)', self)
        reset_x_action.setShortcut('R')
        reset_x_action.triggered.connect(self.on_reset_x_clicked)
        view_menu.addAction(reset_x_action)
        
        reset_y_action = QAction('Reset Y-Zoom (Y)', self)
        reset_y_action.setShortcut('Y')
        reset_y_action.triggered.connect(self.on_reset_y_clicked)
        view_menu.addAction(reset_y_action)
        
        round_x_action = QAction('Round X to Grid (X)', self)
        round_x_action.setShortcut('X')
        round_x_action.triggered.connect(self.on_round_x_clicked)
        view_menu.addAction(round_x_action)
        
        view_menu.addSeparator()
        
        # Add margin adjustment
        margin_action = QAction('Adjust Margins (M)', self)
        margin_action.setShortcut('M')
        margin_action.triggered.connect(self.adjust_margins)
        view_menu.addAction(margin_action)
        
        # In create_menu_bar(), add:
        reset_margins_action = QAction('Reset Margins to Defaults', self)
        reset_margins_action.triggered.connect(self.reset_current_margins)
        view_menu.addAction(reset_margins_action)
    
    def import_pscad_data(self):
        """Import PSCAD data using the data import dialog"""
        dialog = DataImportDialog(self, existing_data=self.imported_data)
        if dialog.exec_() == QDialog.Accepted:
            # Get the imported data
            self.imported_data = dialog.get_imported_data()
            # No popup message - just update the data silently

    
    def add_new_page(self, width=8.27, height=11.69):
        """Add a new page to the tab widget"""
        page_index = len(self.pages)
        page_widget = PageWidget(page_index, width, height)
        self.pages.append(page_widget)
        
        # Add to tab widget
        tab_name = f"Page {page_index + 1}"
        self.tab_widget.addTab(page_widget, tab_name)
        self.tab_widget.setCurrentIndex(page_index)
        
        # Update current page index
        self.current_page_index = page_index
        
        # Update status bar
        self.update_status_bar()
        
        return page_widget
    
    def close_page(self, index):
        """Close a page"""
        if len(self.pages) <= 1:
            return  # Don't close the last page
            
        # Remove page
        self.pages.pop(index)
        self.tab_widget.removeTab(index)
        
        # Update page indices
        for i, page in enumerate(self.pages):
            page.page_index = i
            self.tab_widget.setTabText(i, f"Page {i + 1}")
        
        # Update current page index
        if index < len(self.pages):
            self.current_page_index = index
        else:
            self.current_page_index = max(0, len(self.pages) - 1)
            
        self.tab_widget.setCurrentIndex(self.current_page_index)
        self.update_status_bar()
    
    def get_current_page(self):
        """Get the currently active page"""
        if self.current_page_index < len(self.pages):
            return self.pages[self.current_page_index]
        return None
    
    def get_current_page_widget(self):
        """Get the currently active page widget"""
        return self.tab_widget.currentWidget()
    
    def update_status_bar(self):
        """Update the status bar with page information"""
        total_pages = len(self.pages)
        current_page = self.current_page_index + 1
        self.status_label.setText(f"Keys: 1-6 (plots) | A/D (pan) | R (reset x) | Y (reset y) | X (grid) | E (export) | M (margins) | Double-click tabs to rename pages | Page {current_page}/{total_pages}")
    
    def on_page_changed(self, index):
        """Handle page change event"""
        self.current_page_index = index
        self.update_status_bar()
    
    def rename_page(self, index):
        """Rename a page"""
        if index < 0 or index >= len(self.pages):
            return
            
        page = self.pages[index]
        old_name = page.page_name
        new_name, ok = QInputDialog.getText(self, "Rename Page", "Enter new page name:", text=old_name)
        
        if ok and new_name:
            page.page_name = new_name
            self.tab_widget.setTabText(index, new_name)
    
    def new_canvas(self):
        """Create a new canvas with selected size"""
        # Get current page dimensions
        current_page = self.get_current_page()
        default_width = None
        default_height = None
        
        if current_page:
            # Convert inches back to mm for display
            default_width = round(current_page.width * 25.4)
            default_height = round(current_page.height * 25.4)
        
        dialog = CanvasSizeDialog(self, default_width, default_height)
        if dialog.exec_() == QDialog.Accepted:
            width, height, is_predefined = dialog.get_canvas_size()
            
            # Create new page with the selected size
            self.add_new_page(width, height)
    
    def get_current_margins(self):
        """Get current subplot margins from the figure"""
        current_page = self.get_current_page()
        if current_page:
            return current_page.get_current_margins()
        return {'left': 0.125, 'bottom': 0.1, 'right': 0.9, 'top': 0.9, 'wspace': 0.5, 'hspace': 0.5}
    
    def adjust_margins(self):
        """Adjust plot margins using percentage values"""
        current_page = self.get_current_page()
        if not current_page:
            return
            
        # Get current margins
        current_margins = current_page.get_current_margins()
        
        # Create margin dialog with current values
        dialog = MarginDialog(self, current_margins)
        if dialog.exec_() == QDialog.Accepted:
            margins = dialog.get_margins()
            
            # Apply margins to current page
            current_page.adjust_margins(margins)
            
    def reset_current_margins(self):
        """Reset margins to default values"""
        current_page = self.get_current_page()
        if current_page and current_page.plot_canvas:
            current_page.plot_canvas.reset_default_margins()
    
    def keyPressEvent(self, event):
        # Handle key press events directly on the main window
        key = event.key()
        
        # Number keys 1-6 for subplot count
        if Qt.Key_1 <= key <= Qt.Key_6:
            current_page = self.get_current_page()
            if current_page:
                subplot_count = key - Qt.Key_1 + 1
                current_page.update_plots(subplot_count)
                self.plot_count_label.setText(f"Plots: {subplot_count}")
            event.accept()
            return
            
        # Pan left with A key
        elif key == Qt.Key_A:
            current_page = self.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.pan_horizontal(-1)  # Pan left
            event.accept()
            return
            
        # Pan right with D key
        elif key == Qt.Key_D:
            current_page = self.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.pan_horizontal(1)  # Pan right
            event.accept()
            return
            
        # Reset x-zoom with R key
        elif key == Qt.Key_R:
            current_page = self.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.reset_x_zoom()
            event.accept()
            return
            
        # Reset y-zoom with Y key
        elif key == Qt.Key_Y:
            current_page = self.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.reset_y_zoom()
            event.accept()
            return
            
        # Round x to grid with X key
        elif key == Qt.Key_X:
            current_page = self.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.round_x_to_grid()
            event.accept()
            return
            
        # Export with E key
        elif key == Qt.Key_E:
            self.on_export_clicked()
            event.accept()
            return

        # Import data with C key
        elif key == Qt.Key_C:
            self.import_pscad_data()
            event.accept()
            return
            
        # Adjust margins with M key
        elif key == Qt.Key_M:
            self.adjust_margins()
            event.accept()
            return
            
        # Pass other keys to parent class
        super().keyPressEvent(event)
    
    def on_reset_x_clicked(self):
        current_page = self.get_current_page()
        if current_page and current_page.plot_canvas:
            current_page.plot_canvas.reset_x_zoom()
    
    def on_reset_y_clicked(self):
        current_page = self.get_current_page()
        if current_page and current_page.plot_canvas:
            current_page.plot_canvas.reset_y_zoom()
    
    def on_round_x_clicked(self):
        current_page = self.get_current_page()
        if current_page and current_page.plot_canvas:
            current_page.plot_canvas.round_x_to_grid()
    
    def on_export_clicked(self):
        """Export all pages using standard save dialog"""
        if not self.pages:
            return
            
        # Get file path using standard save dialog with multiple format options
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, 
            "Save File", 
            "document_plot.png", 
            "PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Determine the format from the selected filter
        file_format = 'png'  # default
        if selected_filter == "PDF Files (*.pdf)":
            file_format = 'pdf'
        elif selected_filter == "PNG Files (*.png)":
            file_format = 'png'
        
        # Extract directory and base filename without extension
        import os
        directory = os.path.dirname(file_path)
        filename_without_ext = os.path.splitext(os.path.basename(file_path))[0]
        
        # Export each page
        for i, page in enumerate(self.pages):
            # Use page name directly in filename
            page_filename = f"{filename_without_ext}_{page.page_name.replace(' ', '_')}.{file_format}"
            # Sanitize filename to remove invalid characters
            import re
            page_filename = re.sub(r'[^\w\-_\.]', '_', page_filename)
            filepath = os.path.join(directory, page_filename)
            
            try:
                # Save the current page
                page.plot_canvas.fig.savefig(
                    filepath, 
                    dpi=100, 
                    bbox_inches=None,  # This preserves the full figure size
                    pad_inches=0, 
                    facecolor='white', 
                    format=file_format
                )
                print(f"Exported: {filepath}")
            except Exception as e:
                print(f"Error exporting {page_filename}: {e}")
        
        QMessageBox.information(self, "Export Complete", f"Exported {len(self.pages)} pages to {directory}")

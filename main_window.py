# main_window.py
import sys, os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QMenuBar, QMenu, QAction, QFileDialog, QDialog, QFormLayout, 
                            QLineEdit, QPushButton, QComboBox, QSpinBox, QMessageBox, 
                            QDoubleSpinBox, QTabWidget, QTabBar, QToolBar, QToolButton, 
                            QInputDialog, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal

# Import from separate modules
from margin_dialog import MarginDialog
from page_widget import PageWidget
from plot_canvas import InteractivePlotCanvas
from data_import import DataImportDialog
from canvas_size_dialog import CanvasSizeDialog

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
        self.channel_signals = {}  # Dictionary to store signals per channel
        
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
    
    # --- Page Management Methods ---
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
    
    # --- Canvas and Plot Methods ---
    def new_canvas(self):
        """Create a new canvas with selected size"""
        # Get the current page to copy its size
        current_page = self.get_current_page()
        if current_page:
            # Get current page size in mm
            current_width_mm, current_height_mm = current_page.plot_canvas.get_canvas_size_mm()
            
            # Show canvas size dialog
            dialog = CanvasSizeDialog(self, (current_width_mm, current_height_mm))
            if dialog.exec_() == QDialog.Accepted:
                # Get selected size in inches
                width_inch, height_inch = dialog.get_selected_size()
                # Create new page with selected size
                self.add_new_page(width_inch, height_inch)
        else:
            # If no current page, use default size
            dialog = CanvasSizeDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                width_inch, height_inch = dialog.get_selected_size()
                self.add_new_page(width_inch, height_inch)
    
    def resize_current_page(self):
        """Resize the current page while preserving signals and x-limits"""
        current_page = self.get_current_page()
        if not current_page:
            return
            
        # Get current page size in mm
        current_width_mm, current_height_mm = current_page.plot_canvas.get_canvas_size_mm()
        
        # Show canvas size dialog with current size as default
        dialog = CanvasSizeDialog(self, (current_width_mm, current_height_mm))
        if dialog.exec_() == QDialog.Accepted:
            # Get selected size in inches
            width_inch, height_inch = dialog.get_selected_size()
            
            # Store current x-limits if they exist
            current_xlim = None
            if current_page.plot_canvas.current_xlim:
                current_xlim = current_page.plot_canvas.current_xlim
            
            # Store current signals for each subplot
            signals_to_restore = []
            for i in range(len(current_page.plot_canvas.axes)):
                if i < len(current_page.subplot_signals):
                    signals_to_restore.append(current_page.subplot_signals[i])
                else:
                    signals_to_restore.append([])
            
            # Update the page with new size
            current_page.width = width_inch
            current_page.height = height_inch
            current_page.plot_canvas.fig.set_size_inches(width_inch, height_inch)
            
            # Update the page widget's scroll area
            current_page.plot_canvas.update_plots(current_page.plot_canvas.subplot_count)
            
            # Restore signals and x-limits
            if current_xlim:
                current_page.plot_canvas.set_x_limits(current_xlim[0], current_xlim[1])
            
            # Restore signals to subplots
            for i, signals in enumerate(signals_to_restore):
                if i < len(current_page.plot_canvas.axes) and signals:
                    current_page.plot_canvas.set_subplot_signals(i, signals)
            
            # Reset margins to tight layout
            current_page.plot_canvas.reset_default_margins()
            
            # Redraw the canvas
            current_page.plot_canvas.draw()
    
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
    
    # --- Data Import Methods ---
    def import_pscad_data(self):
        """Import PSCAD data using the data import dialog"""
        dialog = DataImportDialog(self, existing_data=self.imported_data)
        if dialog.exec_() == QDialog.Accepted:
            # Get the imported data
            self.imported_data = dialog.get_imported_data()
            
            # Update channel signals
            for data in self.imported_data:
                channel = data['channel']
                path = data['path']
                label = data['label']
                
                if channel not in self.channel_signals:
                    self.channel_signals[channel] = []
                
                # Load signal data from the file (assuming a simple format for now)
                with open(path, 'r') as file:
                    lines = file.readlines()
                    x_data = [float(line.split()[0]) for line in lines]
                    y_data = [float(line.split()[1]) for line in lines]
                
                # Store signal data
                self.channel_signals[channel].append({
                    'x': x_data,
                    'y': y_data,
                    'name': label,
                    'channel_name': channel,
                    'group_name': 'Imported'
                })
    
    # --- Keyboard Event Methods ---
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
                
                # Automatically round x to grid after changing subplot count
                # This preserves current x-limits but applies grid rounding
                if current_page.plot_canvas:
                    current_page.plot_canvas.round_x_to_grid()
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
            
        # New canvas with N key
        elif key == Qt.Key_N:
            self.new_canvas()
            event.accept()
            return
            
        # Resize current page with P key
        elif key == Qt.Key_P:
            self.resize_current_page()
            event.accept()
            return
            
        # Pass other keys to parent class
        super().keyPressEvent(event)
    
    # --- Action Methods ---
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
            except Exception as e:
                # Show error in a message box instead of print
                QMessageBox.warning(self, "Export Error", f"Failed to export {page_filename}: {e}")
        
        QMessageBox.information(self, "Export Complete", f"Exported {len(self.pages)} pages to {directory}")

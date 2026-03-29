# main_window.py
import sys, os
import re
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
from page_manager import PageManager
from canvas_manager import CanvasManager
from action_manager import ActionManager
from keyboard_manager import KeyboardManager
from data_manager import DataManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PSPlotter - Power System Results Plotter")
        self.setGeometry(100, 100, 1200, 900)
        
        # Initialize managers
        self.page_manager = PageManager(self)
        self.canvas_manager = CanvasManager(self)
        self.action_manager = ActionManager(self)
        self.keyboard_manager = KeyboardManager(self)
        self.data_manager = DataManager(self)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget for pages
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.page_manager.close_page)
        self.tab_widget.currentChanged.connect(self.page_manager.on_page_changed)
        # Connect tab bar double-click to rename function
        self.tab_widget.tabBar().tabBarDoubleClicked.connect(self.page_manager.rename_page)
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
        self.page_manager.add_new_page()
        
        # Make sure window can receive focus
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
        # Apply theme styling
        self.apply_theme_style()
        
    def apply_theme_style(self):
        """Apply theme-aware styling to the main window"""
        try:
            import darkdetect
            is_dark = darkdetect.isDark()
        except:
            # If darkdetect is not available, default to light mode
            is_dark = False
            
        base_color = "#2b2b2b" if is_dark else "#ffffff"
        text_color = "#ffffff" if is_dark else "#000000"
        alt_bg = "#3a3a3a" if is_dark else "#fafafa"
        sel_bg = "#0078D7"
        
        # Apply styling to main window
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {base_color};
                color: {text_color};
            }}
            QMenuBar {{
                background-color: {base_color};
                color: {text_color};
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 8px;
            }}
            QMenuBar::item:selected {{
                background: {"#555" if is_dark else "#ddd"};
            }}
            QMenuBar::item:pressed {{
                background: {"#666" if is_dark else "#bbb"};
            }}
            QMenu {{
                background-color: {base_color};
                color: {text_color};
                border: 1px solid {"#555" if is_dark else "#ccc"};
            }}
            QMenu::item {{
                padding: 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: {sel_bg};
                color: white;
            }}
            QTabWidget::pane {{
                border: 1px solid {"#444" if is_dark else "#ccc"};
                background-color: {base_color};
            }}
            QTabBar::tab {{
                background-color: {"#3a3a3a" if is_dark else "#f0f0f0"};
                color: {text_color};
                padding: 8px;
                border: 1px solid {"#444" if is_dark else "#ccc"};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: {base_color};
                border-bottom: 2px solid {sel_bg};
            }}
            QTabBar::tab:hover {{
                background-color: {"#555" if is_dark else "#e0e0e0"};
            }}
            QStatusBar {{
                background-color: {base_color};
                color: {text_color};
            }}
            QScrollArea {{
                background-color: {base_color};
                border: 1px solid {"#444" if is_dark else "#ccc"};
            }}
            QLabel {{
                color: {text_color};
            }}
        """)
        
        # Update status label styling based on theme
        if is_dark:
            self.status_label.setStyleSheet("QLabel { background-color : #3a3a3a; color: #ffffff; padding : 5px; }")
        else:
            self.status_label.setStyleSheet("QLabel { background-color : #e0e0e0; color: #000000; padding : 5px; }")
        
    def create_menu_bar(self):
        """Create menu bar with action items"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        new_plot_action = QAction('New Plot (N)', self)
        new_plot_action.setShortcut('N')
        new_plot_action.triggered.connect(self.canvas_manager.new_canvas)
        file_menu.addAction(new_plot_action)
        
        # Add data import action
        import_data_action = QAction('Import Data (C)', self)
        import_data_action.setShortcut('C')
        import_data_action.triggered.connect(self.data_manager.import_pscad_data)
        file_menu.addAction(import_data_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('Export All Pages (E)', self)
        export_action.setShortcut('E')
        export_action.triggered.connect(self.action_manager.on_export_clicked)
        file_menu.addAction(export_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        reset_x_action = QAction('Reset X-Zoom (R)', self)
        reset_x_action.setShortcut('R')
        reset_x_action.triggered.connect(self.action_manager.on_reset_x_clicked)
        view_menu.addAction(reset_x_action)
        
        reset_y_action = QAction('Reset Y-Zoom (Y)', self)
        reset_y_action.setShortcut('Y')
        reset_y_action.triggered.connect(self.action_manager.on_reset_y_clicked)
        view_menu.addAction(reset_y_action)
        
        round_x_action = QAction('Round X to Grid (X)', self)
        round_x_action.setShortcut('X')
        round_x_action.triggered.connect(self.action_manager.on_round_x_clicked)
        view_menu.addAction(round_x_action)
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        
        # Add margin adjustment
        margin_action = QAction('Adjust Margins (M)', self)
        margin_action.setShortcut('M')
        margin_action.triggered.connect(self.canvas_manager.adjust_margins)
        settings_menu.addAction(margin_action)
        
        # In create_menu_bar(), add:
        reset_margins_action = QAction('Reset Margins to Defaults', self)
        reset_margins_action.triggered.connect(self.canvas_manager.reset_current_margins)
        settings_menu.addAction(reset_margins_action)
    
    # Delegate methods to page_manager
    def add_new_page(self, width=8.27, height=11.69):
        return self.page_manager.add_new_page(width, height)
    
    def get_current_page(self):
        return self.page_manager.get_current_page()
    
    def get_current_page_widget(self):
        return self.page_manager.get_current_page_widget()
    
    def update_status_bar(self):
        self.page_manager.update_status_bar()
    
    # Delegate methods to canvas_manager
    def new_canvas(self):
        self.canvas_manager.new_canvas()
    
    def resize_current_page(self):
        self.canvas_manager.resize_current_page()
    
    def get_current_margins(self):
        return self.canvas_manager.get_current_margins()
    
    def adjust_margins(self):
        self.canvas_manager.adjust_margins()
    
    def reset_current_margins(self):
        self.canvas_manager.reset_current_margins()
    
    # Delegate methods to data_manager
    def import_pscad_data(self):
        self.data_manager.import_pscad_data()
    
    # Delegate methods to action_manager
    def on_reset_x_clicked(self):
        self.action_manager.on_reset_x_clicked()
    
    def on_reset_y_clicked(self):
        self.action_manager.on_reset_y_clicked()
    
    def on_round_x_clicked(self):
        self.action_manager.on_round_x_clicked()
    
    def on_export_clicked(self):
        self.action_manager.on_export_clicked()
    
    # Override keyPressEvent to use keyboard_manager
    def keyPressEvent(self, event):
        self.keyboard_manager.keyPressEvent(event)

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

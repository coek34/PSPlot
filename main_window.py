# main_window.py
import sys, os
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QMenuBar, QMenu, QAction, QFileDialog, QDialog, QFormLayout, 
                            QLineEdit, QPushButton, QComboBox, QSpinBox, QMessageBox, 
                            QDoubleSpinBox, QTabWidget, QTabBar, QToolBar, QToolButton, 
                            QInputDialog, QScrollArea, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import from separate modules
from config import WINDOW_TITLE, DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_POS
from config import SUBPLOT_CONFIG, get_status_text
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
from theme import get_theme
from settings import get_settings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        
        # Initialize settings
        self.settings = get_settings()
        
        # Apply window geometry from settings if available
        if self.settings.preferences.window_geometry:
            x, y, w, h = self.settings.preferences.window_geometry
            self.setGeometry(x, y, w, h)
        else:
            x, y = DEFAULT_WINDOW_POS
            width, height = DEFAULT_WINDOW_SIZE
            self.setGeometry(x, y, width, height)
        
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
        self.status_label = QLabel(get_status_text())
        status_layout.addWidget(self.status_label)
        main_layout.addLayout(status_layout)
        
        # Plot count label
        self.plot_count_label = QLabel("Plots: 1")
        self.plot_count_label.setStyleSheet("QLabel { font-weight: bold; padding: 5px; }")
        main_layout.addWidget(self.plot_count_label)
        
        # Restore or Add initial page
        if not self.restore_app_state():
            self.page_manager.add_new_page()
        
        # Make sure window can receive focus
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
        # Apply theme styling
        self.apply_theme_style()
        
        # Group name in legend flag
        self.group_name_in_legend = False

    def restore_app_state(self) -> bool:
        """Restore application state from settings."""
        logger = logging.getLogger(__name__)
        state = self.settings.state
        if not state.pages:
            logger.warning("No saved pages in settings.state, cannot restore")
            return False
            
        logger.info(f"=== RESTORING APP STATE ===")
        logger.info(f"Restoring state with {len(state.pages)} pages")
        logger.info(f"Imported files to restore: {state.imported_files}")
        
        # 1. Restore imported data
        if state.imported_files:
            logger.info(f"Loading {len(state.imported_files)} imported files...")
            self.data_manager.load_from_paths_info(state.imported_files)
            logger.info(f"Data manager now has {len(self.data_manager.channel_signals)} channels")
        else:
            logger.info("No imported files to restore")
        
        # 2. Restore pages
        while self.tab_widget.count() > 0:
            self.tab_widget.removeTab(0)
        self.page_manager.pages = []
        
        for page_idx, p_state in enumerate(state.pages):
            logger.info(f"Restoring page {page_idx}: '{p_state.name}' with {p_state.subplot_count} subplots")
            page = self.page_manager.add_new_page(width=p_state.width, height=p_state.height)
            page.page_name = p_state.name
            
            # Ensure page has reference to main_window
            page.main_window = self
            
            self.tab_widget.setTabText(page.page_index, p_state.name)
            
            # Restore margins
            if p_state.margins:
                page.adjust_margins(p_state.margins)
                logger.info(f"  Restored margins: {p_state.margins}")
            
            # Restore subplot count
            page.update_plots(p_state.subplot_count)
            
            # Restore signals (Rehydration)
            logger.info(f"  Restoring {len(p_state.subplots_signals)} subplots with signal refs...")
            for subplot_idx, sig_refs in enumerate(p_state.subplots_signals):
                logger.info(f"    Subplot {subplot_idx}: {len(sig_refs)} signal references")
                page_signals = []
                for ref_idx, ref in enumerate(sig_refs):
                    logger.debug(f"      Ref {ref_idx}: {ref}")
                    # Find the actual data in data_manager
                    rehydrated = self._find_signal_data(ref)
                    if rehydrated:
                        logger.info(f"      ✓ Rehydrated '{ref.get('name')}' from {ref.get('channel_name')}")
                        page_signals.append(rehydrated)
                    else:
                        logger.warning(f"      ✗ FAILED to rehydrate '{ref.get('name')}' - signal not found!")
                
                if page_signals:
                    logger.info(f"    Plotting {len(page_signals)} signals to subplot {subplot_idx}")
                    page.set_subplot_signals(subplot_idx, page_signals)
                else:
                    logger.warning(f"    No signals available to plot in subplot {subplot_idx}")
            
        # Restore current page
        self.tab_widget.setCurrentIndex(state.current_page_index)
        logger.info(f"=== RESTORE COMPLETE ===")
        return True

    def _find_signal_data(self, ref: dict):
        """Find raw signals data from metadata reference (Imported or Dummy)"""
        logger = logging.getLogger(__name__)
        name = ref.get('name')
        file_path = ref.get('file_path')
        channel_name = str(ref.get('channel_name'))
        group_name = ref.get('group_name')
        
        logger.debug(f"_find_signal_data: Looking for '{name}' in channel='{channel_name}', group='{group_name}', file='{file_path}'")
        
        # 1. Look through imported data in manager
        logger.debug(f"  Searching in imported data ({len(self.data_manager.channel_signals)} channels)...")
        for channel, signals in self.data_manager.channel_signals.items():
            if str(channel) == channel_name:
                for sig in signals:
                    if sig.get('name') == name and sig.get('file_path') == file_path:
                        logger.debug(f"  ✓ FOUND in imported data!")
                        return sig

        # 2. Look through dummy data in the first available canvas
        logger.debug(f"  Searching in dummy data...")
        page = self.get_current_page()
        if page and page.plot_canvas:
            for channel in page.plot_canvas.dummy_signals:
                if channel.get('name') == channel_name:
                    for group in channel.get('groups', []):
                        if group.get('name') == group_name:
                            for sig in group.get('signals', []):
                                if sig.get('name') == name:
                                    # Format as full signal dict for rehydration
                                    result = {
                                        **sig,
                                        'channel_name': channel_name,
                                        'group_name': group_name
                                    }
                                    logger.debug(f"  ✓ FOUND in dummy data!")
                                    return result
        
        logger.debug(f"  ✗ NOT FOUND anywhere")
        return None

    def closeEvent(self, event):
        """Save settings and state on window close."""
        import traceback
        logger = logging.getLogger(__name__)
        logger.info("=== CLOSING APPLICATION ===")
        
        try:
            # Save window geometry
            geom = self.geometry()
            self.settings.preferences.window_geometry = [geom.x(), geom.y(), geom.width(), geom.height()]
            logger.info(f"Saved window geometry: {[geom.x(), geom.y(), geom.width(), geom.height()]}")
            
            # Save imported files
            self.settings.state.imported_files = self.data_manager.get_imported_paths_info()
            logger.info(f"Saved {len(self.settings.state.imported_files)} imported files")
            
            # Save app state
            self.settings.state.current_page_index = self.tab_widget.currentIndex()
            logger.info(f"Current page index: {self.settings.state.current_page_index}")
            
            logger.info("Getting page states...")
            page_states = self.page_manager.get_all_pages_state()
            self.settings.state.pages = page_states
            logger.info(f"Got {len(page_states)} page states")
            
            # Save settings to file
            logger.info("Saving to file...")
            self.settings.save()
            logger.info("=== CLOSE COMPLETE ===")
            
        except Exception as e:
            logger.error(f"ERROR during close: {e}")
            logger.error(traceback.format_exc())
        
        event.accept()
        
    def apply_theme_style(self):
        """Apply theme-aware styling to the main window"""
        theme = get_theme()
        
        # Apply full application stylesheet
        self.setStyleSheet(theme.get_style_sheet())
        
        # Update status label styling based on theme
        self.status_label.setStyleSheet(theme.get_status_label_style())
        
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
        
        # Add group name in legend checkbox
        self.group_name_in_legend_action = QAction('Group name in legend', self)
        self.group_name_in_legend_action.setCheckable(True)
        self.group_name_in_legend_action.setChecked(False)
        self.group_name_in_legend_action.triggered.connect(self.toggle_group_name_in_legend)
        settings_menu.addAction(self.group_name_in_legend_action)
    
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
    
    def toggle_group_name_in_legend(self, checked):
        """Toggle group name in legend"""
        logger.debug(f"Toggle group name in legend: {checked}")
        self.group_name_in_legend = checked
        logger.debug(f"Updated group_name_in_legend flag to: {self.group_name_in_legend}")
        
        # Update all pages to reflect the new setting
        for page in self.page_manager.pages:
            if page.plot_canvas:
                logger.debug(f"Updating page {page.page_index} with new legend setting")
                # Get existing signals for each subplot
                signals_to_restore = []
                for i in range(len(page.plot_canvas.axes)):
                    existing_signals = page.plot_canvas.get_existing_signals_for_subplot(i)
                    signals_to_restore.append(existing_signals)
                
                # Replot all signals with new legend format
                for i, signals in enumerate(signals_to_restore):
                    if i < len(page.plot_canvas.axes) and signals:
                        logger.debug(f"Replotting signals for subplot {i}")
                        # Replot with new legend format
                        page.plot_canvas.set_subplot_signals(i, signals)
        
        logger.debug("Legend update complete")

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

# main_window.py
import sys
import os
import logging
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTabWidget, QAction, QMessageBox, QLabel, QSplitter,
                             QScrollArea, QFrame, QApplication)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QPoint, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices

from page_manager import PageManager
from canvas_manager import CanvasManager
from data_manager import DataManager
from action_manager import ActionManager
from keyboard_manager import KeyboardManager
from theme import get_theme
from settings import get_settings, PageState
import config


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Application wide logging is already setup in main.py
        logger = logging.getLogger(__name__)
        logger.info("Initializing PSPlot Plotter Application...")

        self.setWindowTitle("PSPlot: Professional Power System Output Plotter")

        # Set Window Icon
        if hasattr(sys, '_MEIPASS'):
            icon_path = os.path.join(sys._MEIPASS, "PSPlot_icon.png")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "PSPlot_icon.png")

        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            self.icon_path = icon_path
        else:
            self.icon_path = None

        # 1. Load Settings & Preferences
        self.settings = get_settings()
        if self.settings.preferences.window_geometry:
            g = self.settings.preferences.window_geometry
            self.setGeometry(g[0], g[1], g[2], g[3])
        else:
            self.resize(1200, 800)

        # 2. Managers
        self.data_manager = DataManager(self)
        self.page_manager = PageManager(self)
        self.canvas_manager = CanvasManager(self)
        self.action_manager = ActionManager(self)
        self.keyboard_manager = KeyboardManager(self)

        # 3. Main UI Layout
        self.setup_ui()

        # 4. Global Flags/Options for all pages
        self.group_name_in_legend = False
        self.channel_name_in_legend = False

        self.apply_theme_style()
        self.create_menu_bar()

        # 5. Restore State (if exists)
        self.restore_app_state()

        logger.info("Application initialized successfully.")

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Tab widget for multiple pages/canvases
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabBarDoubleClicked.connect(self._on_tab_double_clicked)
        self.tab_widget.tabCloseRequested.connect(self.page_manager.close_page)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.main_layout.addWidget(self.tab_widget)

        # Status Bar Replacement (Internal)
        self.status_frame = QFrame()
        self.status_frame.setFixedHeight(30)
        self.status_layout = QHBoxLayout(self.status_frame)
        self.status_layout.setContentsMargins(10, 0, 10, 0)

        self.status_help_label = QLabel("Ready")
        self.status_layout.addWidget(self.status_help_label)

        # Plot count label (required by KeyboardManager)
        self.plot_count_label = QLabel("Plots: 1")
        self.status_layout.addWidget(self.plot_count_label)

        self.status_layout.addStretch()

        # Cursor measurement info label (High contrast)
        self.measurement_label = QLabel("")
        self.measurement_label.setVisible(False)
        self.status_layout.addWidget(self.measurement_label)

        self.main_layout.addWidget(self.status_frame)

    def keyPressEvent(self, event):
        """Pass keyboard events to KeyboardManager"""
        self.keyboard_manager.keyPressEvent(event)

    # --- Proxy Methods for KeyboardManager ---
    def import_pscad_data(self):
        self.data_manager.import_pscad_data()

    def on_export_clicked(self):
        self.action_manager.on_export_clicked()

    def adjust_margins(self):
        self.canvas_manager.adjust_margins()

    def new_canvas(self):
        self.canvas_manager.new_canvas()

    def resize_current_page(self):
        self.canvas_manager.resize_current_page()
    # ----------------------------------------

    def on_tab_changed(self, index):
        """Update managers when current tab changes"""
        if index >= 0:
            current_page = self.tab_widget.widget(index)
            self.update_status_bar()

    def update_status_bar(self, message=None):
        if message:
            self.measurement_label.setText(message)
            self.measurement_label.setVisible(True)
        else:
            # Check the current page's cursor status
            page = self.get_current_page()
            if page and page.plot_canvas and getattr(page.plot_canvas, 'cursors_active', False):
                pass
            else:
                self.measurement_label.setText("")
                self.measurement_label.setVisible(False)

            if page:
                total_pages = self.tab_widget.count()
                current_idx = self.tab_widget.currentIndex() + 1
                help_text = "1-6: #Plots | C:Import Data | N:New page | E:Export | A/D:Pan | R/Y:Reset view | X:Horizontal limits | T:Cursor | M:Margins | P: Page size"
                self.status_help_label.setText(f"{help_text} | Page {current_idx}/{total_pages}")
                if page.plot_canvas:
                    self.plot_count_label.setText(f"Plots: {page.plot_canvas.subplot_count}")
                    is_active = getattr(page.plot_canvas, 'cursors_active', False)
                    self.measurement_label.setVisible(is_active and self.measurement_label.text() != "")

    def get_current_page(self):
        idx = self.tab_widget.currentIndex()
        if idx >= 0:
            return self.tab_widget.widget(idx)
        return None

    def restore_app_state(self):
        """Restore application state from settings."""
        logger = logging.getLogger(__name__)
        state = self.settings.state
        if not state.pages:
            logger.warning("No saved pages in settings.state, cannot restore")
            return False

        logger.info("=== RESTORING APP STATE ===")
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

            page.main_window = self

            self.tab_widget.setTabText(page.page_index, p_state.name)

            if p_state.margins:
                page.adjust_margins(p_state.margins)
                logger.info(f"  Restored margins: {p_state.margins}")

            if p_state.x_limits and len(p_state.x_limits) == 2:
                if page.plot_canvas:
                    page.plot_canvas.set_x_limits(p_state.x_limits[0], p_state.x_limits[1])
                    logger.info(f"  Restored x-limits: {p_state.x_limits}")

            if p_state.y_labels and page.plot_canvas:
                y_labels = {int(k): str(v) for k, v in p_state.y_labels.items()}
                page.plot_canvas.y_labels = y_labels
                logger.info(f"  Restored y-labels: {y_labels}")

            if p_state.y_lims and page.plot_canvas:
                y_lims = {int(k): tuple(v) for k, v in p_state.y_lims.items()}
                page.plot_canvas.current_ylim_dict = y_lims
                logger.info(f"  Restored y-limits: {y_lims}")
            else:
                logger.info("  No y-limits to restore (will auto-fit on data load)")

            page.update_plots(p_state.subplot_count)

            logger.info(f"  Restoring {len(p_state.subplots_signals)} subplots with signal refs...")
            for subplot_idx, sig_refs in enumerate(p_state.subplots_signals):
                logger.info(f"    Subplot {subplot_idx}: {len(sig_refs)} signal references")
                page_signals = []
                for ref_idx, ref in enumerate(sig_refs):
                    logger.debug(f"      Ref {ref_idx}: {ref}")
                    rehydrated = self._find_signal_data(ref)
                    if rehydrated:
                        logger.info(f"        Rehydrated '{ref.get('name')}' from {ref.get('channel_name')}")
                        rehydrated['scale'] = float(ref.get('scale', 1.0))
                        page_signals.append(rehydrated)
                    else:
                        logger.warning(f"        FAILED to rehydrate '{ref.get('name')}' - signal not found!")

                if page_signals:
                    logger.info(f"    Plotting {len(page_signals)} signals to subplot {subplot_idx}")
                    page.set_subplot_signals(subplot_idx, page_signals)
                else:
                    logger.warning(f"    No signals available to plot in subplot {subplot_idx}")

        self.tab_widget.setCurrentIndex(state.current_page_index)
        logger.info("=== RESTORE COMPLETE ===")
        return True

    def _find_signal_data(self, ref: dict):
        """Find raw signals data from metadata reference (Imported or Dummy)"""
        logger = logging.getLogger(__name__)
        name = ref.get('name')
        channel_name = str(ref.get('channel_name'))
        group_name = ref.get('group_name')

        logger.debug(f"_find_signal_data: Looking for '{name}' in channel='{channel_name}', group='{group_name}'")

        page = self.get_current_page()
        if page and page.plot_canvas:
            for channel in page.plot_canvas.dummy_signals:
                if channel.get('name') == channel_name:
                    for group in channel.get('groups', []):
                        if group.get('name') == group_name:
                            for sig in group.get('signals', []):
                                if sig.get('name') == name:
                                    logger.debug("    FOUND in dummy data!")
                                    return {**sig, 'channel_name': channel_name, 'group_name': group_name}

        file_path = None
        for data in self.data_manager.imported_data:
            if data['label'] == channel_name:
                file_path = data['path']
                if file_path.lower().endswith('.inf'):
                    file_path = file_path[:-4]
                break

        if file_path:
            logger.debug(f"  Dynamically resolved file: {file_path}")
            load_ref = {**ref, 'file_path': file_path}
            loaded = self.data_manager.load_signal_data(load_ref)
            if loaded:
                logger.debug(f"    Successfully reloaded '{name}' from current channel source")
                return loaded

        logger.debug("    NOT FOUND anywhere")
        return None

    def closeEvent(self, event):
        """Save settings and state on window close."""
        import traceback
        logger = logging.getLogger(__name__)
        logger.info("=== CLOSING APPLICATION ===")

        try:
            for page in self.page_manager.pages:
                if page.plot_canvas:
                    logger.info(f"Gathering signals for page: {page.page_name}")
                    for i in range(6):
                        if i < len(page.plot_canvas.axes):
                            sigs = page.plot_canvas.get_existing_signals_for_subplot(i)
                            if sigs:
                                page.subplot_signals[i] = sigs

            geom = self.geometry()
            self.settings.preferences.window_geometry = [geom.x(), geom.y(), geom.width(), geom.height()]
            logger.info(f"Saved window geometry: {[geom.x(), geom.y(), geom.width(), geom.height()]}")

            self.settings.state.imported_files = self.data_manager.get_imported_paths_info()
            logger.info(f"Saved {len(self.settings.state.imported_files)} imported files")

            self.settings.state.current_page_index = self.tab_widget.currentIndex()
            logger.info(f"Current page index: {self.settings.state.current_page_index}")

            logger.info("Getting page states...")
            page_states = self.page_manager.get_all_pages_state()
            self.settings.state.pages = page_states
            logger.info(f"Got {len(page_states)} page states")

            logger.info("Saving to file...")
            self.settings.save()
            logger.info("=== CLOSE COMPLETE ===")

        except Exception as e:
            logger.error(f"ERROR during close: {e}")
            logger.error(traceback.format_exc())

        event.accept()

    def apply_theme_style(self):
        """Apply theme-aware styling to the main window"""
        from theme import get_theme
        theme = get_theme()

        self.setStyleSheet(theme.get_style_sheet())

        self.status_frame.setStyleSheet(f"background-color: {theme.colors.status_bg}; border-top: 1px solid {theme.colors.border};")
        self.status_help_label.setStyleSheet(theme.get_status_label_style())
        self.plot_count_label.setStyleSheet(theme.get_status_label_style())
        self.measurement_label.setStyleSheet(theme.get_status_label_style())

    def create_menu_bar(self):
        """Create menu bar with action items"""
        menubar = self.menuBar()
        menubar.setNativeMenuBar(True)

        # File menu
        file_menu = menubar.addMenu('File')

        new_plot_action = QAction('New Plot (N)', self)
        new_plot_action.setShortcut('N')
        new_plot_action.triggered.connect(self.new_canvas)
        file_menu.addAction(new_plot_action)

        import_data_action = QAction('Import Data (C)', self)
        import_data_action.setShortcut('C')
        import_data_action.triggered.connect(self.import_pscad_data)
        file_menu.addAction(import_data_action)

        open_template_action = QAction('Open Template...', self)
        open_template_action.triggered.connect(self.action_manager.on_open_template_clicked)
        file_menu.addAction(open_template_action)

        save_template_action = QAction('Save Template...', self)
        save_template_action.triggered.connect(self.action_manager.on_save_template_clicked)
        file_menu.addAction(save_template_action)

        file_menu.addSeparator()

        export_action = QAction('Export to PDF (E)', self)
        export_action.setShortcut('E')
        export_action.triggered.connect(self.on_export_clicked)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menu
        view_menu = menubar.addMenu('View')

        reset_x_action = QAction('Reset X-Axis (R)', self)
        reset_x_action.setShortcut('R')
        reset_x_action.triggered.connect(lambda: self._call_canvas_method('reset_x_zoom'))
        view_menu.addAction(reset_x_action)

        reset_y_action = QAction('Reset Y-Axis (Y)', self)
        reset_y_action.setShortcut('Y')
        reset_y_action.triggered.connect(lambda: self._call_canvas_method('reset_y_zoom'))
        view_menu.addAction(reset_y_action)

        view_menu.addSeparator()

        grid_action = QAction('Round X to Grid (X)', self)
        grid_action.setShortcut('X')
        grid_action.triggered.connect(lambda: self._call_canvas_method('round_x_to_grid'))
        view_menu.addAction(grid_action)

        cursor_action = QAction('Toggle Cursors (T)', self)
        cursor_action.setShortcut('T')
        cursor_action.triggered.connect(lambda: self._call_canvas_method('toggle_measurement_cursors'))
        view_menu.addAction(cursor_action)

        # Settings Menu
        settings_menu = menubar.addMenu('Settings')

        adjust_margins_action = QAction('Adjust Margins (M)', self)
        adjust_margins_action.setShortcut('M')
        adjust_margins_action.triggered.connect(self.adjust_margins)
        settings_menu.addAction(adjust_margins_action)

        settings_menu.addSeparator()

        self.group_name_action = QAction('Group name in legend', self, checkable=True)
        self.group_name_action.setChecked(self.group_name_in_legend)
        self.group_name_action.triggered.connect(self.toggle_group_name_in_legend)
        settings_menu.addAction(self.group_name_action)

        self.channel_name_action = QAction('Channel name in legend', self, checkable=True)
        self.channel_name_action.setChecked(self.channel_name_in_legend)
        self.channel_name_action.triggered.connect(self.toggle_channel_name_in_legend)
        settings_menu.addAction(self.channel_name_action)

        # Help Menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About PSPlot...', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def toggle_group_name_in_legend(self, checked):
        self.group_name_in_legend = checked
        self._refresh_all_plots()

    def toggle_channel_name_in_legend(self, checked):
        self.channel_name_in_legend = checked
        self._refresh_all_plots()

    def _refresh_all_plots(self):
        """Helper to refresh all subplots across all pages when legend settings change"""
        for page in self.page_manager.pages:
            if page.plot_canvas:
                for i in range(page.plot_canvas.subplot_count):
                    signals = page.plot_canvas.get_existing_signals_for_subplot(i)
                    if signals:
                        page.plot_canvas.set_subplot_signals(
                            i, signals,
                            use_group_name=self.group_name_in_legend,
                            use_channel_name=self.channel_name_in_legend
                        )

    def _on_tab_double_clicked(self, index):
        if 0 <= index < len(self.page_manager.pages):
            self.page_manager.rename_page(index)

    def _call_canvas_method(self, method_name):
        """Helper to call a method on the current plot canvas"""
        page = self.get_current_page()
        if page and page.plot_canvas and hasattr(page.plot_canvas, method_name):
            getattr(page.plot_canvas, method_name)()

    def show_about_dialog(self):
        """Show the About dialog with icon and creator info."""
        dialog = QMessageBox(self)
        dialog.setWindowTitle("About PSPlot")
        
        # Load and set application icon
        ip = getattr(self, "icon_path", None)
        if ip and os.path.exists(ip):
            pm = QPixmap(ip)
            if pm.width() > 0:
                sp = pm.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                dialog.setIconPixmap(sp)
            else:
                dialog.setIcon(QMessageBox.Information)
        else:
            dialog.setIcon(QMessageBox.Information)
        
        dialog.setText("PSPlot: Professional Power System Output Plotter")
        dialog.setInformativeText(
            "<b>Version:</b> 1.0.0<br>"
            "<b>Developer:</b> Dr. Roni Irnawan<br>"
            "<b>Email:</b> roniirnawan@ugm.ac.id<br>"
            "<b>Organization:</b> Department of Electrical Engineering,<br>"
            "Faculty of Engineering, Universitas Gadjah Mada<br><br>"
            "PSPlot is a professional tool for plotting and exporting<br>"
            "power system signals from PSCAD and COMTRADE data formats.<br><br>"
            "Copyright 2026 PSPlot - All rights reserved."
        )
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()

# plot_modules/canvas_base.py
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QWidget, QMenu, QAction, QMessageBox, QDialog, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
                             QLabel, QMenuBar, QFileDialog, QInputDialog, QComboBox, QListView)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from PyQt5.QtCore import Qt

try:
    from theme import get_theme
except ImportError:
    get_theme = None

class BaseInteractiveCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8.27, height=11.69):
        # Initialize main window reference early
        self.main_window = None
        
        # Create figure with specified dimensions (default A4 portrait)
        self.fig = Figure(figsize=(width, height), dpi=100)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background-color: white; border: 1px solid black;")
        
        self.subplot_count = 1
        self.axes = []
        self.rect_selectors = []
        self.current_xlim = None  # Track shared x-limits
        self.current_ylim_dict = {}  # Track individual y-limits for each subplot
        self.x_data_range = (0, 10)  # Full data range
        
        # Measurement Cursors
        self.cursors_active = False
        self.cursor_lines_a = [] # List of vertical lines for cursor A
        self.cursor_lines_b = [] # List of vertical lines for cursor B
        self.cursor_texts_a = [] # List of text labels for values at cursor A
        self.cursor_texts_b = [] # List of text labels for values at cursor B
        self.cursor_pos_a = None # X position of cursor A
        self.cursor_pos_b = None # X position of cursor B
        self.active_cursor = None # 'A' or 'B' being dragged
        
        # Store custom margins
        self.custom_margins = None  # Start with None to use tight_layout by default
        
        # Track last clicked subplot
        self.last_clicked_subplot = None
        
        # Enable mouse tracking for interactive features
        self.setMouseTracking(True)
        
        # Add context menu support
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
        # Add regular click event handler for subplot detection
        self.fig.canvas.mpl_connect('button_press_event', self.on_regular_click)
        
        # Connect cursor events
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        
        # Available signals from DataManager
        self.dummy_signals = [] 
        
    def generate_dummy_signals(self):
        """No longer used"""
        return []

    def update_plots(self, subplot_count):
        self.subplot_count = max(1, min(6, subplot_count))
        self.fig.clear()
        
        # Reset cursor state - cursors must be re-enabled after layout change
        self.cursors_active = False
        self.cursor_lines_a = []
        self.cursor_lines_b = []
        self.cursor_texts_a = []
        self.cursor_texts_b = []
        
        # Explicitly clear status info when changing plots
        if hasattr(self, 'main_window') and self.main_window:
            if hasattr(self.main_window, 'measurement_label'):
                self.main_window.measurement_label.setText("")
                self.main_window.measurement_label.setVisible(False)
        
        self.axes = []
        self.rect_selectors = []
        
        if self.subplot_count == 1:
            ax = self.fig.add_subplot(111)
            self.axes = [ax]
        else:
            self.axes = [self.fig.add_subplot(self.subplot_count, 1, i+1) 
                        for i in range(self.subplot_count)]
        
        # Plot different data for each subplot
        for i, ax in enumerate(self.axes):
            # Initially plot nothing (blank plot)
            ax.plot([], [], linewidth=2, label=f'Subplot {i+1}')
            
            # Only show x-label on the bottom subplot
            if i == len(self.axes) - 1:  # Last subplot
                ax.set_xlabel('Time (s)')
            else:
                ax.set_xlabel('')  # Hide x-label for upper subplots
            
            # Remove title (as requested)
            ax.set_title('')  # No title
            
            # Show y-label on all subplots
            y_label = getattr(self, 'y_labels', {}).get(i, 'Amplitude')
            ax.set_ylabel(y_label)
            ax.legend(fontsize=8, loc='upper right')
            ax.grid(True, alpha=0.3)
            
            # Restore previous y-limits if they exist
            if i in self.current_ylim_dict:
                ax.set_ylim(self.current_ylim_dict[i])
            
            # Add rectangle selector for zooming
            selector = RectangleSelector(
                ax, self.on_select, useblit=True,
                button=[1], minspanx=5, minspany=5, spancoords='pixels',
                interactive=True
            )
            # If cursors are active, stay in measurement mode (disable zoom)
            if self.cursors_active:
                selector.set_active(False)
            self.rect_selectors.append(selector)
        
        # Apply shared x-limits if they exist (this preserves x-limits when changing subplot count)
        if self.current_xlim is not None:
            for ax in self.axes:
                ax.set_xlim(self.current_xlim)
        
        # Apply custom margins or use tight_layout
        if self.custom_margins is not None:
            self.fig.subplots_adjust(
                left=self.custom_margins['left'],
                right=self.custom_margins['right'],
                top=self.custom_margins['top'],
                bottom=self.custom_margins['bottom'],
                wspace=self.custom_margins['wspace'],
                hspace=self.custom_margins['hspace']
            )
        else:
            # Use tight_layout for minimal whitespace by default
            self.fig.tight_layout(pad=2.0)
        
        self.draw()
    
    def on_select(self, eclick, erelease):
        """Handle rectangle selection for zooming"""
        if eclick.xdata is None or erelease.xdata is None:
            return
            
        # Get the limits from the selection
        x1, x2 = sorted([eclick.xdata, erelease.xdata])
        y1, y2 = sorted([eclick.ydata, erelease.ydata])
        
        # Prevent identical limits (causes warnings)
        if abs(x2 - x1) < 1e-10:
            x2 = x1 + 0.1
        if abs(y2 - y1) < 1e-10:
            y2 = y1 + 0.1
        
        # Store the shared x-limits
        self.current_xlim = (x1, x2)
        
        # Apply the same x-limits to all subplots and update y-limits
        for i, ax in enumerate(self.axes):
            ax.set_xlim(x1, x2)
            ax.set_ylim(y1, y2)
            # Store y-limits for this subplot
            self.current_ylim_dict[i] = (y1, y2)
        
        self.draw()
        
        # Clear all rectangle selectors to make them disappear
        for selector in self.rect_selectors:
            selector.clear()
        self.fig.canvas.draw_idle()
    
    def on_regular_click(self, event):
        """Store which subplot was last clicked and handle cursor selection"""
        if event.inaxes in self.axes:
            # Find which subplot was clicked
            for i, ax in enumerate(self.axes):
                if event.inaxes == ax:
                    self.last_clicked_subplot = i
                    break
        
        if self.cursors_active and event.xdata is not None:
            # Check if clicking near a cursor to start dragging
            tol = (self.fig.get_axes()[0].get_xlim()[1] - self.fig.get_axes()[0].get_xlim()[0]) * 0.02
            if abs(event.xdata - self.cursor_pos_a) < tol:
                self.active_cursor = 'A'
            elif abs(event.xdata - self.cursor_pos_b) < tol:
                self.active_cursor = 'B'

    def on_mouse_move(self, event):
        """Handle cursor dragging and delta calculation"""
        if not self.cursors_active or self.active_cursor is None or event.xdata is None:
            return
            
        if self.active_cursor == 'A':
            self.cursor_pos_a = event.xdata
        else:
            self.cursor_pos_b = event.xdata
            
        self._update_cursor_positions()
        
    def on_mouse_release(self, event):
        """Stop dragging cursor"""
        self.active_cursor = None

    def toggle_measurement_cursors(self):
        """Enable/Disable measurement vertical lines and toggle zoom availability"""
        self.cursors_active = not self.cursors_active
        
        # When cursors are active, we should disable the zoom selectors to prevent conflicts
        zoom_enabled = not self.cursors_active
        for selector in self.rect_selectors:
            selector.set_active(zoom_enabled)
        
        if self.cursors_active:
            xlim = self.axes[0].get_xlim()
            if self.cursor_pos_a is None:
                self.cursor_pos_a = xlim[0] + (xlim[1] - xlim[0]) * 0.25
            if self.cursor_pos_b is None:
                self.cursor_pos_b = xlim[0] + (xlim[1] - xlim[0]) * 0.75
            
            # Create lines and text on each axes
            self.cursor_lines_a = []
            self.cursor_lines_b = []
            self.cursor_texts_a = []
            self.cursor_texts_b = []
            
            for ax in self.axes:
                la = ax.axvline(self.cursor_pos_a, color='red', linestyle='--', linewidth=1.5, alpha=0.8)
                lb = ax.axvline(self.cursor_pos_b, color='blue', linestyle='--', linewidth=1.5, alpha=0.8)
                self.cursor_lines_a.append(la)
                self.cursor_lines_b.append(lb)
                
                # Add text labels with background box for readability
                bbox = dict(boxstyle='round,pad=0.3', fc='white', ec='red', alpha=0.9, lw=1)
                ta = ax.text(self.cursor_pos_a, 0, "", color='red', fontsize=8, fontweight='bold', bbox=bbox, zorder=5)
                
                bbox_b = dict(boxstyle='round,pad=0.3', fc='white', ec='blue', alpha=0.9, lw=1)
                tb = ax.text(self.cursor_pos_b, 0, "", color='blue', fontsize=8, fontweight='bold', bbox=bbox_b, zorder=5)
                
                self.cursor_texts_a.append(ta)
                self.cursor_texts_b.append(tb)
            
            self._update_cursor_positions() # Initial info update
        else:
            # Explicitly hide and remove all cursor-related artists
            all_objs = self.cursor_lines_a + self.cursor_lines_b + self.cursor_texts_a + self.cursor_texts_b
            for obj in all_objs:
                try:
                    obj.set_visible(False)
                    if hasattr(obj, 'remove'):
                        obj.remove()
                except Exception:
                    pass

            self.cursor_lines_a = []
            self.cursor_lines_b = []
            self.cursor_texts_a = []
            self.cursor_texts_b = []
            
            # Reset status bar info to empty for this canvas
            if hasattr(self, 'main_window') and self.main_window:
                if hasattr(self.main_window, 'measurement_label'):
                    self.main_window.measurement_label.setText("")
                    self.main_window.measurement_label.setVisible(False)
                self.main_window.update_status_bar()
            
        self.draw()

    def _update_cursor_positions(self):
        """Sync line positions and update delta info in status bar and on-plot labels"""
        if not hasattr(self, 'axes') or not self.axes or not self.cursors_active:
            return
            
        xlim = self.axes[0].get_xlim()
        x_range = xlim[1] - xlim[0]
        
        # Helper to get all interpolated values at X for all data lines in this subplot
        def get_all_vals_at(ax, x_pos):
            vals = []
            for line in ax.get_lines():
                if line.get_label() != '_nolegend_' and not hasattr(line, '_cursor_marker'):
                    xd = np.asarray(line.get_xdata())
                    yd = np.asarray(line.get_ydata())
                    if len(xd) > 1:
                        try:
                            label = line.get_label().strip('_nolegend_')
                            vals.append((label, np.interp(x_pos, xd, yd)))
                        except:
                            pass
            return vals

        for i, (ax, la, lb, ta, tb) in enumerate(zip(self.axes, self.cursor_lines_a, self.cursor_lines_b, self.cursor_texts_a, self.cursor_texts_b)):
            # Update Vertical Lines
            la.set_xdata([self.cursor_pos_a, self.cursor_pos_a])
            lb.set_xdata([self.cursor_pos_b, self.cursor_pos_b])
            
            # Update Text A - Display ALL signals values
            all_vals_a = get_all_vals_at(ax, self.cursor_pos_a)
            if all_vals_a:
                lines_a = [f"{name}: {val:.4f}" for name, val in all_vals_a]
                ta.set_text("\n".join(lines_a))
                # Position near the first/average value
                y_vals_a = [v for _, v in all_vals_a]
                avg_y_a = sum(y_vals_a) / len(y_vals_a)
                ta.set_position((self.cursor_pos_a + x_range*0.01, avg_y_a))
                ta.set_visible(True)
            else:
                ta.set_visible(False)
                
            # Update Text B - Display ALL signals values
            all_vals_b = get_all_vals_at(ax, self.cursor_pos_b)
            if all_vals_b:
                lines_b = [f"{name}: {val:.4f}" for name, val in all_vals_b]
                tb.set_text("\n".join(lines_b))
                # Position near the first/average value
                y_vals_b = [v for _, v in all_vals_b]
                avg_y_b = sum(y_vals_b) / len(y_vals_b)
                tb.set_position((self.cursor_pos_b + x_range*0.01, avg_y_b))
                tb.set_visible(True)
            else:
                tb.set_visible(False)
        
        # Calculate Delta for status bar
        dx = abs(self.cursor_pos_b - self.cursor_pos_a)
        freq = 1.0/dx if dx > 0 else 0
        
        if hasattr(self, 'main_window') and self.main_window:
            msg = f"A: {self.cursor_pos_a:.4f}s | B: {self.cursor_pos_b:.4f}s | Δt: {dx:.4f}s | f: {freq:.2f}Hz"
            self.main_window.update_status_bar(msg)
            
        self.draw_idle()

    def show_context_menu(self, position):
        """Show context menu when right-clicking on the canvas"""
        # Create context menu
        menu = QMenu(self)
        
        # Apply theme-aware styling to the menu
        if get_theme:
            menu.setStyleSheet(get_theme().get_menu_style())
        
        # Add action to show data label for the specific subplot
        action = menu.addAction("Add/Change Data")
        action.triggered.connect(lambda: self.show_signal_selector(position))
        
        # Add action to change y-label if a subplot was clicked
        if self.last_clicked_subplot is not None:
            y_label_action = menu.addAction("Change Y-Label")
            y_label_action.triggered.connect(self.change_y_label)
            
            # Add scaling action
            scale_action = menu.addAction("Scale")
            scale_action.triggered.connect(self.change_signal_scale)
        
        menu.exec_(self.mapToGlobal(position))

    def _apply_dialog_style(self, dialog):
        """Helper to apply consistent theme styling with high contrast selection views"""
        if not get_theme:
            return
            
        theme = get_theme()
        c = theme.colors
        
        # Use a high-contrast selection color for dropdowns (Standard Windows/macOS Blue)
        selection_bg = "#0078D7" 
        
        dialog_style = f"""
            QDialog {{ 
                background-color: {c.base}; 
            }}
            QLabel {{ 
                color: {c.text}; 
                font-size: 11pt; 
            }}
            QComboBox {{
                background-color: {c.alt};
                color: {c.text};
                border: 1px solid {c.border};
                border-radius: 4px;
                padding: 4px;
                min-height: 25px;
            }}
            /* High-contrast list styling for the dropdown popup */
            QComboBox QAbstractItemView, QListView {{
                background-color: {c.base};
                color: {c.text};
                border: 1px solid {c.border};
                selection-background-color: {selection_bg};
                selection-color: white;
                outline: none;
            }}
            /* Specific fix for white-on-white text selection in dropdowns */
            QComboBox QAbstractItemView::item:selected {{
                background-color: {selection_bg};
                color: white;
            }}
            QLineEdit {{
                background-color: {c.alt};
                color: {c.text};
                border: 1px solid {c.border};
                border-radius: 4px;
                padding: 6px;
                font-size: 11pt;
            }}
        """
        dialog.setStyleSheet(dialog_style)
        
        # Set persistent view style for combo boxes to avoid platform native hijacking
        for combo in dialog.findChildren(QComboBox):
            view = QListView()
            view.setStyleSheet(f"selection-background-color: {selection_bg}; selection-color: white; background-color: {c.base}; color: {c.text};")
            combo.setView(view)
        
        # Style buttons with explicit high-contrast colors and visible text
        for button in dialog.findChildren(QPushButton):
            btn_text = button.text().replace("&", "").strip()
            if btn_text in ["Select", "Apply", "OK"]:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c.success};
                        color: white !important;
                        font-weight: bold;
                        border: none;
                        padding: 8px 20px;
                        border-radius: 5px;
                        min-width: 100px;
                    }}
                    QPushButton:hover {{
                        background-color: {theme._darken(c.success, 0.8)};
                    }}
                """)
            elif btn_text in ["Cancel"]:
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {c.danger};
                        color: white !important;
                        font-weight: bold;
                        border: none;
                        padding: 8px 20px;
                        border-radius: 5px;
                        min-width: 100px;
                    }}
                    QPushButton:hover {{
                        background-color: {theme._darken(c.danger, 0.8)};
                    }}
                """)

    def change_signal_scale(self):
        """Show custom dialog to change the scaling factor for a signal in the current subplot"""
        if self.last_clicked_subplot is not None:
            # Get existing signals for this subplot
            existing_signals = self.get_existing_signals_for_subplot(self.last_clicked_subplot)
            if not existing_signals:
                QMessageBox.information(self, "Info", "No signals found in this subplot.")
                return

            # Let user choose signal if more than one
            selected_signal = None
            if len(existing_signals) == 1:
                selected_signal = existing_signals[0]
            else:
                items = [f"{s.get('name')} (Scale: {s.get('scale', 1.0)})" for s in existing_signals]
                
                dialog = QInputDialog(self)
                dialog.setWindowTitle("Select Signal")
                dialog.setLabelText("Which signal do you want to scale?")
                dialog.setComboBoxItems(items)
                dialog.setOkButtonText("Select")
                self._apply_dialog_style(dialog)
                
                if dialog.exec_() == QDialog.Accepted:
                    idx = items.index(dialog.textValue())
                    selected_signal = existing_signals[idx]
                else:
                    return

            if selected_signal:
                # Get new scale factor using a styled numeric dialog
                current_scale = float(selected_signal.get('scale', 1.0))
                
                dialog = QInputDialog(self)
                dialog.setWindowTitle("Scale Factor")
                dialog.setLabelText(f"Enter scale factor for {selected_signal['name']}:")
                dialog.setDoubleValue(current_scale)
                dialog.setDoubleDecimals(4)
                dialog.setDoubleRange(-1e12, 1e12)
                dialog.setOkButtonText("Apply")
                self._apply_dialog_style(dialog)
                
                if dialog.exec_() == QDialog.Accepted:
                    new_scale = dialog.doubleValue()
                    # Update the scale in metadata
                    selected_signal['scale'] = new_scale
                    
                    # Re-plot all signals in this subplot with updated scale
                    if hasattr(self, 'set_subplot_signals'):
                        use_group_name = False
                        use_channel_name = False
                        if hasattr(self, 'main_window') and self.main_window:
                            use_group_name = getattr(self.main_window, 'group_name_in_legend', False)
                            use_channel_name = getattr(self.main_window, 'channel_name_in_legend', False)
                        
                        self.set_subplot_signals(self.last_clicked_subplot, existing_signals, 
                                               use_group_name=use_group_name, 
                                               use_channel_name=use_channel_name)
    
    def change_y_label(self):
        """Show dialog to change the y-label for the last clicked subplot"""
        if self.last_clicked_subplot is not None:
            # Get current y-label
            current_label = getattr(self, 'y_labels', {}).get(self.last_clicked_subplot, 'Amplitude')
            
            # Create a dialog with Test4.py template
            dialog = YLabelDialog(current_label, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                new_label = dialog.get_label()
                # Set the new y-label
                if not hasattr(self, 'y_labels'):
                    self.y_labels = {}
                self.y_labels[self.last_clicked_subplot] = new_label
                
                # Update the label immediately
                if self.last_clicked_subplot < len(self.axes):
                    self.axes[self.last_clicked_subplot].set_ylabel(new_label)
                    self.draw()

    def show_signal_selector(self, position):
        """Show signal selector dialog for the clicked subplot"""
        # Automatically disable measurement cursors before opening selector
        # to prevent interaction issues and clear existing markers
        if getattr(self, 'cursors_active', False):
            self.toggle_measurement_cursors()

        # If position is exactly (0,0), it might be an automated trigger from import
        # In that case, we should default to subplot 0 if none was clicked
        if self.last_clicked_subplot is None:
            self.last_clicked_subplot = 0
            
        from signal_explorer import SignalExplorerDialog
        
        # Get existing signals for this subplot to show in the dialog
        existing_signals = self.get_existing_signals_for_subplot(self.last_clicked_subplot)
        
        # Get data from data manager if available
        available_data = self.dummy_signals
        data_manager = None
        if hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, 'data_manager'):
            data_manager = self.main_window.data_manager
            imported = data_manager.get_all_available_data()
            available_data = self.dummy_signals + imported
        
        # Create a dialog with dummy + imported signals and existing signals
        dialog = SignalExplorerDialog(available_data, existing_signals, parent=self)
        if dialog.exec_() == dialog.Accepted:
            selected_ref = dialog.get_selected_signals()
            final_signals = []
            
            if selected_ref:
                for ref in selected_ref:
                    # If ref doesn't have 'x' and 'y' data (meaning it's just metadata from .inf), load it
                    if ('x' not in ref or 'y' not in ref) and data_manager:
                        # Load data via data_manager
                        loaded_data = data_manager.load_signal_data(ref)
                        if loaded_data:
                            # Merge original ref with loaded data to preserve metadata
                            merged = {**ref, **loaded_data}
                            final_signals.append(merged)
                    else:
                        # Data already exists (e.g., dummy signals or already loaded)
                        final_signals.append(ref)
                
                if final_signals:
                    # Plot all selected signals in the same subplot
                    # Use set_subplot_signals if available (via mixin), otherwise fallback
                    if hasattr(self, 'set_subplot_signals'):
                        # Check for flags in main_window
                        use_group_name = False
                        use_channel_name = False
                        if hasattr(self, 'main_window') and self.main_window:
                            use_group_name = getattr(self.main_window, 'group_name_in_legend', False)
                            use_channel_name = getattr(self.main_window, 'channel_name_in_legend', False)
                        
                        self.set_subplot_signals(self.last_clicked_subplot, final_signals, 
                                               use_group_name=use_group_name, 
                                               use_channel_name=use_channel_name)
                    else:
                        # Fallback for base class if mixin not correctly initialized
                        ax = self.axes[self.last_clicked_subplot]
                        ax.clear()
                        for sig in final_signals:
                            ax.plot(sig['x'], sig['y'], label=sig['name'])
                        ax.legend()
                        self.draw()


class YLabelDialog(QDialog):
    """Dialog for changing y-label with UI similar to Test4.py"""
    
    def __init__(self, current_label="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Y-Label")
        self.setModal(True)
        self.resize(400, 200)
        self.current_label = current_label
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Menu bar (similar to Test4.py)
        menubar = QMenuBar(self)
        options_menu = menubar.addMenu('Options')
        
        # Add a sample action (like in Test4.py)
        say_hi_action = QAction('Say Hi', self)
        say_hi_action.triggered.connect(self.say_hi)
        options_menu.addAction(say_hi_action)
        
        layout.setMenuBar(menubar)
        
        # Main content area
        content_layout = QVBoxLayout()
        
        # Title label
        title_label = QLabel("Enter new y-label:")
        title_label.setStyleSheet("font-size: 12pt; font-weight: bold; padding: 10px;")
        content_layout.addWidget(title_label)
        
        # Input field
        self.label_input = QLineEdit()
        self.label_input.setText(self.current_label)
        self.label_input.selectAll()
        self.label_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 11pt;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        content_layout.addWidget(self.label_input)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        if get_theme:
            ok_button.setStyleSheet(get_theme().get_button_ok_style())
        button_layout.addWidget(ok_button)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        if get_theme:
            cancel_button.setStyleSheet(get_theme().get_button_cancel_style())
        button_layout.addWidget(cancel_button)
        
        content_layout.addLayout(button_layout)
        layout.addLayout(content_layout)
        
        # Apply theme-aware styling
        if get_theme:
            self.setStyleSheet(get_theme().get_style_sheet())

    def say_hi(self):
        QMessageBox.information(self, "Hi", "Hello from PSPlot!")

    def get_label(self):
        return self.label_input.text()

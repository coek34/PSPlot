# plot_modules/canvas_base.py
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QMenuBar, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from PyQt5.QtCore import Qt

class BaseInteractiveCanvas(FigureCanvas):
    def __init__(self, parent=None, width=8.27, height=11.69):
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
        
        # Dummy signals data
        self.dummy_signals = self.generate_dummy_signals()
    
    def generate_dummy_signals(self):
        """Generate dummy signals organized in channels with groups"""
        # Create hierarchical structure: Channel -> Groups -> Signals
        signals = []
        x = np.linspace(0, 10, 1000)
        
        # Create Dummy channel with Trigonometry and Exponential groups
        dummy_channel = {
            'name': 'Dummy',
            'groups': []
        }
        
        # Trigonometry group (4 signals)
        trig_group = {
            'name': 'Trigonometry',
            'signals': []
        }
        
        for i in range(4):
            if i == 0:
                # Sine wave
                y = np.sin(x * (i+1)) * np.exp(-x/10)
            elif i == 1:
                # Cosine wave
                y = np.cos(x * (i+1)) * np.exp(-x/8)
            elif i == 2:
                # Sine with different frequency
                y = np.sin(x * 2) * np.cos(x * (i+1))
            else:
                # Combined signal
                y = np.sin(x) * np.cos(x * (i+1)) * np.exp(-x/5)
            
            trig_group['signals'].append({
                'name': f'Trig_{i+1}',
                'x': x,
                'y': y
            })
        
        # Exponential group (4 signals)
        exp_group = {
            'name': 'Exponential',
            'signals': []
        }
        
        for i in range(4):
            if i == 0:
                # Exponential decay
                y = np.exp(-x/(i+1)) * np.sin(x * (i+1))
            elif i == 1:
                # Exponential growth
                y = np.exp(x/(i+1)) * np.cos(x * (i+1))
            elif i == 2:
                # Damped oscillation
                y = np.exp(-x/5) * np.sin(x * (i+1)) * np.cos(x * (i+1))
            else:
                # Complex exponential
                y = np.exp(-x/3) * np.sin(x * (i+1)) * np.exp(-x/2)
            
            exp_group['signals'].append({
                'name': f'Exp_{i+1}',
                'x': x,
                'y': y
            })
        
        # Add groups to channel
        dummy_channel['groups'].extend([trig_group, exp_group])
        signals.append(dummy_channel)
        
        # Create another channel with different signals
        dummy2_channel = {
            'name': 'Dummy2',
            'groups': []
        }
        
        # Another trigonometry group
        trig_group2 = {
            'name': 'Trigonometry',
            'signals': []
        }
        
        for i in range(4):
            if i == 0:
                # Sine wave with different amplitude
                y = 2 * np.sin(x * (i+1)) * np.exp(-x/10)
            elif i == 1:
                # Cosine wave with different frequency
                y = np.cos(x * 3) * np.exp(-x/8)
            elif i == 2:
                # Combined signal
                y = np.sin(x * 2) * np.cos(x * (i+1)) * np.exp(-x/5)
            else:
                # Sine with phase shift
                y = np.sin(x + np.pi/4) * np.exp(-x/3)
            
            trig_group2['signals'].append({
                'name': f'Trig2_{i+1}',
                'x': x,
                'y': y
            })
        
        dummy2_channel['groups'].append(trig_group2)
        signals.append(dummy2_channel)
        
        return signals
    
    def update_plots(self, subplot_count):
        self.subplot_count = max(1, min(6, subplot_count))
        self.fig.clear()
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
        """Store which subplot was last clicked for context menu use"""
        if event.inaxes in self.axes:
            # Find which subplot was clicked
            for i, ax in enumerate(self.axes):
                if event.inaxes == ax:
                    self.last_clicked_subplot = i
                    break
    
    def show_context_menu(self, position):
        """Show context menu when right-clicking on the canvas"""
        # Create context menu
        menu = QMenu(self)
        
        # Apply theme-aware styling to the menu
        is_dark = False
        try:
            # Try to detect dark mode using system settings
            import darkdetect
            is_dark = darkdetect.isDark()
        except:
            # If darkdetect is not available, default to light mode
            pass
            
        base_color = "#2b2b2b" if is_dark else "#ffffff"
        text_color = "#ffffff" if is_dark else "#000000"
        border_color = "#444" if is_dark else "#ccc"
        
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {base_color};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 4px;
                font-family: 'Arial', sans-serif;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border: none;
            }}
            QMenu::item:selected {{
                background-color: #0078D7;
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {border_color};
                margin: 4px 0;
            }}
        """)
        
        # Add action to show data label for the specific subplot
        action = menu.addAction("Add/Change Data")
        action.triggered.connect(lambda: self.show_signal_selector(position))
        
        # Add action to change y-label if a subplot was clicked
        if self.last_clicked_subplot is not None:
            y_label_action = menu.addAction("Change Y-Label")
            y_label_action.triggered.connect(self.change_y_label)
        
        menu.exec_(self.mapToGlobal(position))
    
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
        # Use the stored last clicked subplot
        if self.last_clicked_subplot is not None:
            from signal_explorer import SignalExplorerDialog
            
            # Get existing signals for this subplot to show in the dialog
            existing_signals = self.get_existing_signals_for_subplot(self.last_clicked_subplot)
            
            # Create a dialog with dummy signals and existing signals
            dialog = SignalExplorerDialog(self.dummy_signals, existing_signals, parent=self)
            if dialog.exec_() == dialog.Accepted:
                selected_signals = dialog.get_selected_signals()
                if selected_signals:
                    # Plot all selected signals in the same subplot
                    self.set_subplot_signals(self.last_clicked_subplot, selected_signals)
        else:
            # If no subplot was clicked, show a message
            QMessageBox.information(self, "Info", "Please click on a subplot first to select a signal.")


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
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(ok_button)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 12px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        button_layout.addWidget(cancel_button)
        
        content_layout.addLayout(button_layout)
        layout.addLayout(content_layout)
        
        # Apply theme-aware stylesheet
        self.apply_theme_style()
        
        # Focus on input field
        self.label_input.setFocus()
        
    def apply_theme_style(self):
        """Apply theme-aware styling to the dialog"""
        try:
            import darkdetect
            is_dark = darkdetect.isDark()
        except:
            is_dark = False
            
        base_color = "#2b2b2b" if is_dark else "#ffffff"
        text_color = "#ffffff" if is_dark else "#000000"
        
        style = f"""
            QWidget {{
                background-color: {base_color};
                color: {text_color};
            }}
        """
        self.setStyleSheet(style)
        
    def say_hi(self):
        """Sample function like in Test4.py"""
        QMessageBox.information(self, "Message", "Hi!")
        
    def get_label(self):
        """Return the entered label"""
        return self.label_input.text()

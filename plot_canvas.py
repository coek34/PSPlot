# plot_canvas.py
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QWidget, QMenu, QAction, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector
from PyQt5.QtCore import Qt

class InteractivePlotCanvas(FigureCanvas):
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
        
        # Create initial plots
        self.update_plots(1)
        
        # Add context menu support
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
        # Add regular click event handler for subplot detection
        self.fig.canvas.mpl_connect('button_press_event', self.on_regular_click)
        
        # Dummy signals data
        self.dummy_signals = self.generate_dummy_signals()
    
    def generate_dummy_signals(self):
        """Generate dummy signals for plotting"""
        signals = []
        x = np.linspace(0, 10, 1000)
        
        # Generate 12 different signals (8 in Dummy, 4 in Dummy2)
        for i in range(12):
            # Different signal types
            if i % 4 == 0:
                # Sine wave
                y = np.sin(x * (i+1)) * np.exp(-x/10)
            elif i % 4 == 1:
                # Cosine wave
                y = np.cos(x * (i+1)) * np.exp(-x/8)
            elif i % 4 == 2:
                # Exponential decay
                y = np.exp(-x/(i+1)) * np.sin(x * (i+1))
            else:
                # Combined signal
                y = np.sin(x) * np.cos(x * (i+1)) * np.exp(-x/5)
            
            signals.append({
                'name': f'Signal_{i+1}',
                'x': x,
                'y': y
            })
        
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
            ax.set_ylabel('Amplitude')
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
    
    def set_subplot_signal(self, subplot_index, signal_data):
        """Set a signal to a specific subplot"""
        if subplot_index < 0 or subplot_index >= len(self.axes):
            return
            
        ax = self.axes[subplot_index]
        
        # Clear existing plot
        ax.clear()
        
        # Plot the signal
        if signal_data and 'x' in signal_data and 'y' in signal_data:
            # Ensure signal_data has a 'name' field
            name = signal_data.get('name', f'Signal_{subplot_index+1}')
            ax.plot(signal_data['x'], signal_data['y'], linewidth=2, label=name)
        else:
            # Plot default signal if no data provided
            ax.plot([], [], linewidth=2, label=f'Subplot {subplot_index+1}')
        
        # Set labels
        if subplot_index == len(self.axes) - 1:  # Last subplot
            ax.set_xlabel('Time (s)')
        else:
            ax.set_xlabel('')  # Hide x-label for upper subplots
        
        # Remove title (as requested)
        ax.set_title('')  # No title
        
        ax.set_ylabel('Amplitude')
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Restore previous y-limits if they exist
        if subplot_index in self.current_ylim_dict:
            ax.set_ylim(self.current_ylim_dict[subplot_index])
        
        # Add rectangle selector for zooming
        selector = RectangleSelector(
            ax, self.on_select, useblit=True,
            button=[1], minspanx=5, minspany=5, spancoords='pixels',
            interactive=True
        )
        self.rect_selectors[subplot_index] = selector
        
        self.draw()
        
        # Automatically round x to grid after adding signal
        self.round_x_to_grid()
    
    def set_subplot_signals(self, subplot_index, signal_data_list):
        """Set multiple signals to a specific subplot"""
        if subplot_index < 0 or subplot_index >= len(self.axes):
            return
            
        ax = self.axes[subplot_index]
        
        # Clear existing plot
        ax.clear()
        
        # Plot all signals
        if signal_data_list:
            
            for signal_data in signal_data_list:
                if signal_data and 'x' in signal_data and 'y' in signal_data:
                    # Ensure signal_data has a 'name' field
                    name = signal_data.get('name', f'Signal_{subplot_index+1}')
                    ax.plot(signal_data['x'], signal_data['y'], linewidth=2, label=name)
        else:
            # Plot default signal if no data provided
            ax.plot([], [], linewidth=2, label=f'Subplot {subplot_index+1}')
   	 
        # Set labels
        if subplot_index == len(self.axes) - 1:  # Last subplot
            ax.set_xlabel('Time (s)')
        else:
            ax.set_xlabel('')  # Hide x-label for upper subplots
        
        # Remove title (as requested)
        ax.set_title('')  # No title
        
        ax.set_ylabel('Amplitude')
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Restore previous y-limits if they exist
        if subplot_index in self.current_ylim_dict:
            ax.set_ylim(self.current_ylim_dict[subplot_index])
        
        # Add rectangle selector for zooming
        selector = RectangleSelector(
            ax, self.on_select, useblit=True,
            button=[1], minspanx=5, minspany=5, spancoords='pixels',
            interactive=True
        )
        self.rect_selectors[subplot_index] = selector
        
        self.draw()
        
        # Automatically round x to grid after adding signals
        self.round_x_to_grid()
    
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
    
    def set_x_limits(self, x_min, x_max):
        """Unified function to set x-limits for all subplots"""
        # Ensure valid limits
        x_min = max(self.x_data_range[0], x_min)
        x_max = min(self.x_data_range[1], x_max)
        
        if x_min >= x_max:
            x_min, x_max = self.x_data_range
            
        # Store and apply limits
        self.current_xlim = (x_min, x_max)
        for ax in self.axes:
            ax.set_xlim(x_min, x_max)
        
        self.draw()
    
    def reset_x_zoom(self):
        """Reset to original x-view (full data range)"""
        self.set_x_limits(self.x_data_range[0], self.x_data_range[1])
    
    def reset_y_zoom(self):
        """Reset y-axis to show only visible data in current x-range"""
        if self.current_xlim is not None:
            x_min, x_max = self.current_xlim
        else:
            x_min, x_max = self.x_data_range  # Default range
            
        # Reset y-limits for each subplot based on visible data
        self.current_ylim_dict.clear()
        
        for i, ax in enumerate(self.axes):
            # Collect y-data from all lines in this subplot
            all_visible_y = []
            
            # Get all the line data
            lines = ax.get_lines()
            for line in lines:
                # Skip lines with '_nolegend_' label (these are from rectangle selectors)
                if line.get_label() != '_nolegend_':
                    x_data = line.get_xdata()
                    y_data = line.get_ydata()
                    
                    # Find indices within current x-range
                    mask = (x_data >= x_min) & (x_data <= x_max)
                    if np.any(mask):
                        visible_y = y_data[mask]
                        all_visible_y.extend(visible_y)
            
            # Calculate y-limits based on all visible data
            if all_visible_y:
                y_array = np.array(all_visible_y)
                y_margin = (y_array.max() - y_array.min()) * 0.05  # 5% margin
                y_min = y_array.min() - y_margin if y_margin > 0 else y_array.min() - 0.1
                y_max = y_array.max() + y_margin if y_margin > 0 else y_array.max() + 0.1
                ax.set_ylim(y_min, y_max)
                self.current_ylim_dict[i] = (y_min, y_max)
        
        self.draw()
    
    def round_x_to_grid(self):
        """Round current x-axis limits to nearest grid values"""
        if self.current_xlim is None:
            current_x_min, current_x_max = self.x_data_range
        else:
            current_x_min, current_x_max = self.current_xlim
        
        # Define grid intervals (you can adjust these as needed)
        grid_intervals = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
        
        # Find the best grid interval based on current zoom level
        range_size = current_x_max - current_x_min
        target_interval = range_size / 10  # Aim for about 10 grid lines
        
        # Find closest grid interval
        best_interval = min(grid_intervals, key=lambda x: abs(x - target_interval))
        
        # Round to nearest grid points
        rounded_min = round(current_x_min / best_interval) * best_interval
        rounded_max = round(current_x_max / best_interval) * best_interval
        
        # Ensure we don't go beyond reasonable bounds
        rounded_min = max(self.x_data_range[0], rounded_min)
        rounded_max = min(self.x_data_range[1], rounded_max)
        
        # Make sure min < max
        if rounded_min >= rounded_max:
            # If they're too close, expand slightly
            center = (rounded_min + rounded_max) / 2
            rounded_min = center - best_interval/2
            rounded_max = center + best_interval/2
            rounded_min = max(self.x_data_range[0], rounded_min)
            rounded_max = min(self.x_data_range[1], rounded_max)
        
        # Apply rounded limits using unified function
        self.set_x_limits(rounded_min, rounded_max)
    
    def pan_horizontal(self, direction):
        """Pan horizontally left (-1) or right (+1)"""
        # Get current limits or set default if none
        if self.current_xlim is None:
            # Set initial zoom for panning (full range)
            current_x_min, current_x_max = self.x_data_range
        else:
            current_x_min, current_x_max = self.current_xlim
            
        range_size = current_x_max - current_x_min
        
        # Pan by 1% of current range
        pan_amount = range_size * 0.01 * direction
        
        new_min = current_x_min + pan_amount
        new_max = current_x_max + pan_amount
        
        # Boundary checking
        if new_min < self.x_data_range[0]:
            new_min = self.x_data_range[0]
            new_max = new_min + range_size
        elif new_max > self.x_data_range[1]:
            new_max = self.x_data_range[1]
            new_min = new_max - range_size
        
        # Apply new limits using unified function
        self.set_x_limits(new_min, new_max)
    
    def get_canvas_size_mm(self):
        """Get the current canvas size in mm"""
        width_inch = self.fig.get_size_inches()[0]
        height_inch = self.fig.get_size_inches()[1]
        # Convert inches to mm (1 inch = 25.4 mm)
        width_mm = width_inch * 25.4
        height_mm = height_inch * 25.4
        return width_mm, height_mm

    def set_custom_margins(self, margins):
        """
        Set custom margins that will be preserved when updating plots.
        
        Args:
            margins (dict): Dictionary containing margin values for left, right, top, bottom, wspace, hspace
        """
        self.custom_margins = margins
        # Apply immediately if we have a figure
        if hasattr(self, 'fig') and self.fig:
            self.fig.subplots_adjust(
                left=margins['left'],
                right=margins['right'],
                top=margins['top'],
                bottom=margins['bottom'],
                wspace=margins['wspace'],
                hspace=margins['hspace']
            )
            self.draw()
            
    def reset_default_margins(self):
        """Reset to use tight_layout instead of custom margins"""
        self.custom_margins = None
        self.fig.tight_layout(pad=2.0)
        self.draw()

    def get_current_margins(self):
        """Get current custom margins or None if using tight_layout"""
        return self.custom_margins
    
    def show_context_menu(self, position):
        """Show context menu when right-clicking on the canvas"""
        # Create context menu
        menu = QMenu(self)
        
        # Add action to show data label for the specific subplot
        action = menu.addAction("Add/Change Data")
        action.triggered.connect(lambda: self.show_signal_selector(position))
        
        menu.exec_(self.mapToGlobal(position))
        
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
    
    def get_existing_signals_for_subplot(self, subplot_index):
        """Get the list of existing signals for a specific subplot"""
        existing_signals = []
        
        if subplot_index < 0 or subplot_index >= len(self.axes):
            return existing_signals
            
        ax = self.axes[subplot_index]
        lines = ax.get_lines()
        
        # Collect all lines from this subplot that are not rectangle selectors
        for line in lines:
            # Skip lines with '_nolegend_' label (these are from rectangle selectors)
            if line.get_label() != '_nolegend_':
                x_data = line.get_xdata()
                y_data = line.get_ydata()
                if len(x_data) > 0 and len(y_data) > 0:
                    # Create a simple representation of the signal
                    signal_data = {
                        'name': line.get_label() if line.get_label() else f'Signal_{subplot_index+1}',
                        'x': x_data,
                        'y': y_data
                    }
                    existing_signals.append(signal_data)
        
        return existing_signals

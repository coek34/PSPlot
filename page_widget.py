# page_widget.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QMessageBox
from PyQt5.QtCore import Qt
from plot_canvas import InteractivePlotCanvas

class PageWidget(QWidget):
    def __init__(self, page_index, width=8.27, height=11.69, parent=None):
        super().__init__(parent)
        self.page_index = page_index
        self.width = width
        self.height = height
        self.plot_canvas = None
        self.page_name = f"Page {page_index + 1}"
        self.subplot_signals = [None] * 6  # Store signals for up to 6 subplots
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create plot canvas
        self.plot_canvas = InteractivePlotCanvas(width=self.width, height=self.height)
        
        # Scroll area for canvas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setStyleSheet("background-color: #f0f0f0;")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.plot_canvas)
        
        layout.addWidget(self.scroll_area)
        
        # Status label
        self.status_label = QLabel(f"{self.page_name}")
        self.status_label.setStyleSheet("QLabel { background-color : #e0e0e0; padding : 5px; }")
        layout.addWidget(self.status_label)
        
    def update_plots(self, subplot_count):
        """Update plots while preserving existing signals"""
        # Store current signals before updating
        if self.plot_canvas and hasattr(self.plot_canvas, 'axes'):
            # Save current signals for each subplot
            for i in range(min(len(self.plot_canvas.axes), 6)):
                if i < len(self.plot_canvas.axes):
                    ax = self.plot_canvas.axes[i]
                    lines = ax.get_lines()
                    if lines:
                        # Store the first line's data as a simple representation
                        line = lines[0]
                        x_data = line.get_xdata()
                        y_data = line.get_ydata()
                        if len(x_data) > 0 and len(y_data) > 0:
                            # Store a simple representation of the signal
                            self.subplot_signals[i] = {
                                'x': x_data,
                                'y': y_data,
                                'label': line.get_label() if line.get_label() else f'Subplot {i+1}'
                            }
        
        # Update the plots
        self.plot_canvas.update_plots(subplot_count)
        
        # Restore signals to new subplots if they exist
        if self.plot_canvas and hasattr(self.plot_canvas, 'axes'):
            for i in range(min(subplot_count, 6)):
                if i < len(self.plot_canvas.axes) and self.subplot_signals[i] is not None:
                    signal_data = self.subplot_signals[i]
                    # Plot the saved signal
                    self.plot_canvas.set_subplot_signal(i, signal_data)
        
    def get_current_margins(self):
        """Get current subplot margins from the figure"""
        try:
            # Get current subplot parameters
            subplot_params = self.plot_canvas.fig.subplotpars
            return {
                'left': subplot_params.left,
                'bottom': subplot_params.bottom,
                'right': subplot_params.right,
                'top': subplot_params.top,
                'wspace': subplot_params.wspace,
                'hspace': subplot_params.hspace
            }
        except:
            # Return default margins if there's an error
            return {'left': 0.125, 'bottom': 0.1, 'right': 0.9, 'top': 0.9, 'wspace': 0.5, 'hspace': 0.5}
    
    # In page_widget.py, modify the adjust_margins method:
    def adjust_margins(self, margins):
        """Adjust margins for this page"""
        try:
            # Update the canvas's custom margins
            self.plot_canvas.set_custom_margins(margins)
            self.plot_canvas.draw()
            
            # Optional: Log current margins
            current = self.plot_canvas.get_current_margins()
            print(f"Current margins: {current}")
        except Exception as e:
            print(f"Margin adjustment error: {e}")
            # Optionally show a message box to user
            QMessageBox.warning(self, "Margin Error", f"Failed to adjust margins: {e}")
            
    def set_subplot_signal(self, subplot_index, signal_data):
        """Set signal data for a specific subplot"""
        self.plot_canvas.set_subplot_signal(subplot_index, signal_data)
        # Also store the signal for preservation
        if 0 <= subplot_index < 6:
            self.subplot_signals[subplot_index] = signal_data

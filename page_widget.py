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
        self.subplot_signals = [[] for _ in range(6)]  # Store lists of signals for up to 6 subplots
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
        # Store current signals before updating - ensure we capture all 6 subplots
        if self.plot_canvas and hasattr(self.plot_canvas, 'axes'):
            # Save current signals for each subplot (up to 6)
            for i in range(6):  # Always check all 6 possible subplots
                if i < len(self.plot_canvas.axes):
                    ax = self.plot_canvas.axes[i]
                    lines = ax.get_lines()
                    # Clear the existing list for this subplot
                    self.subplot_signals[i] = []
                    # Save all lines from this subplot that are not rectangle selectors
                    for line in lines:
                        # Skip lines with '_nolegend_' label (these are from rectangle selectors)
                        if line.get_label() != '_nolegend_':
                            x_data = line.get_xdata()
                            y_data = line.get_ydata()
                            if len(x_data) > 0 and len(y_data) > 0:
                                # Store a representation of the signal with channel/group info if available
                                signal_data = {
                                    'x': x_data,
                                    'y': y_data,
                                    'name': line.get_label() if line.get_label() else f'Signal_{i+1}'
                                }
                                
                                # Try to get channel and group info from the existing signal data
                                if i < len(self.subplot_signals) and self.subplot_signals[i]:
                                    # Look for matching signal in existing signals
                                    for existing_signal in self.subplot_signals[i]:
                                        if existing_signal.get('name') == signal_data['name']:
                                            signal_data['channel_name'] = existing_signal.get('channel_name', 'Unknown')
                                            signal_data['group_name'] = existing_signal.get('group_name', 'Unknown')
                                            break
                                    else:
                                        # If not found, use defaults
                                        signal_data['channel_name'] = 'Unknown'
                                        signal_data['group_name'] = 'Unknown'
                                else:
                                    # Use defaults if no existing signals
                                    signal_data['channel_name'] = 'Unknown'
                                    signal_data['group_name'] = 'Unknown'
                                    
                                self.subplot_signals[i].append(signal_data)
        
        # Update the plots
        self.plot_canvas.update_plots(subplot_count)
        
        # Restore signals to new subplots if they exist
        if self.plot_canvas and hasattr(self.plot_canvas, 'axes'):
            for i in range(min(subplot_count, 6)):
                if i < len(self.plot_canvas.axes) and self.subplot_signals[i]:
                    # Plot all signals for this subplot
                    self.plot_canvas.set_subplot_signals(i, self.subplot_signals[i])
        
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
    
    def adjust_margins(self, margins):
        """Adjust margins for this page"""
        try:
            # Update the canvas's custom margins
            self.plot_canvas.set_custom_margins(margins)
            self.plot_canvas.draw()
        except Exception as e:
            print(f"Margin adjustment error: {e}")
            # Optionally show a message box to user
            QMessageBox.warning(self, "Margin Error", f"Failed to adjust margins: {e}")
            
    def set_subplot_signal(self, subplot_index, signal_data):
        """Set signal data for a specific subplot"""
        self.plot_canvas.set_subplot_signal(subplot_index, signal_data)
        # Also store the signal for preservation
        if 0 <= subplot_index < 6:
            # Preserve channel and group information if available
            if isinstance(signal_data, dict) and 'channel_name' in signal_data and 'group_name' in signal_data:
                self.subplot_signals[subplot_index] = [signal_data]
            else:
                # If no channel/group info, create a minimal structure
                minimal_signal = signal_data.copy() if isinstance(signal_data, dict) else {'name': str(signal_data)}
                minimal_signal['channel_name'] = signal_data.get('channel_name', 'Unknown') if isinstance(signal_data, dict) else 'Unknown'
                minimal_signal['group_name'] = signal_data.get('group_name', 'Unknown') if isinstance(signal_data, dict) else 'Unknown'
                self.subplot_signals[subplot_index] = [minimal_signal]
            
    def set_subplot_signals(self, subplot_index, signal_data_list):
        """Set multiple signals for a specific subplot"""
        self.plot_canvas.set_subplot_signals(subplot_index, signal_data_list)
        # Also store the signals for preservation
        if 0 <= subplot_index < 6:
            # Ensure all signals have channel and group information
            processed_signals = []
            for signal_data in signal_data_list:
                if isinstance(signal_data, dict) and 'channel_name' in signal_data and 'group_name' in signal_data:
                    processed_signals.append(signal_data)
                else:
                    # If no channel/group info, create a minimal structure
                    minimal_signal = signal_data.copy() if isinstance(signal_data, dict) else {'name': str(signal_data)}
                    minimal_signal['channel_name'] = signal_data.get('channel_name', 'Unknown') if isinstance(signal_data, dict) else 'Unknown'
                    minimal_signal['group_name'] = signal_data.get('group_name', 'Unknown') if isinstance(signal_data, dict) else 'Unknown'
                    processed_signals.append(minimal_signal)
            self.subplot_signals[subplot_index] = processed_signals

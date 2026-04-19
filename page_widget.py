# page_widget.py
import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QMessageBox
from PyQt5.QtCore import Qt
from plot_canvas import InteractivePlotCanvas
from theme import get_theme
from settings import PageState

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
        
    def get_state(self) -> PageState:
        """Return a serializable PageState object"""
        logger = logging.getLogger(__name__)
        logger.info(f"Getting state for page '{self.page_name}' (index {self.page_index})")
        
        # Create a lightweight version of subplot_signals without raw data
        serializable_signals = []
        for subplot_idx, subplot in enumerate(self.subplot_signals):
            subplot_list = []
            for signal in subplot:
                if isinstance(signal, dict):
                    # Keep metadata, drop large arrays and absolute file paths
                    sig_ref = {
                        'name': signal.get('name'),
                        'channel_name': signal.get('channel_name'),
                        'group_name': signal.get('group_name')
                    }
                    subplot_list.append(sig_ref)
                    logger.debug(f"  Subplot {subplot_idx}: Saving signal ref (chan-linked) - {sig_ref}")
            serializable_signals.append(subplot_list)
            logger.info(f"  Subplot {subplot_idx}: {len(subplot_list)} signals saved")

        state = PageState(
            name=self.page_name,
            width=self.width,
            height=self.height,
            subplot_count=self.plot_canvas.subplot_count if self.plot_canvas else 1,
            margins=self.get_current_margins(),
            x_limits=list(self.plot_canvas.current_xlim) if self.plot_canvas and self.plot_canvas.current_xlim else None,
            y_labels={int(k): str(v) for k, v in getattr(self.plot_canvas, 'y_labels', {}).items()},
            subplots_signals=serializable_signals
        )
        logger.info(f"Page state created: {state.name}, {len(serializable_signals)} subplots with signals")
        return state
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create plot canvas
        self.plot_canvas = InteractivePlotCanvas(width=self.width, height=self.height)
        
        # Scroll area for canvas
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # Apply theme-aware styling to scroll area background
        theme = get_theme()
        self.scroll_area.setStyleSheet(theme.get_scroll_area_style())
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.plot_canvas)
        
        layout.addWidget(self.scroll_area)
        
        # Status label with theme-aware styling
        self.status_label = QLabel(f"{self.page_name}")
        self.status_label.setStyleSheet(theme.get_status_label_style())
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
        """Set signal data for a specific subplot (handles both single and multiple signals)"""
        # Handle both single signal and list of signals
        if isinstance(signal_data, list):
            # Multiple signals - call set_subplot_signals for the list
            self.plot_canvas.set_subplot_signals(subplot_index, signal_data)
        else:
            # Single signal - convert to list and call set_subplot_signals
            self.plot_canvas.set_subplot_signals(subplot_index, [signal_data])
        
        # Also store the signal(s) for preservation
        if 0 <= subplot_index < 6:
            # Ensure all signals have channel and group information
            processed_signals = []
            if isinstance(signal_data, list):
                # Handle list of signals
                for signal in signal_data:
                    if isinstance(signal, dict) and 'channel_name' in signal and 'group_name' in signal:
                        processed_signals.append(signal)
                    else:
                        # If no channel/group info, create a minimal structure
                        minimal_signal = signal.copy() if isinstance(signal, dict) else {'name': str(signal)}
                        minimal_signal['channel_name'] = signal.get('channel_name', 'Unknown') if isinstance(signal, dict) else 'Unknown'
                        minimal_signal['group_name'] = signal.get('group_name', 'Unknown') if isinstance(signal, dict) else 'Unknown'
                        processed_signals.append(minimal_signal)
            else:
                # Handle single signal
                if isinstance(signal_data, dict) and 'channel_name' in signal_data and 'group_name' in signal_data:
                    processed_signals = [signal_data]
                else:
                    # If no channel/group info, create a minimal structure
                    minimal_signal = signal_data.copy() if isinstance(signal_data, dict) else {'name': str(signal_data)}
                    minimal_signal['channel_name'] = signal_data.get('channel_name', 'Unknown') if isinstance(signal_data, dict) else 'Unknown'
                    minimal_signal['group_name'] = signal_data.get('group_name', 'Unknown') if isinstance(signal_data, dict) else 'Unknown'
                    processed_signals = [minimal_signal]
            
            self.subplot_signals[subplot_index] = processed_signals
    
    def set_subplot_signals(self, subplot_index, signal_data_list):
        """Set multiple signals for a specific subplot"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Get the settings from main_window
        use_group_name = False
        use_channel_name = False
        try:
            if hasattr(self, 'main_window') and self.main_window:
                use_group_name = getattr(self.main_window, 'group_name_in_legend', False)
                use_channel_name = getattr(self.main_window, 'channel_name_in_legend', False)
                logger.info(f"PageWidget: use_channel_name = {use_channel_name}, use_group_name = {use_group_name}")
        except:
            pass
        
        # Pass the settings to canvas
        if self.plot_canvas:
            self.plot_canvas.set_subplot_signals(
                subplot_index, signal_data_list, 
                use_group_name=use_group_name, 
                use_channel_name=use_channel_name
            )
        
        # Also store the signals for preservation
        if 0 <= subplot_index < 6:
            processed_signals = []
            for signal_data in signal_data_list:
                if isinstance(signal_data, dict) and 'channel_name' in signal_data and 'group_name' in signal_data:
                    processed_signals.append(signal_data)
                else:
                    minimal_signal = signal_data.copy() if isinstance(signal_data, dict) else {'name': str(signal_data)}
                    minimal_signal['channel_name'] = signal_data.get('channel_name', 'Unknown') if isinstance(signal_data, dict) else 'Unknown'
                    minimal_signal['group_name'] = signal_data.get('group_name', 'Unknown') if isinstance(signal_data, dict) else 'Unknown'
                    processed_signals.append(minimal_signal)
            self.subplot_signals[subplot_index] = processed_signals

            logger.info(f"Stored {len(processed_signals)} signals in subplot_signals[{subplot_index}]")

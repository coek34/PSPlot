# plot_modules/signal_handler.py
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SignalHandlerMixin:
    """Mixin class for signal-related functionality"""
    
    def set_subplot_signal(self, subplot_index, signal_data):
        """Set a signal to a specific subplot"""
        logger.debug(f"set_subplot_signal called for subplot {subplot_index}")
        if subplot_index < 0 or subplot_index >= len(self.axes):
            logger.debug(f"Invalid subplot index {subplot_index}")
            return
            
        ax = self.axes[subplot_index]
        
        # Clear existing plot
        ax.clear()
        
        # Extract actual signal data if it's wrapped in a nested structure
        if isinstance(signal_data, dict) and 'signal_data' in signal_data:
            actual_signal_data = signal_data['signal_data']
            channel_name = signal_data.get('channel_name', 'Unknown')
            group_name = signal_data.get('group_name', 'Unknown')
        else:
            actual_signal_data = signal_data
            channel_name = signal_data.get('channel_name', 'Unknown')
            group_name = signal_data.get('group_name', 'Unknown')
            
        signal_name = actual_signal_data.get('name', f'Signal_{subplot_index+1}')
        
        # Create label based on group name in legend setting
        # Check if main_window exists and has the flag
        use_group_name = False
        
        # Try to access the flag from different possible locations
        try:
            # Method 1: Direct access to main_window if it exists
            if hasattr(self, 'main_window') and self.main_window is not None:
                if hasattr(self.main_window, 'group_name_in_legend'):
                    use_group_name = self.main_window.group_name_in_legend
                    logger.debug(f"Found flag in main_window: {use_group_name}")
                elif hasattr(self.main_window, 'parent') and self.main_window.parent() is not None:
                    # Try parent if main_window has one
                    parent = self.main_window.parent()
                    if hasattr(parent, 'group_name_in_legend'):
                        use_group_name = parent.group_name_in_legend
                        logger.debug(f"Found flag in parent: {use_group_name}")
            else:
                # Method 2: Try to find it in the widget hierarchy
                widget = self
                while widget is not None:
                    if hasattr(widget, 'group_name_in_legend'):
                        use_group_name = widget.group_name_in_legend
                        logger.debug(f"Found flag in widget hierarchy: {use_group_name}")
                        break
                    widget = widget.parent()
        except Exception as e:
            logger.debug(f"Error accessing group_name_in_legend flag: {e}")
        
        logger.debug(f"Using group name in legend: {use_group_name}")
        
        if use_group_name:
            logger.debug(f"Using group name in legend: group_name={group_name}, signal_name={signal_name}")
            if group_name and group_name != 'Unknown':
                label = f"{group_name}.{signal_name}"
            else:
                label = signal_name
        else:
            logger.debug(f"Not using group name in legend: signal_name={signal_name}")
            label = signal_name
        
        logger.debug(f"Final label for signal: {label}")
        
        # Plot the signal
        if actual_signal_data and 'x' in actual_signal_data and 'y' in actual_signal_data:
            ax.plot(actual_signal_data['x'], actual_signal_data['y'], linewidth=2, label=label)
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
        
        # Use custom y-label if provided, otherwise default to 'Amplitude'
        y_label = getattr(self, 'y_labels', {}).get(subplot_index, 'Amplitude')
        ax.set_ylabel(y_label)
        
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Restore previous y-limits if they exist
        if subplot_index in self.current_ylim_dict:
            ax.set_ylim(self.current_ylim_dict[subplot_index])
        
        # Add rectangle selector for zooming
        selector = self._create_rectangle_selector(ax, subplot_index)
        self.rect_selectors[subplot_index] = selector
        
        self.draw()
        
        # Automatically round x to grid after adding signal
        self.round_x_to_grid()
    
    def set_subplot_signals(self, subplot_index, signal_data_list):
        """Set multiple signals to a specific subplot"""
        logger.debug(f"set_subplot_signals called for subplot {subplot_index} with {len(signal_data_list)} signals")
        if subplot_index < 0 or subplot_index >= len(self.axes):
            logger.debug(f"Invalid subplot index {subplot_index}")
            return
            
        ax = self.axes[subplot_index]
        
        # Clear existing plot
        ax.clear()
        
        # Plot all signals
        if signal_data_list:
            for signal_data in signal_data_list:
                # Extract actual signal data if it's wrapped in a nested structure
                if isinstance(signal_data, dict) and 'signal_data' in signal_data:
                    actual_signal_data = signal_data['signal_data']
                    channel_name = signal_data.get('channel_name', 'Unknown')
                    group_name = signal_data.get('group_name', 'Unknown')
                else:
                    actual_signal_data = signal_data
                    channel_name = signal_data.get('channel_name', 'Unknown')
                    group_name = signal_data.get('group_name', 'Unknown')
                    
                signal_name = actual_signal_data.get('name', f'Signal_{subplot_index+1}')
                
                # Create label based on group name in legend setting
                # Check if main_window exists and has the flag
                use_group_name = False
                
                # Try to access the flag from different possible locations
                try:
                    # Method 1: Direct access to main_window if it exists
                    if hasattr(self, 'main_window') and self.main_window is not None:
                        if hasattr(self.main_window, 'group_name_in_legend'):
                            use_group_name = self.main_window.group_name_in_legend
                            logger.debug(f"Found flag in main_window: {use_group_name}")
                        elif hasattr(self.main_window, 'parent') and self.main_window.parent() is not None:
                            # Try parent if main_window has one
                            parent = self.main_window.parent()
                            if hasattr(parent, 'group_name_in_legend'):
                                use_group_name = parent.group_name_in_legend
                                logger.debug(f"Found flag in parent: {use_group_name}")
                    else:
                        # Method 2: Try to find it in the widget hierarchy
                        widget = self
                        while widget is not None:
                            if hasattr(widget, 'group_name_in_legend'):
                                use_group_name = widget.group_name_in_legend
                                logger.debug(f"Found flag in widget hierarchy: {use_group_name}")
                                break
                            widget = widget.parent()
                except Exception as e:
                    logger.debug(f"Error accessing group_name_in_legend flag: {e}")
                
                logger.debug(f"Using group name in legend: {use_group_name}")
                
                if use_group_name:
                    logger.debug(f"Using group name in legend for signal {signal_name}: group_name={group_name}")
                    if group_name and group_name != 'Unknown':
                        label = f"{group_name}.{signal_name}"
                    else:
                        label = signal_name
                else:
                    logger.debug(f"Not using group name in legend for signal {signal_name}")
                    label = signal_name
                
                logger.debug(f"Plotting signal with label: {label}")
                
                if actual_signal_data and 'x' in actual_signal_data and 'y' in actual_signal_data:
                    ax.plot(actual_signal_data['x'], actual_signal_data['y'], linewidth=2, label=label)
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
        
        # Use custom y-label if provided, otherwise default to 'Amplitude'
        y_label = getattr(self, 'y_labels', {}).get(subplot_index, 'Amplitude')
        ax.set_ylabel(y_label)
        
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Restore previous y-limits if they exist
        if subplot_index in self.current_ylim_dict:
            ax.set_ylim(self.current_ylim_dict[subplot_index])
        
        # Add rectangle selector for zooming
        selector = self._create_rectangle_selector(ax, subplot_index)
        self.rect_selectors[subplot_index] = selector
        
        self.draw()
        
        # Automatically round x to grid after adding signals
        self.round_x_to_grid()
    
    def set_y_label(self, subplot_index, label):
        """Set custom y-label for a specific subplot"""
        if not hasattr(self, 'y_labels'):
            self.y_labels = {}
        self.y_labels[subplot_index] = label
        
        # Update the label immediately if the subplot exists
        if subplot_index < len(self.axes):
            self.axes[subplot_index].set_ylabel(label)
            self.draw()
    
    def _create_rectangle_selector(self, ax, subplot_index):
        """Create a rectangle selector for zooming"""
        from matplotlib.widgets import RectangleSelector
        selector = RectangleSelector(
            ax, self.on_select, useblit=True,
            button=[1], minspanx=5, minspany=5, spancoords='pixels',
            interactive=True
        )
        return selector
    
    def get_existing_signals_for_subplot(self, subplot_index):
        """Get the list of existing signals for a specific subplot with channel/group info"""
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
                    # Try to retrieve channel and group info from the line's properties
                    # We'll store this info in the line's label when plotting
                    signal_name = line.get_label() if line.get_label() else f'Signal_{subplot_index+1}'
                    
                    # Extract channel and group from the signal name if possible
                    # For dummy signals, we can look them up
                    channel_name = 'Unknown'
                    group_name = 'Unknown'
                    
                    # Try to find the signal in our dummy signals to get channel/group info
                    signal_info = self.find_signal_by_name_with_channel(signal_name)
                    if signal_info:
                        channel_name = signal_info['channel_name']
                        group_name = signal_info['group_name']
                    
                    # Create a representation of the signal with channel/group info
                    signal_data = {
                        'name': signal_name,
                        'x': x_data,
                        'y': y_data,
                        'channel_name': channel_name,
                        'group_name': group_name
                    }
                    existing_signals.append(signal_data)
        
        return existing_signals
    
    def find_signal_by_name_with_channel(self, signal_name):
        """Find a signal by name in the dummy signals structure and return with channel info"""
        # Search through all channels
        for channel in self.dummy_signals:
            channel_name = channel['name']
            # Search through all groups in this channel
            for group in channel['groups']:
                group_name = group['name']
                # Search through all signals in this group
                for signal in group['signals']:
                    if signal['name'] == signal_name:
                        return {
                            'signal': signal,
                            'channel_name': channel_name,
                            'group_name': group_name
                        }
        
        # Signal not found
        return None
    
    def find_signal_by_name(self, signal_name, channel_name=None):
        """Find a signal by name in the dummy signals structure"""
        # Search through all channels
        for channel in self.dummy_signals:
            # If channel name is specified, match it
            if channel_name and channel['name'] != channel_name:
                continue
                
            # Search through all groups in this channel
            for group in channel['groups']:
                # Search through all signals in this group
                for signal in group['signals']:
                    if signal['name'] == signal_name:
                        return signal
        
        # Signal not found
        return None

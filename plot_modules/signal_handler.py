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
        # (This remains as fallback for single signals)
        self.set_subplot_signals(subplot_index, [signal_data])
    
    def set_subplot_signals(self, subplot_index, signal_data_list, use_group_name=False, use_channel_name=False):
        """Set multiple signals to a specific subplot"""
        logger.info(f"\n=== SIGNAL HANDLER: set_subplot_signals ===")
        logger.info(f"  Subplot: {subplot_index}, Signals Count: {len(signal_data_list)}")
        if subplot_index < 0 or subplot_index >= len(self.axes):
            return
            
        ax = self.axes[subplot_index]
        ax.clear()
        
        if signal_data_list:
            for signal_data in signal_data_list:
                # Handle potential nesting vs flat data
                if isinstance(signal_data, dict) and 'signal_data' in signal_data:
                    meta = signal_data
                    actual_signal_data = signal_data['signal_data']
                else:
                    meta = signal_data
                    actual_signal_data = signal_data
                
                # Extract metadata with fallback logic
                signal_name = actual_signal_data.get('name') or meta.get('name', f'Signal_{subplot_index+1}')
                channel_name = meta.get('channel_name') or actual_signal_data.get('channel_name', 'Unknown')
                group_name = meta.get('group_name') or actual_signal_data.get('group_name', 'Unknown')
                file_path = meta.get('file_path') or actual_signal_data.get('file_path', '')
                
                logger.debug(f"  Plotting: {signal_name} (Chan: {channel_name}, Group: {group_name})")

                # Build legend label
                parts = []
                if use_channel_name and channel_name and channel_name != 'Unknown':
                    parts.append(str(channel_name))
                if use_group_name and group_name and group_name != 'Unknown':
                    parts.append(str(group_name))
                parts.append(str(signal_name))
                label = '.'.join(parts)
                
                if actual_signal_data and 'x' in actual_signal_data and 'y' in actual_signal_data:
                    line, = ax.plot(actual_signal_data['x'], actual_signal_data['y'], linewidth=2, label=label)
                    # Force set attributes for persistence
                    line._original_signal_name = str(signal_name)
                    line._channel_name = str(channel_name)
                    line._group_name = str(group_name)
                    line._file_path = str(file_path)
                    
                    # Store unit on line for possible later use
                    line._units = str(actual_signal_data.get('units', ''))
        
        # Set axes labels and appearance
        if subplot_index == len(self.axes) - 1:
            ax.set_xlabel('Time (s)')
        else:
            ax.set_xlabel('')
            
        ax.set_title('')
        
        # Determine Y Label: 
        # 1. Use existing manual label if it's not the default 'Amplitude'
        # 2. Otherwise, use the unit of the first signal if available
        # 3. Fallback to 'Amplitude'
        existing_y = getattr(self, 'y_labels', {}).get(subplot_index, 'Amplitude')
        
        if existing_y == 'Amplitude' and signal_data_list:
            # Try to get unit from the first signal in the list
            first_sig = signal_data_list[0]
            # Handle both nested and flat structure
            if isinstance(first_sig, dict):
                unit = first_sig.get('units') or first_sig.get('signal_data', {}).get('units', '')
                if unit:
                    # Update internal y_labels dict and set on axes
                    if not hasattr(self, 'y_labels'): self.y_labels = {}
                    self.y_labels[subplot_index] = str(unit)
                    existing_y = str(unit)

        ax.set_ylabel(existing_y)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)
        
        if subplot_index in self.current_ylim_dict:
            ax.set_ylim(self.current_ylim_dict[subplot_index])
        
        selector = self._create_rectangle_selector(ax, subplot_index)
        self.rect_selectors[subplot_index] = selector
        
        self.draw()
        self.round_x_to_grid()
    
    def set_y_label(self, subplot_index, label):
        """Set custom y-label for a specific subplot"""
        if not hasattr(self, 'y_labels'):
            self.y_labels = {}
        self.y_labels[subplot_index] = label
        if subplot_index < len(self.axes):
            self.axes[subplot_index].set_ylabel(label)
            self.draw()
    
    def _create_rectangle_selector(self, ax, subplot_index):
        from matplotlib.widgets import RectangleSelector
        return RectangleSelector(ax, self.on_select, useblit=True, button=[1], minspanx=5, minspany=5, spancoords='pixels', interactive=True)
    
    def get_existing_signals_for_subplot(self, subplot_index):
        """Get the list of existing signals for a specific subplot with metadata preserved"""
        existing_signals = []
        if subplot_index < 0 or subplot_index >= len(self.axes):
            return existing_signals
            
        ax = self.axes[subplot_index]
        for line in ax.get_lines():
            if line.get_label() != '_nolegend_':
                x_data = line.get_xdata()
                y_data = line.get_ydata()
                if len(x_data) > 0:
                    signal_name = getattr(line, '_original_signal_name', line.get_label())
                    channel_name = getattr(line, '_channel_name', 'Unknown')
                    group_name = getattr(line, '_group_name', 'Unknown')
                    file_path = getattr(line, '_file_path', '')
                    
                    existing_signals.append({
                        'name': signal_name,
                        'x': x_data,
                        'y': y_data,
                        'channel_name': channel_name,
                        'group_name': group_name,
                        'file_path': file_path
                    })
        return existing_signals
    
    def find_signal_by_name_with_channel(self, signal_name):
        """Find a signal by name in the dummy signals structure"""
        for channel in self.dummy_signals:
            for group in channel['groups']:
                for signal in group['signals']:
                    if signal['name'] == signal_name:
                        return {'signal': signal, 'channel_name': channel['name'], 'group_name': group['name']}
        return None
    
    def find_signal_by_name(self, signal_name, channel_name=None):
        for channel in self.dummy_signals:
            if channel_name and channel['name'] != channel_name: continue
            for group in channel['groups']:
                for signal in group['signals']:
                    if signal['name'] == signal_name: return signal
        return None

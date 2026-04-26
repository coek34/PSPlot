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
        self.set_subplot_signals(subplot_index, [signal_data])

    def set_subplot_signals(self, subplot_index, signal_data_list, use_group_name=False, use_channel_name=False):
        """Set signals for a subplot. Pass empty list to clear all signals."""
        import logging
        logger = logging.getLogger(__name__)
        
        if subplot_index < 0 or subplot_index >= len(self.axes):
            return
            
        ax = self.axes[subplot_index]
        
        # 1. VISUAL CLEAR: Always clear the axes assets
        ax.clear()
        
        # Deep cleaning of all matplotlib internal lists for this axes
        for attr in ['lines', 'patches', 'collections', 'artists']:
            if hasattr(ax, attr):
                coll = getattr(ax, attr)
                while coll:
                    coll[0].remove()
        
        if ax.get_legend():
            ax.get_legend().remove()

        # 2. SHORT CIRCUIT FOR EMPTY LIST:
        if not signal_data_list:
            ax.set_ylabel(getattr(self, 'y_labels', {}).get(subplot_index, 'Amplitude'))
            ax.grid(True, alpha=0.3)
            self.draw()
            return

        # 3. PLOTTING LOGIC
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
                scale = actual_signal_data.get('scale', 1.0) if isinstance(actual_signal_data, dict) else getattr(actual_signal_data, 'scale', 1.0)
                
                logger.debug(f"  Plotting: {signal_name} (Chan: {channel_name}, Group: {group_name}, Scale: {scale})")

                # Build legend label
                parts = []
                if use_channel_name and channel_name and channel_name != 'Unknown':
                    parts.append(str(channel_name))
                if use_group_name and group_name and group_name != 'Unknown':
                    parts.append(str(group_name))
                parts.append(str(signal_name))
                
                # Add scale to label if not 1.0
                label = '.'.join(parts)
                if scale != 1.0:
                    label += f" (x{scale})"
                
                if actual_signal_data and 'x' in actual_signal_data and 'y' in actual_signal_data:
                    # Apply scaling to the Y data for visualization
                    line, = ax.plot(actual_signal_data['x'], actual_signal_data['y'] * scale, linewidth=2, label=label)
                    
                    # Force set attributes for persistence
                    setattr(line, '_original_signal_name', str(signal_name))
                    setattr(line, '_channel_name', str(channel_name))
                    setattr(line, '_group_name', str(group_name))
                    setattr(line, '_file_path', str(file_path))
                    setattr(line, '_scale', float(scale))
                    setattr(line, '_units', str(actual_signal_data.get('units', '')))
                    
                    logger.debug(f"  Metadata attached to line: {signal_name} (Chan: {channel_name})")
        
        # Set axes labels and appearance
        if subplot_index == len(self.axes) - 1:
            ax.set_xlabel('Time (s)')
        else:
            ax.set_xlabel('')
            
        ax.set_title('')
        
        # Determine Y Label
        existing_y = getattr(self, 'y_labels', {}).get(subplot_index, 'Amplitude')
        
        if existing_y in ['Amplitude', ''] and signal_data_list:
            first_sig = signal_data_list[0]
            if isinstance(first_sig, dict):
                unit = first_sig.get('units') or first_sig.get('signal_data', {}).get('units', '')
                if unit:
                    if not hasattr(self, 'y_labels'): self.y_labels = {}
                    self.y_labels[subplot_index] = str(unit)
                    existing_y = str(unit)
        elif not signal_data_list:
            # If no signals, reset label to Amplitude or empty
            existing_y = 'Amplitude'
            if not hasattr(self, 'y_labels'): self.y_labels = {}
            self.y_labels[subplot_index] = 'Amplitude'

        ax.set_ylabel(existing_y)
        
        # Only show legend if there are signals
        if signal_data_list:
            ax.legend(fontsize=8, loc='upper right')
        else:
            leg = ax.get_legend()
            if leg:
                leg.remove()
                
        ax.grid(True, alpha=0.3)
        
        if subplot_index in self.current_ylim_dict:
            ax.set_ylim(self.current_ylim_dict[subplot_index])
        
        selector = self._create_rectangle_selector(ax, subplot_index)
        if getattr(self, 'cursors_active', False):
            selector.set_active(False)
        self.rect_selectors[subplot_index] = selector
        
        self.draw()
        try:
            # Check if method exists in the target class
            if hasattr(self, 'round_x_to_grid'):
                self.round_x_to_grid()
        except Exception:
            pass
    
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
                # We need the original unscaled Y data if possible, or just the scale factor
                # Here we retrieve the attributes we stored
                signal_name = getattr(line, '_original_signal_name', line.get_label())
                
                # If the label contains the scale string, strip it to get the pure name for matching
                if " (x" in signal_name:
                    signal_name = signal_name.split(" (x")[0]
                
                channel_name = getattr(line, '_channel_name', 'Unknown')
                group_name = getattr(line, '_group_name', 'Unknown')
                file_path = getattr(line, '_file_path', '')
                scale = getattr(line, '_scale', 1.0)
                units = getattr(line, '_units', '')
                
                x_data = np.asarray(line.get_xdata())
                y_data_plotted = np.asarray(line.get_ydata())
                
                # Retrieve original data by reversing scale if we only have plotted data
                y_data_original = y_data_plotted / scale if scale != 0 else y_data_plotted
                
                existing_signals.append({
                    'name': signal_name,
                    'x': x_data,
                    'y': y_data_original,
                    'channel_name': channel_name,
                    'group_name': group_name,
                    'file_path': file_path,
                    'scale': scale,
                    'units': units
                })
        return existing_signals

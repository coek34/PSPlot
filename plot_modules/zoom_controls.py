# plot_modules/zoom_controls.py
import numpy as np

class ZoomControlMixin:
    """Mixin class for zoom and pan controls"""
    
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

# plot_modules/layout_manager.py

class LayoutManagerMixin:
    """Mixin class for layout and margin management"""
    
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

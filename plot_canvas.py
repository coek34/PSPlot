# plot_canvas.py
from plot_modules.canvas_base import BaseInteractiveCanvas
from plot_modules.signal_handler import SignalHandlerMixin
from plot_modules.zoom_controls import ZoomControlMixin
from plot_modules.layout_manager import LayoutManagerMixin

class InteractivePlotCanvas(BaseInteractiveCanvas, SignalHandlerMixin, ZoomControlMixin, LayoutManagerMixin):
    def __init__(self, parent=None, width=8.27, height=11.69):
        super().__init__(parent, width, height)
        # Create initial plots
        self.update_plots(1)

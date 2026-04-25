# plot_canvas.py
from psplot.plot_modules.canvas_base import BaseInteractiveCanvas
from psplot.plot_modules.signal_handler import SignalHandlerMixin
from psplot.plot_modules.zoom_controls import ZoomControlMixin
from psplot.plot_modules.layout_manager import LayoutManagerMixin

class InteractivePlotCanvas(BaseInteractiveCanvas, SignalHandlerMixin, ZoomControlMixin, LayoutManagerMixin):
    def __init__(self, parent=None, width=8.27, height=11.69):
        super().__init__(parent, width, height)
        # Create initial plots
        self.update_plots(1)

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from PyQt5.QtWidgets import QApplication
from plot_modules.canvas_base import BaseInteractiveCanvas

def test_blank_subplots():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    canvas = BaseInteractiveCanvas(width=5, height=4)
    # Initially, we have 1 subplot by default
    assert len(canvas.axes) == 1
    ax = canvas.axes[0]
    # There should be no lines plotted (since we removed the dummy plot)
    lines = ax.get_lines()
    assert len(lines) == 0, f"Expected 0 lines, got {len(lines)}: {lines}"

    # Change subplot count to 3
    canvas.update_plots(3)
    assert len(canvas.axes) == 3
    for i, ax in enumerate(canvas.axes):
        lines = ax.get_lines()
        assert len(lines) == 0, f"Subplot {i} has {len(lines)} lines: {lines}"

    print("Test passed: subplots are blank when no signals are set.")

if __name__ == '__main__':
    test_blank_subplots()
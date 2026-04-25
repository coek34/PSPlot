from PyQt5.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

class MarginDialog(QDialog):
    def __init__(self, parent=None, current_margins=None):
        super().__init__(parent)
        self.setWindowTitle("Adjust Plot Margins")
        self.setModal(True)
        self.current_margins = current_margins or {'left': 0.125, 'bottom': 0.1, 'right': 0.9, 'top': 0.9, 'wspace': 0.5, 'hspace': 0.5}
        self.setup_ui()
        
    def setup_ui(self):
        from core.theme import get_theme
        theme = get_theme()
        
        layout = QFormLayout()
        
        # Get current margins for default values
        current = self.current_margins
        
        # Margin settings with percentage values (0.0 to 1.0)
        self.left_margin = QDoubleSpinBox()
        self.left_margin.setRange(0, 1.0)
        self.left_margin.setDecimals(3)
        self.left_margin.setSingleStep(0.01)
        self.left_margin.setValue(current['left'])
        layout.addRow("Left Margin (0-1):", self.left_margin)
        
        self.right_margin = QDoubleSpinBox()
        self.right_margin.setRange(0, 1.0)
        self.right_margin.setDecimals(3)
        self.right_margin.setSingleStep(0.01)
        self.right_margin.setValue(current['right'])
        layout.addRow("Right Margin (0-1):", self.right_margin)
        
        self.top_margin = QDoubleSpinBox()
        self.top_margin.setRange(0, 1.0)
        self.top_margin.setDecimals(3)
        self.top_margin.setSingleStep(0.01)
        self.top_margin.setValue(current['top'])
        layout.addRow("Top Margin (0-1):", self.top_margin)
        
        self.bottom_margin = QDoubleSpinBox()
        self.bottom_margin.setRange(0, 1.0)
        self.bottom_margin.setDecimals(3)
        self.bottom_margin.setSingleStep(0.01)
        self.bottom_margin.setValue(current['bottom'])
        layout.addRow("Bottom Margin (0-1):", self.bottom_margin)
        
        self.subplot_spacing = QDoubleSpinBox()
        self.subplot_spacing.setRange(0, 1.0)
        self.subplot_spacing.setDecimals(3)
        self.subplot_spacing.setSingleStep(0.01)
        self.subplot_spacing.setValue(current['wspace'])
        layout.addRow("Subplot Spacing (0-1):", self.subplot_spacing)
        
         # ADD THIS NEW SPINBOX FOR HSPACE
        self.hspace = QDoubleSpinBox()
        self.hspace.setRange(0, 1.0)
        self.hspace.setDecimals(3)
        self.hspace.setSingleStep(0.01)
        self.hspace.setValue(current['hspace'])
        layout.addRow("Horizontal Spacing (0-1):", self.hspace)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        ok_button.setStyleSheet(theme.get_button_ok_style())
        cancel_button.setStyleSheet(theme.get_button_cancel_style())
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addRow(button_layout)
        reset_button = QPushButton("Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_button)
        
        self.setLayout(layout)
        self.setStyleSheet(theme.get_style_sheet())
        
    def get_margins(self):
        # Add validation to ensure margins are within reasonable bounds
        margins = {
            'left': max(0.0, min(1.0, self.left_margin.value())),
            'right': max(0.0, min(1.0, self.right_margin.value())),
            'top': max(0.0, min(1.0, self.top_margin.value())),
            'bottom': max(0.0, min(1.0, self.bottom_margin.value())),
            'wspace': max(0.0, min(1.0, self.subplot_spacing.value())),
            'hspace': max(0.0, min(1.0, self.hspace.value()))
        }
        return margins
        
    def reset_to_defaults(self):
        """Reset margins to default values"""
        self.left_margin.setValue(0.125)
        self.right_margin.setValue(0.9)
        self.top_margin.setValue(0.9)
        self.bottom_margin.setValue(0.1)
        self.subplot_spacing.setValue(0.5)
        self.hspace.setValue(0.5)


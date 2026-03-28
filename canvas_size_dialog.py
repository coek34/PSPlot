# canvas_size_dialog.py
from PyQt5.QtWidgets import QDialog, QFormLayout, QComboBox, QPushButton, QHBoxLayout, QDoubleSpinBox, QLabel, QWidget
from PyQt5.QtCore import Qt

class CanvasSizeDialog(QDialog):
    def __init__(self, parent=None, current_size_mm=None):
        super().__init__(parent)
        self.setWindowTitle("Select Canvas Size")
        self.setModal(True)
        self.resize(300, 200)
        
        self.current_size_mm = current_size_mm or (210, 297)  # Default to A4 portrait
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QFormLayout()
        
        # Predefined sizes
        sizes = [
            ("A4 Portrait", 210, 297),
            ("A4 Landscape", 297, 210),
            ("A3 Portrait", 297, 420),
            ("A3 Landscape", 420, 297),
            ("A5 Portrait", 148, 210),
            ("A5 Landscape", 210, 148),
            ("Custom", 0, 0)  # Custom size
        ]
        
        self.size_combo = QComboBox()
        for name, width, height in sizes:
            self.size_combo.addItem(name)
        
        # Set default selection to "Custom"
        self.size_combo.setCurrentText("Custom")
        self.size_combo.currentTextChanged.connect(self.on_size_changed)
        layout.addRow("Size:", self.size_combo)
        
        # Custom size inputs
        self.custom_widget = QWidget()
        self.custom_layout = QFormLayout(self.custom_widget)
        
        # Width input
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setDecimals(1)
        self.width_spin.setValue(self.current_size_mm[0])
        self.width_spin.setSuffix(" mm")
        self.custom_layout.addRow("Width:", self.width_spin)
        
        # Height input
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setDecimals(1)
        self.height_spin.setValue(self.current_size_mm[1])
        self.height_spin.setSuffix(" mm")
        self.custom_layout.addRow("Height:", self.height_spin)
        
        layout.addRow(self.custom_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addRow(button_layout)
        
        self.setLayout(layout)
        
        # Initially hide custom size inputs (this will be handled by on_size_changed)
        self.custom_widget.setHidden(False)
        
    def on_size_changed(self, text):
        """Handle size selection change"""
        if text == "Custom":
            self.custom_widget.setHidden(False)
        else:
            self.custom_widget.setHidden(True)
            # Set custom spinboxes to predefined values
            sizes = {
                "A4 Portrait": (210, 297),
                "A4 Landscape": (297, 210),
                "A3 Portrait": (297, 420),
                "A3 Landscape": (420, 297),
                "A5 Portrait": (148, 210),
                "A5 Landscape": (210, 148)
            }
            if text in sizes:
                width, height = sizes[text]
                self.width_spin.setValue(width)
                self.height_spin.setValue(height)
    
    def get_selected_size(self):
        """Get the selected size in inches for matplotlib"""
        size_text = self.size_combo.currentText()
        
        if size_text == "Custom":
            width_mm = self.width_spin.value()
            height_mm = self.height_spin.value()
        else:
            sizes = {
                "A4 Portrait": (210, 297),
                "A4 Landscape": (297, 210),
                "A3 Portrait": (297, 420),
                "A3 Landscape": (420, 297),
                "A5 Portrait": (148, 210),
                "A5 Landscape": (210, 148)
            }
            width_mm, height_mm = sizes[size_text]
        
        # Convert mm to inches (1 inch = 25.4 mm)
        width_inch = width_mm / 25.4
        height_inch = height_mm / 25.4
        
        return width_inch, height_inch

# filter_dialog.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QDoubleSpinBox, QSpinBox, QPushButton,
                             QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt
import theme
from filter_manager import FilterApplier

class FilterDialog(QDialog):
    def __init__(self, available_signals, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter Signal tool - PSPlot")
        self.setMinimumWidth(400)
        self.available_signals = available_signals
        self.result_signal = None
        
        self.setup_ui()
    
    def setup_ui(self):
        current_theme = theme.get_theme()
        layout = QVBoxLayout(self)
        
        # 1. Signal Selection
        sel_group = QGroupBox("Signal Selection")
        sel_layout = QFormLayout()
        
        self.signal_combo = QComboBox()
        for idx, sig in enumerate(self.available_signals):
            label = f"[{sig.get('channel_name')}] {sig.get('name')}"
            self.signal_combo.addItem(label, idx)
        
        sel_layout.addRow("Target Signal:", self.signal_combo)
        sel_group.setLayout(sel_layout)
        layout.addWidget(sel_group)
        
        # 2. Filter Parameters
        param_group = QGroupBox("Filter Configuration")
        self.param_layout = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Butterworth Low-pass", "Butterworth High-pass", "Moving Average"])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        
        self.cutoff_spin = QDoubleSpinBox()
        self.cutoff_spin.setRange(0.1, 1000000.0)
        self.cutoff_spin.setValue(50.0)
        self.cutoff_spin.setSuffix(" Hz")
        
        self.order_spin = QSpinBox()
        self.order_spin.setRange(1, 10)
        self.order_spin.setValue(4)
        
        self.window_spin = QSpinBox()
        self.window_spin.setRange(2, 10000)
        self.window_spin.setValue(100)
        self.window_spin.setSuffix(" samples")
        self.window_spin.setVisible(False)
        
        self.param_layout.addRow("Filter Type:", self.type_combo)
        self.param_layout.addRow("Cutoff Freq:", self.cutoff_spin)
        self.param_layout.addRow("Filter Order:", self.order_spin)
        self.param_layout.addRow("Window Size:", self.window_spin)
        
        param_group.setLayout(self.param_layout)
        layout.addWidget(param_group)
        
        # 3. Destination
        dest_group = QGroupBox("Output")
        dest_layout = QFormLayout()
        self.dest_combo = QComboBox()
        self.dest_combo.addItems(["Current Subplot", "New Subplot (if space)"])
        dest_layout.addRow("Destination:", self.dest_combo)
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)
        
        # Help text
        help_label = QLabel("Note: Filters use Zero-Phase (sosfiltfilt) to prevent time delay.")
        help_label.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        layout.addWidget(help_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Apply Filter")
        self.apply_btn.clicked.connect(self.on_apply)
        self.apply_btn.setStyleSheet(current_theme.get_button_ok_style())
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(current_theme.get_button_cancel_style())
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setStyleSheet(current_theme.get_style_sheet())
        
    def on_type_changed(self, index):
        is_ma = (index == 2)
        self.cutoff_spin.setVisible(not is_ma)
        self.order_spin.setVisible(not is_ma)
        self.window_spin.setVisible(is_ma)
        
        # Toggle label visibility is tricky in QFormLayout, so we just hide the widgets
        self.param_layout.labelForField(self.cutoff_spin).setVisible(not is_ma)
        self.param_layout.labelForField(self.order_spin).setVisible(not is_ma)
        self.param_layout.labelForField(self.window_spin).setVisible(is_ma)

    def on_apply(self):
        sig_idx = self.signal_combo.currentData()
        source_sig = self.available_signals[sig_idx]
        
        x = source_sig['x']
        y = source_sig['y']
        
        filter_type = self.type_combo.currentText()
        
        if "Butterworth" in filter_type:
            fs = FilterApplier.estimate_sampling_frequency(x)
            btype = 'low' if 'Low-pass' in filter_type else 'high'
            y_filtered = FilterApplier.apply_butterworth(
                y, fs, self.cutoff_spin.value(), self.order_spin.value(), btype
            )
            suffix = f"_LPF{int(self.cutoff_spin.value())}" if btype == 'low' else f"_HPF{int(self.cutoff_spin.value())}"
        else:
            y_filtered = FilterApplier.apply_moving_average(y, self.window_spin.value())
            suffix = f"_MA{self.window_spin.value()}"
            
        self.result_signal = {
            'x': x,
            'y': y_filtered,
            'name': f"{source_sig['name']}{suffix}",
            'channel_name': source_sig['channel_name'],
            'group_name': "Filters",
            'units': source_sig.get('units', ''),
            'file_path': source_sig.get('file_path', ''),
            'scale': source_sig.get('scale', 1.0),
            'destination': self.dest_combo.currentIndex() # 0: current, 1: new
        }
        
        self.accept()

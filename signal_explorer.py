# signal_explorer.py
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                            QTreeWidgetItem, QPushButton, QSplitter, QLabel,
                            QCheckBox, QGroupBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class SignalExplorerDialog(QDialog):
    signal_selected = pyqtSignal(str, str)  # signal_name, channel_label
    
    def __init__(self, imported_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Signal Explorer")
        self.setModal(True)
        self.resize(800, 600)
        
        # Store imported data
        self.imported_data = imported_data or []
        
        self.selected_signals = []
        self.setup_ui()
        self.populate_tree()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Signal tree
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        tree_label = QLabel("Available Signals")
        tree_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(tree_label)
        
        self.signal_tree = QTreeWidget()
        self.signal_tree.setHeaderLabels(["Signals"])
        self.signal_tree.setRootIsDecorated(True)
        self.signal_tree.setAlternatingRowColors(True)
        self.signal_tree.itemDoubleClicked.connect(self.on_signal_double_clicked)
        
        left_layout.addWidget(self.signal_tree)
        
        # Right panel - Selected signals
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        selected_label = QLabel("Selected Signals")
        selected_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(selected_label)
        
        self.selected_signals_list = QTreeWidget()
        self.selected_signals_list.setHeaderLabels(["Signal"])
        self.selected_signals_list.setRootIsDecorated(False)
        self.selected_signals_list.setAlternatingRowColors(True)
        # Connect double-click to remove signal
        self.selected_signals_list.itemDoubleClicked.connect(self.on_selected_signal_double_clicked)
        
        right_layout.addWidget(self.selected_signals_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        clear_button = QPushButton("Clear Selected")
        clear_button.clicked.connect(self.clear_selected_signals)
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
        layout.addLayout(button_layout)
        
    def populate_tree(self):
        """Populate the signal tree with available signals from imported data"""
        self.signal_tree.clear()
        
        # Create a "Dummy" parent node
        dummy_parent = QTreeWidgetItem(self.signal_tree, ["Dummy"])
        dummy_parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        dummy_parent.setExpanded(True)  # Expand by default
        
        # Process each imported signal and add to dummy parent
        for i, signal_data in enumerate(self.imported_data):
            if not signal_data.get('name'):
                continue
                
            signal_name = signal_data['name']
            signal_item = QTreeWidgetItem(dummy_parent, [signal_name])
            signal_item.setData(0, Qt.UserRole, signal_data)  # Store signal data
        
        # Expand all items
        self.signal_tree.expandAll()
        
    def on_signal_double_clicked(self, item, column):
        """Handle double-click on signal item"""
        # Only process if it's a child of the dummy parent (not the parent itself)
        if item.parent() is not None and item.parent().text(0) == "Dummy":
            # This is a signal item
            signal_data = item.data(0, Qt.UserRole)
            if signal_data:
                # Add to selected signals list
                self.add_to_selected_signals(item.text(0), signal_data)
    
    def on_selected_signal_double_clicked(self, item, column):
        """Handle double-click on selected signal - remove it"""
        # Remove the item from the selected signals list
        self.selected_signals_list.takeTopLevelItem(self.selected_signals_list.indexOfTopLevelItem(item))
    
    def add_to_selected_signals(self, signal_name, signal_data):
        """Add signal to selected signals list"""
        # Check if signal already exists
        for i in range(self.selected_signals_list.topLevelItemCount()):
            existing_item = self.selected_signals_list.topLevelItem(i)
            if existing_item.text(0) == signal_name:
                return  # Already selected
        
        # Add to selected list
        selected_item = QTreeWidgetItem(self.selected_signals_list, [signal_name])
        selected_item.setData(0, Qt.UserRole, signal_data)
    
    def clear_selected_signals(self):
        """Clear all selected signals"""
        self.selected_signals_list.clear()
    
    def get_selected_signals(self):
        """Get the list of selected signals"""
        signals = []
        for i in range(self.selected_signals_list.topLevelItemCount()):
            item = self.selected_signals_list.topLevelItem(i)
            signal_data = item.data(0, Qt.UserRole)
            if signal_data:
                signals.append(signal_data)
        return signals
    
    def accept(self):
        """Handle dialog accept"""
        selected_signals = self.get_selected_signals()
        if selected_signals:
            # Emit signal for each selected signal
            for signal_data in selected_signals:
                self.signal_selected.emit(signal_data['name'], signal_data['name'])
        super().accept()

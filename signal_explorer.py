# signal_explorer.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                            QTreeWidgetItem, QPushButton, QSplitter, QLabel,
                            QCheckBox, QGroupBox, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class SignalExplorerDialog(QDialog):
    signal_selected = pyqtSignal(str, str)  # signal_name, channel_label
    
    def __init__(self, imported_data, existing_signals=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Signal Explorer")
        self.setModal(True)
        self.resize(800, 600)
        
        # Store imported data
        self.imported_data = imported_data or []
        self.existing_signals = existing_signals or []
        
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
        # Disable multi-selection - only allow single selection
        self.signal_tree.setSelectionMode(QTreeWidget.SingleSelection)
        
        left_layout.addWidget(self.signal_tree)
        
        # Right panel - Selected signals (with same hierarchical structure)
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        selected_label = QLabel("Currently Plotted Signals")
        selected_label.setFont(QFont("Arial", 10, QFont.Bold))
        right_layout.addWidget(selected_label)
        
        self.selected_signals_tree = QTreeWidget()
        self.selected_signals_tree.setHeaderLabels(["Signals"])
        self.selected_signals_tree.setRootIsDecorated(True)
        self.selected_signals_tree.setAlternatingRowColors(True)
        # Connect double-click to remove signal
        self.selected_signals_tree.itemDoubleClicked.connect(self.on_selected_signal_double_clicked)
        
        right_layout.addWidget(self.selected_signals_tree)
        
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
        """Populate the signal tree with available signals organized in channels, groups, and signals"""
        self.signal_tree.clear()
        
        # Process each imported signal and organize by channel -> group -> signal
        for channel_data in self.imported_data:
            # Create channel parent node
            channel_name = channel_data['name']
            channel_parent = QTreeWidgetItem(self.signal_tree, [channel_name])
            channel_parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            channel_parent.setExpanded(True)
            
            # Add groups to channel
            for group_data in channel_data['groups']:
                group_name = group_data['name']
                group_parent = QTreeWidgetItem(channel_parent, [group_name])
                group_parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                group_parent.setExpanded(True)
                
                # Add signals to group
                for signal_data in group_data['signals']:
                    signal_name = signal_data['name']
                    signal_item = QTreeWidgetItem(group_parent, [signal_name])
                    # Store channel and group information along with signal data
                    signal_item.setData(0, Qt.UserRole, {
                        'signal_data': signal_data,
                        'channel_name': channel_name,
                        'group_name': group_name
                    })
        
        # Expand all items
        self.signal_tree.expandAll()
        
        # Add existing signals to the selected list with same hierarchical structure
        self.populate_selected_signals()
    
    def populate_selected_signals(self):
        """Populate the selected signals tree with existing signals organized in same hierarchy"""
        self.selected_signals_tree.clear()
        
        # Create a mapping of existing signals by channel and group for easier organization
        signal_mapping = {}
        for signal_data in self.existing_signals:
            # For existing signals, we'll create a simple structure
            # Since we don't have channel/group info for existing signals, we'll put them in a "Current" channel
            channel_name = "Current"
            if channel_name not in signal_mapping:
                signal_mapping[channel_name] = {'groups': {}}
            
            group_name = "Selected"
            if group_name not in signal_mapping[channel_name]['groups']:
                signal_mapping[channel_name]['groups'][group_name] = []
            
            signal_mapping[channel_name]['groups'][group_name].append(signal_data)
        
        # Add the existing signals to the tree with hierarchical structure
        for channel_name, channel_data in signal_mapping.items():
            channel_parent = QTreeWidgetItem(self.selected_signals_tree, [channel_name])
            channel_parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            channel_parent.setExpanded(True)
            
            for group_name, signals in channel_data['groups'].items():
                group_parent = QTreeWidgetItem(channel_parent, [group_name])
                group_parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                group_parent.setExpanded(True)
                
                for signal_data in signals:
                    signal_name = signal_data['name']
                    signal_item = QTreeWidgetItem(group_parent, [signal_name])
                    signal_item.setData(0, Qt.UserRole, {
                        'signal_data': signal_data,
                        'channel_name': channel_name,
                        'group_name': group_name
                    })
        
        # Expand all items in selected signals tree
        self.selected_signals_tree.expandAll()
    
    def on_signal_double_clicked(self, item, column):
        """Handle double-click on signal item"""
        # Only process if it's a child of a group parent (not the channel or group parent itself)
        if item.parent() is not None and item.parent().parent() is not None:
            # This is a signal item
            signal_data = item.data(0, Qt.UserRole)
            if signal_data:
                # Add to selected signals tree with hierarchical structure
                self.add_to_selected_signals(item.text(0), signal_data)
    
    def on_selected_signal_double_clicked(self, item, column):
        """Handle double-click on selected signal - remove it"""
        # Remove the item from the selected signals tree
        parent = item.parent()
        if parent:
            # Remove the item from its parent
            parent.removeChild(item)
        else:
            # If it's a top-level item, remove from the tree
            self.selected_signals_tree.takeTopLevelItem(self.selected_signals_tree.indexOfTopLevelItem(item))
    
    def add_to_selected_signals(self, signal_name, signal_data):
        """Add signal to selected signals tree with hierarchical structure"""
        # Extract channel and group information
        channel_name = signal_data['channel_name']
        group_name = signal_data['group_name']
        signal_info = signal_data['signal_data']
        
        # Create a hierarchical structure for the selected signal
        # Find or create channel parent
        channel_parent = None
        for i in range(self.selected_signals_tree.topLevelItemCount()):
            if self.selected_signals_tree.topLevelItem(i).text(0) == channel_name:
                channel_parent = self.selected_signals_tree.topLevelItem(i)
                break
        
        if not channel_parent:
            channel_parent = QTreeWidgetItem(self.selected_signals_tree, [channel_name])
            channel_parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            channel_parent.setExpanded(True)
        
        # Find or create group parent
        group_parent = None
        for i in range(channel_parent.childCount()):
            if channel_parent.child(i).text(0) == group_name:
                group_parent = channel_parent.child(i)
                break
        
        if not group_parent:
            group_parent = QTreeWidgetItem(channel_parent, [group_name])
            group_parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            group_parent.setExpanded(True)
        
        # Add signal to group
        signal_item = QTreeWidgetItem(group_parent, [signal_name])
        signal_item.setData(0, Qt.UserRole, signal_data)
        
        # Expand the tree
        self.selected_signals_tree.expandAll()
    
    def clear_selected_signals(self):
        """Clear all selected signals"""
        self.selected_signals_tree.clear()
    
    def get_selected_signals(self):
        """Get the list of selected signals"""
        signals = []
        
        # Recursively collect signals from the tree structure
        def collect_signals_from_tree(parent_item):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                # If this is a leaf node (signal), get its data
                if child.childCount() == 0:
                    signal_data = child.data(0, Qt.UserRole)
                    if signal_data:
                        signals.append(signal_data)
                else:
                    # Recursively process child nodes
                    collect_signals_from_tree(child)
        
        # Process all top-level items
        for i in range(self.selected_signals_tree.topLevelItemCount()):
            collect_signals_from_tree(self.selected_signals_tree.topLevelItem(i))
        
        # Extract actual signal data from the nested structure for proper plotting
        actual_signals = []
        for signal_data in signals:
            # Check if it's already in the correct format (no nested 'signal_data' key)
            if 'signal_data' in signal_data and isinstance(signal_data['signal_data'], dict):
                # This is the nested format - extract the actual signal data
                actual_signal_data = signal_data['signal_data']
                actual_signal_data['channel_name'] = signal_data['channel_name']
                actual_signal_data['group_name'] = signal_data['group_name']
                actual_signals.append(actual_signal_data)
            else:
                # This is already the correct format
                actual_signals.append(signal_data)
        
        return actual_signals
    
    def accept(self):
        """Handle dialog accept"""
        selected_signals = self.get_selected_signals()
        print(f"DEBUG: Selected signals in dialog: {selected_signals}")
        if selected_signals:
            # Emit signal for each selected signal with channel and group info
            for signal_data in selected_signals:
                # Extract the actual signal data
                if 'signal_data' in signal_data and isinstance(signal_data['signal_data'], dict):
                    # Nested format - extract the actual signal data
                    actual_signal_data = signal_data['signal_data']
                    channel_name = signal_data['channel_name']
                    group_name = signal_data['group_name']
                else:
                    # Direct format
                    actual_signal_data = signal_data
                    channel_name = signal_data.get('channel_name', 'Unknown')
                    group_name = signal_data.get('group_name', 'Unknown')
                
                signal_name = actual_signal_data['name']
                print(f"DEBUG: Emitting signal - Name: {signal_name}, Channel: {channel_name}")
                # Emit with signal name and channel name
                self.signal_selected.emit(signal_name, channel_name)
        # Call parent accept to close dialog
        super().accept()

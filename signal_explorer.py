# signal_explorer.py
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                            QTreeWidgetItem, QPushButton, QSplitter, QLabel,
                            QFrame, QMenuBar, QAction, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from theme import get_theme, get_colors

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
        
        # Get theme colors
        c = get_colors()
        
        # Search area
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter signals by name...")
        self.search_input.textChanged.connect(self.filter_signals)
        
        # Style search input
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c.alt};
                color: {c.text};
                border: 1px solid {c.border_light};
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Signal tree
        left_panel = QFrame()
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        left_panel.setFrameShape(QFrame.NoFrame)  # Removes the border
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {c.base};  /* Match the theme */
                border: none;                     /* Explicitly remove border */
            }}
        """)
        
        self.signal_tree = QTreeWidget()
        self.signal_tree.setHeaderLabels(["Available Signals"])
        self.signal_tree.setRootIsDecorated(True)
        self.signal_tree.setAlternatingRowColors(True)
        self.signal_tree.itemDoubleClicked.connect(self.on_signal_double_clicked)
        # Disable multi-selection - only allow single selection
        self.signal_tree.setSelectionMode(QTreeWidget.SingleSelection)
        
        # Apply theme-aware styling to the tree widget
        self.apply_theme_style()
        
        left_layout.addWidget(self.signal_tree)
        
        # Right panel - Selected signals (with same hierarchical structure)
        right_panel = QFrame()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        right_panel.setFrameShape(QFrame.NoFrame)  # Removes the border
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {c.base};  /* Match the theme */
                border: none;                     /* Explicitly remove border */
            }}
        """)
        
        self.selected_signals_tree = QTreeWidget()
        self.selected_signals_tree.setHeaderLabels(["Selected Signals"])
        self.selected_signals_tree.setRootIsDecorated(True)
        self.selected_signals_tree.setAlternatingRowColors(True)
        # Connect double-click to remove signal
        self.selected_signals_tree.itemDoubleClicked.connect(self.on_selected_signal_double_clicked)
        
        # Apply theme-aware styling to the selected signals tree widget
        self.selected_signals_tree.setStyleSheet(self.get_tree_style())
        
        right_layout.addWidget(self.selected_signals_tree)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([400, 400])
        
        # Apply theme-aware styling to the splitter
        splitter.setStyleSheet(f"""
            QSplitter {{
                background-color: {c.base};
                border: 1px solid {c.border};
            }}
            QSplitter::handle {{
                background-color: {c.alt};
                border: 1px solid {c.border};
            }}
            QSplitter::handle:horizontal {{
                width: 4px;
            }}
            QSplitter::handle:vertical {{
                height: 4px;
            }}
        """)
        
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        clear_button = QPushButton("Clear Selected")
        clear_button.clicked.connect(self.clear_selected_signals)
        
        # Make buttons look consistent with other dialogs
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        # Apply theme-aware styling to buttons
        theme = get_theme()
        c = get_colors()
        ok_button.setStyleSheet(theme.get_button_ok_style())
        cancel_button.setStyleSheet(theme.get_button_cancel_style())
        clear_button.setStyleSheet(theme.get_button_ok_style())  # Keep clear green for now
        
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Apply theme-aware stylesheet to dialog
        self.setStyleSheet(f"QDialog {{ background-color: {c.base}; }}")
        
    def apply_theme_style(self):
        """Apply theme-aware styling to the dialog"""
        # Get the current style sheet
        style_sheet = self.get_tree_style()
        self.signal_tree.setStyleSheet(style_sheet)
        
    def get_tree_style(self):
        """Get theme-aware styling for tree widgets"""
        c = get_colors()
        
        style = f"""
            QTreeWidget {{
                border: 1px solid {c.border_light};
                border-radius: 6px;
                padding: 4px;
                background-color: {c.base};
                alternate-background-color: {c.alt};
                color: {c.text};
                font-family: 'Arial', sans-serif;
            }}
            QTreeWidget::item {{
                padding: 6px;
            }}
            QTreeWidget::item:selected {{
                background-color: {c.selection};
                color: white;
            }}
            QTreeWidget::item:hover {{
                background-color: {c.hover};
            }}
            QHeaderView::section {{
                background-color: {c.alt};
                border: none;
                padding: 6px;
                font-weight: 600;
                color: {c.text};
            }}
            QWidget {{
                background-color: {c.base};
                color: {c.text};
            }}
            QLabel {{
                color: {c.text};
            }}
            QMenuBar {{
                background-color: {c.base};
                color: {c.text};
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 8px;
            }}
            QMenuBar::item:selected {{
                background: {c.hover};
            }}
            QMenuBar::item:pressed {{
                background: {"#666" if c.base == "#2b2b2b" else "#bbb"};
            }}
            QMenu {{
                background-color: {c.base};
                color: {c.text};
                border: 1px solid {c.border_light};
            }}
            QMenu::item {{
                padding: 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: {c.hover};
            }}
        """
        return style
    
    def filter_signals(self, text):
        """Filter the signal tree based on search text"""
        search_text = text.lower()
        
        # Iterate through all top-level items (Channels)
        for i in range(self.signal_tree.topLevelItemCount()):
            channel_item = self.signal_tree.topLevelItem(i)
            channel_visible = False
            
            # Iterate through Groups
            for j in range(channel_item.childCount()):
                group_item = channel_item.child(j)
                group_visible = False
                
                # Iterate through Signals
                for k in range(group_item.childCount()):
                    signal_item = group_item.child(k)
                    # Check if signal name matches search text
                    matches = search_text in signal_item.text(0).lower()
                    signal_item.setHidden(not matches)
                    if matches:
                        group_visible = True
                
                # Show group if any signal matches, or if group name itself matches
                if search_text in group_item.text(0).lower():
                    group_visible = True
                    # If group name matches, show all its signals
                    for k in range(group_item.childCount()):
                        group_item.child(k).setHidden(False)
                
                group_item.setHidden(not group_visible)
                if group_visible:
                    channel_visible = True
            
            # Show channel if any group/signal matches, or if channel name matches
            if search_text in channel_item.text(0).lower():
                channel_visible = True
                # If channel matches, show everything inside
                self._set_subtree_hidden(channel_item, False)
            
            channel_item.setHidden(not channel_visible)
            if channel_visible and search_text:
                channel_item.setExpanded(True)

    def _set_subtree_hidden(self, parent_item, hidden):
        """Recursively set hidden state for all children"""
        parent_item.setHidden(hidden)
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            self._set_subtree_hidden(child, hidden)

    def populate_tree(self):
        """Populate the signal tree with available signals organized in channels, groups, and signals"""
        self.signal_tree.clear()
        
        # Process each imported signal and organize by channel -> group -> signal
        for channel_data in self.imported_data:
            # Create channel parent node
            channel_name = channel_data.get('name', f'Channel {channel_data.get("channel", "Unknown")}')
            channel_parent = QTreeWidgetItem(self.signal_tree, [channel_name])
            channel_parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
            channel_parent.setExpanded(True)
            
            # Add groups to channel
            groups = channel_data.get('groups', [])
            for group_data in groups:
                group_name = group_data.get('name', 'Unknown Group')
                group_parent = QTreeWidgetItem(channel_parent, [group_name])
                group_parent.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                group_parent.setExpanded(True)
                
                # Add signals to group
                signals = group_data.get('signals', [])
                for signal_data in signals:
                    signal_name = signal_data.get('name', 'Unknown Signal')
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
        
        # Only populate if there are existing signals
        if self.existing_signals:
            # Create a mapping of existing signals by channel and group for easier organization
            signal_mapping = {}
            
            for signal_data in self.existing_signals:
                # Extract channel and group information from the signal data
                if isinstance(signal_data, dict) and 'channel_name' in signal_data and 'group_name' in signal_data:
                    channel_name = signal_data['channel_name']
                    group_name = signal_data['group_name']
                    signal_name = signal_data.get('name', 'Unknown')
                else:
                    # If no channel/group info, put in a default "Current" channel
                    channel_name = "Current"
                    group_name = "Selected"
                    signal_name = signal_data.get('name', 'Unknown')
                
                # Create the hierarchical structure
                if channel_name not in signal_mapping:
                    signal_mapping[channel_name] = {'groups': {}}
                
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
                        signal_item.setData(0, Qt.UserRole, signal_data)
        # If no existing signals, leave the tree empty
        
        # Expand all items in selected signals tree
        self.selected_signals_tree.expandAll()
    
    def on_signal_double_clicked(self, item, column):
        """Handle double-click on signal item"""
        # Only process if it's a child of a group parent (not the channel or group parent itself)
        if item.parent() is not None and item.parent().parent() is not None:
            # This is a signal item
            signal_data = item.data(0, Qt.UserRole)
            if signal_data:
                signal_name = signal_data.get('signal_data', {}).get('name', 'Unknown')
                channel_name = signal_data.get('channel_name', 'Unknown')
                group_name = signal_data.get('group_name', 'Unknown')
                # Add to selected signals tree with hierarchical structure
                self.add_to_selected_signals(signal_data)
                
        # Clear selection to remove highlight
        self.signal_tree.clearSelection()
    
    def on_selected_signal_double_clicked(self, item, column):
        """Handle double-click on selected signal - remove it"""
        # Remove the item from the selected signals tree
        parent = item.parent()
        if parent:
            # Remove the item from its parent
            parent.removeChild(item)
            # Clean up empty parents
            self.cleanup_empty_parents(parent)
        else:
            # If it's a top-level item, remove from the tree
            self.selected_signals_tree.takeTopLevelItem(self.selected_signals_tree.indexOfTopLevelItem(item))
        
        # Clear selection to remove highlight
        self.selected_signals_tree.clearSelection()
    
    def cleanup_empty_parents(self, parent_item):
        """Recursively clean up empty parent items (groups and channels)"""
        # If parent has no children, remove it
        if parent_item.childCount() == 0:
            grandparent = parent_item.parent()
            if grandparent:
                # Remove parent from grandparent
                grandparent.removeChild(parent_item)
                # Continue cleaning up
                self.cleanup_empty_parents(grandparent)
            else:
                # Parent is a top-level item, remove it from the tree
                for i in range(self.selected_signals_tree.topLevelItemCount()):
                    if self.selected_signals_tree.topLevelItem(i) == parent_item:
                        self.selected_signals_tree.takeTopLevelItem(i)
                        break
    
    def add_to_selected_signals(self, signal_data):
        """Add signal to selected signals tree with hierarchical structure"""
        # Extract channel and group information
        if isinstance(signal_data, dict) and 'channel_name' in signal_data and 'group_name' in signal_data:
            channel_name = signal_data['channel_name']
            group_name = signal_data['group_name']
            signal_name = signal_data.get('name', 'Unknown')
            if 'signal_data' in signal_data and isinstance(signal_data['signal_data'], dict):
                signal_name = signal_data['signal_data'].get('name', signal_name)
        else:
            # If no channel/group info, put in a default structure
            channel_name = "Current"
            group_name = "Selected"
            signal_name = signal_data.get('name', 'Unknown')
        
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
                # This is the nested format - extract a copy to avoid modifying the original data source
                actual_signal_data = signal_data['signal_data'].copy()
                actual_signal_data['channel_name'] = signal_data['channel_name']
                actual_signal_data['group_name'] = signal_data['group_name']
                actual_signals.append(actual_signal_data)
            else:
                # This is already the correct format (usually existing signals or dummy)
                actual_signals.append(signal_data.copy())
        
        return actual_signals
    
    def accept(self):
        """Handle dialog accept"""
        selected_signals = self.get_selected_signals()
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
                # Emit with signal name and channel name
                self.signal_selected.emit(signal_name, channel_name)
        # Call parent accept to close dialog
        super().accept()

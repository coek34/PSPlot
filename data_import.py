# data_import.py
import os, sys
import numpy as np
from PyQt5.QtWidgets import (QDialog, QFormLayout, QHBoxLayout, QVBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFileDialog, 
                            QTableWidget, QTableWidgetItem, QHeaderView, 
                            QMessageBox, QCheckBox, QGridLayout, QWidget, QApplication)
from PyQt5.QtCore import Qt

class DataImportDialog(QDialog):
    def __init__(self, parent=None, existing_data=None):
        super().__init__(parent)
        self.setWindowTitle("Import PSCAD Data")
        self.setModal(True)
        self.resize(800, 400)  # Increased width for better visibility
        
        # Store imported data
        self.imported_data = []
        
        # Load existing data if provided
        self.existing_data = existing_data or []
        
        self.setup_ui()
        
        # Load existing data into the table
        if self.existing_data:
            self.load_existing_data()
        
    def load_existing_data(self):
        """Load existing data into the table"""
        for data in self.existing_data:
            row = data['channel'] - 1  # Convert to 0-based index
            if row < 6:  # Only load if within table bounds
                # Set path
                path_item = self.table.item(row, 0)
                if path_item:
                    path_item.setText(data['path'])
                
                # Set label
                label_input = self.table.cellWidget(row, 1)
                if label_input:
                    label_input.setText(data['label'])
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Table for showing imported data (6 channels)
        self.table = QTableWidget(6, 2)
        self.table.setHorizontalHeaderLabels(["Path", "Label"])
        
        # Set column widths to be more user-friendly
        self.table.setColumnWidth(0, 400)  # Path column
        self.table.setColumnWidth(1, 200)  # Label column
        
        # Allow manual resizing of columns
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        
        # Set row height
        for i in range(6):
            self.table.setRowHeight(i, 30)
        
        # Fill table with initial data
        for row in range(6):
            # Path column (clickable)
            path_item = QTableWidgetItem("")
            path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, path_item)
            
            # Label column
            label_input = QLineEdit()
            self.table.setCellWidget(row, 1, label_input)
        
        # Connect cell click to browse functionality
        self.table.cellClicked.connect(self.on_cell_clicked)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept_data)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addStretch()
        
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        
    def on_cell_clicked(self, row, column):
        """Handle cell click - allow browsing for file paths"""
        if column == 0:  # Path column
            self.browse_file(row)
    
    def browse_file(self, row):
        """Browse for PSCAD .inf file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select PSCAD .inf File",
            "",
            "PSCAD Files (*.inf);;All Files (*)"
        )
        
        if file_path:
            # Update the path in the table
            path_item = self.table.item(row, 0)
            if path_item:
                path_item.setText(file_path)
            
            # Auto-fill label based on filename
            filename = os.path.basename(file_path)
            if filename.endswith('.inf'):
                filename = filename[:-4]  # Remove .inf extension
            label_input = self.table.cellWidget(row, 1)
            if label_input and not label_input.text():
                label_input.setText(filename)
    
    def accept_data(self):
        """Accept the data configuration"""
        self.imported_data = []
        
        # Get data from each row
        for row in range(6):
            # Get path
            path_item = self.table.item(row, 0)
            path = path_item.text() if path_item else ""
            
            # Get label
            label_input = self.table.cellWidget(row, 1)
            label = label_input.text() if label_input else ""
            
            # Only add if path exists
            if path:
                self.imported_data.append({
                    'channel': row + 1,
                    'path': path,
                    'label': label or f"Channel {row + 1}"
                })
        
        # Validate that at least one channel has data
        has_data = any(data['path'] for data in self.imported_data)
        if not has_data:
            QMessageBox.warning(self, "Warning", "Please select at least one data file")
            return
            
        self.accept()
    
    def get_imported_data(self):
        """Return the imported data"""
        return self.imported_data

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = DataImportDialog()
    dialog.show()
    sys.exit(app.exec_())

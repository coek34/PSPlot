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
        self.setWindowTitle("Import Data (PSCAD/COMTRADE/CSV)")
        self.setModal(True)
        self.resize(800, 400)
        
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
            row = data.get('channel', 1) - 1 # Use get() as channel might be missing in some versions
            if row < 6:
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
        
        # Instructions
        instr = QLabel("Double-click a row in 'Path' to select a PSCAD (.inf), Comtrade (.cfg), or CSV file.")
        instr.setStyleSheet("font-weight: bold; padding-bottom: 5px;")
        layout.addWidget(instr)

        # Table for showing imported data (6 channels)
        self.table = QTableWidget(6, 2)
        self.table.setHorizontalHeaderLabels(["Path", "Label"])
        
        # Set column widths to be more user-friendly
        self.table.setColumnWidth(0, 480)   # Path column
        self.table.setColumnWidth(1, 240)   # Label column
        
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
            label_input.setPlaceholderText(f"Channel {row+1} Name")
            self.table.setCellWidget(row, 1, label_input)
        
        # Connect cell click to browse functionality
        self.table.cellClicked.connect(self.on_cell_clicked)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.setMinimumWidth(100)
        ok_button.clicked.connect(self.accept_data)
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        
        # Style buttons if possible (standard look)
        from core.theme import get_theme
        theme = get_theme()
        if theme:
            ok_button.setStyleSheet(theme.get_button_ok_style())
            cancel_button.setStyleSheet(theme.get_button_cancel_style())

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        
        # Apply theme to dialog
        if theme:
            self.setStyleSheet(theme.get_style_sheet())
        
    def on_cell_clicked(self, row, column):
        """Handle cell click - allow browsing for file paths"""
        if column == 0:   # Path column
            self.browse_file(row)
    
    def browse_file(self, row):
        """Browse for PSCAD .inf, COMTRADE .cfg, or CSV file"""
        last_dir = ""  # Could get from settings
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File (PSCAD, COMTRADE, or CSV)",
            last_dir,
            "Combined Files (*.inf *.cfg *.CSV *.csv *.CFG);;PSCAD Files (*.inf);;COMTRADE Files (*.cfg *.CSV);;CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            # Update the path in the table
            path_item = self.table.item(row, 0)
            if path_item:
                path_item.setText(file_path)
            
            # Auto-fill label based on filename
            filename = os.path.basename(file_path)
            # Remove extensions
            for ext in ['.inf', '.cfg', '.CSV', '.csv', '.CFG']:
                if filename.lower().endswith(ext):
                    filename = filename[:-len(ext)]
                    break
            
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
                # Detect type
                ftype = 'pscad'
                if path.lower().endswith('.cfg'):
                    ftype = 'comtrade'
                elif path.lower().endswith('.csv'):
                    ftype = 'csv'
                
                self.imported_data.append({
                    'channel': row + 1,
                    'path': path,
                    'label': label or f"Channel {row + 1}",
                    'type': ftype
                })
        
        # Validate that at least one channel has data
        if not self.imported_data:
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

# data_manager.py
from PyQt5.QtWidgets import QMessageBox
import os

class DataManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.imported_data = []
        self.channel_signals = {}  # Dictionary to store signals per channel
    
    def import_pscad_data(self):
        """Import PSCAD data using the data import dialog"""
        from data_import import DataImportDialog
        dialog = DataImportDialog(self.main_window, existing_data=self.imported_data)
        if dialog.exec_() == dialog.Accepted:
            # Get the imported data
            self.imported_data = dialog.get_imported_data()
            
            # Update channel signals
            for data in self.imported_data:
                channel = data['channel']
                path = data['path']
                label = data['label']
                
                if channel not in self.channel_signals:
                    self.channel_signals[channel] = []
                
                # Load signal data from the file (assuming a simple format for now)
                with open(path, 'r') as file:
                    lines = file.readlines()
                    x_data = [float(line.split()[0]) for line in lines]
                    y_data = [float(line.split()[1]) for line in lines]
                
                # Store signal data
                self.channel_signals[channel].append({
                    'x': x_data,
                    'y': y_data,
                    'name': label,
                    'channel_name': channel,
                    'group_name': 'Imported'
                })

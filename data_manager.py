# data_manager.py
from PyQt5.QtWidgets import QMessageBox
import os
import logging

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.imported_data = []
        self.channel_signals = {}  # Dictionary to store signals per channel
    
    def get_imported_paths_info(self):
        """Get information about imported files for persistence"""
        return self.imported_data

    def get_all_available_data(self):
        """Get all data (Imported + Dummy) formatted for SignalExplorerDialog"""
        # Start with imported data (already has channel/group hierarchy)
        # We need to wrap it in the expected format: 
        # list of {name: str, groups: [ {name: str, signals: [...] } ] }
        
        # Note: self.imported_data is already a list of channels
        # but we might want to add dummy signals here too.
        all_data = [] + self.imported_data
        
        # Add Dummy data if it's not already there
        # We can get this from plot_canvas but for now let's keep it clean
        return all_data

    def load_from_paths_info(self, paths_info):
        """Reload data from saved paths info on startup"""
        if not paths_info:
            return
        
        self.imported_data = paths_info
        for data in self.imported_data:
            self._load_single_file(data)

    def _load_single_file(self, data):
        """Internal method to load data from a single file path info"""
        channel = data['channel']
        path = data['path']
        label = data['label']
        
        if not os.path.exists(path):
            logger.warning(f"File not found: {path}")
            return

        if channel not in self.channel_signals:
            self.channel_signals[channel] = []
        
        try:
            with open(path, 'r') as file:
                lines = file.readlines()
                x_data = [float(line.split()[0]) for line in lines]
                y_data = [float(line.split()[1]) for line in lines]
            
            # Store signal data
            self.channel_signals[channel].append({
                'x': x_data,
                'y': y_data,
                'name': label,
                'channel_name': str(channel),
                'group_name': 'Imported',
                'file_path': path
            })
            logger.info(f"Loaded {len(x_data)} points from {path}")
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")

    def import_pscad_data(self):
        """Import PSCAD data using the data import dialog"""
        from data_import import DataImportDialog
        dialog = DataImportDialog(self.main_window, existing_data=self.imported_data)
        if dialog.exec_() == dialog.Accepted:
            # Get the imported data
            self.imported_data = dialog.get_imported_data()
            
            # Update channel signals
            for data in self.imported_data:
                self._load_single_file(data)

# data_manager.py
from PyQt5.QtWidgets import QMessageBox
import os
import logging
from pscad_reader import PSCADReader

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.imported_data = []  # Stores path info from DataImportDialog
        self.channel_signals = {}  # Dictionary to store loaded actual data per channel
        self.available_signals = [] # Hierarchical structure for SignalExplorer
        self.pscad_reader = PSCADReader()
    
    def get_imported_paths_info(self):
        """Get information about imported files for persistence"""
        return self.imported_data

    def get_all_available_data(self):
        """Get all data formatted for SignalExplorerDialog. 
        Rebuilds from .inf files to ensure the latest signal list is available."""
        if self.imported_data:
            logger.info("Rebuilding available_signals from .inf files...")
            self._rebuild_available_signals()
            
        return self.available_signals

    def load_from_paths_info(self, paths_info):
        """Reload data from saved paths info on startup"""
        if not paths_info:
            return
        
        self.imported_data = paths_info
        self._rebuild_available_signals()

    def _rebuild_available_signals(self):
        """Build hierarchical signal structure from imported paths"""
        self.available_signals = []
        for data in self.imported_data:
            path = data['path']
            label = data['label']
            
            # Use path without extension for reader
            base_path = path
            if base_path.lower().endswith('.inf'):
                base_path = base_path[:-4]
            
            # List signals from .inf file
            signals = self.pscad_reader.list_signals(base_path, verbose=False)
            
            if signals:
                # Organize by group
                groups_dict = {}
                for sig in signals:
                    grp_name = sig['group']
                    if grp_name not in groups_dict:
                        groups_dict[grp_name] = []
                    
                    # Prepare signal dict for explorer
                    groups_dict[grp_name].append({
                        'name': sig['desc'],
                        'index': sig['index'],
                        'units': sig['units'],
                        'file_path': base_path # Store base path to read data later
                    })
                
                # Create groups list
                groups = []
                for grp_name, sig_list in groups_dict.items():
                    groups.append({
                        'name': grp_name,
                        'signals': sig_list
                    })
                
                # Add to hierarchical structure
                self.available_signals.append({
                    'name': label,
                    'groups': groups,
                    'path': path
                })

    def import_pscad_data(self):
        """Import PSCAD data using the data import dialog"""
        from data_import import DataImportDialog
        dialog = DataImportDialog(self.main_window, existing_data=self.imported_data)
        if dialog.exec_() == dialog.Accepted:
            # Get the imported data (list of paths/labels)
            self.imported_data = dialog.get_imported_data()
            
            # Rebuild the available signals tree
            self._rebuild_available_signals()
            
            # Check if any signals were actually found
            if not self.available_signals:
                QMessageBox.warning(self.main_window, "Warning", "No valid signals found in the selected .inf files.")
            else:
                logger.info(f"Imported {len(self.available_signals)} channels with hierarchical signals.")
                # Automatically open Signal Explorer if data was imported
                page = self.main_window.get_current_page()
                if page and page.plot_canvas:
                    # Provide an empty position or a default one if needed
                    from PyQt5.QtCore import QPoint
                    page.plot_canvas.show_signal_selector(QPoint(0, 0))

    def load_signal_data(self, signal_info):
        """
        Loads actual x, y data for a selected signal.
        signal_info is the dict stored in the tree node data.
        """
        base_path = signal_info.get('file_path')
        sgn_name = signal_info.get('name')
        grp_name = signal_info.get('group_name')
        chn_name = signal_info.get('channel_name')
        
        if not base_path or not sgn_name or not grp_name:
            logger.error(f"Incomplete signal info: {signal_info}")
            return None
            
        t, data = self.pscad_reader.read_signal(base_path, sgn_name, grp_name)
        
        if t.size > 0:
            return {
                'x': t,
                'y': data,
                'name': sgn_name,
                'channel_name': chn_name or 'Unknown',
                'units': signal_info.get('units', ''),
                'group_name': grp_name,
                'file_path': base_path
            }
        return None

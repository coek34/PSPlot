# data_manager.py
from PyQt5.QtWidgets import QMessageBox
import os
import logging
import numpy as np
from readers.pscad_reader import PSCADReader
from readers.comtrade_reader import ComtradeReader
from readers.csv_reader import CSVReader

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.imported_data = []   # Stores path info from DataImportDialog
        self.channel_signals = {}   # Dictionary to store loaded actual data per channel
        self.available_signals = [] # Hierarchical structure for SignalExplorer
        self.pscad_reader = PSCADReader()
        self.comtrade_reader = ComtradeReader()
        self.csv_reader = CSVReader()
    
    def get_imported_paths_info(self):
        """Get information about imported files for persistence"""
        return self.imported_data

    def get_all_available_data(self):
        """Get all data formatted for SignalExplorerDialog. 
        Rebuilds from .inf/.cfg files to ensure the latest signal list is available."""
        if self.imported_data:
            logger.info("Rebuilding available_signals from data files...")
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
            
            # Always detect type from file extension first (prioritize over stored type)
            if path.lower().endswith('.cfg'):
                ftype = 'comtrade'
            elif path.lower().endswith('.csv'):
                ftype = 'csv'
            else:
                ftype = data.get('type', 'pscad')
            
            # Extract signals using appropriate reader
            signals = []
            if ftype == 'comtrade':
                signals = self.comtrade_reader.list_signals(path, verbose=False)
            elif ftype == 'csv':
                signals = self.csv_reader.list_signals(path, verbose=False)
            else:
                # Use base path without extension for PSCAD
                base_path = path
                if base_path.lower().endswith('.inf'):
                    base_path = base_path[:-4]
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
                        'file_path': path,    # Store full path
                        'type': ftype
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
                    'path': path,
                    'type': ftype
                })

    def import_pscad_data(self):
        """Import PSCAD/COMTRADE data using the data import dialog"""
        from readers.data_import import DataImportDialog
        dialog = DataImportDialog(self.main_window, existing_data=self.imported_data)
        if dialog.exec_() == dialog.Accepted:
            # Get the imported data (list of paths/labels/types)
            self.imported_data = dialog.get_imported_data()
            
            # Rebuild the available signals tree
            self._rebuild_available_signals()
            
            # Check if any signals were actually found
            if not self.available_signals:
                QMessageBox.warning(self.main_window, "Warning", "No valid signals found in the selected files.")
            else:
                logger.info(f"Imported {len(self.available_signals)} channels with hierarchical signals.")
                # Automatically open Signal Explorer if data was imported
                page = self.main_window.get_current_page()
                if page and page.plot_canvas:
                    from PyQt5.QtCore import QPoint
                    page.plot_canvas.show_signal_selector(QPoint(0, 0))

    def load_signal_data(self, signal_info):
        """
        Loads actual x, y data for a selected signal.
        signal_info is the dict stored in the tree node data.
        """
        file_path = signal_info.get('file_path')
        sgn_name = signal_info.get('name')
        grp_name = signal_info.get('group_name')
        chn_name = signal_info.get('channel_name')
        ftype = signal_info.get('type')
        
        if not file_path or not sgn_name or not grp_name:
            logger.error(f"Incomplete signal info: {signal_info}")
            return None
            
         # Detect type if missing (e.g., during reload/rehydration)
        if not ftype:
            if file_path.lower().endswith('.cfg'):
                ftype = 'comtrade'
            elif file_path.lower().endswith('.csv'):
                ftype = 'csv'
            else:
                ftype = 'pscad'
            
        t, data = np.array([]), np.array([])
        if ftype == 'comtrade':
            t, data = self.comtrade_reader.read_signal(file_path, sgn_name, grp_name)
        elif ftype == 'csv':
            t, data = self.csv_reader.read_signal(file_path, sgn_name, grp_name)
        else:
            # PSCADReader uses base path (no extension)
            base_path = file_path
            if base_path.lower().endswith('.inf'):
                base_path = base_path[:-4]
            t, data = self.pscad_reader.read_signal(base_path, sgn_name, grp_name)
        
        if t.size > 0:
            return {
                'x': t,
                'y': data,
                'name': sgn_name,
                'channel_name': chn_name or 'Unknown',
                'units': signal_info.get('units', ''),
                'group_name': grp_name,
                'file_path': file_path,
                'type': ftype
            }
        return None

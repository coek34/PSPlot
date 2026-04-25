# action_manager.py
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class ActionManager:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def on_reset_x_clicked(self):
        current_page = self.main_window.get_current_page()
        if current_page and current_page.plot_canvas:
            current_page.plot_canvas.reset_x_zoom()
    
    def on_reset_y_clicked(self):
        current_page = self.main_window.get_current_page()
        if current_page and current_page.plot_canvas:
            current_page.plot_canvas.reset_y_zoom()
    
    def on_round_x_clicked(self):
        current_page = self.main_window.get_current_page()
        if current_page and current_page.plot_canvas:
            current_page.plot_canvas.round_x_to_grid()
    
    def on_export_clicked(self):
        """Export all pages using standard save dialog"""
        if not self.main_window.page_manager.pages:
            return
            
        # Get file path using standard save dialog with multiple format options
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self.main_window, 
            "Save File", 
            "document_plot.png", 
            "PNG Files (*.png);;PDF Files (*.pdf);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Determine the format from the selected filter
        file_format = 'png'  # default
        if selected_filter == "PDF Files (*.pdf)":
            file_format = 'pdf'
        elif selected_filter == "PNG Files (*.png)":
            file_format = 'png'
        
        # Extract directory and base filename without extension
        import os
        directory = os.path.dirname(file_path)
        filename_without_ext = os.path.splitext(os.path.basename(file_path))[0]
        
        # Export each page
        for i, page in enumerate(self.main_window.page_manager.pages):
            # Use page name directly in filename
            page_filename = f"{filename_without_ext}_{page.page_name.replace(' ', '_')}.{file_format}"
            # Sanitize filename to remove invalid characters
            import re
            page_filename = re.sub(r'[^\w\-_.]', '_', page_filename)
            filepath = os.path.join(directory, page_filename)
            
            try:
                # Save the current page
                page.plot_canvas.fig.savefig(
                    filepath, 
                    dpi=100, 
                    bbox_inches=None,  # This preserves the full figure size
                    pad_inches=0, 
                    facecolor='white', 
                    format=file_format
                )
            except Exception as e:
                # Show error in a message box instead of print
                QMessageBox.warning(self.main_window, "Export Error", f"Failed to export {page_filename}: {e}")
        
        QMessageBox.information(self.main_window, "Export Complete", f"Exported {len(self.main_window.page_manager.pages)} pages to {directory}")

    def on_save_template_clicked(self):
        """Save current application state to a .psp template file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Save Template",
            "template.psp",
            "PSPlot Template (*.psp);;All Files (*)"
        )
        
        if not file_path:
            return

        try:
            # Gather current state (logic from closeEvent)
            self._sync_all_signals()
            
            # Prepare state dict
            import os
            from dataclasses import asdict
            
            # Update settings object with current state
            self.main_window.settings.state.imported_files = self.main_window.data_manager.get_imported_paths_info()
            self.main_window.settings.state.current_page_index = self.main_window.tab_widget.currentIndex()
            self.main_window.settings.state.pages = self.main_window.page_manager.get_all_pages_state()
            
            # Save to the specific file
            import json
            data = {
                "preferences": asdict(self.main_window.settings.preferences),
                "state": asdict(self.main_window.settings.state)
            }
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
                
            QMessageBox.information(self.main_window, "Success", f"Template saved to {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to save template: {e}")

    def on_open_template_clicked(self):
        """Load application state from a .psp template file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Open Template",
            "",
            "PSPlot Template (*.psp);;All Files (*)"
        )
        
        if not file_path:
            return

        try:
            # Load and parse
            import json
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Temporarily override settings state and restore
            from psplot.core.settings import AppState, PageState, UserPreferences
            
            state_data = data.get("state", {})
            pages_data = state_data.get("pages", [])
            pages = [PageState(**p) for p in pages_data]
            
            new_state = AppState(
                pages=pages,
                current_page_index=state_data.get("current_page_index", 0),
                imported_files=state_data.get("imported_files", [])
            )
            
            # Application the state
            self.main_window.settings.state = new_state
            self.main_window.restore_app_state()
            
            QMessageBox.information(self.main_window, "Success", "Template loaded successfully")
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self.main_window, "Error", f"Failed to load template: {e}")

    def _sync_all_signals(self):
        """Sync signals from canvas to storage (internal helper)"""
        import logging
        logger = logging.getLogger(__name__)
        for page in self.main_window.page_manager.pages:
            if page.plot_canvas:
                for i in range(6):
                    if i < len(page.plot_canvas.axes):
                        sigs = page.plot_canvas.get_existing_signals_for_subplot(i)
                        if sigs:
                            page.subplot_signals[i] = sigs

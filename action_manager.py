# action_manager.py
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
        if not self.main_window.pages:
            return
            
        # Get file path using standard save dialog with multiple format options
        file_path, selected_filter = self.main_window.getSaveFileName(
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
        for i, page in enumerate(self.main_window.pages):
            # Use page name directly in filename
            page_filename = f"{filename_without_ext}_{page.page_name.replace(' ', '_')}.{file_format}"
            # Sanitize filename to remove invalid characters
            import re
            page_filename = re.sub(r'[^\w\-_\.]', '_', page_filename)
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
                self.main_window.warning(self.main_window, "Export Error", f"Failed to export {page_filename}: {e}")
        
        self.main_window.information(self.main_window, "Export Complete", f"Exported {len(self.main_window.pages)} pages to {directory}")

# keyboard_manager.py
from PyQt5.QtCore import Qt

class KeyboardManager:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def keyPressEvent(self, event):
        # Handle key press events directly on the main window
        key = event.key()
        
        # Number keys 1-6 for subplot count
        if Qt.Key_1 <= key <= Qt.Key_6:
            current_page = self.main_window.get_current_page()
            if current_page:
                subplot_count = key - Qt.Key_1 + 1
                current_page.update_plots(subplot_count)
                self.main_window.plot_count_label.setText(f"Plots: {subplot_count}")
                
                # Automatically round x to grid after changing subplot count
                # This preserves current x-limits but applies grid rounding
                if current_page.plot_canvas:
                    current_page.plot_canvas.round_x_to_grid()
            event.accept()
            return
            
        # Pan left with A key
        elif key == Qt.Key_A:
            current_page = self.main_window.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.pan_horizontal(-1)  # Pan left
            event.accept()
            return
            
        # Pan right with D key
        elif key == Qt.Key_D:
            current_page = self.main_window.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.pan_horizontal(1)  # Pan right
            event.accept()
            return
            
        # Reset x-zoom with R key
        elif key == Qt.Key_R:
            current_page = self.main_window.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.reset_x_zoom()
            event.accept()
            return
            
        # Reset y-zoom with Y key
        elif key == Qt.Key_Y:
            current_page = self.main_window.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.reset_y_zoom()
            event.accept()
            return
            
        # Round x to grid with X key
        elif key == Qt.Key_X:
            current_page = self.main_window.get_current_page()
            if current_page and current_page.plot_canvas:
                current_page.plot_canvas.round_x_to_grid()
            event.accept()
            return
            
        # Export with E key
        elif key == Qt.Key_E:
            self.main_window.on_export_clicked()
            event.accept()
            return

        # Import data with C key
        elif key == Qt.Key_C:
            self.main_window.import_pscad_data()
            event.accept()
            return
            
        # Adjust margins with M key
        elif key == Qt.Key_M:
            self.main_window.adjust_margins()
            event.accept()
            return
            
        # New canvas with N key
        elif key == Qt.Key_N:
            self.main_window.new_canvas()
            event.accept()
            return
            
        # Resize current page with P key
        elif key == Qt.Key_P:
            self.main_window.resize_current_page()
            event.accept()
            return
            
        # Pass other keys to parent class
        super().keyPressEvent(event)

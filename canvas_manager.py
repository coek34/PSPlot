# canvas_manager.py
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QDialog
from PyQt5.QtCore import Qt
from signal_explorer import SignalExplorerDialog

class CanvasManager:
    def __init__(self, main_window):
        self.main_window = main_window
    
    def new_canvas(self):
        """Create a new canvas with selected size"""
        # Get the current page to copy its size
        current_page = self.main_window.get_current_page()
        if current_page:
            # Get current page size in mm
            current_width_mm, current_height_mm = current_page.plot_canvas.get_canvas_size_mm()
            
            # Show canvas size dialog
            from canvas_size_dialog import CanvasSizeDialog
            dialog = CanvasSizeDialog(self.main_window, (current_width_mm, current_height_mm))
            if dialog.exec_() == QDialog.Accepted:
                # Get selected size in inches
                width_inch, height_inch = dialog.get_selected_size()
                # Create new page with selected size
                self.main_window.add_new_page(width_inch, height_inch)
        else:
            # If no current page, use default size
            from canvas_size_dialog import CanvasSizeDialog
            dialog = CanvasSizeDialog(self.main_window)
            if dialog.exec_() == QDialog.Accepted:
                width_inch, height_inch = dialog.get_selected_size()
                self.main_window.add_new_page(width_inch, height_inch)
    
    def resize_current_page(self):
        """Resize the current page while preserving signals and x-limits"""
        current_page = self.main_window.get_current_page()
        if not current_page:
            return
            
        # Get current page size in mm
        current_width_mm, current_height_mm = current_page.plot_canvas.get_canvas_size_mm()
        
        # Show canvas size dialog with current size as default
        from canvas_size_dialog import CanvasSizeDialog
        dialog = CanvasSizeDialog(self.main_window, (current_width_mm, current_height_mm))
        if dialog.exec_() == QDialog.Accepted:
            # Get selected size in inches
            width_inch, height_inch = dialog.get_selected_size()
            
            # Store current x-limits if they exist
            current_xlim = None
            if current_page.plot_canvas.current_xlim:
                current_xlim = current_page.plot_canvas.current_xlim
            
            # Store current signals for each subplot
            signals_to_restore = []
            for i in range(len(current_page.plot_canvas.axes)):
                if i < len(current_page.subplot_signals):
                    signals_to_restore.append(current_page.subplot_signals[i])
                else:
                    signals_to_restore.append([])
            
            # Update the page with new size
            current_page.width = width_inch
            current_page.height = height_inch
            
            # Create a new canvas with the new size
            from plot_canvas import InteractivePlotCanvas
            new_canvas = InteractivePlotCanvas(width=width_inch, height=height_inch)
            
            # Replace the old canvas with the new one
            scroll_area = current_page.scroll_area
            scroll_area.takeWidget()  # Remove old canvas
            scroll_area.setWidget(new_canvas)  # Set new canvas
            current_page.plot_canvas = new_canvas
            
            # Restore subplot count and signals
            new_canvas.update_plots(len(signals_to_restore))
            
            # Restore signals to subplots
            for i, signals in enumerate(signals_to_restore):
                if i < len(new_canvas.axes) and signals:
                    new_canvas.set_subplot_signals(i, signals)
            
            # Restore x-limits if they existed
            if current_xlim:
                new_canvas.set_x_limits(current_xlim[0], current_xlim[1])
            
            # Apply tight layout (reset margins to defaults)
            new_canvas.reset_default_margins()
    
    def get_current_margins(self):
        """Get current subplot margins from the figure"""
        current_page = self.main_window.get_current_page()
        if current_page:
            return current_page.get_current_margins()
        return {'left': 0.125, 'bottom': 0.1, 'right': 0.9, 'top': 0.9, 'wspace': 0.5, 'hspace': 0.5}
    
    def adjust_margins(self):
        """Adjust plot margins using percentage values"""
        current_page = self.main_window.get_current_page()
        if not current_page:
            return
            
        # Get current margins
        current_margins = current_page.get_current_margins()
        
        # Create margin dialog with current values
        from margin_dialog import MarginDialog
        dialog = MarginDialog(self.main_window, current_margins)
        if dialog.exec_() == QDialog.Accepted:
            margins = dialog.get_margins()
            
            # Apply margins to current page
            current_page.adjust_margins(margins)
            
    def reset_current_margins(self):
        """Reset margins to default values"""
        current_page = self.main_window.get_current_page()
        if current_page and current_page.plot_canvas:
            current_page.plot_canvas.reset_default_margins()
    
    def show_context_menu(self, position):
        """Show context menu when right-clicking on the canvas"""
        # Create context menu
        menu = QMenu(self.main_window)
        
        # Apply theme-aware styling to the menu
        is_dark = False
        try:
            # Try to detect dark mode using system settings
            import darkdetect
            is_dark = darkdetect.isDark()
        except:
            # If darkdetect is not available, default to light mode
            pass
            
        base_color = "#2b2b2b" if is_dark else "#ffffff"
        text_color = "#ffffff" if is_dark else "#000000"
        border_color = "#444" if is_dark else "#ccc"
        
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {base_color};
                color: {text_color};
                border: 1px solid {border_color};
                padding: 4px;
                font-family: 'Arial', sans-serif;
            }}
            QMenu::item {{
                padding: 6px 20px;
                border: none;
            }}
            QMenu::item:selected {{
                background-color: #0078D7;
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {border_color};
                margin: 4px 0;
            }}
        """)
        
        # Add action to show data label for the specific subplot
        action = menu.addAction("Add/Change Data")
        action.triggered.connect(lambda: self.show_signal_selector(position))
        
        menu.exec_(self.main_window.mapToGlobal(position))
        
    def show_signal_selector(self, position):
        """Show signal selector dialog for the clicked subplot"""
        # Use the stored last clicked subplot
        current_page = self.main_window.get_current_page()
        if current_page and current_page.plot_canvas.last_clicked_subplot is not None:
            # Get existing signals for this subplot to show in the dialog
            existing_signals = current_page.plot_canvas.get_existing_signals_for_subplot(current_page.plot_canvas.last_clicked_subplot)
            
            # Create a dialog with dummy signals and existing signals
            dialog = SignalExplorerDialog(current_page.plot_canvas.dummy_signals, existing_signals, parent=self.main_window)
            if dialog.exec_() == dialog.Accepted:
                selected_signals = dialog.get_selected_signals()
                if selected_signals:
                    # Plot all selected signals in the same subplot
                    current_page.plot_canvas.set_subplot_signals(current_page.plot_canvas.last_clicked_subplot, selected_signals)
        else:
            # If no subplot was clicked, show a message
            QMessageBox.information(self.main_window, "Info", "Please click on a subplot first to select a signal.")

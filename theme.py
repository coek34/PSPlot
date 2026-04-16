"""Theme utility module for PSPlot - centralized theme detection and styling.

Provides consistent theming across the application with support for
light/dark mode detection and color constants.
"""

from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
    """Color palette for a specific theme."""
    # Background colors
    base: str           # Primary background
    alt: str            # Alternative background (panels, tabs)
    scroll_area: str    # Scroll area background
    
    # Text and foreground
    text: str           # Primary text color
    
    # Borders and dividers
    border: str         # Primary border
    border_light: str   # Lighter border for subtle separation
    
    # Interactive elements
    selection: str      # Selected/highlighted item
    hover: str          # Hover state
    
    # Misc
    status_bg: str      # Status bar background
    
    # Action colors
    success: str        # Success/OK buttons
    danger: str         # Danger/Cancel buttons


class ThemeManager:
    """Centralized theme management for PSPlot.
    
    Usage:
        from theme import ThemeManager
        
        theme = ThemeManager()
        widget.setStyleSheet(f"background-color: {theme.colors.base}; color: {theme.colors.text}")
    """
    
    DARK = ThemeColors(
        base="#2b2b2b",
        alt="#3a3a3a",
        scroll_area="#3a3a3a",
        text="#ffffff",
        border="#444",
        border_light="#555",
        selection="#0078D7",
        hover="#555",
        status_bg="#3a3a3a",
        success="#4CAF50",
        danger="#f44336",
    )
    
    LIGHT = ThemeColors(
        base="#ffffff",
        alt="#fafafa",
        scroll_area="#f0f0f0",  # Pale gray instead of white for scroll areas
        text="#000000",
        border="#ccc",
        border_light="#ddd",
        selection="#0078D7",
        hover="#e0e0e0",
        status_bg="#f0f0f0",
        success="#4CAF50",
        danger="#f44336",
    )
    
    def __init__(self):
        self._is_dark: Optional[bool] = None
    
    @property
    def is_dark(self) -> bool:
        """Detect if dark mode is active (cached)."""
        if self._is_dark is None:
            self._is_dark = self._detect_dark_mode()
        return self._is_dark
    
    def _detect_dark_mode(self) -> bool:
        """Detect system dark mode using darkdetect library."""
        try:
            import darkdetect
            return darkdetect.isDark()
        except ImportError:
            return False
    
    @property
    def colors(self) -> ThemeColors:
        """Get the current theme's color palette."""
        return self.DARK if self.is_dark else self.LIGHT
    
    def get_style_sheet(self) -> str:
        """Get the full application stylesheet for the current theme."""
        c = self.colors
        hover_bg = "#555" if self.is_dark else "#e0e0e0"
        pressed_bg = "#666" if self.is_dark else "#bbb"
        tab_bg = "#3a3a3a" if self.is_dark else "#f0f0f0"
        
        return f"""
            QMainWindow {{
                background-color: {c.base};
                color: {c.text};
            }}
            QMenuBar {{
                background-color: {c.base};
                color: {c.text};
            }}
            QMenuBar::item {{
                background: transparent;
                padding: 4px 8px;
            }}
            QMenuBar::item:selected {{
                background: {hover_bg};
            }}
            QMenuBar::item:pressed {{
                background: {pressed_bg};
            }}
            QMenu {{
                background-color: {c.base};
                color: {c.text};
                border: 1px solid {c.border_light};
            }}
            QMenu::item {{
                padding: 6px 20px;
            }}
            QMenu::item:selected {{
                background-color: {c.selection};
                color: white;
            }}
            QTabWidget::pane {{
                border: 1px solid {c.border};
                background-color: {c.base};
            }}
            QTabBar::tab {{
                background-color: {tab_bg};
                color: {c.text};
                padding: 8px;
                border: 1px solid {c.border};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: {c.base};
                border-bottom: 2px solid {c.selection};
            }}
            QTabBar::tab:hover {{
                background-color: {hover_bg};
            }}
            QStatusBar {{
                background-color: {c.base};
                color: {c.text};
            }}
            QScrollArea {{
                background-color: {c.base};
                border: 1px solid {c.border};
            }}
            QLabel {{
                color: {c.text};
            }}
            QFrame {{
                background-color: {c.base};
                border: none;
            }}
        """
    
    def get_menu_style(self) -> str:
        """Get stylesheet for context menus."""
        c = self.colors
        return f"""
            QMenu {{
                background-color: {c.base};
                color: {c.text};
                border: 1px solid {c.border};
                padding: 4px;
            }}
            QMenu::item {{
                padding: 6px 24px;
            }}
            QMenu::item:selected {{
                background-color: {c.selection};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {c.border};
                margin: 4px 0;
            }}
        """
    
    def get_tree_widget_style(self) -> str:
        """Get stylesheet for tree widgets (signal explorer)."""
        c = self.colors
        return f"""
            QTreeWidget {{
                border: 1px solid {c.border};
                border-radius: 6px;
                padding: 4px;
                background-color: {c.base};
                alternate-background-color: {c.alt};
                color: {c.text};
            }}
            QTreeWidget::item {{
                padding: 4px 0;
            }}
            QTreeWidget::item:selected {{
                background-color: {c.selection};
                color: white;
            }}
        """
    
    def get_button_ok_style(self) -> str:
        """Get stylesheet for OK/Confirm buttons."""
        c = self.colors
        return f"""
            QPushButton {{
                background-color: {c.success};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self._darken(c.success)};
            }}
        """
    
    def get_button_cancel_style(self) -> str:
        """Get stylesheet for Cancel/Delete buttons."""
        c = self.colors
        return f"""
            QPushButton {{
                background-color: {c.danger};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {self._darken(c.danger)};
            }}
        """
    
    @staticmethod
    def _darken(color: str, factor: float = 0.9) -> str:
        """Darken a hex color by a factor."""
        # Simple darkening - remove '#' and convert to int
        r = int(int(color[1:3], 16) * factor)
        g = int(int(color[3:5], 16) * factor)
        b = int(int(color[5:7], 16) * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def get_status_label_style(self) -> str:
        """Get stylesheet for status labels."""
        c = self.colors
        return f"QLabel {{ background-color: {c.scroll_area}; color: {c.text}; padding: 5px; }}"
    
    def get_scroll_area_style(self) -> str:
        """Get stylesheet for scroll areas."""
        c = self.colors
        return f"background-color: {c.scroll_area}; border: 1px solid {c.border};"


# Singleton instance for global use
_theme_manager: Optional[ThemeManager] = None


def get_theme() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager


def is_dark_mode() -> bool:
    """Quick check if dark mode is active."""
    return get_theme().is_dark


def get_colors() -> ThemeColors:
    """Get current theme colors."""
    return get_theme().colors

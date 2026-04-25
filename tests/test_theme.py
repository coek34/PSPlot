"""Tests for theme module."""

import pytest
import sys
from unittest.mock import patch, MagicMock

# Mock darkdetect before importing theme
sys.modules['darkdetect'] = MagicMock()
sys.modules['darkdetect'].theme = MagicMock(return_value='Dark')
sys.modules['darkdetect'].isDark = MagicMock(return_value=True)

from core.theme import (
    ThemeColors,
    ThemeManager,
    is_dark_mode,
    get_theme,
    get_colors,
)


class TestThemeColors:
    """Tests for ThemeColors dataclass."""
    
    def test_dark_colors_from_manager(self):
        """Test dark mode colors from ThemeManager."""
        manager = ThemeManager()
        colors = manager.colors
        
        assert colors.base == "#2b2b2b"
        assert colors.text == "#ffffff"
        assert colors.alt == "#3a3a3a"
        assert colors.scroll_area == "#3a3a3a"
        assert colors.border == "#444"
    
    def test_light_colors_from_manager(self):
        """Test light mode colors from ThemeManager."""
        manager = ThemeManager()
        manager._is_dark = False  # Force light mode
        colors = manager.colors
        
        assert colors.base == "#ffffff"
        assert colors.text == "#000000"
        assert colors.alt == "#fafafa"
        assert colors.scroll_area == "#f0f0f0"
        assert colors.border == "#ccc"
    
    def test_frozen_dataclass(self):
        """Test that ThemeColors is immutable."""
        manager = ThemeManager()
        colors = manager.colors
        
        with pytest.raises(Exception):
            colors.base = "#000000"


class TestThemeManager:
    """Tests for ThemeManager class."""
    
    def test_singleton(self):
        """Test that ThemeManager is accessed via get_theme()."""
        theme1 = get_theme()
        theme2 = get_theme()
        
        # Should be the same instance
        assert theme1 is theme2
    
    def test_default_theme(self):
        """Test default theme detection."""
        theme = ThemeManager()
        
        # Based on mocked darkdetect
        assert theme.is_dark is True
    
    def test_get_style_sheet(self):
        """Test that get_style_sheet returns non-empty string."""
        theme = ThemeManager()
        style = theme.get_style_sheet()
        
        assert isinstance(style, str)
        assert len(style) > 0
        assert "QMainWindow" in style or "QMenu" in style or "background-color" in style
    
    def test_get_status_label_style(self):
        """Test status label style generation."""
        theme = ThemeManager()
        style = theme.get_status_label_style()
        
        assert isinstance(style, str)
        assert "background-color" in style
        assert "color" in style
    
    def test_get_scroll_area_style(self):
        """Test scroll area style generation."""
        theme = ThemeManager()
        style = theme.get_scroll_area_style()
        
        assert isinstance(style, str)
        assert "background-color" in style
    
    def test_get_menu_style(self):
        """Test menu style generation."""
        theme = ThemeManager()
        style = theme.get_menu_style()
        
        assert isinstance(style, str)
        assert "QMenu" in style
    
    def test_get_tree_widget_style(self):
        """Test tree widget style generation."""
        theme = ThemeManager()
        style = theme.get_tree_widget_style()
        
        assert isinstance(style, str)
        assert "QTreeWidget" in style
    
    def test_get_button_ok_style(self):
        """Test OK button style generation."""
        theme = ThemeManager()
        style = theme.get_button_ok_style()
        
        assert isinstance(style, str)
        assert "background-color" in style
        assert theme.colors.success in style
    
    def test_get_button_cancel_style(self):
        """Test cancel button style generation."""
        theme = ThemeManager()
        style = theme.get_button_cancel_style()
        
        assert isinstance(style, str)
        assert "background-color" in style
        assert theme.colors.danger in style
    
    def test_darken_static_method(self):
        """Test the _darken static method."""
        original = "#4CAF50"
        darkened = ThemeManager._darken(original, 0.5)
        
        # Should return a darker color
        assert darkened.startswith('#')
        assert len(darkened) == 7


class TestIsDarkMode:
    """Tests for is_dark_mode function."""
    
    def test_detects_dark_mode(self):
        """Test dark mode detection."""
        # Based on mocked darkdetect.theme()
        assert is_dark_mode() is True
    
    def test_detects_light_mode(self):
        """Test light mode detection."""
        # Reset the singleton to test different mode
        import theme as theme_module
        old_manager = theme_module._theme_manager
        
        theme_module._theme_manager = None  # Reset singleton
        
        # Mock darkdetect for light mode
        sys.modules['darkdetect'].isDark = MagicMock(return_value=False)
        
        result = is_dark_mode()
        
        theme_module._theme_manager = old_manager  # Restore
        assert result is False


class TestGetColors:
    """Tests for get_colors function."""
    
    def test_returns_theme_colors(self):
        """Test that get_colors returns ThemeColors instance."""
        colors = get_colors()
        
        assert isinstance(colors, ThemeColors)
    
    def test_dark_colors_structure(self):
        """Test structure of dark mode colors."""
        manager = ThemeManager()
        colors = manager.colors
        
        # Check all required fields exist
        assert hasattr(colors, 'base')
        assert hasattr(colors, 'alt')
        assert hasattr(colors, 'scroll_area')
        assert hasattr(colors, 'text')
        assert hasattr(colors, 'border')
        assert hasattr(colors, 'border_light')
        assert hasattr(colors, 'selection')
        assert hasattr(colors, 'hover')
        assert hasattr(colors, 'status_bg')
        assert hasattr(colors, 'success')
        assert hasattr(colors, 'danger')
    
    def test_color_formats(self):
        """Test that colors are valid hex strings."""
        manager = ThemeManager()
        colors = manager.colors
        
        # All color values should start with # and be valid hex
        for attr_name in ['base', 'alt', 'scroll_area', 'text', 'border', 
                          'border_light', 'selection', 'hover', 'status_bg', 
                          'success', 'danger']:
            value = getattr(colors, attr_name)
            assert value.startswith('#')
            # Allow both #RGB and #RRGGBB formats
            hex_part = value[1:]
            assert len(hex_part) in (3, 6), f"Color {attr_name}={value} has invalid length"
            try:
                int(hex_part, 16)  # Verify valid hex
            except ValueError:
                raise AssertionError(f"Color {attr_name}={value} is not valid hex")


class TestThemeConsistency:
    """Tests for theme consistency across modes."""
    
    def test_colors_have_same_structure(self):
        """Test dark and light modes have same attributes."""
        manager = ThemeManager()
        
        # Get dark colors
        manager._is_dark = None  # Force re-detection
        sys.modules['darkdetect'].isDark = MagicMock(return_value=True)
        dark = manager.colors
        
        # Get light colors
        manager._is_dark = None
        sys.modules['darkdetect'].isDark = MagicMock(return_value=False)
        light = manager.colors
        
        dark_attrs = {k for k, v in dark.__dict__.items()}
        light_attrs = {k for k, v in light.__dict__.items()}
        
        assert dark_attrs == light_attrs
    
    def test_dark_colors_different_from_light(self):
        """Test that dark mode uses darker colors."""
        manager = ThemeManager()
        
        # Dark mode
        manager._is_dark = True
        dark_bg = int(manager.colors.base[1:], 16)
        
        # Light mode
        manager._is_dark = False
        light_bg = int(manager.colors.base[1:], 16)
        
        # Background should be darker in dark mode
        assert dark_bg < light_bg
    
    def test_success_danger_colors_consistent(self):
        """Test that success/danger colors are same across modes."""
        manager = ThemeManager()
        
        # Same colors in both modes
        assert ThemeManager.DARK.success == ThemeManager.LIGHT.success
        assert ThemeManager.DARK.danger == ThemeManager.LIGHT.danger


class TestStyleSheetContent:
    """Tests for style sheet content."""
    
    def test_style_sheet_contains_qt_selectors(self):
        """Test that style sheet contains Qt widget selectors."""
        theme = ThemeManager()
        style = theme.get_style_sheet()
        
        # Should contain common Qt selectors
        assert any(selector in style for selector in [
            'QWidget', 'QMainWindow', 'QPushButton', 'QLineEdit',
            'QComboBox', 'QMenu', 'QMenuBar', 'QStatusBar', 'QTabWidget'
        ])
    
    def test_style_sheet_uses_theme_colors(self):
        """Test that style sheet uses colors from theme."""
        theme = ThemeManager()
        colors = theme.colors
        style = theme.get_style_sheet()
        
        # Check that theme colors appear in stylesheet
        assert colors.base in style
        assert colors.text in style

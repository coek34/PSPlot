"""Tests for configuration module."""

import pytest
import logging
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from core import config
from core.config import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_WINDOW_SIZE,
    DEFAULT_WINDOW_POS,
    CANVAS_SIZES,
    SUBPLOT_SHORTCUTS,
    CanvasDefaults,
    SubplotConfig,
    MarginDefaults,
    ZoomConfig,
    KeyboardShortcuts,
    SignalDefaults,
    ExportConfig,
    setup_logging,
    get_status_text,
)


class TestConstants:
    """Tests for module-level constants."""
    
    def test_app_info(self):
        """Test application info constants."""
        assert APP_NAME == "PSPlotter"
        assert APP_VERSION == "1.0.0"
        assert "PSPlotter" in config.WINDOW_TITLE
    
    def test_window_defaults(self):
        """Test window default constants."""
        assert len(DEFAULT_WINDOW_SIZE) == 2
        assert DEFAULT_WINDOW_SIZE[0] == 1200
        assert DEFAULT_WINDOW_SIZE[1] == 900
        assert len(DEFAULT_WINDOW_POS) == 2
    
    def test_canvas_sizes(self):
        """Test canvas size constants."""
        assert "A4" in CANVAS_SIZES
        assert "Letter" in CANVAS_SIZES
        assert "A3" in CANVAS_SIZES
        assert "A5" in CANVAS_SIZES
        
        # Verify A4 dimensions
        assert CANVAS_SIZES["A4"] == (8.27, 11.69)
    
    def test_subplot_shortcuts(self):
        """Test subplot shortcut mappings."""
        assert SUBPLOT_SHORTCUTS[1] == '1'
        assert SUBPLOT_SHORTCUTS[6] == '6'
        assert len(SUBPLOT_SHORTCUTS) == 6


class TestCanvasDefaults:
    """Tests for CanvasDefaults dataclass."""
    
    def test_default_values(self):
        """Test default canvas dimensions."""
        defaults = CanvasDefaults()
        assert defaults.width == 8.27
        assert defaults.height == 11.69
    
    def test_custom_values(self):
        """Test custom canvas dimensions."""
        defaults = CanvasDefaults(width=11.0, height=17.0)
        assert defaults.width == 11.0
        assert defaults.height == 17.0


class TestSubplotConfig:
    """Tests for SubplotConfig dataclass."""
    
    def test_default_values(self):
        """Test default subplot configuration."""
        conf = SubplotConfig()
        assert conf.max_count == 6
        assert conf.min_count == 1
    
    def test_custom_values(self):
        """Test custom subplot configuration."""
        conf = SubplotConfig(max_count=4, min_count=0)
        assert conf.max_count == 4
        assert conf.min_count == 0


class TestMarginDefaults:
    """Tests for MarginDefaults dataclass."""
    
    def test_default_values(self):
        """Test default margin values."""
        margins = MarginDefaults()
        assert margins.left == 0.12
        assert margins.right == 0.95
        assert margins.top == 0.95
        assert margins.bottom == 0.12
    
    def test_as_dict(self):
        """Test as_dict method."""
        margins = MarginDefaults()
        d = margins.as_dict()
        
        assert isinstance(d, dict)
        assert d['left'] == 0.12
        assert d['right'] == 0.95
        assert d['top'] == 0.95
        assert d['bottom'] == 0.12


class TestZoomConfig:
    """Tests for ZoomConfig dataclass."""
    
    def test_default_values(self):
        """Test default zoom configuration."""
        zoom = ZoomConfig()
        assert zoom.x_pan_factor == 0.2
        assert zoom.reset_zoom_padding == 0.05


class TestKeyboardShortcuts:
    """Tests for KeyboardShortcuts dataclass."""
    
    def test_shortcut_values(self):
        """Test shortcut constants."""
        assert KeyboardShortcuts.NEW_PLOT == 'N'
        assert KeyboardShortcuts.IMPORT_DATA == 'C'
        assert KeyboardShortcuts.EXPORT_ALL == 'E'
        assert KeyboardShortcuts.RESET_X_ZOOM == 'R'
        assert KeyboardShortcuts.RESET_Y_ZOOM == 'Y'
        assert KeyboardShortcuts.ROUND_X_GRID == 'X'
        assert KeyboardShortcuts.ADJUST_MARGINS == 'M'
        assert KeyboardShortcuts.PAN_LEFT == 'A'
        assert KeyboardShortcuts.PAN_RIGHT == 'D'
    
    def test_get_all_shortcuts(self):
        """Test get_all_shortcuts method."""
        shortcuts = KeyboardShortcuts.get_all_shortcuts()
        
        assert isinstance(shortcuts, dict)
        assert shortcuts['N'] == 'New Plot'
        assert shortcuts['C'] == 'Import Data'
        assert shortcuts['E'] == 'Export All'
        assert 'R' in shortcuts
        assert 'Y' in shortcuts


class TestSignalDefaults:
    """Tests for SignalDefaults dataclass."""
    
    def test_default_values(self):
        """Test default signal settings."""
        defaults = SignalDefaults()
        assert defaults.default_channel_name == "Unknown"
        assert defaults.default_group_name == "Unknown"
        assert defaults.default_signal_name == "Unknown Signal"
        assert defaults.tree_expanded_by_default is True


class TestExportConfig:
    """Tests for ExportConfig dataclass."""
    
    def test_default_values(self):
        """Test default export configuration."""
        config = ExportConfig()
        assert config.default_dpi == 300
        assert '.png' in config.supported_formats
        assert '.pdf' in config.supported_formats
        assert '.svg' in config.supported_formats
        assert '.jpg' in config.supported_formats
        assert config.default_format == '.png'


class TestSetupLogging:
    """Tests for setup_logging function."""
    
    def test_setup_logging_with_defaults(self, tmp_path):
        """Test logging setup with default parameters."""
        # Reset handlers
        root_logger = logging.getLogger()
        root_logger.handlers = []
        root_logger.setLevel(logging.WARNING)  # Reset to default
        
        # Patch Path.home() to use temp directory
        with patch.object(Path, 'home', return_value=tmp_path):
            setup_logging()
            
            # Verify logging was configured
            assert len(root_logger.handlers) >= 2  # console + file
            assert logging.getLogger("matplotlib").level == logging.WARNING
            
        # Clean up
        root_logger.handlers = []
        root_logger.setLevel(logging.WARNING)
    
    def test_setup_logging_custom_level(self):
        """Test logging setup with custom level."""
        # Reset handlers
        root_logger = logging.getLogger()
        root_logger.handlers = []
        
        setup_logging(log_level=logging.DEBUG)
        
        assert root_logger.level == logging.DEBUG
    
    def test_setup_logging_custom_file(self, tmp_path):
        """Test logging setup with custom file path."""
        log_file = tmp_path / "custom.log"
        
        # Reset handlers
        root_logger = logging.getLogger()
        root_logger.handlers = []
        
        setup_logging(log_file=str(log_file))
        
        assert log_file.parent.exists()
    
    def test_matplotlib_loggers_silenced(self):
        """Test that matplotlib loggers are set to WARNING level."""
        # Reset handlers
        root_logger = logging.getLogger()
        root_logger.handlers = []
        
        setup_logging()
        
        assert logging.getLogger("matplotlib").level == logging.WARNING
        assert logging.getLogger("matplotlib.font_manager").level == logging.WARNING
        assert logging.getLogger("PIL").level == logging.WARNING


class TestGetStatusText:
    """Tests for get_status_text function."""
    
    def test_contains_shortcuts(self):
        """Test that status text contains keyboard shortcuts."""
        status = get_status_text()
        
        assert "Keys:" in status
        assert "1-6" in status  # Subplot shortcuts
        assert "A/D" in status or "A" in status  # Pan shortcuts
        assert "R" in status  # Reset X
        assert "Y" in status  # Reset Y
        assert "X" in status  # Round X
        assert "E" in status  # Export
        assert "M" in status  # Margins
    
    def test_contains_instructions(self):
        """Test that status text contains instructions."""
        status = get_status_text()
        
        assert "plots" in status
        assert "pan" in status
        assert "export" in status
        assert "margins" in status


class TestSingletonInstances:
    """Tests that singleton instances are properly created."""
    
    def test_singletons_exist(self):
        """Test that singleton instances exist."""
        # These are imported at module level
        assert hasattr(config, 'CANVAS_DEFAULTS')
        assert hasattr(config, 'SUBPLOT_CONFIG')
        assert hasattr(config, 'MARGIN_DEFAULTS')
        assert hasattr(config, 'ZOOM_CONFIG')
        assert hasattr(config, 'SIGNAL_DEFAULTS')
        assert hasattr(config, 'EXPORT_CONFIG')
    
    def test_instance_types(self):
        """Test that instances are correct types."""
        assert isinstance(config.CANVAS_DEFAULTS, CanvasDefaults)
        assert isinstance(config.SUBPLOT_CONFIG, SubplotConfig)
        assert isinstance(config.MARGIN_DEFAULTS, MarginDefaults)
        assert isinstance(config.ZOOM_CONFIG, ZoomConfig)
        assert isinstance(config.SIGNAL_DEFAULTS, SignalDefaults)
        assert isinstance(config.EXPORT_CONFIG, ExportConfig)

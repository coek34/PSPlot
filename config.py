"""Configuration module for PSPlot - centralized constants and defaults.

This module contains all magic numbers, default values, and application-wide
constants to ensure consistency across the codebase.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

# Version info
APP_NAME = "PSPlotter"
APP_VERSION = "1.0.0"
WINDOW_TITLE = f"{APP_NAME} - Power System Results Plotter"

# Window defaults
DEFAULT_WINDOW_SIZE = (1200, 900)  # width, height in pixels
DEFAULT_WINDOW_POS = (100, 100)    # x, y position


@dataclass(frozen=True)
class CanvasDefaults:
    """Default canvas dimensions and settings."""
    # Default A4 size in inches
    width: float = 8.27
    height: float = 11.69
    
    # Common paper sizes (width, height in inches)
    SIZES: Dict[str, Tuple[float, float]] = {
        'A4': (8.27, 11.69),
        'Letter': (8.5, 11.0),
        'A3': (11.69, 16.53),
        'A5': (5.83, 8.27),
    }


@dataclass(frozen=True)
class SubplotConfig:
    """Subplot configuration constants."""
    max_count: int = 6
    min_count: int = 1
    
    # Keyboard shortcuts for subplot counts
    shortcuts: Dict[int, str] = {
        1: '1',
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6',
    }


@dataclass(frozen=True)
class MarginDefaults:
    """Default plot margins (fractions of figure size)."""
    left: float = 0.12
    right: float = 0.95
    top: float = 0.95
    bottom: float = 0.12
    
    @classmethod
    def as_dict(cls) -> Dict[str, float]:
        return {
            'left': cls.left,
            'right': cls.right,
            'top': cls.top,
            'bottom': cls.bottom,
        }


@dataclass(frozen=True)
class ZoomConfig:
    """Zoom and pan behavior settings."""
    x_pan_factor: float = 0.2  # Fraction of view to pan with A/D keys
    reset_zoom_padding: float = 0.05  # Padding when resetting zoom
    
    
@dataclass(frozen=True)
class KeyboardShortcuts:
    """Application keyboard shortcuts."""
    # File operations
    NEW_PLOT = 'N'
    IMPORT_DATA = 'C'
    EXPORT_ALL = 'E'
    
    # View operations
    RESET_X_ZOOM = 'R'
    RESET_Y_ZOOM = 'Y'
    ROUND_X_GRID = 'X'
    
    # Settings
    ADJUST_MARGINS = 'M'
    
    # Subplot navigation (1-6 handled by SubplotConfig)
    PAN_LEFT = 'A'
    PAN_RIGHT = 'D'
    
    @classmethod
    def get_all_shortcuts(cls) -> Dict[str, str]:
        """Get all shortcuts as a dictionary."""
        return {
            cls.NEW_PLOT: 'New Plot',
            cls.IMPORT_DATA: 'Import Data',
            cls.EXPORT_ALL: 'Export All',
            cls.RESET_X_ZOOM: 'Reset X-Zoom',
            cls.RESET_Y_ZOOM: 'Reset Y-Zoom',
            cls.ROUND_X_GRID: 'Round X to Grid',
            cls.ADJUST_MARGINS: 'Adjust Margins',
            cls.PAN_LEFT: 'Pan Left',
            cls.PAN_RIGHT: 'Pan Right',
        }


@dataclass(frozen=True)
class SignalDefaults:
    """Default values for signal data."""
    default_channel_name: str = "Unknown"
    default_group_name: str = "Unknown"
    default_signal_name: str = "Unknown Signal"
    
    # Signal tree display settings
    tree_expanded_by_default: bool = True
    

@dataclass(frozen=True)
class ExportConfig:
    """Export settings."""
    default_dpi: int = 300
    supported_formats: Tuple[str, ...] = ('.png', '.pdf', '.svg', '.jpg')
    default_format: str = '.png'


# Create singleton instances for import
CANVAS_DEFAULTS = CanvasDefaults()
SUBPLOT_CONFIG = SubplotConfig()
MARGIN_DEFAULTS = MarginDefaults()
ZOOM_CONFIG = ZoomConfig()
SIGNAL_DEFAULTS = SignalDefaults()
EXPORT_CONFIG = ExportConfig()


def get_status_text() -> str:
    """Get the status bar hint text."""
    return (
        f"Keys: 1-{SUBPLOT_CONFIG.max_count} (plots) | "
        f"{KeyboardShortcuts.PAN_LEFT}/{KeyboardShortcuts.PAN_RIGHT} (pan) | "
        f"{KeyboardShortcuts.RESET_X_ZOOM} (reset x) | "
        f"{KeyboardShortcuts.RESET_Y_ZOOM} (reset y) | "
        f"{KeyboardShortcuts.ROUND_X_GRID} (grid) | "
        f"{KeyboardShortcuts.EXPORT_ALL} (export) | "
        f"{KeyboardShortcuts.ADJUST_MARGINS} (margins) | "
        "Double-click tabs to rename pages"
    )

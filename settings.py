import json
import logging
import os
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Use the standard macOS Application Support directory for settings
if sys.platform == 'darwin':
    # ~/Library/Application Support/PSPlot
    SETTINGS_DIR = Path.home() / "Library" / "Application Support" / "PSPlot"
else:
    # Fallback/Default
    SETTINGS_DIR = Path(__file__).parent

SETTINGS_FILE = SETTINGS_DIR / "settings.psp"

@dataclass
class PageState:
    name: str
    width: float
    height: float
    subplot_count: int
    margins: Dict[str, float]
    # Current x-axis limits [min, max]
    x_limits: Optional[List[float]] = None
    # Custom y-labels for each subplot index
    y_labels: Dict[int, str] = field(default_factory=dict)
    # List of subplots, each contains a list of signal references
    # Signal ref: {"file_path": str, "channel": str, "group": str, "name": str}
    subplots_signals: List[List[Dict[str, str]]] = field(default_factory=list)

@dataclass
class AppState:
    pages: List[PageState] = field(default_factory=list)
    current_page_index: int = 0
    imported_files: List[str] = field(default_factory=list)

@dataclass
class UserPreferences:
    theme: str = "auto"  # auto, light, dark
    last_import_dir: str = str(Path.home())
    last_export_dir: str = str(Path.home())
    window_geometry: Optional[List[int]] = None # [x, y, w, h]

class SettingsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.preferences = UserPreferences()
        self.state = AppState()
        self.load()
        self._initialized = True

    def load(self):
        """Load settings from JSON file."""
        if not SETTINGS_FILE.exists():
            return

        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                
            # Load preferences
            prefs_data = data.get("preferences", {})
            self.preferences = UserPreferences(**{k: v for k, v in prefs_data.items() if k in UserPreferences.__dataclass_fields__})
            
            # Load state
            state_data = data.get("state", {})
            pages_data = state_data.get("pages", [])
            
            pages = []
            for p in pages_data:
                pages.append(PageState(**p))
            
            self.state = AppState(
                pages=pages,
                current_page_index=state_data.get("current_page_index", 0),
                imported_files=state_data.get("imported_files", [])
            )
            logger.info("Settings loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")

    def save(self):
        """Save settings to JSON file."""
        try:
            SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                "preferences": asdict(self.preferences),
                "state": asdict(self.state)
            }
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"Settings saved to {SETTINGS_FILE}")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

def get_settings():
    return SettingsManager()

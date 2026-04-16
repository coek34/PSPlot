# PSPlot Improvement Roadmap

This document tracks planned improvements and technical debt for the PSPlot application.

**Last Updated:** 2026-04-16  
**Current Version:** 1.0.0  
**Status:** Active Development

---

## ✅ Completed Improvements

### High Priority (Done)

| # | Improvement | Status | Commit |
|---|-------------|--------|--------|
| 1 | **Theme Consolidation** | ✅ Complete | `849e61c` - Centralized ThemeManager with ThemeColors dataclass |
| 2 | **Configuration Module** | ✅ Complete | `5b6b528` - Extracted magic numbers to config.py constants |
| 3 | **Signal Dataclass** | ✅ Complete | `5b6b528` - Replaced fragile dict-based signal data with Signal dataclass |
| 4 | **Logging Infrastructure** | ✅ Complete | `de3fc89` - setup_logging() with rotating file handlers, reduced matplotlib spam |
| 5 | **Type Hints** | ✅ Complete | `de3fc89` - Full type annotations in main.py, config.py, models.py |
| 6 | **Input Validation** | ✅ Complete | `de3fc89` - New validation.py module with comprehensive validators |
| 7 | **Fix Mutable Defaults** | ✅ Complete | `f567aec` - Moved mutable dicts from dataclass fields to module-level constants |

### Summary of Completed Work

**New Modules Created:**
- `theme.py` - ThemeManager singleton, color management, is_dark_mode(), button styles
- `config.py` - All magic numbers, constants, singletons (CanvasDefaults, SubplotConfig, etc.)
- `models.py` - Data models: Signal, SignalGroup, Channel, ImportedData dataclasses
- `validation.py` - Input validation: file paths, signal names, colors, margins

**Files Modified:**
- `main_window.py` - Uses theme and config imports, centralized styling
- `signal_explorer.py` - Theme-aware colors, removed hardcoded #4CAF50
- `canvas_manager.py` - Theme imports for menu styling
- `plot_modules/canvas_base.py` - Theme method usage for dialogs
- `page_widget.py` - Theme imports for scroll area styling

---

## 🚧 Pending Improvements

### HIGH IMPACT (Recommended Next)

#### 1. Unit Tests ⭐ PRIORITY
**Effort:** Medium | **Impact:** High | **Risk:** Low

Test coverage for new validation and model logic:

```
tests/
├── test_models.py          # Signal, SignalGroup, Channel tests
├── test_validation.py      # validate_*, sanitize_* tests
├── test_config.py          # Config singleton tests
└── test_theme.py           # Theme color switching tests
```

**Test Cases Needed:**
- Signal validation: empty name, mismatched arrays, invalid colors
- Signal.from_dict() with missing keys, type conversions
- validate_file_path() with non-existent files, wrong extensions
- validate_margins() with invalid ranges, wrong types
- sanitize_filename() with forbidden characters
- ThemeColors dark/light switching

**Tech Stack:** pytest, pytest-cov for coverage

---

#### 2. Configuration Persistence
**Effort:** Medium | **Impact:** High | **Risk:** Low

Save and restore user preferences between sessions.

**Settings to Persist:**
- Window size and position
- Last used import directory
- Export directory
- Theme preference (if manual toggle added)
- Recently used files (MRU list)
- Default subplot count
- Custom margin presets

**Implementation:**
- Use `~/.config/psplot/settings.json` (XDG compliant)
- Or `~/.psplot/settings.json` for simplicity
- JSON format for human readability
- Auto-save on exit, load on startup

**Example Code:**
```python
# settings.py
import json
from pathlib import Path

SETTINGS_FILE = Path.home() / ".psplot" / "settings.json"

def load_settings() -> dict:
    if SETTINGS_FILE.exists():
        return json.loads(SETTINGS_FILE.read_text())
    return {}

def save_settings(settings: dict) -> None:
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps(settings, indent=2))
```

---

#### 3. Recent Files Menu
**Effort:** Low | **Impact:** Medium | **Risk:** Low

Quick access to last opened files.

**Requirements:**
- "Recent Files" submenu under File menu
- Max 5-10 files
- Persist in settings.json
- Clear recent files option
- Handle missing files gracefully

**UI Integration:**
```python
# In main_window.py menu setup
self.recent_files_menu = self.file_menu.addMenu("Recent Files")
self.update_recent_files_menu()

def update_recent_files_menu(self):
    self.recent_files_menu.clear()
    for file_path in settings.get_recent_files():
        action = QAction(file_path, self)
        action.triggered.connect(lambda: self.open_recent_file(file_path))
        self.recent_files_menu.addAction(action)
```

---

#### 4. Error Handling & User Feedback
**Effort:** Medium | **Impact:** High | **Risk:** Medium

Wrap operations in try-except with QMessageBox for user-friendly errors.

**Operations to Wrap:**
- File import (PSCAD, CSV, etc.)
- Export operations
- Plot configuration changes
- Memory-intensive operations (large datasets)

**Example Pattern:**
```python
from PyQt5.QtWidgets import QMessageBox

def safe_import_file(self, file_path: str) -> bool:
    try:
        self.import_file(file_path)
        return True
    except FileValidationError as e:
        QMessageBox.warning(self, "Import Failed", str(e))
    except Exception as e:
        logger.exception("Unexpected import error")
        QMessageBox.critical(
            self, 
            "Import Error", 
            f"An unexpected error occurred:\n{str(e)}\n\n"
            "Please check the log file for details."
        )
    return False
```

---

### MEDIUM IMPACT

#### 5. Progress Indicators
**Effort:** Medium | **Impact:** Medium | **Risk:** Low

Loading dialog for long operations.

**Use Cases:**
- Large file imports (>100MB)
- Bulk export operations
- Signal processing on many channels

**Implementation:**
- QProgressDialog for simple cases
- Custom dialog with cancel button for long operations
- Threading to keep UI responsive

---

#### 6. Search/Filter in Signal Tree
**Effort:** Medium | **Impact:** Medium | **Risk:** Low

Text filter for finding signals quickly in large datasets.

**Features:**
- Search bar above signal tree
- Filter by name, group, or channel
- Highlight matching items
- Clear filter button
- Regex support (optional)

---

#### 7. Keyboard Shortcuts Audit
**Effort:** Low | **Impact:** Medium | **Risk:** Low

Verify all shortcuts in `KeyboardShortcuts` enum are wired up.

**Shortcuts Defined in config.py:**
- NEW_PLOT = 'N'
- IMPORT_DATA = 'C'
- EXPORT_ALL = 'E'
- RESET_X_ZOOM = 'R'
- RESET_Y_ZOOM = 'Y'
- ROUND_X_GRID = 'X'
- ADJUST_MARGINS = 'M'
- PAN_LEFT = 'A'
- PAN_RIGHT = 'D'

**Audit Checklist:**
- [ ] Verify each shortcut is connected in main_window.py
- [ ] Check for conflicts with text input fields
- [ ] Add shortcut hints to menu items
- [ ] Document in README

---

#### 8. Auto-save Plot State
**Effort:** Medium | **Impact:** Medium | **Risk:** Medium

Periodic save of current plot state for crash recovery.

**Auto-save Every 60 seconds:**
- Current subplot configuration
- Y-axis label states
- Signal visibility settings
- Which signals are plotted where

**Implementation:**
- QTimer in main_window.py
- Save to `~/.psplot/autosave/` with timestamp
- Clean up old autosaves (keep last 10)
- Offer recovery on startup after crash

---

### LOWER PRIORITY / NICE TO HAVE

#### 9. Dark Mode Toggle
**Effort:** Low | **Impact:** Medium | **Risk:** Low

Manual theme override despite system settings.

**UI:** View menu → Theme → Auto / Light / Dark

---

#### 10. Export Preview
**Effort:** High | **Impact:** Medium | **Risk:** Medium

Show thumbnail preview before exporting.

**Challenges:**
- Render subplot at low resolution quickly
- Handle multiple subplots in single view

---

#### 11. Drag & Drop Signals
**Effort:** High | **Impact:** Medium | **Risk:** High

Drag signals from tree to subplots or between subplots.

**Implementation:**
- Qt drag-drop events
- MIME data for signal IDs
- Visual feedback during drag

---

#### 12. Tooltips
**Effort:** Low | **Impact:** Low | **Risk:** Low

Add helpful tooltips to UI elements.

**Candidates:**
- Signal tree items (show full path)
- Toolbar buttons
- Menu items
- Plot area (show keyboard shortcuts)

---

### INFRASTRUCTURE

#### 13. Pre-commit Hooks
**Effort:** Low | **Impact:** Medium | **Risk:** None**

Automated code quality checks on commit.

**Tools:**
- black (formatting)
- ruff (linting)
- mypy (type checking)

**Setup:**
```bash
pip install pre-commit
pre-commit install
```

---

#### 14. CI/CD Pipeline
**Effort:** Medium | **Impact:** Medium | **Risk:** None**

GitHub Actions workflow for automated testing.

**Workflow:**
- Run pytest on Python 3.10, 3.11, 3.12
- Run type checking with mypy
- Run linting with ruff
- Build and test PyQt5 app

---

#### 15. Packaging & Distribution
**Effort:** Medium | **Impact:** High | **Risk:** Low

Prepare for distribution.

**Tasks:**
- Add pyproject.toml with proper metadata
- Create entry point script
- Add __main__.py for `python -m psplot`
- Consider PyInstaller for standalone executable

---

## 📊 Technical Debt

### Known Issues

1. **Matplotlib font warnings** - Reduced but still some noise on startup
2. **Dummy signal logic** - Traversal pattern scattered across files
3. **PSCAD importer** - No test coverage, fragile parsing
4. **Y-axis label dialog** - Could use theme.get_dialog_style() consistently

### Code Organization

**Good:**
- ✓ Manager pattern for plots
- ✓ Centralized configuration
- ✓ Theme system extracted
- ✓ Type hints added

**Needs Work:**
- Some files still too long (>500 lines)
- Plot module imports are tightly coupled
- No dependency injection for testing

---

## 🎯 Next Sprint Recommendations

### Sprint 1: Stability
1. ✅ Unit tests (validation.py, models.py)
2. ✅ Error handling with QMessageBox
3. ✅ Configuration persistence

### Sprint 2: UX Polish
4. Recent files menu
5. Keyboard shortcuts audit + fixes
6. Auto-save plot state
7. Tooltips throughout UI

### Sprint 3: Performance
8. Progress indicators for large imports
9. Signal tree search/filter
10. Optimize large dataset rendering

### Sprint 4: Distribution
11. Pre-commit hooks
12. CI/CD pipeline
13. Packaging (pyproject.toml)

---

## 📝 Notes

### Development Guidelines

**Remember:**
- Use `uv run python3 main.py` for testing
- Commit with descriptive messages following conventional commits
- Run `git status` before committing to avoid unintended changes
- Test on both light and dark macOS themes
- Add log messages for new features

### Testing Commands

```bash
# Run app
uv run python3 main.py

# Run tests (when added)
uv run pytest

# Type checking
uv run mypy .

# Linting
uv run ruff check .
```

---

*Last updated by: Hermes Agent*  
*Status: Ready for next sprint*

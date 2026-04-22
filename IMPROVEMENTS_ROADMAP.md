# PSPlot Improvement Roadmap

This document tracks planned improvements and technical debt for the PSPlot application.

**Last Updated:** 2026-04-20  
**Current Version:** 1.1.0  
**Status:** Active Development

---

## ✅ Completed Improvements

### High Priority (Done)

| # | Improvement | Status | Details |
|---|-------------|--------|---------|
| 1 | **Theme Consolidation** | ✅ | Centralized ThemeManager with ThemeColors dataclass |
| 2 | **Configuration Module** | ✅ | Extracted constants and config singletons to config.py |
| 3 | **Signal Dataclass** | ✅ | Replaced fragile dict-based signal data with Signal dataclass |
| 4 | **Logging Infrastructure** | ✅ | setup_logging() with rotating file handlers |
| 5 | **Type Hints** | ✅ | Full type annotations across major modules |
| 6 | **Input Validation** | ✅ | New validation.py with comprehensive validators |
| 7 | **Fix Mutable Defaults** | ✅ | Cleaned up mutable defaults in dataclasses |
| 8 | **Configuration Persistence** | ✅ | Save/Restore window geometry and app state via settings.json |
| 9 | **Auto-save Plot State** | ✅ | Automatic state gathering and saving on application close |
| 10| **Kursor Measurement Fix** | ✅ | Fixed crash when removing kursor artists after ax.clear() |
    | 11| **NumPy Array Conversion** | ✅ | Fixed TypeError in Reset Y Zoom by forcing np.asarray() |
    | 12| **Search & Filter in Signal Tree** | ✅ | Added search bar to Signal Explorer for rapid signal discovery |
    | 13| **Quick Scaling** | ✅ | Implemented per-signal scaling via right-click 'Skala' with .psp persistence |
    
    ---

## 🚧 Pending Improvements

### 🔴 HIGH PRIORITY: Research & Analysis
*   **Multi-Format Support**: Expand the data management layer to support **COMTRADE (IEEE C37.111)** and generic **CSV** files, allowing PSPlot to analyze data from hardware-in-the-loop (HIL) tests and other simulation tools.
|   **CLI & Batch Processing**: Implement a Command Line Interface to process multiple PSCAD files automatically using layout templates (.psp), enabling high-throughput analysis without manual GUI interaction.
*   **FFT Analysis Window**: Add a dedicated window/pane for Fast Fourier Transform (FFT) analysis of zoomed signals.
*   **THD Calculation**: Automatic Total Harmonic Distortion calculation on measurement cursors.
*   **Filtering Modules**: Implementation of Low-pass, High-pass, and Moving Average filters in the UI.
*   **SCR Estimation Integration**: Special visualization mode for Short-Circuit Ratio (SCR) time-series estimation data.

### 🟡 MEDIUM PRIORITY: UX & Workflow
*   **Session Templating**: Advanced export/import of `.psp` files to allow applying a layout to different simulation files (Templating).
*   **Multi-File Comparison (Overlay)**: Automated mode to plot signals from multiple `.out` files on a single subplot for comparison.
*   **Batch Export & LaTeX Support**: Workflow to export all pages as high-quality PDFs and generate LaTeX inclusion code.
*   **Unit Tests**: (tests/test_models.py, test_validation.py) - Verify core logic and prevent regressions.

### 🔵 LOW PRIORITY: Interface Polish
*   **Hover Tooltip/Data Inquiry**: Display (x, y) coordinates on mouse hover over plot lines.
*   **Drag & Drop Signals**: UI interaction to drag signals from tree to axes or between subplots.
*   **Adjustable Subplot Heights**: Interactive resizing of subplot row heights.
*   **Recent Files (MRU)**: Submenu in 'File' menu for recently opened PSCAD files.
*   **Background Data Loading**: Move heavy CSV/OUT reading to a separate thread to prevent UI freezing.

---

## 📊 Technical Debt
1. **Matplotlib Font Performance**: Optimizing startup time spent on font cache scanning.
2. **PSCAD Importer Robustness**: Further refining .inf parsing for edge cases in signal names.
3. **Signal Tree Sync**: Ensuring real-time sync if underlying .inf files change during a session.

---

*Last updated by: Hermes Agent*  
*Status: Roadmap updated with Quick Scaling and Search completion.*

# PSPlot Improvement Roadmap

This document tracks planned improvements and technical debt for the PSPlot application.

**Last Updated:** 2026-04-26  
**Current Version:** 1.5.0 (Pakuwon Jogja Edition)  
**Status:** Active Development

---

## ✅ Completed Improvements

### Phase 4: Professional Packaging & UI Polish (April 2026)
| # | Improvement | Status | Details |
|---|-------------|--------|---------|
| 26| **Modular Packaging** | ✅ | Restructured code into a formal `psplot/` namespace package with `pyproject.toml` |
| 27| **Cross-Platform Support** | ✅ | Standard paths for Settings/Logs on macOS, Windows (%APPDATA%), and Linux |
| 28| **"Scorched Earth" Clear** | ✅ | Guaranteed clean subplot after clearing signals (flushing artists & legends) |
| 29| **Legend Persistence** | ✅ | "Channel/Group name in legend" settings now persist in `.psp` state files |
| 30| **Measurement Reset** | ✅ | Double-click status bar measurement label to reset cursors to 25%/75% view |
| 31| **Interactive Debug Mode** | ✅ | Toggleable Log level (WARNING/INFO) via Settings menu with session persistence |
| 32| **UI Bug Squashing** | ✅ | Fixed ghost cursors during layout change, locked keys 1-6 in Cursor Mode, and fixed About icon |
| 33| **Asset Consolidation** | ✅ | Centralized all images/icons into `psplot/assets/` using `importlib.resources` |
| 34| **Git/GitHub Hygiene** | ✅ | Streamlined `requirements.txt` from 161 to 6 essential libs and tightened `.gitignore` |

### Phase 1-3: Core Stability & Fieldwork Features
*(Previous milestones including PSCAD, COMTRADE, CSV support, Theme centralization, and Keyboard Shortcuts audit are fully completed and validated in previous sprints).*

---

## 🚧 Pending Improvements

### 🔴 HIGH PRIORITY: Advanced Visualization
*   **Bar Chart Mode**: Implement bar chart visualization for statistical analysis and harmonic magnitudes.
*   **Dual Y-Axis Support**: Allow sharing the same X-axis with two independent Y-axes for signals with different units (e.g., Voltage and Current).
*   **X-Y Plot (Trajectory)**: Add a mode to plot one signal against another (X vs Y) for Phase Portrait or Lissajous-style analysis.
*   **FFT & Harmonic Analysis**: Dedicated window for real-time Fast Fourier Transform and harmonic spectrum visualization.

### 🔴 HIGH PRIORITY: Research & Automation
*   **CLI & Batch Processing**: Command Line Interface to apply `.psp` templates to batches of PSCAD/COMTRADE files for mass-export.
*   **SCR Estimation Integration**: Visualization module for time-series Short-Circuit Ratio estimations in weak grid studies.

### 🟡 MEDIUM PRIORITY: UX & Workflow
*   **Multi-File Overlay Comparison**: Automated comparison mode to overlay signals from multiple studies/files on a single subplot.
*   **Hover Data Inquiry**: Real-time (x, y) coordinate tooltips on mouse hover.
*   **Draggable Subplot Rows**: Interactive GUI to adjust individual subplot vertical spacing.

---

## 📊 Technical Debt
1. **GitHub Documentation Ops**: Automating screenshot updates when UI changes.
2. **Matplotlib Backend Optimization**: Ensuring maximum FPS on high-Hz displays (ProMotion/Windows VRR).
3. **Data Threading**: Refactoring file readers into QThreads to prevent UI blocking during 500MB+ COMTRADE loads.

---

*Developed by Dr. Roni Irnawan - Universitas Gadjah Mada*  
*Last updated by: Hermes Agent*  
*Status: Roadmap updated following the "Pakuwon Jogja" UI & Data Handling Sprint.*

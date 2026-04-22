# PSPlot: Power System Signal Analysis Tool

![PSPlot UI Mockup](psplot_ui_mockup.svg)

PSPlot is a high-performance, PyQt5-based visualization and analysis tool designed for electrical engineers and researchers. It specializes in processing large-scale transient data from simulation environments (PSCAD) and field recordings (IEEE COMTRADE).

## 🚀 Capabilities

- **Multi-Format Support**: 
  - **PSCAD**: Native support for `.inf` and `.out` file pairs.
  - **IEEE COMTRADE**: Full compatibility with C37.111-1991, 1999, and 2013 standards (ASCII and Binary formats).
- **Advanced Visualization**: 
  - Synchronized multi-subplot scrolling and zooming.
  - Interactive measurement cursors (Shortcut: `T`).
- **Quick Scaling Tool**: Right-click any signal to apply real-time scaling factors (e.g., CT/PT ratios) without modifying the raw data.
- **Session Persistence**: Save and reload your workspace configurations (layouts, scaling, and signals) using `.psp` session files.
- **Fieldwork Optimized**: High-contrast UI theme designed for technical audits and on-site analysis (tested at PHR Duri sites).

## 🛠 Installation

PSPlot uses the `uv` package manager for fast, reproducible environment setup.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/irnawan/PSPlot.git
   cd PSPlot
   ```

2. **Setup environment**:
   ```bash
   # Using uv (Recommended)
   uv venv
   uv pip install -r requirements.txt
   ```

3. **Dependencies**:
   - Python 3.10+
   - PyQt5
   - NumPy
   - Matplotlib

## 📖 How to Use

### 1. Importing Data
Launch the application and click **File > Import Data** (Shortcut: `C`). 
- For PSCAD: Select the `.inf` file.
- For COMTRADE: Select the `.cfg` file.

### 2. Signal Explorer
The **Signal Explorer** on the left allows you to:
- Browse signals organized by type (Analog/Digital).
- Drag and drop signals directly into any subplot.
- Right-click for **Quick Scale** (Multiplier/Gain setup).

### 3. Managing Layouts
Double-click a signal in the tree to add it to a new plot, or use keyboard shortcuts to change the window layout instantly.

### 4. Keyboard Shortcuts Reference
Used for rapid analysis during field sessions:

| Key | Action |
| :--- | :--- |
| **`T`** | Toggle Measurement Cursors |
| **`1` - `6`** | Change number of subplots (1 to 6) |
| **`A` / `D`** | Pan Left / Right |
| **`R` / `Y`** | Reset Zoom (R = X-Axis, Y = Y-Axis) |
| **`X`** | Snap/Round X-Axis to Grid |
| **`C`** | Import Data Dialog |
| **`N`** | Add a new blank page/canvas |
| **`E`** | Export current page to PDF |
| **`M`** | Adjust Plot Margins |
| **`P`** | Resize canvas/page dimensions |
| **`Ctrl+Q`** | Exit Application |

---
*Developed by Roni Irnawan, Ph.D. - Universitas Gadjah Mada*

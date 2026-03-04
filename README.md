# STOMP Node Output GUI

Python GUI tool for visualizing STOMP simulation node output data.

## Features

- **Interactive visualization** of STOMP reference-node outputs
- **Node selection** with IJK coordinate display
- **Variable customization**: rename labels, apply multipliers for unit conversion
- **Flexible axes**: x-axis unit conversion (seconds/hours/days/years), log scales, custom y-axis labels
- **Drag-and-drop** file loading (with tkinterdnd2)
- **CSV export** of selected node data
- **Fast parsing** optimized for large files (612K+ rows)
- **Progress tracking** during file loading

## Screenshots

### Main Interface
![Figure 1](docs/images/Figure1.png)

### GUI with Data Loaded
![GUI Screenshot](docs/images/Screenshot%20GUI.png)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the GUI:**
   ```bash
   python3 node_output_gui_v1.py
   ```

3. **Load sample file:**
   ```
   results/output_ex.txt
   ```

4. **Select nodes and variables** to visualize

## Case Study: Frio Formation Analysis

**Input:** STOMP simulation output for CO₂ storage in Frio Formation
- **File size:** 612,000 rows, 15.45 MB
- **Reference nodes:** 3 monitoring wells
- **Variables inspected:** 
  - Pressure (PG, PL) — tracking plume migration
  - Saturation (SG) — water/gas interface
  - Temperature (T) — thermodynamic changes
- **Time range:** ~500 days of simulation
- **Insight:** Pressure buildup patterns confirmed plume behavior consistent with geological model predictions

This tool enabled rapid visualization of multiple variables across monitoring points without manual data post-processing.

## Requirements

### Python Version
- Python 3.7 or higher

### Required Libraries
- **pandas** (>= 1.3.0) — Data manipulation and analysis
- **matplotlib** (>= 3.3.0) — Plotting and visualization
- **tkinter** — GUI framework (included with Python)

### Optional
- **tkinterdnd2** (>= 0.3.0) — Drag-and-drop file support

## Installation

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas matplotlib tkinterdnd2
```

## Usage

### GUI Viewer (node_output_gui_v1.py)

```bash
python3 node_output_gui_v1.py
```

**Workflow:**
1. Load a STOMP output file (extensionless or `.txt`)
2. Select reference node(s) by cell ID (IJK coordinates shown)
3. Choose variables to plot
4. Customize:
   - Rename labels for legend
   - Apply multipliers for unit conversion
   - Adjust x-axis units and scales
5. Export selected data to CSV if needed

## Technical Details

Built-in libraries (no extra installation):
- `os` — File path operations
- `re` — Regular expressions for parsing
- `tkinter` — GUI components
- `threading` — Background file loading

## Documentation

- **Architecture & Design:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Sample Data Notes:** [docs/DATA.md](docs/DATA.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **License:** [LICENSE](LICENSE) (MIT)

## License

MIT License — See [LICENSE](LICENSE) for details.

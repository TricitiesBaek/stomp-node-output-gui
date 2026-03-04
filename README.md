# STOMP Node Output GUI

Python GUI tool for visualizing STOMP simulation node output data (https://stomp-userguide.pnnl.gov/mode_specific_guides/all_modes/syntax/output_cntrl_syntax.html). 

This tool enabled rapid visualization of multiple variables across monitoring points without manual data post-processing with STOMP simulation (https://stomp-userguide.pnnl.gov/).  

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
![GUI Screenshot](docs/images/Screenshot%20GUI.png)

### GUI with Data Plotted
![Figure 1](docs/images/Screenshot%Figure1.png)

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
   results/output_ex
   ```

4. **Select nodes and variables** to visualize

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

# STOMP Node Output GUI

Python GUI tool for visualizing STOMP simulation node output data.

## Included

1. **node_output_gui_v1.py** - Interactive GUI for visualization
2. **results/output_ex.txt** - Sample working input file

## Requirements

### Python Version
- Python 3.7 or higher

### Required Libraries
- **pandas** (>= 1.3.0) - Data manipulation and analysis
- **matplotlib** (>= 3.3.0) - Plotting and visualization
- **tkinter** - GUI framework (usually included with Python)

### Optional Libraries
- **tkinterdnd2** (>= 0.3.0) - Enables drag-and-drop file support (app works without it)

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas matplotlib tkinterdnd2
```

## Usage

### GUI Viewer (node_output_gui_v1.py)

Interactive visualization tool with customization options.

```bash
python3 node_output_gui_v1.py
```

Then load the sample file:

```text
results/output_ex.txt
```

**Features:**
- Load STOMP (node) output files (extensionless or .txt)
- Select reference nodes by cell ID with IJK display
- Choose variables to plot with inline customization:
  - Rename variable labels for legend
  - Apply multipliers for unit conversion
  - Units displayed automatically
- Interactive x-axis unit conversion (seconds/hours/days/years)
- Logarithmic scale options for X and Y axes
- Custom Y-axis label
- Drag-and-drop file loading (if tkinterdnd2 is installed)
- Export node data to CSV
- Fast loading with optimized parsing for large files
- Progress bar during file loading

## Notes

Built-in libraries used (no installation needed):
- `os` - File path operations
- `re` - Regular expressions for parsing
- `tkinter` - GUI components
- `threading` - Background file loading and progress updates

## Project Documentation

- Architecture and diagrams: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Sample data note: [docs/DATA.md](docs/DATA.md)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)
- License: [LICENSE](LICENSE)

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

## Portfolio Tips

- Add 1-2 screenshots/GIFs of the GUI and include them in this README.
- Add one short case study using `results/output_ex.txt` (what variables were inspected and what insight was found).
- Keep sample data small and anonymized before publishing.
- Pin this repository on your GitHub profile.

## Quick GitHub Publish Steps

1. Create a new repository on GitHub (for example: `stomp-node-output-tools`).
2. In this folder, initialize Git and push:

```bash
git init
git add .
git commit -m "Initial commit: STOMP node output visualiation GUI tool"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

3. In GitHub repository settings:
  - Enable the repository description and topics (for discoverability).
  - Confirm license is detected.
4. In your profile:
  - Pin the repository.
  - Add 1-2 bullet points in your profile README linking to this project.

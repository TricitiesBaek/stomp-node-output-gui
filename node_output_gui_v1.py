#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
First version GUI for STOMP node output visualization.

- Reads STOMP output text file (e.g., 'output' or 'output.txt')
- Extracts reference node IDs from lines like:
  Reference Node(s) (48,23,100:557616) (48,23,50:276816) (48,23,1:1632)
- Lets user choose node(s) and variable(s)
- Plots selected variables versus time

This script is standalone and does not modify existing analysis scripts.
"""

import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

import pandas as pd
import matplotlib.pyplot as plt


NUM_PATTERN = r"[-+]?\d*\.?\d+(?:[Ee][-+]?\d+)?"


def extract_reference_nodes(lines):
    """Extract unique node IDs and IJK mapping from 'Reference Node(s) ...' lines."""
    nodes = []
    seen = set()
    node_ijk_map = {}

    for line in lines:
        if "Reference Node(s)" not in line:
            continue

        # Capture tuple groups from text like: (48,23,100:557616)
        found = re.findall(r"\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*:\s*(\d+)\)", line)
        for i_s, j_s, k_s, n_s in found:
            nid = int(n_s)
            if nid not in seen:
                seen.add(nid)
                nodes.append(nid)
            if nid not in node_ijk_map:
                node_ijk_map[nid] = (int(i_s), int(j_s), int(k_s))

    return nodes, node_ijk_map


def extract_header(lines):
    """Find the first table header line that starts with Step."""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Step") and "Node" in stripped and "Time" in stripped:
            return stripped.split()
    return []


def extract_units(lines):
    """Extract units from the line(s) following the header line.
    
    Units are in the format [unit] aligned under each column.
    Can span multiple lines if many columns exist.
    Returns a dict mapping column name to unit string.
    """
    units_dict = {}
    header_idx = None
    header_line = None
    
    # Find the header line
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Step") and "Node" in stripped and "Time" in stripped:
            header_idx = i
            header_line = line
            headers = stripped.split()
            break
    
    if header_idx is None or header_idx + 1 >= len(lines):
        return units_dict
    
    # Collect unit lines (may span multiple lines, look for lines with [...])
    unit_lines = []
    for i in range(header_idx + 1, min(header_idx + 5, len(lines))):
        line = lines[i]
        # Stop if we hit data rows (starts with numbers)
        if line.strip() and line.strip()[0].isdigit():
            break
        # Skip empty lines
        if not line.strip():
            continue
        if '[' in line:
            unit_lines.append(line)
    
    if not unit_lines:
        return units_dict
    
    # Combine unit lines preserving positions
    # Use the first unit line as reference for positions
    unit_line = unit_lines[0] if len(unit_lines) == 1 else " ".join(unit_lines)
    
    # Extract all [unit] patterns in order
    unit_pattern = re.compile(r'\[([^\]]+)\]')
    units_list = [match.group(1).strip() for match in unit_pattern.finditer(unit_line)]
    
    if not units_list:
        return units_dict
    
    # Known dimensionless variables that don't have units
    dimensionless = {"Step", "Node", "Itr", "SG", "XLA", "RPL", "RPG"}
    
    # Map units to headers by counting through both lists
    # Skip dimensionless headers when assigning units
    unit_idx = 0
    for header in headers:
        if header in dimensionless:
            units_dict[header] = ""
        elif unit_idx < len(units_list):
            units_dict[header] = units_list[unit_idx]
            unit_idx += 1
        else:
            units_dict[header] = ""
    
    return units_dict


def parse_numeric_table(lines, headers):
    """
    Parse numeric data rows using pandas for speed.
    
    A valid row should have at least len(headers) numbers, and the first two
    values (Step, Node) should be integer-like.
    """
    if not headers:
        return pd.DataFrame()
    
    # Filter to only data lines (skip headers, separators, etc.)
    data_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip obviously non-data lines
        if not stripped or stripped.startswith('---') or 'Reference Node' in stripped:
            continue
        if 'Step' in stripped and 'Node' in stripped:
            continue  # Skip header repeats
        # Check if line starts with a number (data row)
        if stripped and (stripped[0].isdigit() or stripped[0] == '-'):
            data_lines.append(line)
    
    if not data_lines:
        return pd.DataFrame(columns=headers)
    
    # Use pandas to parse - much faster than regex
    from io import StringIO
    data_text = ''.join(data_lines)
    
    try:
        df = pd.read_csv(
            StringIO(data_text),
            sep=r'\s+',
            header=None,
            names=headers,
            engine='python',
            on_bad_lines='skip'
        )
        
        # Convert integer columns
        for col in ["Step", "Node", "Itr"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        return df
    except Exception as e:
        # Fallback to empty dataframe
        return pd.DataFrame(columns=headers)


def parse_output_file(file_path):
    """Parse file and return (reference_nodes, dataframe, node_ijk_map, units_dict).
    
    Optimized to read only the reference node section for faster loading.
    """
    reference_nodes = []
    node_ijk_map = {}
    headers = []
    units_dict = {}
    
    # First pass: find the reference node section (fast scan)
    ref_section_start = None
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f):
                if "Reference Node Output Record" in line:
                    ref_section_start = line_num
                    break
    except Exception as e:
        raise Exception(f"Could not read file: {e}")
    
    if ref_section_start is None:
        raise Exception("Could not find 'Reference Node Output Record' section in file")
    
    # Second pass: read only the reference section
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Skip to reference section
            for _ in range(ref_section_start):
                next(f)
            
            # Read reference section (typically starts around line found)
            lines = []
            for i, line in enumerate(f):
                lines.append(line)
                # Read enough to get headers, units, and some data
                # Stop after we have substantial data or hit next section
                if i > 1000:  # Read first ~1000 lines of reference section
                    break
                if i > 20 and "---" in line and "---" in lines[-2]:
                    break  # Hit next section separator
    except Exception as e:
        raise Exception(f"Could not read file: {e}")

    if not lines:
        raise Exception("File reference section is empty")

    reference_nodes, node_ijk_map = extract_reference_nodes(lines)
    headers = extract_header(lines)
    units_dict = extract_units(lines)
    
    if not headers:
        raise Exception("Could not find data table headers in file")
    
    # For very large files, we'll parse in chunks to avoid memory issues
    # Read the full reference section now
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            # Skip to reference section
            for _ in range(ref_section_start):
                next(f)
            
            all_lines = []
            line_count = 0
            for line in f:
                all_lines.append(line)
                line_count += 1
                # Stop if we hit the next major section
                if len(all_lines) > 100 and "---" in line and "Record" in line and line != all_lines[0]:
                    break
    except Exception as e:
        raise Exception(f"Could not read full reference section: {e}")
    
    df = parse_numeric_table(all_lines, headers)

    # Fallback: if no reference line found, use nodes from parsed table
    if not reference_nodes and "Node" in df.columns:
        reference_nodes = sorted(df["Node"].dropna().astype(int).unique().tolist())

    return reference_nodes, df, node_ijk_map, units_dict


class NodeOutputApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STOMP Node Output Viewer (v1)")
        self.root.geometry("760x520")

        self.df = pd.DataFrame()
        self.reference_nodes = []
        self.node_ijk_map = {}
        self.units_dict = {}
        
        # Store current plot state for interactive updates
        self.current_fig = None
        self.current_ax = None
        self.current_node_id = None
        self.current_node_df = None
        self.current_variables = []
        
        # Store checkbox variables for variables selection
        self.var_checkboxes = {}
        self.var_label_entries = {}   # Store label entry widgets
        self.var_mult_entries = {}    # Store multiplier entry widgets
        
        # Log scale options
        self.xlog_var = tk.BooleanVar(value=False)
        self.ylog_var = tk.BooleanVar(value=False)
        
        # Variable customization: display names and multipliers
        self.var_custom_labels = {}  # {var_name: custom_label}
        self.var_multipliers = {}    # {var_name: multiplier}
        self.ylabel_var = tk.StringVar(value="Value")

        self._build_ui()
        self._setup_drag_drop()

    def _build_ui(self):
        pad = {"padx": 8, "pady": 6}

        # File row
        frm_file = ttk.Frame(self.root)
        frm_file.pack(fill="x", **pad)

        ttk.Label(frm_file, text="Output file:").pack(side="left")
        self.file_var = tk.StringVar()
        self.entry_file = ttk.Entry(frm_file, textvariable=self.file_var)
        self.entry_file.pack(side="left", fill="x", expand=True, padx=6)

        ttk.Button(frm_file, text="Browse", command=self.browse_file).pack(side="left", padx=4)
        ttk.Button(frm_file, text="Load", command=self.load_file).pack(side="left", padx=4)

        # Node row
        frm_node = ttk.Frame(self.root)
        frm_node.pack(fill="x", **pad)

        ttk.Label(frm_node, text="Reference Node (cellID):").pack(side="left")
        self.node_var = tk.StringVar()
        self.node_combo = ttk.Combobox(frm_node, textvariable=self.node_var, state="readonly", width=20)
        self.node_combo.pack(side="left", padx=6)

        self.node_ijk_text = tk.StringVar(value="IJK: -")
        lbl_ijk = tk.Label(frm_node, textvariable=self.node_ijk_text, fg="white", bg="#333333", padx=8, pady=2)
        lbl_ijk.pack(side="left", padx=8)
        self.node_combo.bind("<<ComboboxSelected>>", self.on_node_selected)

        # X-axis unit row
        frm_xaxis = ttk.Frame(self.root)
        frm_xaxis.pack(fill="x", **pad)

        ttk.Label(frm_xaxis, text="X-axis unit:").pack(side="left")
        self.x_unit_var = tk.StringVar(value="years")
        self.x_unit_combo = ttk.Combobox(
            frm_xaxis,
            textvariable=self.x_unit_var,
            state="readonly",
            width=15,
            values=["seconds", "hours", "days", "years"],
        )
        self.x_unit_combo.pack(side="left", padx=6)
        self.x_unit_combo.bind("<<ComboboxSelected>>", self.on_plot_option_changed)
        
        ttk.Checkbutton(frm_xaxis, text="Log X", variable=self.xlog_var, command=self.on_plot_option_changed).pack(side="left", padx=10)
        ttk.Checkbutton(frm_xaxis, text="Log Y", variable=self.ylog_var, command=self.on_plot_option_changed).pack(side="left", padx=4)
        
        ttk.Label(frm_xaxis, text="Y-axis:").pack(side="left", padx=(20, 2))
        ylabel_entry = ttk.Entry(frm_xaxis, textvariable=self.ylabel_var, width=15)
        ylabel_entry.pack(side="left", padx=4)
        ylabel_entry.bind("<Return>", self.on_plot_option_changed)

        # Variables row
        frm_vars = ttk.Frame(self.root)
        frm_vars.pack(fill="both", expand=True, **pad)

        frm_vars_header = ttk.Frame(frm_vars)
        frm_vars_header.pack(fill="x")
        
        # Column headers
        header_left = ttk.Frame(frm_vars_header)
        header_left.pack(side="left", fill="x", expand=True)
        ttk.Label(header_left, text="☑", width=3).pack(side="left")
        ttk.Label(header_left, text="Variable", width=12).pack(side="left")
        ttk.Label(header_left, text="Display Label", width=18).pack(side="left", padx=2)
        ttk.Label(header_left, text="Multiplier", width=10).pack(side="left", padx=2)
        
        # Buttons
        ttk.Button(frm_vars_header, text="Clear All", command=self.clear_all_vars, width=10).pack(side="right", padx=2)
        ttk.Button(frm_vars_header, text="Select All", command=self.select_all_vars, width=10).pack(side="right")
        
        # Create scrollable frame for variable rows
        canvas = tk.Canvas(frm_vars, height=200)
        scrollbar = ttk.Scrollbar(frm_vars, orient="vertical", command=canvas.yview)
        self.var_checkbox_frame = ttk.Frame(canvas)
        
        self.var_checkbox_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.var_checkbox_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, pady=4)
        scrollbar.pack(side="right", fill="y")

        # Button row
        frm_btn = ttk.Frame(self.root)
        frm_btn.pack(fill="x", **pad)

        ttk.Button(frm_btn, text="Plot Selected", command=self.plot_selected).pack(side="left")
        ttk.Button(frm_btn, text="Export Node CSV", command=self.export_node_csv).pack(side="left", padx=6)

        self.status_var = tk.StringVar(value="Load an output file to begin.")
        ttk.Label(self.root, textvariable=self.status_var, foreground="navy").pack(anchor="w", padx=10, pady=4)
        
        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(self.root, mode='indeterminate', length=300)
        self.progress_visible = False

    def _setup_drag_drop(self):
        """Enable drag-and-drop file support."""
        if not HAS_DND:
            return  # Drag-and-drop not available
        
        def on_drop(event):
            # macOS and Linux use event.data, Windows may differ
            file_path = event.data.strip()
            # Remove curly braces if present (macOS behavior)
            if file_path.startswith('{') and file_path.endswith('}'):
                file_path = file_path[1:-1]
            self.file_var.set(file_path)
            self.load_file()
        
        # Register drag-and-drop on the file entry widget
        try:
            self.entry_file.drop_target_register(DND_FILES)
            self.entry_file.dnd_bind('<<Drop>>', on_drop)
        except:
            pass  # Silently fail if drag-drop setup fails
    
    def _show_progress(self):
        """Show progress bar."""
        if not self.progress_visible:
            self.progress.pack(anchor="w", padx=10, pady=4)
            self.progress.start(10)  # Update every 10ms
            self.progress_visible = True
            self.root.update_idletasks()
    
    def _hide_progress(self):
        """Hide progress bar."""
        if self.progress_visible:
            self.progress.stop()
            self.progress.pack_forget()
            self.progress_visible = False
            self.root.update_idletasks()

    def browse_file(self):
        # macOS note: filtering by extensions can hide/disable extensionless files
        # like "output", so we intentionally use "All files" only.
        cwd = os.getcwd()
        default_dir = os.path.join(cwd, "results") if os.path.isdir(os.path.join(cwd, "results")) else cwd

        file_path = filedialog.askopenfilename(
            title="Select STOMP output file",
            initialdir=default_dir,
            filetypes=[("All files", "*")],
        )
        if file_path:
            self.file_var.set(file_path)

    def load_file(self):
        file_path = self.file_var.get().strip()
        if not file_path or not os.path.isfile(file_path):
            messagebox.showerror("File error", "Please choose a valid output file.")
            return

        self.status_var.set("Parsing file... Please wait.")
        self._show_progress()

        try:
            reference_nodes, df, node_ijk_map, units_dict = parse_output_file(file_path)
        except Exception as exc:
            self._hide_progress()
            self.status_var.set("Error parsing file.")
            messagebox.showerror("Parse error", f"Failed to parse file:\n{exc}")
            return
        finally:
            self._hide_progress()

        if df.empty:
            messagebox.showwarning("No data", "No numeric table data was parsed from this file.")
            return

        self.df = df
        self.reference_nodes = reference_nodes
        self.node_ijk_map = node_ijk_map
        self.units_dict = units_dict

        node_values = [str(n) for n in self.reference_nodes]
        self.node_combo["values"] = node_values
        if node_values:
            self.node_combo.current(0)
            self.on_node_selected()
        else:
            self.node_ijk_text.set("IJK: -")

        # Clear existing widgets
        for widget in self.var_checkbox_frame.winfo_children():
            widget.destroy()
        self.var_checkboxes.clear()
        self.var_label_entries.clear()
        self.var_mult_entries.clear()
        
        exclude = {"Step", "Node", "Time", "Timestep", "Itr"}
        vars_for_plot = [c for c in df.columns if c not in exclude]
        
        # Don't preselect any variables by default
        for v in vars_for_plot:
            var_state = tk.BooleanVar(value=False)
            self.var_checkboxes[v] = var_state
            
            # Create row frame for this variable
            row_frame = ttk.Frame(self.var_checkbox_frame)
            row_frame.pack(fill="x", pady=1)
            
            # Checkbox
            cb = ttk.Checkbutton(row_frame, variable=var_state, width=3)
            cb.pack(side="left")
            
            # Variable name with unit
            unit = self.units_dict.get(v, "")
            var_display = f"{v} [{unit}]" if unit else v
            ttk.Label(row_frame, text=var_display, width=12).pack(side="left")
            
            # Display label entry
            label_var = tk.StringVar(value=self.var_custom_labels.get(v, v))
            label_entry = ttk.Entry(row_frame, textvariable=label_var, width=18)
            label_entry.pack(side="left", padx=2)
            self.var_label_entries[v] = label_var
            
            # Multiplier entry
            mult_var = tk.StringVar(value=str(self.var_multipliers.get(v, 1.0)))
            mult_entry = ttk.Entry(row_frame, textvariable=mult_var, width=10)
            mult_entry.pack(side="left", padx=2)
            self.var_mult_entries[v] = mult_var

        self.status_var.set(
            f"Loaded: {os.path.basename(file_path)} | rows={len(df)} | reference nodes={len(reference_nodes)}"
        )

    def on_node_selected(self, _event=None):
        node_txt = self.node_var.get().strip()
        if not node_txt:
            self.node_ijk_text.set("IJK: -")
            return
        try:
            node_id = int(node_txt)
        except ValueError:
            self.node_ijk_text.set("IJK: -")
            return

        ijk = self.node_ijk_map.get(node_id)
        if ijk is None:
            self.node_ijk_text.set("IJK: not found")
        else:
            self.node_ijk_text.set(f"IJK: ({ijk[0]}, {ijk[1]}, {ijk[2]})")

    def clear_all_vars(self):
        """Uncheck all variable checkboxes."""
        for var_state in self.var_checkboxes.values():
            var_state.set(False)
    
    def select_all_vars(self):
        """Check all variable checkboxes."""
        for var_state in self.var_checkboxes.values():
            var_state.set(True)

    def on_plot_option_changed(self, _event=None):
        """Handle interactive plot option changes (x-unit, log scales) without re-plotting."""
        if self.current_fig is None or self.current_ax is None or self.current_node_df is None:
            return

        # Compute x-axis data based on unit
        unit = self.x_unit_var.get().strip().lower()
        if unit == "seconds":
            x = self.current_node_df["Time"] * 86400.0
            xlabel = "Time (seconds)"
        elif unit == "hours":
            x = self.current_node_df["Time"] * 24.0
            xlabel = "Time (hours)"
        elif unit == "days":
            x = self.current_node_df["Time"]
            xlabel = "Time (days)"
        else:
            x = self.current_node_df["Time"] / 365.25
            xlabel = "Time (years)"

        # Update x-axis data for all lines
        for i, line in enumerate(self.current_ax.get_lines()):
            line.set_xdata(x)
            # Also update y-data if multipliers changed
            if i < len(self.current_variables):
                var = self.current_variables[i]
                mult_str = self.var_mult_entries.get(var, tk.StringVar(value="1.0")).get().strip()
                try:
                    multiplier = float(mult_str) if mult_str else 1.0
                except ValueError:
                    multiplier = 1.0
                y_data = self.current_node_df[var] * multiplier
                line.set_ydata(y_data)

        self.current_ax.set_xlabel(xlabel)
        self.current_ax.set_ylabel(self.ylabel_var.get())
        
        # Apply log scale settings
        if self.xlog_var.get():
            self.current_ax.set_xscale('log')
        else:
            self.current_ax.set_xscale('linear')
            
        if self.ylog_var.get():
            self.current_ax.set_yscale('log')
        else:
            self.current_ax.set_yscale('linear')
        
        # Update limits and redraw
        self.current_ax.relim()
        self.current_ax.autoscale_view()
        self.current_fig.canvas.draw_idle()

    def _get_selected_node_df(self):
        if self.df.empty:
            messagebox.showwarning("No data", "Load a file first.")
            return None, None

        node_txt = self.node_var.get().strip()
        if not node_txt:
            messagebox.showwarning("No node", "Select a node ID.")
            return None, None

        node_id = int(node_txt)
        node_df = self.df[self.df["Node"] == node_id].copy()

        if node_df.empty:
            messagebox.showwarning("No node data", f"No rows found for node {node_id}.")
            return None, None

        node_df = node_df.sort_values("Time")
        return node_id, node_df

    def _get_selected_variables(self):
        selected = [var for var, state in self.var_checkboxes.items() if state.get()]
        if not selected:
            messagebox.showwarning("No variable", "Select at least one variable to plot.")
            return []
        return selected

    def plot_selected(self):
        node_id, node_df = self._get_selected_node_df()
        if node_df is None:
            return

        variables = self._get_selected_variables()
        if not variables:
            return

        # Store state for interactive updates
        self.current_node_id = node_id
        self.current_node_df = node_df
        self.current_variables = variables

        unit = self.x_unit_var.get().strip().lower()
        if unit == "seconds":
            x = node_df["Time"] * 86400.0
            xlabel = "Time (seconds)"
        elif unit == "hours":
            x = node_df["Time"] * 24.0
            xlabel = "Time (hours)"
        elif unit == "days":
            x = node_df["Time"]
            xlabel = "Time (days)"
        else:
            x = node_df["Time"] / 365.25
            xlabel = "Time (years)"

        # Close old figure if exists
        if self.current_fig is not None:
            plt.close(self.current_fig)
        
        # Create new plot
        fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
        
        for var in variables:
            if var in node_df.columns:
                # Read multiplier from entry widget
                mult_str = self.var_mult_entries.get(var, tk.StringVar(value="1.0")).get().strip()
                try:
                    multiplier = float(mult_str) if mult_str else 1.0
                except ValueError:
                    multiplier = 1.0
                
                y_data = node_df[var] * multiplier
                
                # Read custom label from entry widget
                label = self.var_label_entries.get(var, tk.StringVar(value=var)).get().strip()
                if not label:
                    label = var
                
                ax.plot(x, y_data, linewidth=1.0, label=label)

        ax.set_title(f"Node {node_id} | Selected Variables")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(self.ylabel_var.get())
        ax.grid(True, linestyle="--", linewidth=0.4, alpha=0.7)
        ax.legend(fontsize=9, ncol=2)
        
        # Apply initial log scale settings
        if self.xlog_var.get():
            ax.set_xscale('log')
        if self.ylog_var.get():
            ax.set_yscale('log')
            
        fig.tight_layout()
        
        # Store references
        self.current_fig = fig
        self.current_ax = ax
        
        plt.show(block=False)

    def export_node_csv(self):
        node_id, node_df = self._get_selected_node_df()
        if node_df is None:
            return

        save_path = filedialog.asksaveasfilename(
            title="Save node data CSV",
            defaultextension=".csv",
            initialfile=f"node_{node_id}.csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not save_path:
            return

        node_df.to_csv(save_path, index=False)
        messagebox.showinfo("Saved", f"Saved node data to:\n{save_path}")


if __name__ == "__main__":
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = NodeOutputApp(root)
    root.mainloop()

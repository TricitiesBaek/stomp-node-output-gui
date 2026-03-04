# Architecture

## Overview

This repository is focused on one tool:

1. `node_output_gui_v1.py`: interactive viewer for STOMP reference-node outputs

Sample input file included for demonstration:

- `results/output_ex.txt`

## System Diagram

```mermaid
flowchart LR
    A[STOMP output file] --> B[Parser]
    B --> C[DataFrame]
    C --> D[GUI Viewer]

    D --> E[Interactive plots]
    D --> F[CSV export]
```

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant I as Input File
    participant P as Parser
    participant G as GUI

    U->>G: Open STOMP output
    G->>P: Parse headers + numeric table
    P-->>G: DataFrame + metadata
    G-->>U: Plot selected nodes/variables
```

## Key Design Choices

- The parser reads STOMP-style reference-node headers and units directly from the file.
- Numeric parsing uses pandas for performance on large files.
- File loading is done in a background thread to keep the UI responsive.

# Graph_PathFinder

Graph_PathFinder is a small Python project that demonstrates common graph search algorithms (BFS, DFS and A*) on a set of predefined example graphs. It provides both a command-line interface (CLI) for automated runs and a simple Tkinter-based GUI for interactive exploration and step-through animation of the search process.

## Features

- Breadth-First Search (BFS) for unweighted shortest paths (by edge count)
- Depth-First Search (DFS) (not guaranteed shortest, but finds a path)
- A* search with Euclidean heuristic (requires node coordinates)
- 5 predefined sample graphs (grid, ladder, binary tree, hex ring, campus map)
- CLI for scripted runs and quick experiments
- GUI (Tkinter) with visualization, animation speed control, dark mode, zoom & pan, and step-through visited order

## Requirements

- Python 3.10+
- Standard library only (no external pip packages). Tkinter is used for the GUI; on some Linux distributions it may need to be installed separately (e.g., `sudo apt install python3-tk`). On Windows, Tkinter is normally included with the official Python installer.

Tested with: Python 3.10 - 3.12

## Quick start

1. (Optional) Create and activate a virtual environment:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Run the GUI:

```powershell
python ui.py
```

3. Use the CLI (examples below).

## CLI usage

The CLI is implemented in `app.py`. It expects four positional arguments: `graph`, `start`, `goal`, and `algorithm` (one of `bfs`, `dfs`, `astar`). There is also a `--list` flag which lists available graphs and nodes for the chosen graph.

Notes on node literals: node names may be strings (e.g., `"L0"`) or Python literals like tuples. The CLI attempts to parse start/goal using `ast.literal_eval`, falling back to the raw string when parsing fails.

Examples (PowerShell):

List available graphs and nodes for a chosen graph (you must still provide the required positional arguments):

```powershell
python app.py UrbanGrid-6x6 "(0, 0)" "(5, 5)" bfs --list
```

Run BFS on the ladder graph from `L0` to `R4`:

```powershell
python app.py Ladder-10 L0 R4 bfs
```

Run A* on the urban grid using tuple nodes (A* uses node positions for the Euclidean heuristic):

```powershell
python app.py UrbanGrid-6x6 "(0, 0)" "(5, 5)" astar
```

Output includes: algorithm, graph name, visited node count, path length and the path sequence (if found).

## GUI usage

Run the GUI with:

```powershell
python ui.py
```

Controls provided in the sidebar:
- Graph selector
- Algorithm selector (`bfs`, `dfs`, `astar`)
- Start / Goal node pickers (supports tuple and string node labels)
- Animation speed slider
- Dark mode toggle
- Run, Clear and step-through controls (Step / Auto / Reset)

The canvas supports mouse wheel zoom and right-button pan.

## Included example graphs

Defined in `graphs.py` (returned by `get_all_graphs()`):

- `UrbanGrid-6x6` — 6x6 grid (tuple coordinates), some blocked edges and a shortcut
- `Ladder-10` — two rails with rungs (L0..L4 and R0..R4)
- `BinaryTree-15` — complete binary tree (nodes 1..15)
- `HexRing-12` — two concentric rings with spokes/chords
- `CampusMap` — small named-location graph (strings)

These graphs include position data where appropriate (used by A* for the Euclidean heuristic).

## Algorithms (files)

- `algorithms.py` — implementations of `bfs`, `dfs`, `astar`, and result dataclass `SearchResult`.
- `graphs.py` — graph factory functions and a lightweight `Graph` class with `adjacency` and `positions`.
- `app.py` — CLI wrapper and argument parsing.
- `ui.py` — Tkinter GUI and visualization logic.

## Developer notes

- Node formatting: when supplying tuple nodes on the CLI or GUI text fields, use Python literal syntax (for example `(1, 2)`). The code does a `literal_eval` where possible.
- The code intentionally uses only the Python standard library to keep setup minimal.
- If you plan to add larger graphs or heavier visualization, consider adding a requirements file and splitting visualization logic into a module.

## Contributing

Contributions are welcome. Please open issues or PRs to discuss changes. Keep changes focused and add tests if you introduce algorithmic changes.

## License

This project is provided under the MIT License. See the `LICENSE` file if present.

---

If you want, I can also:

- add a minimal `requirements.txt` or `pyproject.toml` (not strictly required since this project uses only stdlib),
- add a short example script (e.g., `examples/quick_run.py`) that runs all algorithms on all graphs and prints comparative statistics,
- or create a small CONTRIBUTING.md template. Let me know which you'd like next.
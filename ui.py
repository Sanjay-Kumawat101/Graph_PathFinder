from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Tuple, List, Hashable, Optional

from graphs import get_all_graphs, Graph
from algorithms import bfs, dfs, astar, SearchResult


Node = Hashable
Position = Tuple[float, float]


class GraphUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Graph Pathfinder UI")
        self.geometry("1000x680")

        self.graphs: Dict[str, Graph] = get_all_graphs()
        self.current_graph_name: tk.StringVar = tk.StringVar(value=list(self.graphs.keys())[0])
        self.algorithm_name: tk.StringVar = tk.StringVar(value="bfs")
        self.start_node: tk.StringVar = tk.StringVar()
        self.goal_node: tk.StringVar = tk.StringVar()

        self.dark_mode: tk.BooleanVar = tk.BooleanVar(value=True)
        self.speed_ms: tk.IntVar = tk.IntVar(value=200)
        # zoom/pan state
        self.user_scale: float = 1.0
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0
        self._pan_last: Tuple[float, float] | None = None
        self._build_widgets()
        self._populate_nodes()
        self._draw_graph()

        self.anim_after_id: Optional[str] = None
        self.current_path: List[Node] = []
        self.visited_order: List[Node] = []
        self._step_index: int = 0

    def _build_widgets(self) -> None:
        # style
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        control = ttk.Frame(self)
        control.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=12)

        ttk.Label(control, text="Graph").pack(anchor=tk.W)
        self.graph_combo = ttk.Combobox(control, state="readonly", textvariable=self.current_graph_name,
                                        values=list(self.graphs.keys()))
        self.graph_combo.pack(fill=tk.X)
        self.graph_combo.bind("<<ComboboxSelected>>", self._on_graph_change)
        # show selected graph name in sidebar
        ttk.Label(control, textvariable=self.current_graph_name).pack(anchor=tk.W, pady=(2, 6))

        ttk.Label(control, text="Algorithm").pack(anchor=tk.W, pady=(8, 0))
        self.alg_combo = ttk.Combobox(control, state="readonly", textvariable=self.algorithm_name,
                                      values=["bfs", "dfs", "astar"])
        self.alg_combo.pack(fill=tk.X)

        ttk.Label(control, text="Start node").pack(anchor=tk.W, pady=(8, 0))
        self.start_combo = ttk.Combobox(control, state="readonly", textvariable=self.start_node)
        self.start_combo.pack(fill=tk.X)

        ttk.Label(control, text="Goal node").pack(anchor=tk.W, pady=(8, 0))
        self.goal_combo = ttk.Combobox(control, state="readonly", textvariable=self.goal_node)
        self.goal_combo.pack(fill=tk.X)

        ttk.Label(control, text="Animation speed (ms)").pack(anchor=tk.W, pady=(10, 0))
        ttk.Scale(control, from_=50, to=800, orient=tk.HORIZONTAL, variable=self.speed_ms).pack(fill=tk.X)

        ttk.Checkbutton(control, text="Dark mode", variable=self.dark_mode, command=self._apply_theme).pack(anchor=tk.W, pady=(8, 0))

        ttk.Button(control, text="Run", command=self._run).pack(fill=tk.X, pady=(10, 0))
        ttk.Button(control, text="Clear", command=self._clear_path).pack(fill=tk.X, pady=(4, 0))

        # step-through controls
        step_frame = ttk.Frame(control)
        step_frame.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(step_frame, text="Step ▶", command=self._step_once).pack(side=tk.LEFT)
        ttk.Button(step_frame, text="Auto ▶▶", command=self._auto_step).pack(side=tk.LEFT, padx=6)
        ttk.Button(step_frame, text="Reset ⟲", command=self._reset_steps).pack(side=tk.LEFT)

        self.info_var = tk.StringVar(value="")
        ttk.Label(control, textvariable=self.info_var, wraplength=220, justify=tk.LEFT).pack(anchor=tk.W, pady=(10, 0))

        # legend moved into sidebar bottom
        legend = ttk.Frame(control)
        legend.pack(side=tk.BOTTOM, fill=tk.X, pady=(14, 0))
        ttk.Label(legend, text="Legend:").grid(row=0, column=0, sticky=tk.W)
        swatch = tk.Canvas(legend, width=16, height=16, bd=0, highlightthickness=0)
        swatch.create_rectangle(0, 0, 16, 16, fill="#1976d2", outline="")
        swatch.grid(row=1, column=0)
        ttk.Label(legend, text="Node").grid(row=1, column=1, sticky=tk.W, padx=4)
        swatch2 = tk.Canvas(legend, width=16, height=16, bd=0, highlightthickness=0)
        swatch2.create_rectangle(0, 6, 16, 10, fill="#ff8f00", outline="")
        swatch2.grid(row=2, column=0)
        ttk.Label(legend, text="Path").grid(row=2, column=1, sticky=tk.W, padx=4)
        swatch3 = tk.Canvas(legend, width=16, height=16, bd=0, highlightthickness=0)
        swatch3.create_rectangle(0, 0, 16, 16, fill="#43a047", outline="")
        swatch3.grid(row=3, column=0)
        ttk.Label(legend, text="Start").grid(row=3, column=1, sticky=tk.W, padx=4)
        swatch4 = tk.Canvas(legend, width=16, height=16, bd=0, highlightthickness=0)
        swatch4.create_rectangle(0, 0, 16, 16, fill="#e53935", outline="")
        swatch4.grid(row=4, column=0)
        ttk.Label(legend, text="Goal").grid(row=4, column=1, sticky=tk.W, padx=4)

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        # zoom & pan bindings
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", self._on_wheel)
        self.canvas.bind("<Button-5>", self._on_wheel)
        self.canvas.bind("<ButtonPress-3>", self._pan_start)
        self.canvas.bind("<B3-Motion>", self._pan_move)
        self.canvas.bind("<ButtonRelease-3>", self._pan_end)
        self.canvas.bind("<Configure>", lambda e: self._draw_graph())

        self._apply_theme()

    def _build_legend(self) -> None:
        # Deprecated by sidebar legend layout
        pass

    def _apply_theme(self) -> None:
        dark = self.dark_mode.get()
        bg = "#0f1216" if dark else "#f7f9fc"
        fg = "#e8eef6" if dark else "#111"
        edge = "#2a2f36" if dark else "#c0c0c0"
        self.configure(bg=bg)
        for child in self.winfo_children():
            try:
                child.configure(style="TFrame")
            except Exception:
                pass
        self.canvas.configure(bg=bg)
        self.edge_color = edge
        self.text_color = fg

    def _on_graph_change(self, _event=None) -> None:
        self._populate_nodes()
        self._draw_graph()
        self._clear_path()

    def _populate_nodes(self) -> None:
        g = self.graphs[self.current_graph_name.get()]
        nodes = list(g.adjacency.keys())
        display_nodes = [self._node_to_str(n) for n in nodes]
        self.start_combo["values"] = display_nodes
        self.goal_combo["values"] = display_nodes
        if display_nodes:
            self.start_node.set(display_nodes[0])
            self.goal_node.set(display_nodes[-1])

    def _draw_graph(self) -> None:
        self.canvas.delete("all")
        g = self.graphs[self.current_graph_name.get()]
        positions = g.positions
        if not positions:
            return

        # Compute bounding box and scaling
        xs = [p[0] for p in positions.values()]
        ys = [p[1] for p in positions.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        pad = 40
        width = self.canvas.winfo_width() or 600
        height = self.canvas.winfo_height() or 600
        inner_w, inner_h = max(1, width - pad * 2), max(1, height - pad * 2)

        span_x = max(1e-6, max_x - min_x)
        span_y = max(1e-6, max_y - min_y)
        base_scale = min(inner_w / span_x, inner_h / span_y)

        # cache transform
        self._transform = {
            "min_x": min_x,
            "min_y": min_y,
            "pad": pad,
            "width": width,
            "height": height,
            "base_scale": base_scale,
        }

        def to_canvas(pos: Position) -> Tuple[float, float]:
            x = pad + (pos[0] - min_x) * base_scale
            y = pad + (pos[1] - min_y) * base_scale
            y = height - y
            # apply user zoom/pan
            x = x * self.user_scale + self.pan_x
            y = y * self.user_scale + self.pan_y
            return x, y

        # Draw edges
        for n, neighbors in g.adjacency.items():
            x1, y1 = to_canvas(positions[n])
            for m in neighbors:
                x2, y2 = to_canvas(positions[m])
                self.canvas.create_line(x1, y1, x2, y2, fill=self.edge_color)

        # Draw nodes with glossy highlight (outer ring)
        self.node_items: Dict[Node, int] = {}
        for n, pos in positions.items():
            x, y = to_canvas(pos)
            r = 10
            # outer glow ring
            self.canvas.create_oval(x - r - 3, y - r - 3, x + r + 3, y + r + 3, outline="#5dade2", width=1)
            item = self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#1976d2", outline="")
            self.node_items[n] = item
            # small glossy reflection
            self.canvas.create_arc(x - r, y - r, x + r, y + r, start=45, extent=90, style=tk.ARC, outline="#bbdefb", width=2)
            self.canvas.create_text(x, y - 16, text=self._node_to_str(n), fill=self.text_color, font=("Segoe UI", 10))

    def _clear_path(self) -> None:
        if self.anim_after_id is not None:
            try:
                self.after_cancel(self.anim_after_id)
            except Exception:
                pass
            self.anim_after_id = None
        # Redraw graph to clear overlays
        self._draw_graph()
        self.info_var.set("")
        self.current_path = []

    def _run(self) -> None:
        try:
            g = self.graphs[self.current_graph_name.get()]
            start = self._str_to_node(self.start_node.get())
            goal = self._str_to_node(self.goal_node.get())
            if start not in g.adjacency or goal not in g.adjacency:
                messagebox.showerror("Invalid nodes", "Start or goal not in graph")
                return

            algo = self.algorithm_name.get()
            if algo == "astar":
                result: SearchResult = astar(g.adjacency, g.positions, start, goal)
            elif algo == "bfs":
                result = bfs(g.adjacency, start, goal)
            else:
                result = dfs(g.adjacency, start, goal)

            if not result.path:
                self.info_var.set("No path found")
                return

            self.current_path = result.path
            self.visited_order = result.visited_order or []
            self._reset_steps()
            self.info_var.set(f"Algorithm: {algo.upper()}  |  Length: {result.distance}  |  Visited: {result.visited_count}")
            self._animate_path(result.path)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _animate_path(self, path: List[Node]) -> None:
        # Overlay the path with thicker orange segments and highlight nodes
        g = self.graphs[self.current_graph_name.get()]
        positions = g.positions

        # use cached transform to map positions
        t = getattr(self, "_transform", None)
        if not t:
            self._draw_graph()
            t = self._transform

        def to_canvas(pos: Position) -> Tuple[float, float]:
            x = t["pad"] + (pos[0] - t["min_x"]) * t["base_scale"]
            y = t["pad"] + (pos[1] - t["min_y"]) * t["base_scale"]
            y = t["height"] - y
            x = x * self.user_scale + self.pan_x
            y = y * self.user_scale + self.pan_y
            return x, y

        # Animate sequentially with glow (draw wide translucent layer then bright core)
        def step(i: int) -> None:
            if i >= len(path) - 1:
                # highlight start/goal
                if path:
                    self._highlight_node(path[0], fill="#43a047")
                    self._highlight_node(path[-1], fill="#e53935")
                return
            a, b = path[i], path[i + 1]
            x1, y1 = to_canvas(positions[a])
            x2, y2 = to_canvas(positions[b])
            # glow backdrop
            self.canvas.create_line(x1, y1, x2, y2, width=8, fill="#ffd180")
            # bright core
            self.canvas.create_line(x1, y1, x2, y2, width=4, fill="#ff8f00")
            self._highlight_node(a, fill="#64b5f6")
            self.anim_after_id = self.after(self.speed_ms.get(), lambda: step(i + 1))

        step(0)

    def _highlight_node(self, node: Node, fill: str) -> None:
        item = self.node_items.get(node)
        if item:
            self.canvas.itemconfigure(item, fill=fill)

    def _node_to_str(self, node: Node) -> str:
        return str(node)

    def _str_to_node(self, text: str) -> Node:
        # Try literal eval first to support tuples/ints
        from ast import literal_eval
        try:
            return literal_eval(text)
        except Exception:
            return text

    # Step-through controls
    def _reset_steps(self) -> None:
        self._step_index = 0
        self._draw_graph()

    def _step_once(self) -> None:
        if not self.visited_order or self._step_index >= len(self.visited_order):
            return
        node = self.visited_order[self._step_index]
        self._highlight_node(node, fill="#8e24aa")
        self._step_index += 1

    def _auto_step(self) -> None:
        if not self.visited_order:
            return
        def tick() -> None:
            if self._step_index >= len(self.visited_order):
                return
            self._step_once()
            self.after(max(50, self.speed_ms.get() // 2), tick)
        tick()

    # Zoom / Pan handlers
    def _on_wheel(self, event) -> None:
        if hasattr(event, "delta") and event.delta != 0:
            delta = event.delta
        elif hasattr(event, "num") and event.num in (4, 5):
            delta = 120 if event.num == 4 else -120
        else:
            delta = 0
        if delta == 0:
            return
        factor = 1.1 if delta > 0 else 1 / 1.1
        x, y = event.x, event.y
        old = self.user_scale
        self.user_scale *= factor
        # keep cursor position stable while zooming
        self.pan_x = x - (x - self.pan_x) * (self.user_scale / old)
        self.pan_y = y - (y - self.pan_y) * (self.user_scale / old)
        self._draw_graph()

    def _pan_start(self, event) -> None:
        self._pan_last = (event.x, event.y)

    def _pan_move(self, event) -> None:
        if not self._pan_last:
            return
        dx = event.x - self._pan_last[0]
        dy = event.y - self._pan_last[1]
        self.pan_x += dx
        self.pan_y += dy
        self._pan_last = (event.x, event.y)
        self._draw_graph()

    def _pan_end(self, _event) -> None:
        self._pan_last = None


if __name__ == "__main__":
    app = GraphUI()
    app.mainloop()



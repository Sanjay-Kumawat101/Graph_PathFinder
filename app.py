from __future__ import annotations

import argparse
from typing import Dict, List

from algorithms import bfs, dfs, astar, SearchResult
from graphs import get_all_graphs, Graph


ALGORITHMS = {
    "bfs": bfs,
    "dfs": dfs,
    "astar": astar,
}


def list_graphs(graphs: Dict[str, Graph]) -> None:
    print("Available graphs:")
    for name, g in graphs.items():
        print(f"- {name}: {len(g.adjacency)} nodes")


def list_nodes(graph: Graph) -> None:
    print("Nodes:")
    nodes: List[str] = [str(n) for n in graph.adjacency.keys()]
    print(", ".join(nodes))


def run_cli() -> None:
    graphs = get_all_graphs()

    parser = argparse.ArgumentParser(
        prog="Graph Pathfinder",
        description="Shortest path finder on 5 predefined graphs (BFS, DFS, A*).",
    )
    parser.add_argument("graph", choices=graphs.keys(), help="Graph to use")
    parser.add_argument("start", help="Start node (stringified; e.g., '(0, 0)' or 'A')")
    parser.add_argument("goal", help="Goal node (stringified)")
    parser.add_argument("algorithm", choices=ALGORITHMS.keys(), help="Algorithm: bfs | dfs | astar")
    parser.add_argument("--list", action="store_true", help="List graphs and nodes")

    args = parser.parse_args()

    if args.list:
        list_graphs(graphs)
        g = graphs[args.graph]
        list_nodes(g)
        return

    g = graphs[args.graph]

    # Parse node literals safely: eval with literal_eval
    from ast import literal_eval

    def parse_node(s: str):
        try:
            return literal_eval(s)
        except Exception:
            return s

    start = parse_node(args.start)
    goal = parse_node(args.goal)

    if start not in g.adjacency:
        raise SystemExit(f"Start node {start!r} not in selected graph")
    if goal not in g.adjacency:
        raise SystemExit(f"Goal node {goal!r} not in selected graph")

    if args.algorithm == "astar":
        result: SearchResult = ALGORITHMS[args.algorithm](g.adjacency, g.positions, start, goal)
    else:
        result = ALGORITHMS[args.algorithm](g.adjacency, start, goal)

    print(f"Algorithm: {args.algorithm.upper()}")
    print(f"Graph: {args.graph}")
    print(f"Visited nodes: {result.visited_count}")
    if result.path:
        print(f"Path length (edges): {result.distance}")
        print(f"Path: {result.path}")
    else:
        print("No path found")


if __name__ == "__main__":
    run_cli()



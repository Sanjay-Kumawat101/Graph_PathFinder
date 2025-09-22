from __future__ import annotations

from typing import Dict, Hashable, Iterable, Tuple


Node = Hashable
Position = Tuple[float, float]


class Graph:
    def __init__(self, adjacency: Dict[Node, Iterable[Node]], positions: Dict[Node, Position]):
        self.adjacency = {n: list(neigh) for n, neigh in adjacency.items()}
        self.positions = positions


def _add_undirected_edge(adj: Dict[Node, list], a: Node, b: Node) -> None:
    adj.setdefault(a, []).append(b)
    adj.setdefault(b, []).append(a)


def urban_grid_6x6() -> Graph:
    # 6x6 grid with some blocked edges and a few shortcuts to increase complexity
    size = 6
    adjacency: Dict[Node, list] = {}
    positions: Dict[Node, Position] = {}
    for r in range(size):
        for c in range(size):
            node = (r, c)
            positions[node] = (float(c), float(r))
    # regular grid connections
    for r in range(size):
        for c in range(size):
            if r + 1 < size:
                _add_undirected_edge(adjacency, (r, c), (r + 1, c))
            if c + 1 < size:
                _add_undirected_edge(adjacency, (r, c), (r, c + 1))
    # block a few streets (reduced for lower complexity)
    blocked = [((1, 1), (1, 2)), ((2, 3), (3, 3))]
    for a, b in blocked:
        if a in adjacency and b in adjacency[a]:
            adjacency[a].remove(b)
        if b in adjacency and a in adjacency[b]:
            adjacency[b].remove(a)
    # add a single shortcut (reduced)
    for a, b in [((0, 0), (2, 2))]:
        _add_undirected_edge(adjacency, a, b)
    return Graph(adjacency, positions)


def ladder_10() -> Graph:
    # Two parallel lines with rungs (ladder), 10 nodes total
    positions: Dict[Node, Position] = {}
    adjacency: Dict[Node, list] = {}
    # left rail L0..L4 and right rail R0..R4
    for i in range(5):
        L = f"L{i}"
        R = f"R{i}"
        positions[L] = (0.0, float(i))
        positions[R] = (2.0, float(i))
        if i > 0:
            _add_undirected_edge(adjacency, f"L{i-1}", L)
            _add_undirected_edge(adjacency, f"R{i-1}", R)
        _add_undirected_edge(adjacency, L, R)
    return Graph(adjacency, positions)


def binary_tree_15() -> Graph:
    # Complete binary tree up to 15 nodes labeled 1..15
    positions: Dict[Node, Position] = {}
    adjacency: Dict[Node, list] = {}
    import math
    for i in range(1, 16):
        level = int(math.floor(math.log2(i)))
        index_in_level = i - (1 << level)
        nodes_in_level = 1 << level
        x = (index_in_level + 1) / (nodes_in_level + 1) * 10.0
        y = level * 2.0
        positions[i] = (x, -y)
        left = 2 * i
        right = 2 * i + 1
        if left <= 15:
            _add_undirected_edge(adjacency, i, left)
        if right <= 15:
            _add_undirected_edge(adjacency, i, right)
    return Graph(adjacency, positions)


def hex_ring_12() -> Graph:
    # 12 nodes arranged roughly on two hexagons with chords
    import math
    positions: Dict[Node, Position] = {}
    adjacency: Dict[Node, list] = {}
    outer = [f"O{i}" for i in range(6)]
    inner = [f"I{i}" for i in range(6)]
    for i, name in enumerate(outer):
        angle = 2 * math.pi * i / 6
        positions[name] = (math.cos(angle) * 6.0, math.sin(angle) * 6.0)
    for i, name in enumerate(inner):
        angle = 2 * math.pi * (i + 0.5) / 6
        positions[name] = (math.cos(angle) * 3.5, math.sin(angle) * 3.5)
    # ring connections
    for i in range(6):
        _add_undirected_edge(adjacency, outer[i], outer[(i + 1) % 6])
        _add_undirected_edge(adjacency, inner[i], inner[(i + 1) % 6])
    # spokes and chords
    for i in range(6):
        _add_undirected_edge(adjacency, outer[i], inner[i])
    # reduced chords for simplicity
    for i in range(0, 6, 4):
        _add_undirected_edge(adjacency, outer[i], inner[(i + 3) % 6])
    return Graph(adjacency, positions)


def campus_map() -> Graph:
    # Named places with criss-cross paths
    names = [
        "Gate", "Library", "Cafeteria", "LabA", "LabB", "Sports", "Admin", "Auditorium", "Hostel", "Parking",
    ]
    positions: Dict[Node, Position] = {
        "Gate": (-5.0, -1.0),
        "Parking": (-6.0, -3.0),
        "Admin": (-2.0, 0.0),
        "Library": (0.0, 2.5),
        "Cafeteria": (1.0, -1.5),
        "LabA": (3.0, 1.5),
        "LabB": (4.5, -0.5),
        "Sports": (6.0, -2.5),
        "Auditorium": (2.0, 3.5),
        "Hostel": (5.5, 2.5),
    }
    adjacency: Dict[Node, list] = {}
    for a, b in [
        ("Gate", "Admin"), ("Gate", "Parking"), ("Admin", "Library"), ("Admin", "Cafeteria"),
        ("Library", "Auditorium"), ("Library", "LabA"), ("Cafeteria", "LabB"), ("LabA", "LabB"),
        ("LabB", "Sports"), ("Auditorium", "Hostel"), ("LabA", "Hostel"),
    ]:
        _add_undirected_edge(adjacency, a, b)
    return Graph(adjacency, positions)


def get_all_graphs() -> Dict[str, Graph]:
    return {
        "UrbanGrid-6x6": urban_grid_6x6(),
        "Ladder-10": ladder_10(),
        "BinaryTree-15": binary_tree_15(),
        "HexRing-12": hex_ring_12(),
        "CampusMap": campus_map(),
    }



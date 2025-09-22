from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from heapq import heappop, heappush
from math import sqrt
from typing import Dict, Hashable, Iterable, List, Optional, Tuple


Node = Hashable


@dataclass
class SearchResult:
    path: List[Node]
    distance: int
    visited_count: int
    visited_order: Optional[List[Node]] = None


def reconstruct_path(came_from: Dict[Node, Optional[Node]], start: Node, goal: Node) -> List[Node]:
    path: List[Node] = []
    current: Optional[Node] = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    # Validate that the path actually starts at start
    if not path or path[0] != start:
        return []
    return path


def bfs(adjacency: Dict[Node, Iterable[Node]], start: Node, goal: Node) -> SearchResult:
    """
    Breadth-First Search for unweighted shortest path (by number of edges).
    """
    frontier: deque[Node] = deque([start])
    came_from: Dict[Node, Optional[Node]] = {start: None}
    visited_count = 0

    visited_order: List[Node] = []
    while frontier:
        current = frontier.popleft()
        visited_count += 1
        visited_order.append(current)
        if current == goal:
            break
        for neighbor in adjacency.get(current, []):
            if neighbor not in came_from:
                came_from[neighbor] = current
                frontier.append(neighbor)

    path = reconstruct_path(came_from, start, goal)
    distance = max(0, len(path) - 1)
    return SearchResult(path=path, distance=distance, visited_count=visited_count, visited_order=visited_order)


def dfs(adjacency: Dict[Node, Iterable[Node]], start: Node, goal: Node) -> SearchResult:
    """
    Depth-First Search. Not guaranteed to find the shortest path, but returns a valid path if one exists.
    Distance reported is number of edges along the found path.
    """
    stack: List[Node] = [start]
    came_from: Dict[Node, Optional[Node]] = {start: None}
    visited_count = 0

    visited_order: List[Node] = []
    while stack:
        current = stack.pop()
        visited_count += 1
        visited_order.append(current)
        if current == goal:
            break
        for neighbor in adjacency.get(current, []):
            if neighbor not in came_from:
                came_from[neighbor] = current
                stack.append(neighbor)

    path = reconstruct_path(came_from, start, goal)
    distance = max(0, len(path) - 1)
    return SearchResult(path=path, distance=distance, visited_count=visited_count, visited_order=visited_order)


def euclidean(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def astar(
    adjacency: Dict[Node, Iterable[Node]],
    positions: Dict[Node, Tuple[float, float]],
    start: Node,
    goal: Node,
) -> SearchResult:
    """
    A* pathfinding with unit edge costs and Euclidean heuristic from provided positions.
    """
    open_heap: List[Tuple[float, Node]] = []
    heappush(open_heap, (0.0, start))

    came_from: Dict[Node, Optional[Node]] = {start: None}
    g_score: Dict[Node, float] = {start: 0.0}
    visited_count = 0

    visited_order: List[Node] = []
    while open_heap:
        _, current = heappop(open_heap)
        visited_count += 1
        visited_order.append(current)
        if current == goal:
            path = reconstruct_path(came_from, start, goal)
            return SearchResult(path=path, distance=max(0, len(path) - 1), visited_count=visited_count, visited_order=visited_order)

        for neighbor in adjacency.get(current, []):
            tentative_g = g_score[current] + 1.0  # unit edge cost
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                h = (
                    euclidean(positions[neighbor], positions[goal])
                    if (neighbor in positions and goal in positions)
                    else 0.0
                )
                f = tentative_g + h
                heappush(open_heap, (f, neighbor))

    # If no path
    return SearchResult(path=[], distance=0, visited_count=visited_count, visited_order=visited_order)



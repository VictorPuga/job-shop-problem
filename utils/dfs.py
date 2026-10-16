import sys

from utils.graph import Graph


class DFS:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.best_makespan: int = sys.maxsize
        self.best_orientation: list[tuple[int, int]] = []
        self.current_orientation: list[tuple[int, int]] = []

    def search(self, position: int) -> None:
        if position == len(self.graph.disjunctive_pairs):
            makespan = self.graph.longest_path()

            if makespan is None:
                return

            if makespan < self.best_makespan:
                self.best_makespan = makespan
                self.best_orientation = list(self.current_orientation)

            return
        a, b = self.graph.disjunctive_pairs[position]

        self.graph.add_edge(a, b)
        self.current_orientation.append((a, b))
        self.search(position + 1)
        self.graph.remove_edge(a, b)
        self.current_orientation.pop()

        self.graph.add_edge(b, a)
        self.current_orientation.append((b, a))
        self.search(position + 1)
        self.graph.remove_edge(b, a)
        self.current_orientation.pop()

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

        for from_id, to_id in ((a, b), (b, a)):
            self.graph.add_edge(from_id, to_id)
            self.current_orientation.append((from_id, to_id))

            longest_path = self.graph.longest_path()
            if longest_path is not None and longest_path < self.best_makespan:
                self.search(position + 1)

            self.graph.remove_edge(from_id, to_id)
            self.current_orientation.pop()

import unittest

from tests.fixtures import (
    TINY_DURATIONS,
    TINY_MACHINES,
    TINY_OPTIMAL_MAKESPAN,
)
from utils.dfs import DFS
from utils.graph import Graph


class DFSTinyInstanceTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(TINY_MACHINES, TINY_DURATIONS)
        self.successors_before = {
            id: list(ids) for id, ids in self.graph.successors.items()
        }
        self.dfs = DFS(self.graph)
        self.dfs.search(0)

    def test_finds_optimal_makespan(self):
        self.assertEqual(self.dfs.best_makespan, TINY_OPTIMAL_MAKESPAN)

    def test_best_orientation_has_one_edge_per_pair(self):
        self.assertEqual(
            len(self.dfs.best_orientation), len(self.graph.disjunctive_pairs)
        )
        for (a, b), (x, y) in zip(self.graph.disjunctive_pairs, self.dfs.best_orientation):
            self.assertEqual({a, b}, {x, y})

    def test_best_orientation_reproduces_best_makespan(self):
        for a, b in self.dfs.best_orientation:
            self.graph.add_edge(a, b)
        self.assertEqual(self.graph.longest_path(), self.dfs.best_makespan)

    def test_graph_is_restored_after_search(self):
        self.assertEqual(self.graph.successors, self.successors_before)

    def test_current_orientation_is_empty_after_search(self):
        self.assertEqual(self.dfs.current_orientation, [])


if __name__ == "__main__":
    unittest.main()

import unittest

import numpy as np

from tests.fixtures import (
    TINY_DURATIONS,
    TINY_MACHINES,
    TINY_OPTIMAL_MAKESPAN,
)
from tests.oracle import brute_force_makespan, random_instance
from utils.dfs import DFS
from utils.graph import Graph
from utils.instances import durations, machines


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


class DFSMatchesBruteForceTests(unittest.TestCase):
    def test_random_instances(self):
        rng = np.random.RandomState(0)
        for n_jobs, n_machines in [(2, 2), (2, 3), (3, 2), (3, 3)] * 5:
            m, d = random_instance(rng, n_jobs, n_machines)
            with self.subTest(machines=m.tolist(), durations=d.tolist()):
                dfs = DFS(Graph(m, d))
                dfs.search(0)
                self.assertEqual(dfs.best_makespan, brute_force_makespan(m, d))

    def test_without_pruning_matches_brute_force(self):
        rng = np.random.RandomState(1)
        for n_jobs, n_machines in [(2, 2), (2, 3), (3, 2)] * 3:
            m, d = random_instance(rng, n_jobs, n_machines)
            with self.subTest(machines=m.tolist(), durations=d.tolist()):
                dfs = DFS(Graph(m, d), prune=False)
                dfs.search(0)
                self.assertEqual(dfs.best_makespan, brute_force_makespan(m, d))

    def test_pruning_visits_fewer_calls(self):
        pruned = DFS(Graph(machines, durations))
        unpruned = DFS(Graph(machines, durations), prune=False)
        pruned.search(0)
        unpruned.search(0)
        self.assertLess(pruned.visited, unpruned.visited)

    def test_on_improvement_is_called_with_each_new_best(self):
        makespans = []
        dfs = DFS(
            Graph(machines, durations),
            on_improvement=lambda d: makespans.append(d.best_makespan),
        )
        dfs.search(0)
        self.assertEqual(makespans, sorted(set(makespans), reverse=True))
        self.assertEqual(makespans[-1], 29)

    def test_full_instance(self):
        dfs = DFS(Graph(machines, durations))
        dfs.search(0)
        self.assertEqual(dfs.best_makespan, 29)

    def test_instance_without_disjunctive_pairs(self):
        m = np.array([[0, 1], [2, 3]])
        d = np.array([[3, 4], [1, 5]])
        dfs = DFS(Graph(m, d))
        dfs.search(0)
        self.assertEqual(dfs.best_makespan, 7)


if __name__ == "__main__":
    unittest.main()

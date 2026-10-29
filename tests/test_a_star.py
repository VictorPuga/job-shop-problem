import unittest

from tests.fixtures import TINY_DURATIONS, TINY_MACHINES
from utils.a_star import AStar
from utils.problem import Problem


class AStarTinyInstanceTests(unittest.TestCase):
    def setUp(self):
        self.problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        self.astar = AStar(self.problem)
        self.astar.search()

    def test_finds_optimal_makespan(self):
        self.skipTest("TODO")

    def test_best_sequence_dispatches_every_operation(self):
        self.skipTest("TODO")

    def test_best_sequence_reproduces_best_makespan(self):
        self.skipTest("TODO")


class AStarMatchesBruteForceTests(unittest.TestCase):
    def test_random_instances(self):
        self.skipTest("TODO")

    def test_matches_dfs(self):
        self.skipTest("TODO")


class AStarHeuristicTests(unittest.TestCase):
    def test_unknown_heuristic_raises(self):
        self.skipTest("TODO")

    def test_heuristics_are_admissible(self):
        self.skipTest("TODO")

    def test_heuristic_is_never_negative(self):
        self.skipTest("TODO")


if __name__ == "__main__":
    unittest.main()

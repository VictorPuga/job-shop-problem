import unittest

import numpy as np

from tests.fixtures import (
    TINY_DURATIONS,
    TINY_MACHINES,
    TINY_OPTIMAL_MAKESPAN,
)
from tests.oracle import brute_force_makespan, random_instance
from utils.dfs import DFS
from utils.instances import durations, machines
from utils.problem import Problem


class DFSTinyInstanceTests(unittest.TestCase):
    def setUp(self):
        self.problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        self.dfs = DFS(self.problem)
        self.dfs.search()

    def test_finds_optimal_makespan(self):
        self.assertEqual(self.dfs.best_makespan, TINY_OPTIMAL_MAKESPAN)

    def test_best_sequence_dispatches_every_operation(self):
        self.assertEqual(len(self.dfs.best_sequence), self.problem.n_operations)
        for job in range(self.problem.n_jobs):
            self.assertEqual(
                self.dfs.best_sequence.count(job), self.problem.n_operations_per_job
            )

    def test_best_sequence_reproduces_best_makespan(self):
        start = self.problem.start_times(self.dfs.best_sequence)
        self.assertEqual((start + TINY_DURATIONS).max(), self.dfs.best_makespan)

    def test_search_from_a_state_only_explores_its_completions(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        state = problem.dispatch(problem.initial_state(), 1)
        dfs = DFS(problem, prune=False)
        dfs.search(state)
        self.assertEqual(dfs.best_sequence[0], 1)


class DFSMatchesBruteForceTests(unittest.TestCase):
    def test_random_instances(self):
        rng = np.random.RandomState(0)
        for n_jobs, n_machines in [(2, 2), (2, 3), (3, 2), (3, 3)] * 5:
            m, d = random_instance(rng, n_jobs, n_machines)
            with self.subTest(machines=m.tolist(), durations=d.tolist()):
                dfs = DFS(Problem(m, d))
                dfs.search()
                self.assertEqual(dfs.best_makespan, brute_force_makespan(m, d))

    def test_without_pruning_matches_brute_force(self):
        rng = np.random.RandomState(1)
        for n_jobs, n_machines in [(2, 2), (2, 3), (3, 2)] * 3:
            m, d = random_instance(rng, n_jobs, n_machines)
            with self.subTest(machines=m.tolist(), durations=d.tolist()):
                dfs = DFS(Problem(m, d), prune=False)
                dfs.search()
                self.assertEqual(dfs.best_makespan, brute_force_makespan(m, d))

    def test_pruned_and_unpruned_agree(self):
        rng = np.random.RandomState(4)
        for n_jobs, n_machines in [(3, 3), (4, 2)] * 3:
            m, d = random_instance(rng, n_jobs, n_machines)
            with self.subTest(machines=m.tolist(), durations=d.tolist()):
                pruned = DFS(Problem(m, d))
                unpruned = DFS(Problem(m, d), prune=False)
                pruned.search()
                unpruned.search()
                self.assertEqual(pruned.best_makespan, unpruned.best_makespan)


class DFSInstanceTests(unittest.TestCase):
    def test_pruning_visits_fewer_calls(self):
        pruned = DFS(Problem(machines, durations))
        unpruned = DFS(Problem(machines, durations), prune=False)
        pruned.search()
        unpruned.search()
        self.assertLess(pruned.visited, unpruned.visited)

    def test_unpruned_visits_every_state(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        dfs = DFS(problem, prune=False)
        dfs.search()
        # 1 root + 2 + 4 + 6 + 6 leaves: the 6 orders of (0, 0, 1, 1) at each depth.
        self.assertEqual(dfs.visited, 1 + 2 + 4 + 6 + 6)

    def test_on_improvement_is_called_with_each_new_best(self):
        makespans = []
        dfs = DFS(
            Problem(machines, durations),
            on_improvement=lambda d: makespans.append(d.best_makespan),
        )
        dfs.search()
        self.assertEqual(makespans, sorted(set(makespans), reverse=True))
        self.assertEqual(makespans[-1], 29)

    def test_full_instance(self):
        dfs = DFS(Problem(machines, durations))
        dfs.search()
        self.assertEqual(dfs.best_makespan, 29)

    def test_instance_without_machine_conflicts(self):
        m = np.array([[0, 1], [2, 3]])
        d = np.array([[3, 4], [1, 5]])
        dfs = DFS(Problem(m, d))
        dfs.search()
        self.assertEqual(dfs.best_makespan, 7)

    def test_single_job(self):
        dfs = DFS(Problem(np.array([[0, 1, 0]]), np.array([[2, 3, 4]])))
        dfs.search()
        self.assertEqual(dfs.best_makespan, 9)
        self.assertEqual(dfs.best_sequence, (0, 0, 0))


if __name__ == "__main__":
    unittest.main()

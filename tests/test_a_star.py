import unittest

import numpy as np

from tests.fixtures import (
    TINY_DURATIONS,
    TINY_MACHINES,
    TINY_OPTIMAL_MAKESPAN,
    TINY_OPTIMAL_SEQUENCE,
)
from tests.oracle import brute_force_makespan, random_instance
from utils.a_star import AStar
from utils.dfs import DFS
from utils.instances import durations, machines
from utils.problem import Problem, State


HEURISTICS = ["lower_bound", "machine_heads_tails"]


def reachable_states(problem: Problem) -> list[State]:
    states = []
    stack = [problem.initial_state()]
    while stack:
        state = stack.pop()
        states.append(state)
        for job in problem.available_jobs(state):
            stack.append(problem.dispatch(state, job))
    return states


class AStarTinyInstanceTests(unittest.TestCase):
    def setUp(self):
        self.problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        self.astar = AStar(self.problem, "lower_bound")
        self.astar.search()

    def test_finds_optimal_makespan(self):
        self.assertEqual(self.astar.best_makespan, TINY_OPTIMAL_MAKESPAN)

    def test_best_sequence_dispatches_every_operation(self):
        self.assertEqual(len(self.astar.best_sequence), 4)
        for job in range(self.problem.n_jobs):
            self.assertEqual(
                self.astar.best_sequence.count(job), self.problem.n_operations_per_job
            )

    def test_best_sequence_reproduces_best_makespan(self):
        start = self.problem.start_times(self.astar.best_sequence)
        self.assertEqual((start + TINY_DURATIONS).max(), self.astar.best_makespan)


class AStarMatchesBruteForceTests(unittest.TestCase):
    def test_random_instances(self):
        rng = np.random.RandomState(0)
        for n_jobs, n_machines in [(2, 2), (2, 3), (3, 2), (3, 3)] * 5:
            m, d = random_instance(rng, n_jobs, n_machines)
            with self.subTest(machines=m.tolist(), durations=d.tolist()):
                astar = AStar(Problem(m, d), "lower_bound")
                astar.search()
                self.assertEqual(astar.best_makespan, brute_force_makespan(m, d))

    def test_matches_dfs(self):
        astar = AStar(Problem(machines, durations), "lower_bound")
        dfs = DFS(Problem(machines, durations))
        astar.search()
        dfs.search()
        self.assertEqual(astar.best_makespan, dfs.best_makespan)

    def test_expands_fewer_states_than_dfs(self):
        astar = AStar(Problem(machines, durations), "lower_bound")
        dfs = DFS(Problem(machines, durations))
        astar.search()
        dfs.search()
        self.assertLess(astar.visited, dfs.visited)


class AStarHeuristicTests(unittest.TestCase):
    def test_unknown_heuristic_raises(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        with self.assertRaises(ValueError):
            AStar(problem, "nonexistent")

    def test_heuristics_are_admissible(self):
        rng = np.random.RandomState(2)
        for n_jobs, n_machines in [(2, 2), (2, 3), (3, 2)] * 2:
            m, d = random_instance(rng, n_jobs, n_machines)
            problem = Problem(m, d)
            for name in HEURISTICS:
                astar = AStar(problem, name)
                for state in reachable_states(problem):
                    with self.subTest(heuristic=name, sequence=state.sequence):
                        dfs = DFS(problem, prune=False)
                        dfs.search(state)
                        remaining = dfs.best_makespan - state.makespan()
                        self.assertLessEqual(astar.heuristic(state), remaining)

    def test_heuristic_is_never_negative(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        for name in HEURISTICS:
            astar = AStar(problem, name)
            for state in reachable_states(problem):
                with self.subTest(heuristic=name, sequence=state.sequence):
                    self.assertGreaterEqual(astar.heuristic(state), 0)

    def test_heuristic_is_zero_at_a_goal(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        goal = problem.initial_state()
        for job in TINY_OPTIMAL_SEQUENCE:
            goal = problem.dispatch(goal, job)
        for name in HEURISTICS:
            with self.subTest(heuristic=name):
                self.assertEqual(AStar(problem, name).heuristic(goal), 0)

    def test_machine_heads_tails_dominates_lower_bound(self):
        rng = np.random.RandomState(3)
        for n_jobs, n_machines in [(2, 3), (3, 3)] * 2:
            m, d = random_instance(rng, n_jobs, n_machines)
            problem = Problem(m, d)
            base = AStar(problem, "lower_bound")
            tight = AStar(problem, "machine_heads_tails")
            for state in reachable_states(problem):
                with self.subTest(sequence=state.sequence):
                    self.assertGreaterEqual(
                        tight.heuristic(state), base.heuristic(state)
                    )

    def test_every_heuristic_finds_the_optimum(self):
        rng = np.random.RandomState(5)
        for n_jobs, n_machines in [(2, 3), (3, 2), (3, 3)] * 2:
            m, d = random_instance(rng, n_jobs, n_machines)
            expected = brute_force_makespan(m, d)
            for name in HEURISTICS:
                with self.subTest(heuristic=name, machines=m.tolist()):
                    astar = AStar(Problem(m, d), name)
                    astar.search()
                    self.assertEqual(astar.best_makespan, expected)


if __name__ == "__main__":
    unittest.main()

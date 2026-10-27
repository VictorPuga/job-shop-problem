import itertools
import unittest

import numpy as np

from tests.fixtures import (
    TINY_DURATIONS,
    TINY_MACHINES,
    TINY_OPTIMAL_MAKESPAN,
    TINY_OPTIMAL_SEQUENCE,
    TINY_OPTIMAL_START,
)
from tests.oracle import brute_force_makespan, random_instance
from utils.instances import durations, machines
from utils.problem import Problem


class ProblemDimensionTests(unittest.TestCase):
    def test_dimensions(self):
        problem = Problem(machines, durations)
        self.assertEqual(problem.n_jobs, 4)
        self.assertEqual(problem.n_operations_per_job, 3)
        self.assertEqual(problem.n_machines, 3)
        self.assertEqual(problem.n_jobs * problem.n_operations_per_job, 12)


class InitialStateTests(unittest.TestCase):
    def setUp(self):
        self.problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        self.state = self.problem.initial_state()

    def test_is_empty(self):
        self.assertEqual(self.state.next_operation, (0, 0))
        self.assertEqual(self.state.job_free, (0, 0))
        self.assertEqual(self.state.machine_free, (0, 0))
        self.assertEqual(self.state.sequence, ())
        self.assertEqual(self.state.makespan, 0)

    def test_is_not_complete(self):
        self.assertFalse(self.problem.is_complete(self.state))

    def test_every_job_is_available(self):
        self.assertEqual(self.problem.available_jobs(self.state), [0, 1])


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        self.initial = self.problem.initial_state()

    def test_first_operation_starts_at_zero(self):
        state = self.problem.dispatch(self.initial, 0)
        self.assertEqual(state.next_operation, (1, 0))
        self.assertEqual(state.job_free, (3, 0))
        self.assertEqual(state.machine_free, (3, 0))
        self.assertEqual(state.sequence, (0,))
        self.assertEqual(state.makespan, 3)

    def test_waits_for_the_job(self):
        state = self.problem.dispatch(self.initial, 0)
        state = self.problem.dispatch(state, 0)
        # Job 0 op 1 runs on machine 1, which is free, but the job is busy until 3.
        self.assertEqual(state.job_free[0], 5)
        self.assertEqual(state.machine_free[1], 5)

    def test_waits_for_the_machine(self):
        state = self.problem.dispatch(self.initial, 0)
        state = self.problem.dispatch(state, 1)
        state = self.problem.dispatch(state, 1)
        # Job 1 op 1 runs on machine 0, which job 0 holds until 3; the job is free at 2.
        self.assertEqual(state.job_free[1], 7)
        self.assertEqual(state.machine_free[0], 7)
        self.assertEqual(state.makespan, 7)

    def test_does_not_modify_the_previous_state(self):
        before = self.problem.initial_state()
        self.problem.dispatch(before, 0)
        self.assertEqual(before, self.initial)

    def test_finished_job_is_unavailable(self):
        state = self.problem.dispatch(self.initial, 0)
        state = self.problem.dispatch(state, 0)
        self.assertEqual(self.problem.available_jobs(state), [1])

    def test_dispatching_a_finished_job_raises(self):
        state = self.problem.dispatch(self.initial, 0)
        state = self.problem.dispatch(state, 0)
        with self.assertRaises(ValueError):
            self.problem.dispatch(state, 0)

    def test_complete_after_every_operation(self):
        state = self.initial
        for job in (0, 1, 0, 1):
            state = self.problem.dispatch(state, job)
        self.assertTrue(self.problem.is_complete(state))
        self.assertEqual(self.problem.available_jobs(state), [])


class LowerBoundTests(unittest.TestCase):
    def test_initial_bound_is_the_largest_machine_load(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        # Machine 0 carries 3 + 4 = 7, machine 1 carries 2 + 2 = 4, the longest job is 6.
        self.assertEqual(problem.lower_bound(problem.initial_state()), 7)

    def test_initial_bound_can_be_the_longest_job(self):
        problem = Problem(np.array([[0, 1], [2, 3]]), np.array([[3, 4], [1, 5]]))
        self.assertEqual(problem.lower_bound(problem.initial_state()), 7)

    def test_complete_state_bound_is_the_makespan(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        state = problem.initial_state()
        for job in TINY_OPTIMAL_SEQUENCE:
            state = problem.dispatch(state, job)
        self.assertEqual(problem.lower_bound(state), state.makespan)

    def test_never_exceeds_the_optimum_of_any_completion(self):
        rng = np.random.RandomState(2)
        for n_jobs, n_machines in [(2, 2), (2, 3), (3, 2)] * 3:
            m, d = random_instance(rng, n_jobs, n_machines)
            problem = Problem(m, d)
            optimum = brute_force_makespan(m, d)
            with self.subTest(machines=m.tolist(), durations=d.tolist()):
                self.assertLessEqual(problem.lower_bound(problem.initial_state()), optimum)

    def test_never_decreases_along_a_dispatch(self):
        problem = Problem(machines, durations)
        state = problem.initial_state()
        bound = problem.lower_bound(state)
        for job in itertools.islice(itertools.cycle(range(4)), 12):
            state = problem.dispatch(state, job)
            self.assertGreaterEqual(problem.lower_bound(state), bound)
            bound = problem.lower_bound(state)


class StartTimesTests(unittest.TestCase):
    def test_known_schedule(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        start = problem.start_times(TINY_OPTIMAL_SEQUENCE)
        np.testing.assert_array_equal(start, TINY_OPTIMAL_START)

    def test_empty_sequence_is_all_zeros(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        np.testing.assert_array_equal(problem.start_times(()), np.zeros((2, 2), dtype=int))

    def test_schedules_are_feasible(self):
        problem = Problem(machines, durations)
        rng = np.random.RandomState(3)
        for _ in range(20):
            sequence = tuple(rng.permutation([0, 1, 2, 3] * 3).tolist())
            with self.subTest(sequence=sequence):
                self.assert_feasible(problem, problem.start_times(sequence))

    def assert_feasible(self, problem, start):
        for job in range(problem.n_jobs):
            for operation in range(problem.n_operations_per_job - 1):
                end = start[job, operation] + problem.durations[job, operation]
                self.assertGreaterEqual(start[job, operation + 1], end)

        for machine in range(problem.n_machines):
            intervals = []
            for job in range(problem.n_jobs):
                for operation in range(problem.n_operations_per_job):
                    if problem.machines[job, operation] == machine:
                        begin = start[job, operation]
                        intervals.append((begin, begin + problem.durations[job, operation]))
            intervals.sort()
            for (_, end), (next_start, _) in zip(intervals, intervals[1:]):
                self.assertGreaterEqual(next_start, end)

    def test_makespan_matches_start_times(self):
        problem = Problem(TINY_MACHINES, TINY_DURATIONS)
        state = problem.initial_state()
        for job in TINY_OPTIMAL_SEQUENCE:
            state = problem.dispatch(state, job)
        start = problem.start_times(TINY_OPTIMAL_SEQUENCE)
        self.assertEqual((start + TINY_DURATIONS).max(), state.makespan)
        self.assertEqual(state.makespan, TINY_OPTIMAL_MAKESPAN)


if __name__ == "__main__":
    unittest.main()

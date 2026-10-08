import tempfile
import unittest
from pathlib import Path

import numpy as np

from utils.generator import generate_instance, read_instance, write_instance
from utils.instances import durations, machines
from utils.local_search import NEIGHBORHOODS, LocalSearch
from utils.problem import Problem


class LocalSearchTests(unittest.TestCase):
    def setUp(self):
        self.problem = Problem(machines, durations)

    def test_neighbors_keep_the_same_jobs(self):
        for neighborhood in NEIGHBORHOODS:
            solver = LocalSearch(self.problem, neighborhood=neighborhood)
            sequence = list(solver._random_sequence())
            for _ in range(50):
                neighbor = solver._neighbor(sequence)
                self.assertEqual(sorted(neighbor), sorted(sequence))

    def test_best_sequence_matches_best_makespan(self):
        for neighborhood in NEIGHBORHOODS:
            solver = LocalSearch(self.problem, neighborhood=neighborhood, seed=3)
            solver.search()
            makespan = solver._makespan(solver.best_sequence)
            self.assertEqual(makespan, solver.best_makespan)

    def test_same_seed_same_result(self):
        results = []
        for _ in range(2):
            solver = LocalSearch(self.problem, neighborhood="insert", seed=7)
            solver.search()
            results.append((solver.best_makespan, solver.best_sequence))
        self.assertEqual(results[0], results[1])


class GeneratorTests(unittest.TestCase):
    def test_same_seed_same_instance(self):
        first = generate_instance(5, 4, 4, 1, 10)
        second = generate_instance(5, 4, 4, 1, 10)
        np.testing.assert_array_equal(first[0], second[0])
        np.testing.assert_array_equal(first[1], second[1])

    def test_each_job_uses_every_machine_once(self):
        generated_machines, generated_durations = generate_instance(1, 6, 5, 2, 9)
        for row in generated_machines:
            self.assertEqual(sorted(row), list(range(5)))
        self.assertGreaterEqual(generated_durations.min(), 2)
        self.assertLessEqual(generated_durations.max(), 9)

    def test_write_then_read(self):
        generated = generate_instance(2, 3, 3, 1, 10)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "instance.json"
            write_instance(path, *generated)
            loaded = read_instance(path)
        np.testing.assert_array_equal(generated[0], loaded[0])
        np.testing.assert_array_equal(generated[1], loaded[1])


if __name__ == "__main__":
    unittest.main()

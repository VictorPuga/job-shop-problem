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

    def test_neighbors_keep_the_operation_multiset(self):
        for neighborhood in NEIGHBORHOODS:
            solver = LocalSearch(self.problem, neighborhood=neighborhood)
            sequence = list(solver._generate_random_sequence())
            for _ in range(50):
                neighbor = solver._neighbor(sequence)
                self.assertEqual(sorted(neighbor), sorted(sequence))

    def test_best_sequence_reproduces_best_makespan(self):
        for neighborhood in NEIGHBORHOODS:
            solver = LocalSearch(self.problem, neighborhood=neighborhood, seed=3)
            solver.search()
            self.assertEqual(
                solver._sequence_makespan(solver.best_sequence), solver.best_makespan
            )

    def test_same_seed_is_reproducible(self):
        results = []
        for _ in range(2):
            solver = LocalSearch(self.problem, neighborhood="insert", seed=7)
            solver.search()
            results.append((solver.best_makespan, solver.best_sequence))
        self.assertEqual(results[0], results[1])

    def test_unknown_neighborhood_is_rejected(self):
        with self.assertRaises(ValueError):
            LocalSearch(self.problem, neighborhood="nope")


class GeneratorTests(unittest.TestCase):
    def test_same_seed_gives_same_instance(self):
        first = generate_instance(5, 4, 4, 1, 10)
        second = generate_instance(5, 4, 4, 1, 10)
        np.testing.assert_array_equal(first[0], second[0])
        np.testing.assert_array_equal(first[1], second[1])

    def test_each_job_visits_every_machine_once(self):
        generated_machines, generated_durations = generate_instance(1, 6, 5, 2, 9)
        for row in generated_machines:
            self.assertEqual(sorted(row), list(range(5)))
        self.assertTrue(((generated_durations >= 2) & (generated_durations <= 9)).all())

    def test_write_then_read_round_trips(self):
        generated = generate_instance(2, 3, 3, 1, 10)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "instance.json"
            write_instance(path, *generated)
            loaded = read_instance(path)
        np.testing.assert_array_equal(generated[0], loaded[0])
        np.testing.assert_array_equal(generated[1], loaded[1])


if __name__ == "__main__":
    unittest.main()

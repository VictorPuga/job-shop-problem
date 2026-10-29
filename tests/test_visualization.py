import unittest

import matplotlib

matplotlib.use("Agg")

from utils.dfs import DFS
from utils.instances import durations, machines
from utils.problem import Problem
from utils.visualization import plot_gantt


class GanttTests(unittest.TestCase):
    def test_draws_one_bar_per_operation(self):
        dfs = DFS(Problem(machines, durations))
        dfs.search()
        axes = plot_gantt(dfs, show=False)

        self.assertEqual(len(axes.patches), 12)
        self.assertIn(str(dfs.best_makespan), axes.get_title())


if __name__ == "__main__":
    unittest.main()

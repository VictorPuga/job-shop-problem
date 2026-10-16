import unittest

import matplotlib

matplotlib.use("Agg")

from utils.dfs import DFS
from utils.graph import Graph
from utils.instances import durations, machines
from utils.visualization import LiveGantt


class LiveGanttTests(unittest.TestCase):
    def test_draws_one_bar_per_operation(self):
        gantt = LiveGantt(pause=0.001)
        dfs = DFS(Graph(machines, durations), on_improvement=gantt.update)
        dfs.search(0)

        self.assertEqual(len(gantt.axes.patches), 12)
        self.assertIn(str(dfs.best_makespan), gantt.axes.get_title())


if __name__ == "__main__":
    unittest.main()

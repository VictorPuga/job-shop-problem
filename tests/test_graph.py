import unittest

from utils.graph import Graph
from utils.instances import durations, machines


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph(machines, durations)

    def test_dimensions(self):
        self.assertEqual(self.graph.n_jobs, 4)
        self.assertEqual(self.graph.n_operations_per_job, 3)
        self.assertEqual(self.graph.n_machines, 3)
        self.assertEqual(self.graph.source, 0)
        self.assertEqual(self.graph.sink, 13)

    def test_node_count_includes_source_and_sink(self):
        self.assertEqual(len(self.graph.nodes), 14)

    def test_node_id(self):
        self.assertEqual(self.graph.calculate_node_id(0, 0), 1)
        self.assertEqual(self.graph.calculate_node_id(1, 2), 6)
        self.assertEqual(self.graph.calculate_node_id(3, 2), 12)

    def test_node_data(self):
        node = self.graph.nodes[self.graph.calculate_node_id(1, 0)]
        self.assertEqual((node.job, node.operation, node.machine, node.duration), (1, 0, 1, 8))

    def test_machine_nodes(self):
        self.assertEqual(self.graph.machine_nodes[0], [1, 5, 7, 11])
        self.assertEqual(self.graph.machine_nodes[1], [2, 4, 9, 12])
        self.assertEqual(self.graph.machine_nodes[2], [3, 6, 8, 10])

    def test_job_chains(self):
        self.assertEqual(self.graph.successors[0], [1, 4, 7, 10])
        self.assertEqual(self.graph.successors[1], [2])
        self.assertEqual(self.graph.successors[2], [3])
        self.assertEqual(self.graph.successors[3], [13])
        self.assertEqual(self.graph.successors[13], [])

    def test_disjunctive_pairs(self):
        self.assertEqual(len(self.graph.disjunctive_pairs), 18)
        self.assertEqual(len(set(self.graph.disjunctive_pairs)), 18)
        for a, b in self.graph.disjunctive_pairs:
            self.assertLess(a, b)
            self.assertEqual(self.graph.nodes[a].machine, self.graph.nodes[b].machine)

    def test_disjunctive_pairs_are_not_edges_yet(self):
        for a, b in self.graph.disjunctive_pairs:
            self.assertNotIn(b, self.graph.successors[a])
            self.assertNotIn(a, self.graph.successors[b])

    def test_add_and_remove_edge(self):
        self.graph.add_edge(1, 5)
        self.assertIn(5, self.graph.successors[1])
        self.graph.remove_edge(1, 5)
        self.assertNotIn(5, self.graph.successors[1])

    def test_remove_missing_edge_raises(self):
        with self.assertRaises(ValueError):
            self.graph.remove_edge(1, 5)


if __name__ == "__main__":
    unittest.main()

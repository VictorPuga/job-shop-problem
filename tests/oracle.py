import itertools

import numpy as np
from numpy.typing import NDArray

from utils.graph import Graph


def brute_force_makespan(machines: NDArray[np.int_], durations: NDArray[np.int_]) -> int:
    """Lowest makespan over every orientation of the disjunctive pairs, with no pruning."""
    graph = Graph(machines, durations)
    pairs = graph.disjunctive_pairs
    best = None

    for directions in itertools.product((0, 1), repeat=len(pairs)):
        edges = [(a, b) if d == 0 else (b, a) for (a, b), d in zip(pairs, directions)]

        for from_id, to_id in edges:
            graph.add_edge(from_id, to_id)
        makespan = graph.longest_path()
        for from_id, to_id in edges:
            graph.remove_edge(from_id, to_id)

        if makespan is not None and (best is None or makespan < best):
            best = makespan

    assert best is not None
    return best


def random_instance(
    rng: np.random.RandomState, n_jobs: int, n_machines: int
) -> tuple[NDArray[np.int_], NDArray[np.int_]]:
    """Each job visits every machine once, in a random order."""
    machines = np.array([rng.permutation(n_machines) for _ in range(n_jobs)])
    durations = rng.randint(1, 10, size=(n_jobs, n_machines))
    return machines, durations

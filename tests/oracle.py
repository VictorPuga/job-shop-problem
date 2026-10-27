import itertools

import numpy as np
from numpy.typing import NDArray


def brute_force_makespan(machines: NDArray[np.int_], durations: NDArray[np.int_]) -> int:
    """Lowest makespan over every order of the operations on each machine, with no search.

    It is independent of `Problem`: start times come from relaxing the job and
    machine precedences until they stop changing, and orders that never settle
    (a cycle) are skipped.
    """
    n_jobs, n_operations = durations.shape
    n_machines = int(machines.max()) + 1

    operations_on = [
        [
            (job, operation)
            for job in range(n_jobs)
            for operation in range(n_operations)
            if machines[job, operation] == machine
        ]
        for machine in range(n_machines)
    ]

    best = None

    for orders in itertools.product(
        *(itertools.permutations(ops) for ops in operations_on)
    ):
        predecessors = {
            (job, operation): [(job, operation - 1)] if operation > 0 else []
            for job in range(n_jobs)
            for operation in range(n_operations)
        }
        for order in orders:
            for before, after in zip(order, order[1:]):
                predecessors[after].append(before)

        start = dict.fromkeys(predecessors, 0)
        settled = False
        for _ in range(n_jobs * n_operations + 1):
            changed = False
            for node, before in predecessors.items():
                earliest = max(
                    (start[p] + int(durations[p]) for p in before), default=0
                )
                if earliest > start[node]:
                    start[node] = earliest
                    changed = True
            if not changed:
                settled = True
                break

        if not settled:
            continue

        makespan = max(start[node] + int(durations[node]) for node in start)
        if best is None or makespan < best:
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

import numpy as np

# Tiny instance: 2 jobs x 2 operations, 2 machines, 2 disjunctive pairs.
# Node ids: 1 = job 0 op 0, 2 = job 0 op 1, 3 = job 1 op 0, 4 = job 1 op 1.
# Pairs: (1, 4) on machine 0 and (2, 3) on machine 1.
TINY_MACHINES = np.array(
    [
        [0, 1],
        [1, 0],
    ]
)

TINY_DURATIONS = np.array(
    [
        [3, 2],
        [2, 4],
    ]
)

# Of the 4 orientations, 3 are valid and 1 is cyclic (4 -> 1 together with 2 -> 3).
# The valid makespans are 7, 11 and 11.
TINY_OPTIMAL_MAKESPAN = 7

# One optimal orientation: job 0 first on machine 0, job 1 first on machine 1.
TINY_OPTIMAL_ORIENTATION = [(1, 4), (3, 2)]

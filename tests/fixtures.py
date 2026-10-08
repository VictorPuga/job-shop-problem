import numpy as np

# Tiny instance: 2 jobs x 2 operations, 2 machines.
# Job 0 runs on machine 0 then machine 1, job 1 on machine 1 then machine 0.
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

TINY_OPTIMAL_MAKESPAN = 7

# Job 0 first on machine 0, job 1 first on machine 1.
TINY_OPTIMAL_SEQUENCE = (0, 1, 0, 1)

# Start times of TINY_OPTIMAL_SEQUENCE, start[job, operation].
TINY_OPTIMAL_START = np.array(
    [
        [0, 3],
        [0, 3],
    ]
)

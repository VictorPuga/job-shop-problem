import numpy as np
from numpy.typing import NDArray

# machines[job, operation] = machine assigned to job operation
machines: NDArray[np.int_] = np.array(
    [
        [0, 1, 2],
        [1, 0, 2],
        [0, 2, 1],
        [2, 0, 1],
    ]
)

# durations[job, operation] = duration of job operation
durations: NDArray[np.int_] = np.array(
    [
        [1, 3, 2],
        [8, 5, 10],
        [5, 4, 8],
        [4, 10, 6],
    ]
)

# example_solution[job, operation] = start time of job operation
example_solution = np.array(
    [
        [5, 8, 23],
        [0, 8, 13],
        [0, 5, 11],
        [0, 13, 23],
    ]
)

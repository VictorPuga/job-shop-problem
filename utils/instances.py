import numpy as np
from numpy.typing import NDArray

from utils.generator import INSTANCES_DIR, read_instance

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

# ft06 (Fisher & Thompson), 6x6, optimal makespan 55
ft06_machines: NDArray[np.int_] = np.array(
    [
        [2, 0, 1, 3, 5, 4],
        [1, 2, 4, 5, 0, 3],
        [2, 3, 5, 0, 1, 4],
        [1, 0, 2, 3, 4, 5],
        [2, 1, 4, 5, 0, 3],
        [1, 3, 5, 0, 4, 2],
    ]
)

ft06_durations: NDArray[np.int_] = np.array(
    [
        [1, 3, 6, 7, 3, 6],
        [8, 5, 10, 10, 10, 4],
        [5, 4, 8, 9, 1, 7],
        [5, 5, 5, 3, 8, 9],
        [9, 3, 5, 4, 3, 1],
        [3, 3, 9, 10, 4, 1],
    ]
)

# ft06 cropped to its first 4 jobs and machines 0-3, 4x4, optimal makespan 33 (computed with the DFS)
ft06_4x4_machines: NDArray[np.int_] = np.array(
    [
        [2, 0, 1, 3],
        [1, 2, 0, 3],
        [2, 3, 0, 1],
        [1, 0, 2, 3],
    ]
)

ft06_4x4_durations: NDArray[np.int_] = np.array(
    [
        [1, 3, 6, 7],
        [8, 5, 10, 4],
        [5, 4, 9, 1],
        [5, 5, 5, 3],
    ]
)

# la01 (Lawrence), 10x5, optimal makespan 666
la01_machines: NDArray[np.int_] = np.array(
    [
        [1, 0, 4, 3, 2],
        [0, 3, 4, 2, 1],
        [3, 4, 1, 2, 0],
        [1, 0, 4, 2, 3],
        [0, 3, 2, 1, 4],
        [1, 2, 4, 0, 3],
        [3, 4, 1, 2, 0],
        [2, 0, 1, 3, 4],
        [3, 1, 4, 0, 2],
        [4, 3, 2, 1, 0],
    ]
)

la01_durations: NDArray[np.int_] = np.array(
    [
        [21, 53, 95, 55, 34],
        [21, 52, 16, 26, 71],
        [39, 98, 42, 31, 12],
        [77, 55, 79, 66, 77],
        [83, 34, 64, 19, 37],
        [54, 43, 79, 92, 62],
        [69, 77, 87, 87, 93],
        [38, 60, 41, 24, 83],
        [17, 49, 25, 44, 98],
        [77, 79, 43, 75, 96],
    ]
)

# ft10 (Fisher & Thompson), 10x10, optimal makespan 930
ft10_machines: NDArray[np.int_] = np.array(
    [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [0, 2, 4, 9, 3, 1, 6, 5, 7, 8],
        [1, 0, 3, 2, 8, 5, 7, 6, 9, 4],
        [1, 2, 0, 4, 6, 8, 7, 3, 9, 5],
        [2, 0, 1, 5, 3, 4, 8, 7, 9, 6],
        [2, 1, 5, 3, 8, 9, 0, 6, 4, 7],
        [1, 0, 3, 2, 6, 5, 9, 8, 7, 4],
        [2, 0, 1, 5, 4, 6, 8, 9, 7, 3],
        [0, 1, 3, 5, 2, 9, 6, 7, 4, 8],
        [1, 0, 2, 6, 8, 9, 5, 3, 4, 7],
    ]
)

ft10_durations: NDArray[np.int_] = np.array(
    [
        [29, 78, 9, 36, 49, 11, 62, 56, 44, 21],
        [43, 90, 75, 11, 69, 28, 46, 46, 72, 30],
        [91, 85, 39, 74, 90, 10, 12, 89, 45, 33],
        [81, 95, 71, 99, 9, 52, 85, 98, 22, 43],
        [14, 6, 22, 61, 26, 69, 21, 49, 72, 53],
        [84, 2, 52, 95, 48, 72, 47, 65, 6, 25],
        [46, 37, 61, 13, 32, 21, 32, 89, 30, 55],
        [31, 86, 46, 74, 32, 88, 19, 48, 36, 79],
        [76, 69, 76, 51, 85, 11, 40, 89, 26, 74],
        [85, 13, 61, 7, 64, 76, 47, 52, 90, 45],
    ]
)

# la36 (Lawrence), 15x15, optimal makespan 1268
la36_machines: NDArray[np.int_] = np.array(
    [
        [4, 3, 6, 14, 10, 2, 9, 1, 0, 7, 8, 5, 12, 11, 13],
        [11, 4, 1, 7, 8, 14, 12, 0, 3, 6, 9, 5, 10, 13, 2],
        [9, 5, 2, 7, 4, 12, 0, 13, 6, 10, 3, 11, 8, 1, 14],
        [5, 0, 9, 6, 4, 13, 7, 8, 11, 12, 2, 1, 10, 14, 3],
        [10, 4, 8, 2, 0, 11, 14, 9, 6, 7, 1, 13, 3, 5, 12],
        [0, 2, 4, 13, 3, 12, 14, 6, 1, 9, 11, 8, 7, 10, 5],
        [8, 4, 12, 0, 7, 11, 6, 10, 3, 13, 1, 5, 14, 2, 9],
        [4, 13, 11, 3, 7, 9, 1, 2, 12, 8, 14, 0, 10, 6, 5],
        [5, 1, 6, 8, 13, 10, 2, 3, 7, 11, 14, 4, 0, 9, 12],
        [11, 5, 4, 8, 7, 0, 9, 6, 14, 3, 10, 13, 2, 12, 1],
        [7, 3, 0, 4, 12, 14, 10, 1, 9, 13, 5, 8, 2, 11, 6],
        [1, 2, 3, 5, 4, 6, 9, 7, 10, 8, 11, 13, 12, 0, 14],
        [3, 7, 13, 5, 11, 12, 2, 4, 10, 1, 9, 6, 14, 8, 0],
        [9, 7, 5, 14, 10, 4, 11, 2, 1, 3, 13, 6, 0, 12, 8],
        [9, 10, 11, 14, 8, 0, 7, 6, 12, 1, 2, 13, 4, 3, 5],
    ]
)

la36_durations: NDArray[np.int_] = np.array(
    [
        [21, 55, 71, 98, 12, 34, 16, 21, 53, 26, 52, 95, 31, 42, 39],
        [54, 83, 77, 64, 34, 79, 43, 55, 77, 19, 37, 79, 92, 62, 66],
        [83, 77, 87, 38, 60, 98, 93, 17, 41, 44, 69, 49, 24, 87, 25],
        [77, 96, 28, 7, 95, 35, 35, 76, 9, 95, 43, 75, 61, 10, 79],
        [87, 28, 50, 59, 46, 45, 9, 43, 52, 27, 91, 41, 16, 59, 39],
        [20, 71, 78, 66, 14, 8, 42, 28, 54, 33, 89, 26, 37, 33, 43],
        [69, 96, 17, 69, 45, 31, 78, 20, 27, 87, 74, 84, 76, 94, 81],
        [58, 90, 76, 81, 23, 28, 18, 32, 86, 99, 97, 24, 45, 72, 25],
        [27, 46, 67, 27, 19, 80, 17, 48, 62, 12, 28, 98, 42, 48, 50],
        [37, 80, 75, 55, 50, 94, 14, 41, 72, 50, 61, 79, 98, 18, 63],
        [65, 96, 47, 75, 69, 58, 33, 71, 22, 32, 57, 79, 14, 31, 60],
        [34, 47, 58, 51, 62, 44, 8, 17, 97, 29, 15, 66, 40, 44, 38],
        [50, 57, 61, 20, 85, 90, 58, 63, 84, 39, 87, 21, 56, 32, 57],
        [84, 45, 15, 41, 18, 82, 29, 70, 67, 30, 50, 23, 20, 21, 38],
        [37, 81, 61, 57, 57, 52, 74, 62, 30, 52, 38, 68, 54, 54, 16],
    ]
)

# Known optimal makespan per instance (ft06_4x4 computed with the DFS, not an official benchmark)
OPTIMAL_MAKESPANS: dict[str, int] = {
    "example": 29,
    "ft06_4x4": 33,
    "ft06": 55,
    "la01": 666,
    "ft10": 930,
    "la36": 1268,
}

# Instances selectable from main.py, each as a (machines, durations) pair
INSTANCES: dict[str, tuple[NDArray[np.int_], NDArray[np.int_]]] = {
    "example": (machines, durations),
    "ft06_4x4": (ft06_4x4_machines, ft06_4x4_durations),
    "ft06": (ft06_machines, ft06_durations),
    "la01": (la01_machines, la01_durations),
    "ft10": (ft10_machines, ft10_durations),
    "la36": (la36_machines, la36_durations),
}

# Instances stored as files in instances/, named after the file
for _path in sorted(INSTANCES_DIR.glob("*.json")):
    INSTANCES[_path.stem] = read_instance(_path)

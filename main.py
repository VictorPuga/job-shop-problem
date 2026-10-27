import time

import numpy as np
from numpy.typing import NDArray

from utils.dfs import DFS
from utils.instances import durations, machines
from utils.problem import Problem

PRUNE_DFS = True
VISUALIZE = False


def describe(job: int, operation: int) -> str:
    return f"J{job + 1}.O{operation + 1}"


def run(prune: bool, gantt=None) -> tuple[Problem, DFS, float]:
    problem = Problem(machines, durations)
    dfs = DFS(problem, prune=prune, on_improvement=gantt.update if gantt else None)

    start = time.perf_counter()
    dfs.search()
    elapsed = time.perf_counter() - start

    return problem, dfs, elapsed


def print_sequence(dfs: DFS) -> None:
    jobs = " ".join(f"J{job + 1}" for job in dfs.best_sequence)
    print(f"Dispatch sequence: {jobs}")


def print_schedule(problem: Problem, start: NDArray[np.int_]) -> None:
    print("Order on each machine (J = job, O = operation):")

    for machine in range(problem.n_machines):
        operations = [
            (job, operation)
            for job in range(problem.n_jobs)
            for operation in range(problem.n_operations_per_job)
            if problem.machines[job, operation] == machine
        ]
        operations.sort(key=lambda op: start[op])
        sequence = " -> ".join(describe(*op) for op in operations)
        print(f"  M{machine + 1}: {sequence}")


def print_start_times(problem: Problem, start: NDArray[np.int_]) -> None:
    print("Start time of each operation (rows = jobs, columns = operations):")
    header = "".join(f"{f'O{op + 1}':>6}" for op in range(problem.n_operations_per_job))
    print(f"{'':<6}{header}")

    for job in range(problem.n_jobs):
        times = "".join(f"{time:>6}" for time in start[job])
        print(f"{f'J{job + 1}':<6}{times}")


def main() -> None:
    gantt = None
    if VISUALIZE:
        from utils.visualization import LiveGantt

        gantt = LiveGantt()

    problem, dfs, elapsed = run(PRUNE_DFS, gantt)
    print(f"DFS Pruning: {'on' if PRUNE_DFS else 'off'}")
    print(f"Best makespan: {dfs.best_makespan}")
    print(f"Search calls: {dfs.visited}")
    print(
        f"Search time: {elapsed:.3f} s{' (includes plotting pauses)' if gantt else ''}"
    )
    print_sequence(dfs)

    start = problem.start_times(dfs.best_sequence)
    print_schedule(problem, start)
    print_start_times(problem, start)

    if gantt:
        gantt.show()


if __name__ == "__main__":
    main()

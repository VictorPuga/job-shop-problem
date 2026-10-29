import logging
import time

import numpy as np
from numpy.typing import NDArray

from utils.dfs import DFS
from utils.instances import INSTANCES
from utils.log import setup_logging
from utils.problem import Problem

INSTANCE = "example"
PRUNE_DFS = True
VISUALIZE = False
LOG_NODES = False


def print_schedule(problem: Problem, start: NDArray[np.int_]) -> None:
    print("Order on each machine:")
    for machine in range(problem.n_machines):
        operations = []
        for job in range(problem.n_jobs):
            for operation in range(problem.n_operations_per_job):
                if problem.machines[job, operation] == machine:
                    operations.append((job, operation))

        operations.sort(key=lambda item: start[item])

        names = []
        for job, operation in operations:
            names.append(f"J{job + 1}.O{operation + 1}")
        print(f"  M{machine + 1}: " + " -> ".join(names))

    print("Start times (rows = jobs, columns = operations):")
    for job in range(problem.n_jobs):
        line = f"  J{job + 1}:"
        for operation in range(problem.n_operations_per_job):
            line += f" {start[job, operation]:>3}"
        print(line)


def main() -> None:
    machines, durations = INSTANCES[INSTANCE]
    problem = Problem(machines, durations)
    dfs = DFS(problem, prune=PRUNE_DFS)

    log_path = setup_logging(
        INSTANCE, "dfs", logging.DEBUG if LOG_NODES else logging.INFO
    )
    print(f"Log file: {log_path}", flush=True)
    logging.getLogger("utils.dfs").info(
        "start instance=%s prune=%s", INSTANCE, PRUNE_DFS
    )

    begin = time.perf_counter()
    dfs.search()
    elapsed = time.perf_counter() - begin

    logging.getLogger("utils.dfs").info(
        "done best=%d visited=%d elapsed=%.3fs", dfs.best_makespan, dfs.visited, elapsed
    )

    print(f"Instance: {INSTANCE}")
    print(f"DFS Pruning: {'on' if PRUNE_DFS else 'off'}")
    print(f"Best makespan: {dfs.best_makespan}")
    print(f"Search calls: {dfs.visited}")
    print(f"Search time: {elapsed:.3f} s")
    sequence = ""
    for job in dfs.best_sequence:
        sequence += f" J{job + 1}"
    print(f"Dispatch sequence:{sequence}")

    print_schedule(problem, problem.start_times(dfs.best_sequence))

    if VISUALIZE:
        from utils.visualization import plot_gantt

        plot_gantt(dfs)


if __name__ == "__main__":
    main()

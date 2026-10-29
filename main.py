import logging
import time

import numpy as np
from numpy.typing import NDArray

from utils.a_star import AStar
from utils.dfs import DFS
from utils.instances import INSTANCES
from utils.log import setup_logging
from utils.problem import Problem

INSTANCE = "example"
ALGORITHM = "dfs"
HEURISTIC = "lower_bound"
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


def build_solver(problem: Problem) -> DFS | AStar:
    if ALGORITHM == "dfs":
        return DFS(problem, prune=PRUNE_DFS)
    if ALGORITHM == "a_star":
        return AStar(problem, heuristic=HEURISTIC)
    raise ValueError(f"Unknown algorithm {ALGORITHM!r}")


def main() -> None:
    machines, durations = INSTANCES[INSTANCE]
    problem = Problem(machines, durations)
    solver = build_solver(problem)

    log_path = setup_logging(
        INSTANCE, ALGORITHM, logging.DEBUG if LOG_NODES else logging.INFO
    )
    print(f"Log file: {log_path}", flush=True)
    logger = logging.getLogger(f"utils.{ALGORITHM}")
    logger.info("start instance=%s algorithm=%s", INSTANCE, ALGORITHM)

    begin = time.perf_counter()
    solver.search()
    elapsed = time.perf_counter() - begin

    logger.info(
        "done best=%d visited=%d elapsed=%.3fs",
        solver.best_makespan,
        solver.visited,
        elapsed,
    )

    print(f"Instance: {INSTANCE}")
    print(f"Algorithm: {ALGORITHM}")
    if ALGORITHM == "dfs":
        print(f"DFS Pruning: {'on' if PRUNE_DFS else 'off'}")
    else:
        print(f"Heuristic: {HEURISTIC}")
    print(f"Best makespan: {solver.best_makespan}")
    print(f"Visited: {solver.visited}")
    print(f"Search time: {elapsed:.3f} s")
    sequence = ""
    for job in solver.best_sequence:
        sequence += f" J{job + 1}"
    print(f"Dispatch sequence:{sequence}")

    print_schedule(problem, problem.start_times(solver.best_sequence))

    if VISUALIZE:
        from utils.visualization import plot_gantt

        plot_gantt(solver)


if __name__ == "__main__":
    main()

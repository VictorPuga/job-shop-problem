import argparse
import logging
import time

import numpy as np
from numpy.typing import NDArray

from utils.a_star import AStar
from utils.dfs import DFS
from utils.instances import INSTANCES
from utils.local_search import LocalSearch
from utils.log import setup_logging
from utils.problem import Problem

ALGORITHMS = ["dfs", "a_star", "local_search"]
HEURISTICS = ["lower_bound", "machine_heads_tails"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Job-shop scheduling solver.")
    parser.add_argument("-a", "--algorithm", choices=ALGORITHMS, default="dfs")
    parser.add_argument("-i", "--instance", choices=sorted(INSTANCES), default="example")
    parser.add_argument(
        "--heuristic",
        choices=HEURISTICS,
        default="machine_heads_tails",
        help="heuristic for a_star",
    )
    parser.add_argument("--no-prune", action="store_true", help="disable DFS pruning")
    parser.add_argument("--seed", type=int, default=42, help="seed for local_search")
    parser.add_argument("--visualize", action="store_true", help="show a Gantt chart")
    parser.add_argument(
        "--log-nodes",
        action="store_true",
        help="log every node and neighbor (very large files)",
    )
    return parser.parse_args()


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


def build_solver(args: argparse.Namespace, problem: Problem) -> DFS | AStar | LocalSearch:
    if args.algorithm == "dfs":
        return DFS(problem, prune=not args.no_prune)
    if args.algorithm == "a_star":
        return AStar(problem, heuristic=args.heuristic)
    return LocalSearch(problem, seed=args.seed)


def main() -> None:
    args = parse_args()
    machines, durations = INSTANCES[args.instance]
    problem = Problem(machines, durations)
    solver = build_solver(args, problem)

    log_path = setup_logging(
        args.instance, args.algorithm, logging.DEBUG if args.log_nodes else logging.INFO
    )
    print(f"Log file: {log_path}", flush=True)
    logger = logging.getLogger(f"utils.{args.algorithm}")
    logger.info("start", extra={"instance": args.instance, "algorithm": args.algorithm})

    begin = time.perf_counter()
    solver.search()
    elapsed = time.perf_counter() - begin

    logger.info(
        "done",
        extra={
            "best": solver.best_makespan,
            "visited": solver.visited,
            "elapsed": round(elapsed, 3),
        },
    )

    print(f"Instance: {args.instance}")
    print(f"Algorithm: {args.algorithm}")
    if args.algorithm == "dfs":
        print(f"DFS Pruning: {'off' if args.no_prune else 'on'}")
    elif args.algorithm == "a_star":
        print(f"Heuristic: {args.heuristic}")
    else:
        print(f"Seed: {args.seed}")
    print(f"Best makespan: {solver.best_makespan}")
    print(f"Visited: {solver.visited}")
    print(f"Search time: {elapsed:.3f} s")
    sequence = ""
    for job in solver.best_sequence:
        sequence += f" J{job + 1}"
    print(f"Dispatch sequence:{sequence}")

    print_schedule(problem, problem.start_times(solver.best_sequence))

    if args.visualize:
        from utils.visualization import plot_gantt

        plot_gantt(solver)


if __name__ == "__main__":
    main()

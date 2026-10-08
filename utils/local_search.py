import logging
import random
import time

from utils.problem import Problem

logger = logging.getLogger(__name__)

NEIGHBORHOODS = ["swap", "insert"]
NEIGHBORS_PER_ITERATION = 25


class LocalSearch:
    def __init__(
        self,
        problem: Problem,
        max_iterations: int = 500,
        restarts: int = 10,
        seed: int = 42,
        neighborhood: str = "swap",
    ):
        self.problem = problem
        self.max_iterations = max_iterations
        self.restarts = restarts
        self.seed = seed
        self.neighborhood = neighborhood
        self.rng = random.Random(seed)
        self.visited = 0
        self.best_makespan = float("inf")
        self.best_sequence = ()
        self.best_found_at = None

    def _makespan(self, sequence):
        state = self.problem.initial_state()
        for job in sequence:
            state = self.problem.dispatch(state, job)
        return state.makespan()

    def _random_sequence(self):
        sequence = []
        for job in range(self.problem.n_jobs):
            sequence += [job] * self.problem.n_operations_per_job
        self.rng.shuffle(sequence)
        return sequence

    def _neighbor(self, sequence):
        i, j = self.rng.sample(range(len(sequence)), 2)
        neighbor = list(sequence)
        if self.neighborhood == "swap":
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        else:
            neighbor.insert(j, neighbor.pop(i))
        return neighbor

    def _update_best(self, sequence, makespan, restart, iteration):
        if makespan >= self.best_makespan:
            return
        self.best_makespan = makespan
        self.best_sequence = tuple(sequence)
        self.best_found_at = time.perf_counter()
        logger.info(
            "new_best",
            extra={
                "makespan": makespan,
                "restart": restart,
                "iteration": iteration,
                "visited": self.visited,
                "sequence": sequence,
            },
        )

    def search(self):
        for restart in range(self.restarts):
            current = self._random_sequence()
            current_makespan = self._makespan(current)
            self.visited += 1
            logger.debug(
                "restart_start",
                extra={
                    "restart": restart,
                    "makespan": current_makespan,
                    "sequence": current,
                },
            )
            self._update_best(current, current_makespan, restart, 0)

            iteration = 0
            improved = True
            while improved and iteration < self.max_iterations:
                improved = False
                iteration += 1
                for _ in range(NEIGHBORS_PER_ITERATION):
                    neighbor = self._neighbor(current)
                    makespan = self._makespan(neighbor)
                    self.visited += 1
                    logger.debug(
                        "neighbor",
                        extra={
                            "restart": restart,
                            "iteration": iteration,
                            "makespan": makespan,
                            "current": current_makespan,
                        },
                    )
                    if makespan < current_makespan:
                        current = neighbor
                        current_makespan = makespan
                        improved = True
                        self._update_best(current, makespan, restart, iteration)
                        break

            logger.info(
                "restart_done",
                extra={
                    "restart": restart,
                    "makespan": current_makespan,
                    "iterations": iteration,
                    "best": self.best_makespan,
                    "visited": self.visited,
                },
            )

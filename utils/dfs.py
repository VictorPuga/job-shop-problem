import logging
import sys
import time

from utils.problem import Problem, State

logger = logging.getLogger(__name__)

PROGRESS_INTERVAL = 100_000


class DFS:
    def __init__(self, problem: Problem, prune: bool = True) -> None:
        self.problem = problem
        self.prune = prune
        self.visited: int = 0
        self.best_makespan: int = sys.maxsize
        self.best_sequence: tuple[int, ...] = ()
        self.best_found_at: float | None = None

    def search(self, state: State | None = None) -> None:
        if state is None:
            state = self.problem.initial_state()

        self.visited += 1
        depth = len(state.sequence)
        logger.debug(
            "visit",
            extra={
                "visited": self.visited,
                "depth": depth,
                "sequence": state.sequence,
            },
        )
        if self.visited % PROGRESS_INTERVAL == 0:
            logger.info(
                "progress",
                extra={
                    "visited": self.visited,
                    "best": self.best_makespan,
                    "depth": depth,
                },
            )

        if self.problem.is_complete(state):
            makespan = state.makespan()
            if makespan < self.best_makespan:
                self.best_makespan = makespan
                self.best_sequence = state.sequence
                self.best_found_at = time.perf_counter()
                logger.info(
                    "new_best",
                    extra={
                        "makespan": makespan,
                        "visited": self.visited,
                        "sequence": state.sequence,
                    },
                )
            return

        if self.prune:
            bound = self.problem.lower_bound(state)
            if bound >= self.best_makespan:
                logger.debug(
                    "prune",
                    extra={"depth": depth, "bound": bound, "best": self.best_makespan},
                )
                return

        for job in self.problem.available_jobs(state):
            self.search(self.problem.dispatch(state, job))

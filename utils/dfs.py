import logging
import sys
from collections.abc import Callable

from utils.problem import Problem, State

logger = logging.getLogger(__name__)

PROGRESS_INTERVAL = 100_000


class DFS:
    def __init__(
        self,
        problem: Problem,
        prune: bool = True,
        on_improvement: Callable[["DFS"], None] | None = None,
    ) -> None:
        self.problem = problem
        self.prune = prune
        self.on_improvement = on_improvement
        self.visited: int = 0
        self.best_makespan: int = sys.maxsize
        self.best_sequence: tuple[int, ...] = ()

    def search(self, state: State | None = None) -> None:
        if state is None:
            state = self.problem.initial_state()

        self.visited += 1
        depth = len(state.sequence)
        logger.debug(
            "visit #%d depth=%d sequence=%s", self.visited, depth, state.sequence
        )
        if self.visited % PROGRESS_INTERVAL == 0:
            logger.info(
                "progress visited=%d best=%d depth=%d",
                self.visited,
                self.best_makespan,
                depth,
            )

        if self.problem.is_complete(state):
            makespan = state.makespan()
            if makespan < self.best_makespan:
                self.best_makespan = makespan
                self.best_sequence = state.sequence
                logger.info(
                    "new best makespan=%d visited=%d sequence=%s",
                    makespan,
                    self.visited,
                    state.sequence,
                )
                if self.on_improvement:
                    self.on_improvement(self)
            return

        if self.prune:
            bound = self.problem.lower_bound(state)
            if bound >= self.best_makespan:
                logger.debug(
                    "prune depth=%d bound=%d best=%d", depth, bound, self.best_makespan
                )
                return

        for job in self.problem.available_jobs(state):
            self.search(self.problem.dispatch(state, job))

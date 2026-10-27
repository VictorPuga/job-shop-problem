import sys
from collections.abc import Callable

from utils.problem import Problem, State


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

        if self.problem.is_complete(state):
            if state.makespan < self.best_makespan:
                self.best_makespan = state.makespan
                self.best_sequence = state.sequence
                if self.on_improvement:
                    self.on_improvement(self)
            return

        if self.prune and self.problem.lower_bound(state) >= self.best_makespan:
            return

        for job in self.problem.available_jobs(state):
            self.search(self.problem.dispatch(state, job))

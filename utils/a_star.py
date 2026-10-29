import heapq
import sys

from utils.problem import Problem, State


class AStar:
    def __init__(self, problem: Problem, heuristic: str):
        self.problem = problem
        self.visited: int = 0
        self.visited_states: set[tuple[tuple[int, ...], ...]] = set()
        self.push_count: int = 0
        self.best_makespan: int = sys.maxsize
        self.best_sequence: tuple[int, ...] = ()

        self.heuristic = self.select_heuristic(heuristic)
        self.frontier: list[tuple[int, int, State]] = []

    def search(self) -> None:
        self.push(self.problem.initial_state())

        while self.frontier:
            _, _, state = heapq.heappop(self.frontier)
            key = state.key()
            if key in self.visited_states:
                continue
            self.visited_states.add(key)

            self.visited += 1

            if self.problem.is_complete(state):
                self.best_makespan = state.makespan()
                self.best_sequence = state.sequence
                return

            for job in self.problem.available_jobs(state):
                new_state = self.problem.dispatch(state, job)
                if new_state.key() not in self.visited_states:
                    self.push(new_state)

    def push(self, state: State) -> None:
        f = state.makespan() + self.heuristic(state)
        self.push_count += 1
        heapq.heappush(self.frontier, (f, self.push_count, state))

    def select_heuristic(self, heuristic: str):
        if heuristic == "lower_bound":
            return self.heuristic_lower_bound
        raise ValueError(f"Unknown heuristic {heuristic}")

    def heuristic_lower_bound(self, state: State) -> int:
        return self.problem.lower_bound(state) - state.makespan()

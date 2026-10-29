import heapq

from utils.problem import Problem, State


class AStar:
    def __init__(self, problem: Problem, heuristic: str):
        self.problem = problem
        self.visited = 0
        self.visited_states: set[tuple[tuple[int, ...], ...]] = set()
        self.push_count = 0
        self.best_makespan = float("inf")
        self.best_sequence: tuple[int, ...] = ()

        self.heuristic = self.select_heuristic(heuristic)
        self.frontier = []

    def search(self, state: State | None = None) -> None:
        if state is None:
            state = self.problem.initial_state()

        f = state.makespan() + self.heuristic(state)

        self.push_count += 1
        heapq.heappush(self.frontier, (f, self.push_count, state))

        while self.frontier:
            f, _, state = heapq.heappop(self.frontier)
            key = (state.next_operation, state.job_free, state.machine_free)
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
                f = new_state.makespan() + self.heuristic(new_state)

                self.push_count += 1
                heapq.heappush(self.frontier, (f, self.push_count, new_state))

    def select_heuristic(self, heuristic: str):
        if heuristic == "lower_bound":
            return self.heuristic_lower_bound
        raise ValueError(f"Unknown heuristic {heuristic}")

    def heuristic_lower_bound(self, state: State) -> int:
        return self.problem.lower_bound(state) - state.makespan()

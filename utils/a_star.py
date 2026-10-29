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
        if heuristic == "machine_heads_tails":
            return self.heuristic_machine_heads_tails
        raise ValueError(f"Unknown heuristic {heuristic}")

    def heuristic_lower_bound(self, state: State) -> int:
        """Remaining makespan estimate from `Problem.lower_bound`, relative to the makespan so far."""
        return self.problem.lower_bound(state) - state.makespan()

    def heuristic_machine_heads_tails(self, state: State) -> int:
        """One-machine relaxation: earliest head + remaining work + smallest tail, per machine."""
        problem = self.problem
        bound = problem.lower_bound(state)

        n_machines = problem.n_machines
        min_head = [sys.maxsize] * n_machines
        min_tail = [sys.maxsize] * n_machines
        work = [0] * n_machines

        for job in range(problem.n_jobs):
            first = state.next_operation[job]
            tail = sum(int(d) for d in problem.durations[job, first:])
            head = state.job_free[job]
            for operation in range(first, problem.n_operations_per_job):
                duration = int(problem.durations[job, operation])
                tail -= duration
                machine = int(problem.machines[job, operation])
                min_head[machine] = min(
                    min_head[machine], max(head, state.machine_free[machine])
                )
                min_tail[machine] = min(min_tail[machine], tail)
                work[machine] += duration
                head += duration

        for machine in range(n_machines):
            if work[machine]:
                bound = max(
                    bound, min_head[machine] + work[machine] + min_tail[machine]
                )

        return bound - state.makespan()

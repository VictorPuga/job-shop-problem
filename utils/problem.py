from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class State:
    """Partial schedule. `sequence` is the job of each dispatched operation, in order."""

    next_operation: tuple[int, ...]
    job_free: tuple[int, ...]
    machine_free: tuple[int, ...]
    sequence: tuple[int, ...]

    def makespan(self) -> int:
        return max(self.machine_free)

    def key(self) -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
        """Identifies the state by what the rest of the search depends on, ignoring `sequence`."""
        return (self.next_operation, self.job_free, self.machine_free)


class Problem:
    def __init__(self, machines: NDArray[np.int_], durations: NDArray[np.int_]) -> None:
        self.machines = machines
        self.durations = durations
        self.n_jobs: int = durations.shape[0]
        self.n_operations_per_job: int = durations.shape[1]
        self.n_machines = int(machines.max()) + 1

    def initial_state(self) -> State:
        return State((0,) * self.n_jobs, (0,) * self.n_jobs, (0,) * self.n_machines, ())

    def is_complete(self, state: State) -> bool:
        return len(state.sequence) == self.n_jobs * self.n_operations_per_job

    def available_jobs(self, state: State) -> list[int]:
        jobs = []
        for job in range(self.n_jobs):
            if state.next_operation[job] < self.n_operations_per_job:
                jobs.append(job)
        return jobs

    def dispatch(self, state: State, job: int) -> State:
        """Returns the state after scheduling the next operation of `job`."""
        operation = state.next_operation[job]
        if operation >= self.n_operations_per_job:
            raise ValueError(f"Job {job} has no operation left")

        machine = int(self.machines[job, operation])
        start = max(state.job_free[job], state.machine_free[machine])
        end = start + int(self.durations[job, operation])

        next_operation = list(state.next_operation)
        job_free = list(state.job_free)
        machine_free = list(state.machine_free)
        next_operation[job] += 1
        job_free[job] = end
        machine_free[machine] = end

        return State(
            tuple(next_operation),
            tuple(job_free),
            tuple(machine_free),
            state.sequence + (job,),
        )

    def lower_bound(self, state: State) -> int:
        """Lowest makespan any completion of `state` could reach."""
        bound = state.makespan()
        machine_end = list(state.machine_free)

        for job in range(self.n_jobs):
            job_end = state.job_free[job]
            for operation in range(state.next_operation[job], self.n_operations_per_job):
                duration = int(self.durations[job, operation])
                job_end += duration
                machine_end[int(self.machines[job, operation])] += duration
            bound = max(bound, job_end)

        return max(bound, max(machine_end))

    def start_times(self, sequence: tuple[int, ...]) -> NDArray[np.int_]:
        """Returns start[job, operation] for the schedule built by dispatching `sequence`."""
        start = np.zeros((self.n_jobs, self.n_operations_per_job), dtype=int)
        state = self.initial_state()

        for job in sequence:
            operation = state.next_operation[job]
            state = self.dispatch(state, job)
            start[job, operation] = state.job_free[job] - int(
                self.durations[job, operation]
            )

        return start

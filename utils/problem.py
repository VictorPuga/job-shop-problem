from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class State:
    """Partial schedule built by dispatching one operation at a time.

    `sequence` lists the job of every dispatched operation, in dispatch order.
    The k-th occurrence of a job in it is that job's k-th operation.
    `next_operation[job]` is the index of the next operation of `job` to dispatch.
    `job_free[job]` is when the last dispatched operation of `job` ends.
    `machine_free[m]` is when the last dispatched operation on machine `m` ends.
    `makespan` is the latest end time among the dispatched operations.
    """

    next_operation: tuple[int, ...]
    job_free: tuple[int, ...]
    machine_free: tuple[int, ...]
    sequence: tuple[int, ...]
    makespan: int


def _replaced(values: tuple[int, ...], index: int, value: int) -> tuple[int, ...]:
    return values[:index] + (value,) + values[index + 1 :]


class Problem:
    """Job shop instance, searched through its operation-sequence state space.

    A state is a `State`, and an action dispatches the next operation of one job.
    The operation starts as soon as both its job and its machine are free.
    Every state is feasible, so there are no precedence or cycle checks.
    The schedules reached are semi-active, and an optimal one is always among them.
    """

    def __init__(self, machines: NDArray[np.int_], durations: NDArray[np.int_]) -> None:
        self.machines = machines
        self.durations = durations
        self.n_jobs = len(durations)
        self.n_operations_per_job = len(durations[0])
        self.n_machines = int(machines.max()) + 1
        self.n_operations = self.n_jobs * self.n_operations_per_job

        self._machines: list[list[int]] = machines.tolist()
        self._durations: list[list[int]] = durations.tolist()

        # _remaining_job_time[job][k] = total duration of operations k.. of job
        self._remaining_job_time = [
            [sum(row[k:]) for k in range(self.n_operations_per_job + 1)]
            for row in self._durations
        ]

    def initial_state(self) -> State:
        """Returns the empty schedule."""
        return State(
            next_operation=(0,) * self.n_jobs,
            job_free=(0,) * self.n_jobs,
            machine_free=(0,) * self.n_machines,
            sequence=(),
            makespan=0,
        )

    def is_complete(self, state: State) -> bool:
        """Returns whether every operation has been dispatched."""
        return len(state.sequence) == self.n_operations

    def available_jobs(self, state: State) -> list[int]:
        """Returns the jobs that still have an operation to dispatch."""
        return [
            job
            for job in range(self.n_jobs)
            if state.next_operation[job] < self.n_operations_per_job
        ]

    def dispatch(self, state: State, job: int) -> State:
        """Returns the state after dispatching the next operation of `job`.

        Raises `ValueError` if `job` has no operation left.
        """
        operation = state.next_operation[job]
        if operation >= self.n_operations_per_job:
            raise ValueError(f"Job {job} has no operation left to dispatch")

        machine = self._machines[job][operation]
        start = max(state.job_free[job], state.machine_free[machine])
        end = start + self._durations[job][operation]

        return State(
            next_operation=_replaced(state.next_operation, job, operation + 1),
            job_free=_replaced(state.job_free, job, end),
            machine_free=_replaced(state.machine_free, machine, end),
            sequence=state.sequence + (job,),
            makespan=max(state.makespan, end),
        )

    def lower_bound(self, state: State) -> int:
        """Returns a lower bound on the makespan of any completion of `state`.

        It is the largest of the current makespan, the end of each job if its
        remaining operations ran back to back, and the end of each machine if
        its remaining operations ran back to back.
        For a complete state it equals the makespan.
        """
        bound = state.makespan
        machine_end = list(state.machine_free)

        for job in range(self.n_jobs):
            operation = state.next_operation[job]
            bound = max(
                bound, state.job_free[job] + self._remaining_job_time[job][operation]
            )
            for k in range(operation, self.n_operations_per_job):
                machine_end[self._machines[job][k]] += self._durations[job][k]

        return max(bound, *machine_end)

    def start_times(self, sequence: tuple[int, ...]) -> NDArray[np.int_]:
        """Returns `start[job, operation]` for the schedule built by dispatching `sequence`."""
        start = np.zeros((self.n_jobs, self.n_operations_per_job), dtype=int)
        state = self.initial_state()

        for job in sequence:
            operation = state.next_operation[job]
            state = self.dispatch(state, job)
            start[job, operation] = state.job_free[job] - self._durations[job][operation]

        return start

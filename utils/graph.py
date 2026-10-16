import itertools
from collections import deque

import numpy as np
from numpy.typing import NDArray


class Node:
    """One operation of a job, or the source/sink (job, operation and machine are -1)."""

    def __init__(
        self, id: int, job: int, operation: int, machine: int, duration: int
    ) -> None:
        self.id = id
        self.job = job
        self.operation = operation
        self.machine = machine
        self.duration = duration

    def __repr__(self) -> str:
        return f"Node(id={self.id}, job={self.job}, op={self.operation}, machine={self.machine}, duration={self.duration})"


class Graph:
    """Disjunctive graph of a job shop instance.

    Node ids: `0` is the source, `1..n_jobs * n_operations_per_job` are the
    operations in job-major order, and the last id is the sink.

    `successors` holds the directed edges: the job chains (source -> first
    operation -> ... -> last operation -> sink) plus any disjunctive edge added
    with `add_edge`.
    `machine_nodes[m]` lists the ids of the operations that run on machine `m`.
    `disjunctive_pairs` lists every unordered pair of operations sharing a
    machine; none of them are in `successors` until they are oriented.
    """

    def __init__(self, machines: NDArray[np.int_], durations: NDArray[np.int_]) -> None:
        self.n_jobs = len(durations)
        self.n_operations_per_job = len(durations[0])
        self.n_machines = int(machines.max()) + 1

        self.source = 0
        self.sink = self.n_jobs * self.n_operations_per_job + 1

        self.nodes: dict[int, Node] = {}

        self.successors: dict[int, list[int]] = {id: [] for id in range(self.sink + 1)}

        self.disjunctive_pairs: list[tuple[int, int]] = []

        self.machine_nodes: list[list[int]] = [[] for _ in range(self.n_machines)]

        self.nodes[self.source] = Node(self.source, -1, -1, -1, 0)
        self.nodes[self.sink] = Node(self.sink, -1, -1, -1, 0)

        for job in range(self.n_jobs):
            for operation in range(self.n_operations_per_job):
                node_id = self.calculate_node_id(job, operation)

                machine = int(machines[job, operation])
                duration = int(durations[job, operation])

                self.nodes[node_id] = Node(node_id, job, operation, machine, duration)
                self.machine_nodes[machine].append(node_id)

        for job in range(self.n_jobs):
            self.successors[self.source].append(self.calculate_node_id(job, 0))

            for operation in range(self.n_operations_per_job - 1):
                edge_source = self.calculate_node_id(job, operation)

                self.successors[edge_source].append(
                    self.calculate_node_id(job, operation + 1)
                )

            self.successors[
                self.calculate_node_id(job, self.n_operations_per_job - 1)
            ].append(self.sink)

        for machine in range(self.n_machines):
            node_ids = self.machine_nodes[machine]
            pairs = itertools.combinations(node_ids, 2)
            self.disjunctive_pairs.extend(pairs)

    def calculate_node_id(self, job: int, operation: int) -> int:
        """Returns the node id of the given job operation."""
        return job * self.n_operations_per_job + operation + 1

    def add_edge(self, from_id: int, to_id: int) -> None:
        """Adds a directed edge, e.g. to orient a disjunctive pair."""
        self.successors[from_id].append(to_id)

    def remove_edge(self, from_id: int, to_id: int) -> None:
        """Removes a directed edge. Raises `ValueError` if it does not exist."""
        self.successors[from_id].remove(to_id)

    def longest_path(self) -> int | None:
        """Returns the length of the longest path from source to sink, or None if there is a cycle."""

        in_degree = dict.fromkeys(range(self.sink + 1), 0)

        for node in self.successors:
            for successor in self.successors[node]:
                in_degree[successor] += 1

        queue = deque(node for node in in_degree if in_degree[node] == 0)
        finish = dict.fromkeys(range(self.sink + 1), 0)

        while queue:
            current = queue.popleft()
            for successor in self.successors[current]:
                in_degree[successor] -= 1

                finish[successor] = max(
                    finish[successor], finish[current] + self.nodes[current].duration
                )

                if in_degree[successor] == 0:
                    queue.append(successor)

        if any(in_degree.values()):
            return None

        return finish[self.sink]

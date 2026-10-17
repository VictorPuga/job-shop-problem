import numpy as np

# machines[job, operation] = machine assigned to job operation
machines = np.array([
    [0, 1, 2],
    [1, 0, 2],
    [0, 2, 1],
    [2, 0, 1],
])

# durations[job, operation] = duration of job operation
durations = np.array([
    [1,  3,  2],
    [8,  5, 10],
    [5,  4,  8],
    [4, 10,  6],
])

# example_solution[job, operation] = start time of job operation
example_solution = np.array([
    [5,  8, 23],
    [0,  8, 13],
    [0,  5, 11],
    [0, 13, 23],
])

import itertools

N_JOBS, N_OPS = machines.shape
N_MAC = machines.max() + 1
EMPTY = (0, 0)

class Node:
    def __init__(self, current, time_left, next_op, time):
        self.current = current        
        self.time_left = time_left    
        self.next_op = next_op        
        self.time = time              

    def is_final(self):
        for job in range(N_JOBS):
            if self.next_op[job] == N_OPS:
                continue
            if (job + 1, N_OPS) in self.current:
                continue
            return False
        return True

    def makespan(self):
        return self.time + max(self.time_left)

    def new_children(self):
        busy = []
        for r in self.time_left:
            if r > 0:
                busy.append(r)

        if busy:
            step = min(busy)
        else:
            step = 0
        time = self.time + step

        left = []
        for r in self.time_left:
            left.append(max(r - step, 0))

        current = []
        next_op = list(self.next_op)
        for m in range(N_MAC):
            if left[m] > 0:
                current.append(self.current[m])
            else:
                job, op = self.current[m]
                if job != 0:
                    next_op[job - 1] = op
                current.append(EMPTY)

        busy_jobs = set()
        for job, op in current:
            if job != 0:
                busy_jobs.add(job)

        options = []
        for m in range(N_MAC):
            if left[m] > 0:
                options.append([current[m]])
            else:
                choices = [EMPTY]
                for j in range(N_JOBS):
                    op = next_op[j]
                    if op < N_OPS and (j + 1) not in busy_jobs and machines[j, op] == m:
                        choices.append((j + 1, op + 1))
                options.append(choices)

        children = []
        for combination in itertools.product(*options): # cartesian product of all machine options
            new_ops = []
            for m in range(N_MAC):
                if left[m] == 0 and combination[m] != EMPTY:
                    new_ops.append(m)

            if not new_ops and not any(left):
                continue

            child_left = list(left)
            for m in new_ops:
                job, op = combination[m]
                child_left[m] = int(durations[job - 1, op - 1])

            children.append(Node(list(combination), child_left, list(next_op), time))
        return children


class DFS:
    def __init__(self):
        self.root = Node([EMPTY] * N_MAC, [0] * N_MAC, [0] * N_JOBS, 0)
        self.best = None
        self.expanded = 0
        self.solutions = 0

    def solve(self):
        stack = [self.root]
        while stack:
            node = stack.pop()
            self.expanded += 1

            if node.is_final():
                self.solutions += 1
                if self.best is None or node.makespan() < self.best.makespan():
                    self.best = node
                    print(f"New best solution: Cmax = {node.makespan()}  (nodes: {self.expanded})")
                continue

            if self.best is not None and node.makespan() >= self.best.makespan():
                continue

            stack.extend(node.new_children())
        return self.best


if __name__ == "__main__":
    dfs = DFS()
    best = dfs.solve()

    print(f"\nExpanded nodes: {dfs.expanded}")
    print(f"Complete solutions found: {dfs.solutions}")
    print(f"Optimal Cmax: {best.makespan()}")
    
# job-shop-problem

## Setup

The project requires Python 3.12.
Create and activate the virtual environment, then install the dependencies:

```sh
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the solver

Run the search on the instance selected by `INSTANCE` at the top of `main.py`:

```sh
python main.py
```

Set `ALGORITHM` to `"dfs"` (default) or `"a_star"` to pick the search.
With `"a_star"`, `HEURISTIC` selects the heuristic by name.
An unknown name raises an error.

The available instances are the keys of `INSTANCES` in `utils/instances.py`:

- `example`: the small 4x3 instance (default).
- `ft06_4x4`: `ft06` cropped to its first 4 jobs and machines 0-3, optimal makespan 33 (computed with the DFS, not an official benchmark).
- `ft06`: Fisher & Thompson, 6x6, optimal makespan 55.
- `la01`: Lawrence, 10x5, optimal makespan 666.
- `ft10`: Fisher & Thompson, 10x10, optimal makespan 930.
- `la36`: Lawrence, 15x15, optimal makespan 1268.

The larger instances are far too big for an exhaustive DFS, so expect them to run for a very long time.

It prints the best makespan, the number of visited states, the search time, the dispatch sequence, the order of operations on each machine, and the start time of each operation.
For DFS, visited counts `search` calls.
For A\*, it counts expanded states, and duplicates skipped are not counted.

DFS Pruning is on by default.
To run without it, set `PRUNE_DFS = False` at the top of `main.py`.

### Logging

Each run writes a log to a new timestamped file, `logs/<algorithm>_<instance>_YYYYMMDD_HHMMSS.log` (for example `logs/dfs_ft06_20261028_171455.log`), and prints its path.
By default it records the start, every improved makespan, a progress line every 100,000 visits, and the final result.
Set `LOG_NODES = True` at the top of `main.py` to also log every visited node and every pruned branch.
That produces very large files, so use it only on small instances.

### Visualization

Set `VISUALIZE = True` at the top of `main.py` to show a Gantt chart of the best schedule once the search ends (requires `matplotlib`, installed from `requirements.txt`).
The chart has one row per machine and one color per job.
The program exits when you close the window.

## How it works

The search runs on an operation-sequence (dispatching) state space, implemented in `utils/problem.py`, `utils/dfs.py` and `utils/a_star.py`.

- **State:** a partial schedule (`State`).
It holds the next operation of each job (`next_operation`), when each job and each machine becomes free (`job_free`, `machine_free`), and the jobs dispatched so far (`sequence`).
The makespan is the latest time any machine becomes free.
- **Action:** dispatch the next operation of one job.
It starts as soon as both its job and its machine are free.
- **Goal:** every operation is dispatched.
The makespan of the state is the schedule's makespan.

Every state is feasible, so there are no cycle or precedence checks.
The schedules it reaches are semi-active, and an optimal schedule is always among them.
Each node has at most one child per job that still has operations left.

A schedule is described by its `sequence`, a list with each job repeated once per operation.
The k-th occurrence of a job is that job's k-th operation.
`Problem.start_times(sequence)` turns it into the start time of every operation.

### Pruning

With `prune=True`, a branch is cut when `Problem.lower_bound(state)` is not below the best makespan found.
The bound is the largest of:

- the current makespan,
- each job's free time plus its remaining durations,
- each machine's free time plus the durations still to run on it.

### A\*

`AStar(problem, heuristic)` in `utils/a_star.py` keeps a frontier ordered by `f = g + h`.

- **g:** the makespan of the state so far (`State.makespan()`).
- **h:** the heuristic selected by name, an estimate of the makespan still to be added.
It must never overestimate, so the first goal popped is optimal.
- **Heuristics:** selected by name, and an unknown name raises `ValueError`.
  - `lower_bound` is `Problem.lower_bound(state) - state.makespan()`, so its `f` equals `Problem.lower_bound`.
  - `machine_heads_tails` is a one-machine relaxation.
For each machine it takes the earliest possible start (head) of its remaining operations, plus their total duration, plus the smallest time left in their jobs after them (tail).
The head of an operation is its job's free time plus the earlier remaining operations of that job, and never before the machine is free.
The result is the maximum of that and `Problem.lower_bound`, so it is never below `lower_bound`.
To add a heuristic, write a method that takes a `State` and returns `h`, then register its name in `AStar.select_heuristic`.
- **Tie-breaking:** frontier entries are `(f, push_count, state)`.
The counter is unique per push, so `State` is never compared and ties pop the oldest entry first.
- **Duplicate detection:** a state is marked as seen when it is popped, keyed by `State.key()`, which is `(next_operation, job_free, machine_free)`.
`sequence` is left out because the future of the search does not depend on it.
A seen key is skipped both when pushing a child and when popping, which is safe because `f` is consistent: it never decreases along an edge, so the first pop of a state has its best `f`.
- **Result:** the search stops at the first goal popped and sets `best_makespan` and `best_sequence`, the same attributes `DFS` exposes.

### Adding another search algorithm

Branch and bound and beam search only need `Problem.initial_state()`, `available_jobs`, `dispatch`, `is_complete` and `lower_bound`.
To work with `main.py` and `plot_gantt`, a solver also needs `problem`, a `search()` method, and the `visited`, `best_makespan` and `best_sequence` attributes.

## Running the unit tests

Tests use the standard library `unittest`, so no extra test dependencies are needed.
Run them from the project root with the virtual environment active:

```sh
python -m unittest discover -s tests -t .
```

To run a single test module with verbose output:

```sh
python -m unittest tests.test_a_star -v
```

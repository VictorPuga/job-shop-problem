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

The available instances are the keys of `INSTANCES` in `utils/instances.py`:

- `example`: the small 4x3 instance (default).
- `ft06_4x4`: `ft06` cropped to its first 4 jobs and machines 0-3, optimal makespan 33 (computed with the DFS, not an official benchmark).
- `ft06`: Fisher & Thompson, 6x6, optimal makespan 55.
- `la01`: Lawrence, 10x5, optimal makespan 666.
- `ft10`: Fisher & Thompson, 10x10, optimal makespan 930.
- `la36`: Lawrence, 15x15, optimal makespan 1268.

The larger instances are far too big for an exhaustive DFS, so expect them to run for a very long time.

It prints the best makespan, the number of search calls, the search time, the dispatch sequence, the order of operations on each machine, and the start time of each operation.

DFS Pruning is on by default.
To run without it, set `PRUNE_DFS = False` at the top of `main.py`.

### Live visualization

Set `VISUALIZE = True` at the top of `main.py` to show a live Gantt chart (requires `matplotlib`, installed from `requirements.txt`).
The chart redraws every time the search finds a better schedule, with one row per machine and one color per job.
The search time then includes the pauses between redraws, so turn the visualization off when comparing timings.
The window stays open after the search ends, and the program exits when you close it.

## How it works

The search runs on an operation-sequence (dispatching) state space, implemented in `utils/problem.py` and `utils/dfs.py`.

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

### Adding another search algorithm

A\*, branch and bound, and beam search only need `Problem.initial_state()`, `available_jobs`, `dispatch`, `is_complete` and `lower_bound`.
`lower_bound` never overestimates the final makespan, so it can serve as the `f` value of A\*, and `State` is hashable for duplicate detection.

## Running the unit tests

Tests use the standard library `unittest`, so no extra test dependencies are needed.
Run them from the project root with the virtual environment active:

```sh
python -m unittest discover -s tests -t .
```

To run a single test module with verbose output:

```sh
python -m unittest tests.test_problem -v
```

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

Run the search with command-line options (`python main.py --help` lists them):

```sh
python main.py -a a_star -i ft06 --heuristic lower_bound
```

- `-a`, `--algorithm`: `dfs` (default), `a_star` or `local_search`.
- `-i`, `--instance`: the instance name (default `example`).
- `--heuristic`: `lower_bound` or `machine_heads_tails` (default), used by `a_star`.
- `--no-prune`: disable DFS pruning.
- `--seed`: seed for `local_search` (default 42).
- `--neighborhood`: `swap` (default) or `insert`, used by `local_search`.
- `--restarts`: number of random restarts for `local_search` (default 10).
- `--visualize`: show a Gantt chart.
- `--log-nodes`: log every node and neighbor.

An unknown algorithm, instance or heuristic is rejected by the argument parser.

To regenerate the report benchmarks, run `bash scripts/benchmark.sh`.
It kills each run after `TIMEOUT` seconds (default 60, the assignment budget, `TIMEOUT=0` for no limit).
The solvers have no internal time limit, so a killed DFS or A\* run leaves a log without a `done` event.
Some slow cases (DFS on `ft06`, A\* on `la01`, `ft10` and `la36`) are commented out in the script's `CASES` list, uncomment them to run them.
The logs of the report are in `results/final_benchmarks/`.

To run every algorithm on the generated instances in `instances/`, run `bash scripts/benchmark_instances.sh [instance ...]`.
With no arguments it uses every `instances/*.json` file, otherwise only the named instances (for example `gen_easy_01 gen_hard_02`).
For each instance it runs DFS, A\* with both heuristics, and local search with `swap` and `insert` over seeds 1-10.
It uses the same `TIMEOUT` variable as `benchmark.sh`.

The available instances are the keys of `INSTANCES` in `utils/instances.py`:

- `example`: the small 4x3 instance (default).
- `ft06_4x4`: `ft06` cropped to its first 4 jobs and machines 0-3, optimal makespan 33 (computed with the DFS, not an official benchmark).
- `ft06`: Fisher & Thompson, 6x6, optimal makespan 55.
- `la01`: Lawrence, 10x5, optimal makespan 666.
- `ft10`: Fisher & Thompson, 10x10, optimal makespan 930.
- `la36`: Lawrence, 15x15, optimal makespan 1268.

Every `instances/<name>.json` file is also available as an instance named `<name>`.

### Local search

The representation is an operation-based dispatch sequence: a permutation with repetition where job `j` appears once per operation.
Any such sequence is a valid schedule, decoded by dispatching the jobs in order, so every neighbor is feasible.
Each restart starts from a random sequence and runs first-improvement hill climbing, sampling up to 25 neighbors per iteration.
The two neighborhoods are:

- `swap`: exchange two positions of the sequence.
- `insert`: remove one position and reinsert it at another, shifting the ones in between.

`swap` can pick two equal job ids, which gives a neighbor identical to the current sequence.
A restart stops after `max_iterations` (500) iterations, or when none of the 25 sampled neighbors improves.
The search is bounded by restarts × iterations, not by the 60 s budget.
The ablations compare `swap` vs `insert`, and `--restarts 10` vs `--restarts 1`.
The 1-restart runs use the same `swap` tag as the 10-restart ones, so tell them apart by the `restarts` field of the `start` event or by `argv`.

### Instance format and generator

Instances are JSON files in `instances/`, with the same layout as `utils/instances.py`:

```json
{
  "machines": [[2, 3, 1, 0], [0, 1, 2, 3]],
  "durations": [[4, 10, 10, 9], [10, 8, 4, 1]]
}
```

`machines[job][operation]` is the machine (0-based) and `durations[job][operation]` its processing time.
Each job visits every machine once, in a fixed order.

The seeded generator creates 20 instances, with instance `i` (in `GENERATED_SPECS` order) using seed `base_seed + i`:

| Family | Count | Size (jobs × machines) | Durations |
|---|---|---|---|
| `gen_easy_01`–`10` | 10 | 3×3 or 4×4 | 1–10 |
| `gen_medium_01`–`08` | 8 | 5×5, 6×6 or 7×7 | 1–50 |
| `gen_hard_01`–`02` | 2 | 10×10, 15×10 | 1–99 |

Regenerate them with `python scripts/generate_instances.py` (`--seed` sets the base seed, default 2026).
Generated instances have no known optimal makespan.

The larger instances are far too big for an exhaustive DFS, so expect them to run for a very long time.

It prints the best makespan, the number of visited states, the search time, the dispatch sequence, the order of operations on each machine, and the start time of each operation.
For DFS, visited counts `search` calls.
For A\*, it counts expanded states, and duplicates skipped are not counted.

DFS Pruning is on by default.
To run without it, pass `--no-prune`.

### Logging

Each run writes a JSON Lines log to its own new file, `logs/<algorithm>_<instance>_<tag>_YYYYMMDD_HHMMSS_mmm.jsonl` (for example `logs/dfs_ft06_noprune_20261028_171455_123.jsonl`), and prints its path.
The tag is `prune` or `noprune` for DFS, the heuristic name for A\*, and `<neighborhood>_seed<N>` for local search (for example `swap_seed3`).
The timestamp has millisecond precision, and the file is created exclusively, so a run never appends to an existing log.
Each line is one JSON object with `ts`, `level`, `event`, and the event's own fields (for example `{"ts": "...", "level": "INFO", "event": "new_best", "makespan": 59, "visited": 120, "sequence": [0, 1]}`).
By default it records the `start` event, the final `done` result, and per algorithm:

- DFS: every `new_best` makespan and a `progress` event every 100,000 visits.
- A\*: a `progress` event every 10 expansions (with `f`, `depth`, `frontier` size and `pushed` count) and the `solution` event.
- Local search: every `new_best` makespan (with `restart` and `iteration`) and a `restart_done` event at the end of each restart.

The `start` event describes the run, so a log can be identified from its contents:

- `algorithm`, `instance`, `n_jobs`, `n_machines`.
- `prune` (DFS), `heuristic` (A\*), `seed`, `neighborhood`, `max_iterations` and `restarts` (local search).
- `log_nodes`, `python`, `platform`, `machine`, `git_commit` (`null` outside a git checkout) and the full `argv`.

The `done` event has:

- `algorithm`, `instance` and the same `prune`, `heuristic` or `seed` and `neighborhood` option.
- `best`, `visited` and `elapsed`.
- `time_to_best`: seconds from the start of the search to the last `new_best` or `solution` (absent if none was found).
- `max_frontier`: the largest frontier size reached (A\* only).
- `optimal`: the known optimal makespan from `OPTIMAL_MAKESPANS` in `utils/instances.py`, and `reached_optimal`: whether `best` equals it.

Pass `--log-nodes` to also log every DFS visited node and pruned branch, every duplicate A\* skips, and every local search restart start and evaluated neighbor.
  That produces very large files, so use it only on small instances.

### Visualization

Pass `--visualize` to show a Gantt chart of the best schedule once the search ends (requires `matplotlib`, installed from `requirements.txt`).
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

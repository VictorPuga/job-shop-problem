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

Run the search on the instance defined in `utils/instances.py`:

```sh
python main.py
```

It prints the best makespan, the number of search calls, the search time, the order of operations on each machine, and the start time of each operation.

DFS Pruning is on by default.
To run without it, set `PRUNE_DFS = False` at the top of `main.py`.

### Live visualization

Set `VISUALIZE = True` at the top of `main.py` to show a live Gantt chart (requires `matplotlib`, installed from `requirements.txt`).
The chart redraws every time the search finds a better schedule, with one row per machine and one color per job.
The search time then includes the pauses between redraws, so turn the visualization off when comparing timings.
The window stays open after the search ends, and the program exits when you close it.

### Graph image

Set `DRAW_GRAPH = True` at the top of `main.py` to save a picture of the graph after the search.
It is saved to `GRAPH_IMAGE_PATH` (`tmp/graph.png` by default).
The image has two panels:

- Left: the disjunctive graph. Gray arrows are the job chains, dashed lines are machine conflicts, colored by machine.
- Right: the same graph with the best orientation applied, where each conflict becomes an arrow.

Each node is labeled with its job, operation, and duration, and is colored by machine.
`S` is the source and `T` is the sink.

## Running the unit tests

Tests use the standard library `unittest`, so no extra test dependencies are needed.
Run them from the project root with the virtual environment active:

```sh
python -m unittest discover -s tests -t .
```

To run a single test module with verbose output:

```sh
python -m unittest tests.test_graph -v
```

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

It prints the best makespan, the number of search calls, the search time, and the order of operations on each machine.

DFS Pruning is on by default.
To run without it, set `PRUNE_DFS = False` at the top of `main.py`.

## Running the unit tests

Tests use the standard library `unittest`, so no extra dependencies are needed.
Run them from the project root with the virtual environment active:

```sh
python -m unittest discover -s tests -t .
```

To run a single test module with verbose output:

```sh
python -m unittest tests.test_graph -v
```

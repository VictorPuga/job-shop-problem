# job-shop-problem

## Setup

The project requires Python 3.12.
Create and activate the virtual environment, then install the dependencies:

```sh
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

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

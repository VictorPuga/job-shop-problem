#!/usr/bin/env bash
# Regenerates the logs behind the tables of the report.
# Runs are sequential and uncapped. Comment out the cases you don't need.
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f venv/bin/activate ]]; then
  source venv/bin/activate
fi

# Local search cases run once per seed.
SEEDS=(1 2 3 4 5 6 7 8 9 10)

# Each entry is the arguments passed to main.py.
CASES=(
  # DFS, pruning off
  "-a dfs -i example --no-prune"
  "-a dfs -i ft06_4x4 --no-prune"

  # DFS, pruning on
  "-a dfs -i example"
  "-a dfs -i ft06_4x4"
  # "-a dfs -i ft06"  # takes too long

  # A*, H1 (lower_bound)
  "-a a_star -i example --heuristic lower_bound"
  "-a a_star -i ft06_4x4 --heuristic lower_bound"
  "-a a_star -i ft06 --heuristic lower_bound"
  # "-a a_star -i la01 --heuristic lower_bound"
  # "-a a_star -i ft10 --heuristic lower_bound"
  # "-a a_star -i la36 --heuristic lower_bound"

  # A*, H2 (machine_heads_tails)
  "-a a_star -i example --heuristic machine_heads_tails"
  "-a a_star -i ft06_4x4 --heuristic machine_heads_tails"
  "-a a_star -i ft06 --heuristic machine_heads_tails"
  # "-a a_star -i la01 --heuristic machine_heads_tails"
  # "-a a_star -i ft10 --heuristic machine_heads_tails"
  # "-a a_star -i la36 --heuristic machine_heads_tails"

  # Local search, one run per seed in SEEDS
  "-a local_search -i example"
  "-a local_search -i ft06_4x4"
  "-a local_search -i ft06"
  "-a local_search -i la01"
  "-a local_search -i ft10"
  "-a local_search -i la36"
)

for args in "${CASES[@]}"; do
  if [[ "$args" == "-a local_search"* ]]; then
    for seed in "${SEEDS[@]}"; do
      echo ">>> python main.py $args --seed $seed"
      python main.py $args --seed "$seed"
    done
  else
    echo ">>> python main.py $args"
    python main.py $args
  fi
done

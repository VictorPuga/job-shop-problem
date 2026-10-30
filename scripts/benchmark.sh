#!/usr/bin/env bash
# Regenerates the logs behind the tables of the report.
# Runs are sequential. Comment out the cases you don't need.
# Each run is killed after TIMEOUT seconds (default 60, the assignment budget, 0 for no limit).
# A killed run leaves a log without a done event.
# For the uncapped runs, use a 1 hour limit: TIMEOUT=3600 scripts/benchmark.sh
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f venv/bin/activate ]]; then
  source venv/bin/activate
fi

# TIMEOUT="${TIMEOUT:-3600}"
TIMEOUT="${TIMEOUT:-60}"

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

  # Local search, one run per seed in SEEDS.
  # Neighborhood ablation: swap vs insert. Restarts ablation: 10 restarts vs 1.
  "-a local_search -i example --neighborhood swap"
  "-a local_search -i example --neighborhood insert"
  "-a local_search -i ft06 --neighborhood swap"
  "-a local_search -i ft06 --neighborhood insert"
  "-a local_search -i ft06 --neighborhood swap --restarts 1"
  "-a local_search -i la01 --neighborhood swap"
  "-a local_search -i la01 --neighborhood insert"
  "-a local_search -i la01 --neighborhood swap --restarts 1"
  "-a local_search -i ft10 --neighborhood swap"
  "-a local_search -i ft10 --neighborhood insert"
  "-a local_search -i ft10 --neighborhood swap --restarts 1"
  "-a local_search -i la36 --neighborhood swap"
  "-a local_search -i la36 --neighborhood insert"
  "-a local_search -i la36 --neighborhood swap --restarts 1"
)

run() {
  echo ">>> python main.py $*"
  local status=0
  perl -e 'alarm shift; exec @ARGV' "$TIMEOUT" python main.py "$@" || status=$?
  if [[ $status -eq 142 ]]; then
    echo "!!! timed out after ${TIMEOUT}s: python main.py $*"
  elif [[ $status -ne 0 ]]; then
    echo "!!! failed with status $status: python main.py $*"
  fi
}

for args in "${CASES[@]}"; do
  if [[ "$args" == "-a local_search"* ]]; then
    for seed in "${SEEDS[@]}"; do
      run $args --seed "$seed"
    done
  else
    run $args
  fi
done

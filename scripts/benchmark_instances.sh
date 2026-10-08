#!/usr/bin/env bash
# Runs every algorithm on the generated instances in instances/.
# Usage: scripts/benchmark_instances.sh [instance ...]
# With no arguments it uses every instances/*.json file, e.g. scripts/benchmark_instances.sh gen_easy_01 gen_hard_02
# Runs are sequential. Each run is killed after TIMEOUT seconds (default 60, 0 for no limit).
# A killed run leaves a log without a done event.
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f venv/bin/activate ]]; then
  source venv/bin/activate
fi

TIMEOUT="${TIMEOUT:-60}"

SEEDS=(1 2 3 4 5 6 7 8 9 10)
HEURISTICS=(lower_bound machine_heads_tails)
NEIGHBORHOODS=(swap insert)

if [[ $# -gt 0 ]]; then
  INSTANCES=("$@")
else
  INSTANCES=()
  for path in instances/*.json; do
    name="$(basename "$path" .json)"
    INSTANCES+=("$name")
  done
fi

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

for instance in "${INSTANCES[@]}"; do
  run -a dfs -i "$instance"

  for heuristic in "${HEURISTICS[@]}"; do
    run -a a_star -i "$instance" --heuristic "$heuristic"
  done

  for neighborhood in "${NEIGHBORHOODS[@]}"; do
    for seed in "${SEEDS[@]}"; do
      run -a local_search -i "$instance" --neighborhood "$neighborhood" --seed "$seed"
    done
  done
done

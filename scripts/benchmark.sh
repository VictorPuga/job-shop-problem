#!/usr/bin/env bash
# Regenerates the logs behind the tables of the report.
# Runs are sequential and uncapped. Comment out the cases you don't need.
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f venv/bin/activate ]]; then
  source venv/bin/activate
fi

# Each entry is the arguments passed to main.py.
CASES=(
  # DFS, pruning off
  "-a dfs -i example --no-prune"
  "-a dfs -i ft06_4x4 --no-prune"

  # DFS, pruning on
  "-a dfs -i example"
  "-a dfs -i ft06_4x4"
  # "-a dfs -i ft06"  # about 44 minutes, does not finish

  # A*, H1 (lower_bound)
  "-a a_star -i example --heuristic lower_bound"
  "-a a_star -i ft06_4x4 --heuristic lower_bound"
  "-a a_star -i ft06 --heuristic lower_bound"

  # A*, H2 (machine_heads_tails)
  "-a a_star -i example --heuristic machine_heads_tails"
  "-a a_star -i ft06_4x4 --heuristic machine_heads_tails"
  "-a a_star -i ft06 --heuristic machine_heads_tails"
)

for args in "${CASES[@]}"; do
  echo ">>> python main.py $args"
  python main.py $args
done

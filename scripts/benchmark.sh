#!/usr/bin/env bash
# Regenerates the logs behind the DFS and A* tables of the report.
# Runs are sequential and uncapped. Set INCLUDE_SLOW=1 to add pruned DFS on ft06 (about 44 minutes).
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ -f venv/bin/activate ]]; then
  source venv/bin/activate
fi

run() {
  echo ">>> python main.py $*"
  python main.py "$@"
}

for instance in example ft06_4x4; do
  run -a dfs -i "$instance" --no-prune
  run -a dfs -i "$instance"
done

for instance in example ft06_4x4 ft06; do
  for heuristic in lower_bound machine_heads_tails; do
    run -a a_star -i "$instance" --heuristic "$heuristic"
  done
done

if [[ "${INCLUDE_SLOW:-0}" == "1" ]]; then
  run -a dfs -i ft06
fi

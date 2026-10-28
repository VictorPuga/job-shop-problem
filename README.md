# job-shop-problem

## Logging

Each run writes a log to a new timestamped file, `logs/<algorithm>_<instance>_YYYYMMDD_HHMMSS.log` (for example `logs/dfs_ft06_20261028_171455.log`), and prints its path.
By default it records the start, every improved makespan, a progress line every 100,000 expanded nodes, and the final result.
Set `LOG_NODES = True` at the top of `main.py` to also log every expanded node and every pruned branch.
That produces very large files, so use it only on small instances.

To follow a run live in another terminal:

```sh
tail -f "$(ls -t logs/*.log | head -1)"
```

"""Builds the report tables and figures from the benchmark logs.

Usage: python scripts/analyze_results.py [--logs LOGS_DIR]
Without --logs it analyzes results/final_benchmarks and results/generated_instances_benchmarks.
The generated instances have no known optimum, so their gaps are measured against the best makespan found in any run.
When a configuration was run more than once on the same instance, only the latest log is used.
Writes the CSVs to results/metrics/, the LaTeX tables to results/tables/ and the figures to results/figures/.
Outputs for the generated instances get a _generated suffix.
"""
import argparse
import csv
import json
import re
import statistics
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent.parent
DEFAULT_LOGS = [
    (ROOT / "results" / "final_benchmarks", ""),
    (ROOT / "results" / "generated_instances_benchmarks", "_generated"),
]
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "results" / "figures"
METRICS = ROOT / "results" / "metrics"

ORDER = ["example", "ft06_4x4", "ft06", "la01", "ft10", "la36"]
OPTIMAL = {"example": 29, "ft06_4x4": 33, "ft06": 55, "la01": 666, "ft10": 930, "la36": 1268}
KNOWN_ORDER = list(ORDER)
KNOWN_OPTIMAL = dict(OPTIMAL)
TAG = ""


def seconds(start, end):
    return (datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds()


def load_run(path):
    events = [json.loads(line) for line in path.read_text().splitlines()]
    start = events[0]
    done = next((e for e in events if e["event"] == "done"), None)
    run = {
        "file": path.name,
        "algorithm": start["algorithm"],
        "instance": start["instance"],
        "timed_out": done is None,
        "argv": " ".join(start["argv"]),
        "python": start["python"],
        "platform": start["platform"],
        "commit": start["git_commit"],
    }
    if start["algorithm"] == "dfs":
        run["config"] = "prune" if start["prune"] else "noprune"
    elif start["algorithm"] == "a_star":
        run["config"] = start["heuristic"]
    else:
        run["config"] = f"{start['neighborhood']}_r{start['restarts']}"
        run["seed"] = start["seed"]

    if done:
        run.update(
            best=done["best"],
            visited=done["visited"],
            elapsed=done["elapsed"],
            time_to_best=done.get("time_to_best"),
            max_frontier=done.get("max_frontier"),
            reached_optimal=done["reached_optimal"],
            lower_bound=None,
        )
        return run

    # killed at the timeout: use the last events
    last = events[-1]
    best_events = [e for e in events if e["event"] in ("new_best", "solution")]
    bests = [e["makespan"] for e in best_events]
    progress = [e for e in events if e["event"] == "progress"]
    run.update(
        best=min(bests) if bests else None,
        visited=progress[-1]["visited"] if progress else last.get("visited"),
        elapsed=round(seconds(start["ts"], last["ts"]), 1),
        time_to_best=round(seconds(start["ts"], best_events[-1]["ts"]), 3) if best_events else None,
        max_frontier=max((e["frontier"] for e in progress if "frontier" in e), default=None),
        reached_optimal=False,
        lower_bound=progress[-1].get("f") if start["algorithm"] == "a_star" else None,
    )
    return run


def load_runs(logs):
    latest = {}
    for path in sorted(logs.glob("*.jsonl"), key=lambda p: re.search(r"\d{8}_\d{6}_\d{3}", p.stem).group()):
        run = load_run(path)
        latest[(run["algorithm"], run["instance"], run["config"], run.get("seed"))] = run
    return list(latest.values())


def difficulty_rank(instance):
    levels = ["easy", "medium", "hard"]
    return next((n for n, level in enumerate(levels) if f"_{level}_" in instance), len(levels))


def configure(runs):
    instances = {r["instance"] for r in runs}
    ORDER[:] = sorted(instances, key=lambda i: (KNOWN_ORDER.index(i) if i in KNOWN_ORDER else len(KNOWN_ORDER), difficulty_rank(i), i))
    OPTIMAL.clear()
    for instance in instances:
        bests = [r["best"] for r in runs if r["instance"] == instance and r["best"] is not None]
        OPTIMAL[instance] = KNOWN_OPTIMAL.get(instance, min(bests))


def gap(best, instance):
    if best is None:
        return None
    return 100 * (best - OPTIMAL[instance]) / OPTIMAL[instance]


def fmt_int(value):
    return "--" if value is None else f"{value:,}".replace(",", "\\,")


def fmt(value, digits=1):
    return "--" if value is None else f"{value:.{digits}f}"


def tex_name(name):
    return "\\texttt{" + name.replace("_", "\\_") + "}"


def write_table(name, header, rows, spec):
    TABLES.mkdir(parents=True, exist_ok=True)
    name = name + TAG
    lines = [f"\\begin{{tabular}}{{{spec}}}", "\\toprule", " & ".join(header) + " \\\\", "\\midrule"]
    lines += [" & ".join(row) + " \\\\" for row in rows]
    lines += ["\\bottomrule", "\\end{tabular}", ""]
    (TABLES / f"{name}.tex").write_text("\n".join(lines))


def dfs_table(runs):
    rows = []
    for run in sorted((r for r in runs if r["algorithm"] == "dfs"), key=lambda r: (ORDER.index(r["instance"]), r["config"])):
        status = "T/O" if run["timed_out"] else "done"
        rows.append([
            tex_name(run["instance"]),
            "on" if run["config"] == "prune" else "off",
            status,
            fmt_int(run["best"]),
            fmt(gap(run["best"], run["instance"])),
            fmt_int(run["visited"]),
            fmt(run["elapsed"], 2 if not run["timed_out"] else 0),
            fmt(run["time_to_best"], 3),
        ])
    write_table("dfs", ["Instance", "Prune", "Status", "Makespan", "Gap (\\%)", "Visits", "Time (s)", "To best (s)"], rows, "llllrrrr")


def astar_table(runs):
    rows = []
    selected = [r for r in runs if r["algorithm"] == "a_star"]
    for run in sorted(selected, key=lambda r: (ORDER.index(r["instance"]), r["config"])):
        rows.append([
            tex_name(run["instance"]),
            "H1" if run["config"] == "lower_bound" else "H2",
            "T/O" if run["timed_out"] else "done",
            fmt_int(run["best"]),
            fmt_int(run["lower_bound"]),
            fmt_int(run["visited"]),
            fmt_int(run["max_frontier"]),
            fmt(run["elapsed"], 3 if not run["timed_out"] else 0),
            fmt_int(round(run["visited"] / run["elapsed"])),
        ])
    write_table("astar", ["Instance", "Heur.", "Status", "Makespan", "Last $f$", "Expanded", "Frontier", "Time (s)", "Exp./s"], rows, "lllrrrrrr")


def ls_summary(runs):
    groups = {}
    for run in runs:
        if run["algorithm"] == "local_search":
            groups.setdefault((run["instance"], run["config"]), []).append(run)
    summary = []
    for (instance, config), group in groups.items():
        bests = [r["best"] for r in group]
        summary.append({
            "instance": instance,
            "config": config,
            "n": len(group),
            "min": min(bests),
            "mean": statistics.mean(bests),
            "std": statistics.stdev(bests) if len(bests) > 1 else 0.0,
            "hits": sum(r["best"] == OPTIMAL[instance] for r in group),
            "gap_mean": gap(statistics.mean(bests), instance),
            "gap_min": gap(min(bests), instance),
            "time": statistics.mean(r["elapsed"] for r in group),
            "to_best": statistics.mean(r["time_to_best"] for r in group),
            "visited": statistics.mean(r["visited"] for r in group),
        })
    return sorted(summary, key=lambda s: (ORDER.index(s["instance"]), s["config"]))


CONFIG_NAMES = {
    "swap_r10": "swap, 10 restarts",
    "insert_r10": "insert, 10 restarts",
    "swap_r1": "swap, 1 restart",
}


def ls_table(summary):
    rows = []
    for s in summary:
        rows.append([
            tex_name(s["instance"]),
            CONFIG_NAMES[s["config"]],
            str(OPTIMAL[s["instance"]]),
            fmt_int(s["min"]),
            fmt(s["mean"]),
            fmt(s["std"]),
            f"{s['hits']}/{s['n']}",
            fmt(s["gap_mean"]),
            fmt(s["time"], 3),
            fmt(s["to_best"], 3),
        ])
    write_table("ls", ["Instance", "Config", "Opt.", "Min", "Mean", "Std", "Hits", "Gap mean (\\%)", "Time (s)", "To best (s)"], rows, "llrrrrrrrr")


def write_csvs(runs, summary):
    METRICS.mkdir(parents=True, exist_ok=True)
    keys = ["file", "algorithm", "instance", "config", "seed", "timed_out", "best", "visited", "elapsed",
            "time_to_best", "max_frontier", "lower_bound", "reached_optimal", "python", "platform", "commit", "argv"]
    with open(METRICS / f"runs{TAG}.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(runs, key=lambda r: r["file"]))
    with open(METRICS / f"local_search_summary{TAG}.csv", "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)


def astar_figure(runs):
    astar = {(r["instance"], r["config"]): r for r in runs if r["algorithm"] == "a_star"}
    fig, ax = plt.subplots(figsize=(max(6, 0.35 * len(ORDER)), 3))
    for offset, config, label in ((-0.2, "lower_bound", "H1"), (0.2, "machine_heads_tails", "H2")):
        values = [astar[(i, config)]["visited"] for i in ORDER]
        bars = ax.bar([x + offset for x in range(len(ORDER))], values, width=0.4, label=label)
        for bar, instance in zip(bars, ORDER):
            if astar[(instance, config)]["timed_out"]:
                bar.set_hatch("//")
    ax.set_yscale("log")
    ax.set_xticks(range(len(ORDER)))
    ax.set_xticklabels(ORDER, fontsize=8, rotation=90 if len(ORDER) > 8 else 0)
    ax.set_ylabel("expanded states")
    ax.set_title("A*: expanded states in 60 s (hatched = timed out)", fontsize=9)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES / f"astar_expanded{TAG}.png", dpi=200)
    plt.close(fig)


def ls_figure(summary):
    by_key = {(s["instance"], s["config"]): s for s in summary}
    configs = [c for c in CONFIG_NAMES if any(key[1] == c for key in by_key)]
    instances = [i for i in ORDER if all((i, c) in by_key for c in configs)]
    width = 0.8 / len(configs)
    fig, ax = plt.subplots(figsize=(max(6, 0.35 * len(instances)), 3))
    for index, config in enumerate(configs):
        offset = (index - (len(configs) - 1) / 2) * width
        values = [by_key[(i, config)]["gap_mean"] for i in instances]
        errors = [100 * by_key[(i, config)]["std"] / OPTIMAL[i] for i in instances]
        ax.bar([x + offset for x in range(len(instances))], values, width=width, yerr=errors, capsize=2, label=CONFIG_NAMES[config])
    ax.set_xticks(range(len(instances)))
    ax.set_xticklabels(instances, fontsize=8, rotation=90 if len(instances) > 8 else 0)
    ax.set_ylabel("mean gap to optimum (%)" if not TAG else "mean gap to best known (%)")
    ax.set_title("Local search, 10 seeds (error bar = std)", fontsize=9)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(FIGURES / f"ls_gap{TAG}.png", dpi=200)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--logs", type=Path)
    args = parser.parse_args()
    for logs, tag in [(args.logs, "")] if args.logs else DEFAULT_LOGS:
        global TAG
        TAG = tag
        runs = load_runs(logs)
        configure(runs)
        print(f"{logs.name}: {len(runs)} runs, {sum(r['timed_out'] for r in runs)} timed out")
        print("environments:", {(r["python"], r["platform"], r["commit"]) for r in runs})
        summary = ls_summary(runs)
        dfs_table(runs)
        astar_table(runs)
        ls_table(summary)
        write_csvs(runs, summary)
        FIGURES.mkdir(parents=True, exist_ok=True)
        astar_figure(runs)
        ls_figure(summary)


if __name__ == "__main__":
    main()

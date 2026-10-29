import matplotlib.pyplot as plt

from utils.a_star import AStar
from utils.dfs import DFS

GANTT_COLORS = ["#FF7F7F", "#B5F26B", "#6FF0F5", "#B070F0"]


def plot_gantt(solver: DFS | AStar, show: bool = True):
    problem = solver.problem
    start = problem.start_times(solver.best_sequence)

    figure, axes = plt.subplots(figsize=(11, 4))
    for job in range(problem.n_jobs):
        for operation in range(problem.n_operations_per_job):
            machine = problem.machines[job, operation]
            duration = problem.durations[job, operation]
            left = start[job, operation]

            axes.barh(
                machine,
                duration,
                left=left,
                color=GANTT_COLORS[job % len(GANTT_COLORS)],
                edgecolor="black",
            )
            axes.text(
                left + duration / 2,
                machine,
                f"J{job + 1}.O{operation + 1}",
                ha="center",
                va="center",
                fontsize=8,
            )

    axes.set_yticks(range(problem.n_machines))
    axes.set_yticklabels([f"M{machine + 1}" for machine in range(problem.n_machines)])
    axes.invert_yaxis()
    axes.set_xlabel("Time")
    axes.set_title(f"Best makespan {solver.best_makespan}")
    figure.tight_layout()

    if show:
        plt.show()
    return axes

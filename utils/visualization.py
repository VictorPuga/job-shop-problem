import matplotlib.pyplot as plt

from utils.dfs import DFS

GANTT_COLORS = ["#FF7F7F", "#B5F26B", "#6FF0F5", "#B070F0"]


class LiveGantt:
    """Gantt chart that redraws every time the search finds a better schedule."""

    def __init__(self, pause: float = 0.4) -> None:
        self.pause = pause
        self.x_limit = 0
        plt.ion()
        self.figure, self.axes = plt.subplots(figsize=(11, 4))

    def update(self, dfs: DFS) -> None:
        """Draws the schedule built by `dfs.best_sequence`."""
        problem = dfs.problem
        start = problem.start_times(dfs.best_sequence)

        self.x_limit = max(self.x_limit, dfs.best_makespan)

        self.axes.clear()
        for job in range(problem.n_jobs):
            for operation in range(problem.n_operations_per_job):
                machine = problem.machines[job, operation]
                duration = problem.durations[job, operation]
                left = start[job, operation]

                self.axes.barh(
                    machine,
                    duration,
                    left=left,
                    color=GANTT_COLORS[job % len(GANTT_COLORS)],
                    edgecolor="black",
                )
                self.axes.text(
                    left + duration / 2,
                    machine,
                    f"J{job + 1}.O{operation + 1}",
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="black",
                )

        self.axes.set_xlim(0, self.x_limit * 1.02)
        self.axes.set_yticks(range(problem.n_machines))
        labels = []
        for machine in range(problem.n_machines):
            labels.append(f"M{machine + 1}")
        self.axes.set_yticklabels(labels)
        self.axes.invert_yaxis()
        self.axes.set_xlabel("Time")
        self.axes.set_title(
            f"Best makespan {dfs.best_makespan} (search call {dfs.visited})"
        )
        self.axes.axvline(dfs.best_makespan, color="gray", linestyle="--", linewidth=1)

        self.figure.tight_layout()
        self.figure.canvas.draw_idle()
        plt.pause(max(self.pause, 0.001))

    def show(self) -> None:
        """Keeps the final chart open until the window is closed."""
        plt.ioff()
        plt.show()

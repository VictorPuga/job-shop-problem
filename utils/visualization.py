import matplotlib.pyplot as plt
from matplotlib import colormaps

from utils.dfs import DFS


class LiveGantt:
    """Gantt chart that redraws every time the search finds a better schedule."""

    def __init__(self, pause: float = 0.4) -> None:
        self.pause = pause
        self.x_limit = 0
        plt.ion()
        self.figure, self.axes = plt.subplots(figsize=(11, 4))

    def update(self, dfs: DFS) -> None:
        """Draws the schedule held by `dfs.graph`, which has the new best orientation applied."""
        graph = dfs.graph
        start = graph.earliest_starts()
        assert start is not None

        self.x_limit = max(self.x_limit, dfs.best_makespan)
        colors = colormaps["tab10"]

        self.axes.clear()
        for node_id, node in graph.nodes.items():
            if node_id in (graph.source, graph.sink):
                continue

            self.axes.barh(
                node.machine,
                node.duration,
                left=start[node_id],
                color=colors(node.job % 10),
                edgecolor="white",
            )
            self.axes.text(
                start[node_id] + node.duration / 2,
                node.machine,
                f"J{node.job + 1}.O{node.operation + 1}",
                ha="center",
                va="center",
                fontsize=8,
                color="white",
            )

        self.axes.set_xlim(0, self.x_limit * 1.02)
        self.axes.set_yticks(range(graph.n_machines))
        self.axes.set_yticklabels([f"M{m + 1}" for m in range(graph.n_machines)])
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

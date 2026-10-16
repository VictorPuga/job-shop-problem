import os

import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch, Patch

from utils.dfs import DFS
from utils.graph import Graph


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


def node_positions(graph: Graph) -> dict[int, tuple[float, float]]:
    """Operations on a grid (column = operation, row = job), source on the left, sink on the right."""
    middle = -(graph.n_jobs - 1) / 2
    positions = {
        graph.source: (0.0, middle),
        graph.sink: (float(graph.n_operations_per_job + 1), middle),
    }
    for job in range(graph.n_jobs):
        for operation in range(graph.n_operations_per_job):
            node_id = graph.calculate_node_id(job, operation)
            positions[node_id] = (float(operation + 1), float(-job))
    return positions


def draw_graph(
    axes: Axes,
    graph: Graph,
    orientation: list[tuple[int, int]] | None = None,
    title: str = "",
) -> None:
    """Draws the disjunctive graph on `axes`.

    Job chains are gray arrows.
    Without `orientation`, every disjunctive pair is a dashed line colored by machine.
    With `orientation`, each pair is a solid arrow in the chosen direction.
    """
    positions = node_positions(graph)
    machine_colors = colormaps["Set1"]
    node_size = 1500
    curvatures = (0.3, -0.3, 0.5, -0.5)

    def add_arrow(from_id, to_id, style, color, linestyle="-", curvature=0.0, alpha=1.0):
        axes.add_patch(
            FancyArrowPatch(
                positions[from_id],
                positions[to_id],
                arrowstyle=style,
                connectionstyle=f"arc3,rad={curvature}",
                color=color,
                linestyle=linestyle,
                alpha=alpha,
                mutation_scale=15,
                shrinkA=22,
                shrinkB=22,
                linewidth=1.6,
                zorder=1,
            )
        )

    for job in range(graph.n_jobs):
        chain = [graph.source]
        chain += [graph.calculate_node_id(job, op) for op in range(graph.n_operations_per_job)]
        chain.append(graph.sink)
        for from_id, to_id in zip(chain, chain[1:]):
            add_arrow(from_id, to_id, "-|>", "gray")

    if orientation is None:
        for index, (a, b) in enumerate(graph.disjunctive_pairs):
            color = machine_colors(graph.nodes[a].machine)
            curvature = curvatures[index % len(curvatures)]
            add_arrow(a, b, "-", color, "--", curvature, alpha=0.8)
    else:
        for index, (from_id, to_id) in enumerate(orientation):
            color = machine_colors(graph.nodes[from_id].machine)
            curvature = curvatures[index % len(curvatures)]
            add_arrow(from_id, to_id, "-|>", color, "-", curvature, alpha=0.8)

    for node_id, (x, y) in positions.items():
        node = graph.nodes[node_id]
        if node_id in (graph.source, graph.sink):
            label = "S" if node_id == graph.source else "T"
            face = "white"
        else:
            label = f"J{node.job + 1}.O{node.operation + 1}\n({node.duration})"
            face = machine_colors(node.machine)
        axes.scatter([x], [y], s=node_size, color=face, edgecolors="black", zorder=3)
        axes.text(x, y, label, ha="center", va="center", fontsize=7, zorder=4)

    axes.legend(
        handles=[
            Patch(color=machine_colors(m), label=f"Machine {m + 1}")
            for m in range(graph.n_machines)
        ],
        loc="lower center",
        ncol=graph.n_machines,
        frameon=False,
    )
    axes.set_title(title)
    axes.set_xlim(-0.7, graph.n_operations_per_job + 1.7)
    axes.set_ylim(-(graph.n_jobs - 1) - 0.9, 0.9)
    axes.set_aspect("equal")
    axes.axis("off")


def save_graph_image(
    graph: Graph, orientation: list[tuple[int, int]], path: str
) -> None:
    """Saves the disjunctive graph, and the same graph with `orientation` applied, side by side."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    figure, (left, right) = plt.subplots(1, 2, figsize=(18, 7))
    draw_graph(left, graph, title="Disjunctive graph (dashed = machine conflict)")
    draw_graph(right, graph, orientation, title="Best orientation (node label: duration)")
    figure.tight_layout()
    figure.savefig(path, dpi=150)
    plt.close(figure)

import time

from utils.dfs import DFS
from utils.graph import Graph
from utils.instances import durations, machines

PRUNE_DFS = True
VISUALIZE = False
DRAW_GRAPH = False
GRAPH_IMAGE_PATH = "tmp/graph.png"


def describe(graph: Graph, node_id: int) -> str:
    node = graph.nodes[node_id]
    return f"J{node.job + 1}.O{node.operation + 1}"


def run(prune: bool, gantt=None) -> tuple[Graph, DFS, float]:
    graph = Graph(machines, durations)
    dfs = DFS(graph, prune=prune, on_improvement=gantt.update if gantt else None)

    start = time.perf_counter()
    dfs.search(0)
    elapsed = time.perf_counter() - start

    return graph, dfs, elapsed


def print_schedule(graph: Graph, dfs: DFS) -> None:
    print("Order on each machine (J = job, O = operation):")

    predecessors = dict.fromkeys(graph.nodes, 0)
    for _, to_id in dfs.best_orientation:
        predecessors[to_id] += 1

    for machine, node_ids in enumerate(graph.machine_nodes):
        ordered = sorted(node_ids, key=lambda node_id: predecessors[node_id])
        sequence = " -> ".join(describe(graph, node_id) for node_id in ordered)
        print(f"  M{machine + 1}: {sequence}")


def print_start_times(graph: Graph, dfs: DFS) -> None:
    for from_id, to_id in dfs.best_orientation:
        graph.add_edge(from_id, to_id)

    start = graph.earliest_starts()
    assert start is not None

    print("Start time of each operation (rows = jobs, columns = operations):")
    header = "".join(f"{f'O{op + 1}':>6}" for op in range(graph.n_operations_per_job))
    print(f"{'':<6}{header}")

    for job in range(graph.n_jobs):
        times = "".join(
            f"{start[graph.calculate_node_id(job, op)]:>6}"
            for op in range(graph.n_operations_per_job)
        )
        print(f"{f'J{job + 1}':<6}{times}")


def main() -> None:
    gantt = None
    if VISUALIZE:
        from utils.visualization import LiveGantt

        gantt = LiveGantt()

    graph, dfs, elapsed = run(PRUNE_DFS, gantt)
    print(f"DFS Pruning: {'on' if PRUNE_DFS else 'off'}")
    print(f"Best makespan: {dfs.best_makespan}")
    print(f"Search calls: {dfs.visited}")
    print(
        f"Search time: {elapsed:.3f} s{' (includes plotting pauses)' if gantt else ''}"
    )
    print_schedule(graph, dfs)

    if DRAW_GRAPH:
        from utils.visualization import save_graph_image

        save_graph_image(graph, dfs.best_orientation, GRAPH_IMAGE_PATH)
        print(f"Graph image saved to {GRAPH_IMAGE_PATH}")

    print_start_times(graph, dfs)

    if gantt:
        gantt.show()


if __name__ == "__main__":
    main()

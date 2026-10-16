import time

from utils.dfs import DFS
from utils.graph import Graph
from utils.instances import durations, machines

PRUNE_DFS = True


def describe(graph: Graph, node_id: int) -> str:
    node = graph.nodes[node_id]
    return f"J{node.job + 1}.O{node.operation + 1}"


def run(prune: bool) -> tuple[Graph, DFS, float]:
    graph = Graph(machines, durations)
    dfs = DFS(graph, prune=prune)

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


def main() -> None:
    graph, dfs, elapsed = run(PRUNE_DFS)
    print(f"DFS Pruning: {'on' if PRUNE_DFS else 'off'}")
    print(f"Best makespan: {dfs.best_makespan}")
    print(f"Search calls: {dfs.visited}")
    print(f"Search time: {elapsed:.3f} s")
    print_schedule(graph, dfs)


if __name__ == "__main__":
    main()

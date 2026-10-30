import json
import random
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

INSTANCES_DIR = Path(__file__).parent.parent / "instances"

# name prefix -> (n_jobs, n_machines, min duration, max duration), one entry per instance
GENERATED_SPECS: dict[str, tuple[int, int, int, int]] = {
    **{f"gen_easy_{i:02d}": (3 + i % 2, 3 + i % 2, 1, 10) for i in range(1, 11)},
    **{f"gen_medium_{i:02d}": (5 + i % 3, 5 + i % 3, 1, 50) for i in range(1, 9)},
    "gen_hard_01": (10, 10, 1, 99),
    "gen_hard_02": (15, 10, 1, 99),
}


def generate_instance(
    seed: int, n_jobs: int, n_machines: int, low: int, high: int
) -> tuple[NDArray[np.int_], NDArray[np.int_]]:
    rng = random.Random(seed)
    machines = []
    durations = []
    for _ in range(n_jobs):
        order = list(range(n_machines))
        rng.shuffle(order)
        machines.append(order)
        durations.append([rng.randint(low, high) for _ in range(n_machines)])
    return np.array(machines), np.array(durations)


def write_instance(
    path: Path, machines: NDArray[np.int_], durations: NDArray[np.int_]
) -> None:
    data = {"machines": machines.tolist(), "durations": durations.tolist()}
    lines = ["{"]
    for key_index, (key, rows) in enumerate(data.items()):
        lines.append(f'  "{key}": [')
        for row_index, row in enumerate(rows):
            comma = "," if row_index < len(rows) - 1 else ""
            lines.append(f"    {json.dumps(row)}{comma}")
        lines.append("  ]" + ("," if key_index < len(data) - 1 else ""))
    lines.append("}")
    path.write_text("\n".join(lines) + "\n")


def read_instance(path: Path) -> tuple[NDArray[np.int_], NDArray[np.int_]]:
    data = json.loads(path.read_text())
    return np.array(data["machines"]), np.array(data["durations"])


def generate_all(base_seed: int = 2026) -> list[Path]:
    INSTANCES_DIR.mkdir(exist_ok=True)
    paths = []
    for index, (name, (n_jobs, n_machines, low, high)) in enumerate(GENERATED_SPECS.items()):
        machines, durations = generate_instance(base_seed + index, n_jobs, n_machines, low, high)
        path = INSTANCES_DIR / f"{name}.json"
        write_instance(path, machines, durations)
        paths.append(path)
    return paths

import json
import random
from pathlib import Path

import numpy as np

INSTANCES_DIR = Path(__file__).parent.parent / "instances"

# (name, n_jobs, n_machines, min duration, max duration)
SPECS = []
for i in range(1, 11):
    size = 3 + i % 2
    SPECS.append((f"gen_easy_{i:02d}", size, size, 1, 10))
for i in range(1, 9):
    size = 5 + i % 3
    SPECS.append((f"gen_medium_{i:02d}", size, size, 1, 50))
SPECS.append(("gen_hard_01", 10, 10, 1, 99))
SPECS.append(("gen_hard_02", 15, 10, 1, 99))


def generate_instance(seed, n_jobs, n_machines, low, high):
    rng = random.Random(seed)
    machines = []
    durations = []
    for _ in range(n_jobs):
        order = list(range(n_machines))
        rng.shuffle(order)
        machines.append(order)
        durations.append([rng.randint(low, high) for _ in range(n_machines)])
    return np.array(machines), np.array(durations)


def format_matrix(matrix):
    rows = [f"    {json.dumps(row)}" for row in matrix.tolist()]
    return "[\n" + ",\n".join(rows) + "\n  ]"


def write_instance(path, machines, durations):
    text = '{\n  "machines": ' + format_matrix(machines) + ",\n"
    text += '  "durations": ' + format_matrix(durations) + "\n}\n"
    path.write_text(text)


def read_instance(path):
    data = json.loads(path.read_text())
    return np.array(data["machines"]), np.array(data["durations"])


def generate_all(base_seed=2026):
    INSTANCES_DIR.mkdir(exist_ok=True)
    for index, (name, n_jobs, n_machines, low, high) in enumerate(SPECS):
        machines, durations = generate_instance(
            base_seed + index, n_jobs, n_machines, low, high
        )
        write_instance(INSTANCES_DIR / f"{name}.json", machines, durations)
        print(name)

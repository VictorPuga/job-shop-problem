import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.generator import generate_all


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the seeded instances.")
    parser.add_argument("--seed", type=int, default=2026, help="base seed")
    args = parser.parse_args()
    for path in generate_all(args.seed):
        print(path)


if __name__ == "__main__":
    main()

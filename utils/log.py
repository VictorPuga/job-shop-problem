import logging
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")


def setup_logging(instance: str, algorithm: str, level: int = logging.INFO) -> Path:
    LOG_DIR.mkdir(exist_ok=True)
    path = LOG_DIR / f"{algorithm}_{instance}_{datetime.now():%Y%m%d_%H%M%S}.log"

    handler = logging.FileHandler(path)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

    logger = logging.getLogger("utils.dfs")
    logger.setLevel(level)
    logger.addHandler(handler)
    return path

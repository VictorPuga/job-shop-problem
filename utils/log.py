import json
import logging
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")

RESERVED = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


class JsonlFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.fromtimestamp(record.created).isoformat(
                timespec="milliseconds"
            ),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        entry.update(
            {key: value for key, value in vars(record).items() if key not in RESERVED}
        )
        return json.dumps(entry, default=list)


def setup_logging(
    instance: str, algorithm: str, tag: str = "", level: int = logging.INFO
) -> Path:
    LOG_DIR.mkdir(exist_ok=True)
    now = datetime.now()
    stamp = f"{now:%Y%m%d_%H%M%S}_{now.microsecond // 1000:03d}"
    parts = [algorithm, instance, tag, stamp]
    path = LOG_DIR / f"{'_'.join(part for part in parts if part)}.jsonl"

    handler = logging.FileHandler(path, mode="x")
    handler.setFormatter(JsonlFormatter())

    logger = logging.getLogger(f"utils.{algorithm}")
    logger.setLevel(level)
    logger.addHandler(handler)
    return path

from loguru import logger
from pathlib import Path

LOG_DIR = Path("logs")

LOG_DIR.mkdir(exist_ok=True)

logger.remove()

logger.add(
    LOG_DIR / "gem.log",
    rotation="10 MB",
    retention="10 days",
    enqueue=True,
    level="INFO"
)

logger.add(
    lambda msg: print(msg, end=""),
    level="INFO"
)

log = logger
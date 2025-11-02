from loguru import logger
from pathlib import Path
import sys

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add(log_dir / "app.log", rotation="1 day", level="DEBUG", backtrace=True, diagnose=True)

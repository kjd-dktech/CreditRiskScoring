from loguru import logger
import os
import sys

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logger.remove()

logger.add(sys.stdout, level="INFO", colorize=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
logger.add(
    os.path.join(log_dir, "credit_scoring.log"),
    rotation="00:00",
    retention="7 days",
    level="DEBUG",
    encoding="utf-8",
    backtrace=True,
    diagnose=True
)

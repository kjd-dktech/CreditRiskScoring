from loguru import logger
import os
import sys
from pathlib import Path

# Utiliser un chemin absolu basé sur l'emplacement de ce fichier
# pour que les logs aillent toujours dans API/logs/ quel que soit le CWD
CURRENT_DIR = Path(__file__).resolve().parent
log_dir = CURRENT_DIR / "logs"
log_dir.mkdir(exist_ok=True)

logger.remove()

logger.add(sys.stdout, level="INFO", colorize=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
logger.add(
    log_dir / "credit_scoring.log",
    rotation="00:00",
    retention="7 days",
    level="DEBUG",
    encoding="utf-8",
    backtrace=True,
    diagnose=True
)

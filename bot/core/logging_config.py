import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    log_level = level or "INFO"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    logger = logging.getLogger("bot")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    return logger

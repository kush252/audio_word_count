import logging
import sys

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Sets up a structured logger that outputs to stdout without being spammy."""
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if already set up
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        
        # Format includes timestamp, level, and message
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

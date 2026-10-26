"""
Retail Sales Analytics - Common Utilities
Provides logging, path resolution, and console formatting helpers.
"""

from pathlib import Path
import logging
import sys

def get_project_root() -> Path:
    """Returns the absolute root directory of the project."""
    return Path(__file__).resolve().parent.parent

def setup_logger(name: str = "retail_sales", level: int = logging.INFO) -> logging.Logger:
    """Configures and returns a structured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def print_section(title: str, width: int = 70, char: str = "=") -> None:
    """Prints a formatted section header."""
    print(f"\n{char * width}")
    print(f" {title.upper()} ")
    print(f"{char * width}")

"""Kept for backward compatibility: equivalent to `python -m src.core.runner --version A`."""

import sys

from src.core.runner import main


if __name__ == "__main__":
    main(["--version", "A"] + sys.argv[1:])

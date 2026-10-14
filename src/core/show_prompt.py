"""Print the exact instructions a version sends to the model, with its hashes.

Usage: python -m src.core.show_prompt --version C > /tmp/prompt_C.txt
"""

import argparse
import importlib

from src.core.agent import sha256_text
from src.core.db import get_schema
from src.core.runner import VERSION_MODULES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, choices=sorted(VERSION_MODULES))
    args = parser.parse_args()

    version = importlib.import_module(VERSION_MODULES[args.version]).VERSION
    schema = get_schema()
    instructions = version.build_instructions(schema)

    print(instructions)
    print("=" * 80)
    print(f"version: {version.name}")
    print(f"prompt_hash: {sha256_text(instructions)}")
    print(f"schema_hash: {sha256_text(schema)}")
    print(f"context_hash: {version.context_hash}")
    print(f"max_repairs: {version.max_repairs}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from office.mission_command.e32_existing_learning_strategy_wheel_inventory import write_all_artifacts


def main() -> int:
    write_all_artifacts(Path(__file__).resolve().parents[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

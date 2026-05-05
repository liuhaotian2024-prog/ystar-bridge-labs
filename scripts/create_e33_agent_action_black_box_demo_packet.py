#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from office.mission_command.e33_agent_action_black_box_builder import write_all_artifacts


def main() -> int:
    write_all_artifacts(Path(__file__).resolve().parents[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

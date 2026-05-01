#!/usr/bin/env python3.11
from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from office.mission_command.mission_summary import build_mission_summary


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        print('Usage: python3.11 office/mission_command/mission_cli.py "Aiden，带团队制定未来 7 天最可能产生第一笔收入的行动方案"')
        return 2
    repo_root = Path(__file__).resolve().parents[2]
    print(build_mission_summary(" ".join(args), repo_root=repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


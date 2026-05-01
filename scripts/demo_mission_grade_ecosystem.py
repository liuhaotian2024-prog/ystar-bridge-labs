#!/usr/bin/env python3.11
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from office.mission_command.mission_summary import build_mission_summary


MISSION = "制定未来 7 天最可能产生第一笔收入的行动方案"


def main() -> int:
    report = build_mission_summary(MISSION, repo_root=ROOT)
    out = ROOT / "reports" / "integration" / "mission_grade_ecosystem_demo.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report + "\n", encoding="utf-8")
    print(report)
    print(f"\nSaved: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def test_all_tracked_readme_files_are_english_only():
    files = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    readmes = [path for path in files if Path(path).name.lower().startswith("readme")]

    assert readmes, "expected tracked README files"
    offenders: list[str] = []
    for rel in readmes:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
        if CJK_RE.search(text):
            offenders.append(rel)

    assert offenders == []

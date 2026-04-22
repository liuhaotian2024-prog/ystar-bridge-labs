"""Skill Library — index scripts/ by docstring trigger patterns.

Voyager-inspired: maintain SQLite library of (trigger → skill → script_path).
Retrieve relevant skill at query time. Increment success count on use.

NOT wired into hooks here — separate integration milestone.
"""
from __future__ import annotations
import sqlite3
import time
from pathlib import Path
from typing import List, Optional

SCRIPTS_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts")
DB_PATH = SCRIPTS_DIR / "skill_library.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_pattern TEXT NOT NULL,
    script_path TEXT NOT NULL UNIQUE,
    success_count INTEGER DEFAULT 0,
    last_used REAL DEFAULT 0,
    provenance TEXT DEFAULT 'auto_docstring'
);
CREATE INDEX IF NOT EXISTS idx_trigger ON skills(trigger_pattern);
"""


class SkillLibrary:
    def __init__(self, db_path: Path = DB_PATH):
        self.conn = sqlite3.connect(str(db_path), timeout=5)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def register_skill(self, trigger: str, path: str, provenance: str = "auto") -> int:
        c = self.conn.execute(
            "INSERT OR IGNORE INTO skills (trigger_pattern, script_path, provenance)"
            " VALUES (?, ?, ?)", (trigger, path, provenance))
        self.conn.commit()
        return c.lastrowid or 0

    def retrieve(self, query: str, limit: int = 3) -> List[dict]:
        tokens = [t for t in query.lower().split() if len(t) >= 3]
        results = []
        seen = set()
        for token in tokens:
            for row in self.conn.execute(
                "SELECT skill_id, trigger_pattern, script_path, success_count, last_used"
                " FROM skills WHERE lower(trigger_pattern) LIKE ?"
                " ORDER BY success_count DESC, last_used DESC LIMIT ?",
                (f"%{token}%", limit)
            ):
                if row[0] not in seen:
                    seen.add(row[0])
                    results.append({
                        "skill_id": row[0], "trigger": row[1],
                        "path": row[2], "success_count": row[3],
                        "last_used": row[4],
                    })
        return results[:limit]

    def increment_success(self, skill_id: int) -> None:
        self.conn.execute(
            "UPDATE skills SET success_count = success_count + 1,"
            " last_used = ? WHERE skill_id = ?", (time.time(), skill_id))
        self.conn.commit()

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]


def bulk_import_from_scripts(lib: SkillLibrary, scripts_dir: Path = SCRIPTS_DIR) -> int:
    added = 0
    for py in scripts_dir.glob("*.py"):
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        docstring = ""
        lines = text.splitlines()
        for i, line in enumerate(lines[:30]):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                for j in range(i + 1, min(i + 10, len(lines))):
                    s = lines[j].strip()
                    if s and not (s.startswith('"""') or s.startswith("'''")):
                        docstring = s
                        break
                break
        if docstring:
            trigger = docstring[:200]
            lib.register_skill(trigger, str(py), provenance="bulk_docstring")
            added += 1
    return added


if __name__ == "__main__":
    lib = SkillLibrary()
    n = bulk_import_from_scripts(lib)
    print(f"[skill_library] imported {n} skills. total={lib.count()}")

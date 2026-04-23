#!/usr/bin/env python3
"""
Phase 2 Role Scope Seed — populate ystar_role_scope table.

Board 2026-04-23 directive: field-functional role-scope alignment.
Each role has scope_keywords (in-scope lexemes) and anti_scope_keywords
(off-scope lexemes). Used by field-functional to measure role alignment.

Idempotent: INSERT OR REPLACE — running twice replaces rows, no duplicates.
"""

import json
import os
import sqlite3
import time
import uuid
from typing import Dict, List

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".ystar_cieu.db",
)

ROLE_SCOPES: Dict[str, Dict[str, List[str]]] = {
    "ceo": {
        "scope_keywords": [
            "board", "report", "strategy", "dispatch", "priority",
            "risk", "escalation", "patent", "compliance", "resource",
            "coordination", "decision", "战略", "风险", "汇报",
        ],
        "anti_scope_keywords": [
            "write code", "edit code", "src/", "scripts/*.py edit",
            "archive", "archival", "organize files", "routine maintenance",
        ],
    },
    "cto": {
        "scope_keywords": [
            "code", "architecture", "test", "build", "deploy",
            "refactor", "CI", "pipeline", "dependency", "performance",
            "debug", "技术架构", "系统健康", "代码交付",
        ],
        "anti_scope_keywords": [
            "blog post", "marketing", "sales outreach", "pricing model",
            "board report", "financial forecast",
        ],
    },
    "cmo": {
        "scope_keywords": [
            "content", "blog", "article", "whitepaper", "launch",
            "campaign", "audience", "messaging", "brand", "SEO",
            "social media", "内容产出", "市场触达", "用户洞察",
        ],
        "anti_scope_keywords": [
            "write code", "edit src/", "database schema", "CI pipeline",
            "financial model", "compliance audit",
        ],
    },
    "secretary": {
        "scope_keywords": [
            "archive", "minutes", "meeting", "index", "knowledge",
            "filing", "record", "amendment", "议事", "档案",
            "知识索引", "议事管理", "档案完整",
        ],
        "anti_scope_keywords": [
            "write code", "marketing campaign", "sales outreach",
            "pricing", "deploy", "architecture decision",
        ],
    },
    "platform": {
        "scope_keywords": [
            "infrastructure", "daemon", "script", "tool", "pipeline",
            "adapter", "CLI", "MCP", "boot", "monitor",
            "基础设施", "工具交付", "数据管道", "稳定",
        ],
        "anti_scope_keywords": [
            "blog post", "board report", "sales outreach",
            "governance rule", "kernel algorithm",
        ],
    },
    "governance": {
        "scope_keywords": [
            "rule", "enforce", "audit", "compliance", "hook",
            "amendment", "CIEU", "ForgetGuard", "boundary", "scope",
            "规则执行", "合规审计", "治理演进", "iron rule",
        ],
        "anti_scope_keywords": [
            "blog post", "marketing", "sales outreach",
            "financial model", "product feature code",
        ],
    },
    "kernel": {
        "scope_keywords": [
            "theory", "algorithm", "proof", "formal", "contract",
            "compiler", "intent", "dimension", "engine", "session",
            "理论验证", "核心算法", "知识库", "scope validation",
        ],
        "anti_scope_keywords": [
            "blog post", "marketing", "sales outreach",
            "daemon", "infrastructure", "governance rule edit",
        ],
    },
}


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ystar_role_scope (
            role_id TEXT PRIMARY KEY,
            scope_keywords TEXT,
            anti_scope_keywords TEXT,
            updated_at REAL
        )
    """)

    # Seed rows (idempotent via INSERT OR REPLACE)
    now = time.time()
    total_scope = 0
    total_anti = 0
    for role_id, kw in ROLE_SCOPES.items():
        scope_json = json.dumps(kw["scope_keywords"], ensure_ascii=False)
        anti_json = json.dumps(kw["anti_scope_keywords"], ensure_ascii=False)
        total_scope += len(kw["scope_keywords"])
        total_anti += len(kw["anti_scope_keywords"])
        cur.execute(
            "INSERT OR REPLACE INTO ystar_role_scope "
            "(role_id, scope_keywords, anti_scope_keywords, updated_at) "
            "VALUES (?, ?, ?, ?)",
            (role_id, scope_json, anti_json, now),
        )

    conn.commit()

    # Emit CIEU event
    event_id = str(uuid.uuid4())
    seq_global = int(time.time() * 1_000_000)  # microsecond timestamp
    # Read session_id from .ystar_session.json if available
    session_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        ".ystar_session.json",
    )
    session_id = "standalone"
    try:
        with open(session_file) as f:
            sdata = json.load(f)
            session_id = sdata.get("session_id", "standalone")
    except Exception:
        pass

    cur.execute(
        """INSERT INTO cieu_events
           (event_id, seq_global, created_at, session_id, agent_id,
            event_type, decision, passed, file_path,
            params_json, result_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            event_id,
            seq_global,
            time.time(),
            session_id,
            "eng-kernel",
            "WAVE2_PHASE2_ROLE_SCOPE_LANDED",
            "auto_approve",
            1,
            "scripts/phase2_role_scope_seed.py",
            json.dumps({
                "roles_seeded": len(ROLE_SCOPES),
                "total_scope_keywords": total_scope,
                "total_anti_scope_keywords": total_anti,
            }),
            json.dumps({"status": "success", "table": "ystar_role_scope"}),
        ),
    )
    conn.commit()
    conn.close()

    print(f"Seeded {len(ROLE_SCOPES)} roles into ystar_role_scope.")
    print(f"  total_scope_keywords: {total_scope}")
    print(f"  total_anti_scope_keywords: {total_anti}")
    print(f"  CIEU event_id: {event_id}")


if __name__ == "__main__":
    main()

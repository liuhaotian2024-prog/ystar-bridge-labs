# NEXT SESSION P0 — YML Session Bridge (最后一公里)

**Priority**: P0 — 任何其他任务前做
**Owner**: Ryan-Platform (dispatch via Ethan-CTO per Path B-lite, CTO 写 task card + CEO 代 spawn)
**Triggered by**: 顾问 2026-04-14 深度 audit catch "YML 作为库完整，作为系统空转"

---

## Context (必读)

**YML 现状 (顾问 audit verified):**
- ✅ Core library 完整: `Y-star-gov/ystar/memory/` models.py / store.py / decay.py / ingest.py
- ✅ gov-mcp tools 全 registered: `gov_remember` (line 3838), `gov_recall` (3889), `gov_forget` (3951), `gov_memory_summary` (3985), `gov_memory_decay` (4009), `gov_memory_reinforce` (4037), `gov_recall_v2` (enhanced)
- ✅ `_State.memory_store` 初始化 (server.py line 96)
- ✅ CIEU→memory 桥接 (ingest.py daemon thread, fail-open)
- ✅ `gov_health` + `gov_health_retrospective` + `health.py` integrated

**真缺:**
- ❌ `scripts/session_memory_boot.py` 不存在
- ❌ `scripts/session_memory_commit.py` 不存在
- ❌ `governance_boot.sh` 没挂接 YML load
- ❌ Session close hook 没挂接 YML commit

**后果**: YML 是没入口出口的仓库 — 每 session 记忆 loss，所有 codify memory 只对当前 session 生效。

---

## Deliverables (3 files, ≤90 min)

### Deliverable 1: `scripts/session_memory_boot.py`

**Purpose**: Session boot 时从 YML auto-load top-N memory events to agent context.

```python
#!/usr/bin/env python3
"""Session memory boot — load top-N YML memory events into boot pack on session start."""
import os, sys, json, sqlite3
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
Y_STAR_GOV = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
sys.path.insert(0, str(Y_STAR_GOV))

from ystar.memory.store import MemoryStore  # 顾问 verified 存在
from ystar.memory.decay import compute_dynamic_score

def main(agent_id: str, top_n: int = 20):
    memory_db = WORKSPACE / ".ystar_memory.db"
    store = MemoryStore(db_path=str(memory_db))
    
    # Recall top-N memory events for this agent, ordered by dynamic_score (decay-aware)
    events = store.recall(actor_id=agent_id, limit=top_n, order_by="dynamic_score DESC")
    
    # Write to boot_pack as Category 0.5 "yml_memory_recall"
    boot_pack_path = WORKSPACE / f"memory/boot_packages/{agent_id}.json"
    if boot_pack_path.exists():
        with open(boot_pack_path) as f:
            pack = json.load(f)
    else:
        pack = {}
    
    pack["category_0_5_yml_memory_recall"] = {
        "generated_at": __import__("time").time(),
        "agent_id": agent_id,
        "top_n": top_n,
        "events": [{"id": e.id, "text": e.text, "score": e.score, "created_at": e.created_at} for e in events]
    }
    
    with open(boot_pack_path, "w") as f:
        json.dump(pack, f, indent=2, ensure_ascii=False)
    
    print(f"[session_memory_boot] Loaded {len(events)} top memories for {agent_id}")
    return 0

if __name__ == "__main__":
    agent_id = sys.argv[1] if len(sys.argv) > 1 else "ceo"
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    sys.exit(main(agent_id, top_n))
```

### Deliverable 2: `scripts/session_memory_commit.py`

**Purpose**: Session 结束时 scan 本 session CIEU events + 提取"重要记忆"(MATURITY_TRANSITION / WHITELIST_DRIFT / FORGET_GUARD / ARTICLE_11_LAYER_COMPLETE 等) + commit to YML via `gov_remember`.

```python
#!/usr/bin/env python3
"""Session memory commit — scan session CIEU, persist important events to YML."""
import os, sys, json, sqlite3, time
from pathlib import Path

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
Y_STAR_GOV = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
sys.path.insert(0, str(Y_STAR_GOV))

from ystar.memory.store import MemoryStore

IMPORTANT_EVENT_TYPES = [
    "MATURITY_TRANSITION",
    "WHITELIST_DRIFT",
    "FORGET_GUARD",
    "DEFER_IN_COMMIT_DRIFT",
    "ARTICLE_11_LAYER_%_COMPLETE",
    "CROBA_CONTRACT_INJECT",
    "BREAK_GLASS_CLAIM",
    "LESSON_CAPTURE_DUE",
]

def main(session_id: str, agent_id: str = "ceo"):
    cieu_db = WORKSPACE / ".ystar_cieu.db"
    memory_db = WORKSPACE / ".ystar_memory.db"
    
    cieu = sqlite3.connect(str(cieu_db))
    memory = MemoryStore(db_path=str(memory_db))
    
    # Scan session events
    cur = cieu.cursor()
    placeholder = " OR ".join(f"event_type LIKE '{t}'" for t in IMPORTANT_EVENT_TYPES)
    cur.execute(f"SELECT event_type, created_at, decision, violations, drift_details FROM cieu_events WHERE session_id=? AND ({placeholder}) ORDER BY created_at DESC LIMIT 200", (session_id,))
    
    count = 0
    for row in cur.fetchall():
        event_type, created_at, decision, violations, drift_details = row
        summary = f"[{event_type}] dec={decision} violations={violations[:200] if violations else ''}"
        memory.remember(actor_id=agent_id, text=summary, score=1.0, source=f"cieu:{event_type}:{created_at}")
        count += 1
    
    print(f"[session_memory_commit] Committed {count} important events to YML for {agent_id}")
    return 0

if __name__ == "__main__":
    session_id = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("CLAUDE_SESSION_ID", "unknown")
    agent_id = sys.argv[2] if len(sys.argv) > 2 else "ceo"
    sys.exit(main(session_id, agent_id))
```

### Deliverable 3: Wire into governance_boot.sh + session close

**governance_boot.sh** 加 STEP 8.7:
```bash
# STEP 8.7: YML memory recall — load top-N memories into boot pack (added 2026-04-14)
echo "[8.7/11] YML memory bridge..."
if python3 "$YSTAR_DIR/scripts/session_memory_boot.py" "$AGENT_ID" 20 2>&1; then
  echo "  ✓ YML memory recalled"
else
  echo "  ⚠️ YML memory recall failed (fail-open)"
fi
```

**Session close** — 加 cron 每 30min auto-commit OR hook on Claude Code session end (如 Claude Code 提供 SessionEnd hook):
```
# Every 30min auto-commit YML memory snapshot
*/30 * * * * cd /Users/haotianliu/.openclaw/workspace/ystar-company && /usr/bin/python3 scripts/session_memory_commit.py "$SESSION_ID" ceo >> scripts/.logs/memory_commit.log 2>&1
```

---

## Tests

1. `python3 scripts/session_memory_boot.py ceo 5` — should load 5 events from YML (may be 0 if never committed)
2. `python3 scripts/session_memory_commit.py <session_id> ceo` — should scan CIEU + commit important events
3. Run `governance_boot.sh ceo` — STEP 8.7 应显示 "YML memory recalled"
4. Verify `memory/boot_packages/ceo.json` 含 `category_0_5_yml_memory_recall` block

---

## Acceptance

- `ls scripts/session_memory_boot.py scripts/session_memory_commit.py` 都存在
- `grep "session_memory_boot" scripts/governance_boot.sh` 找得到
- `crontab -l | grep session_memory_commit` 找得到 (或等价 hook)
- Boot 时 CEO 能 read 进 top memories (如果 YML 非空)
- Session 中产生的 DRIFT events 随后会在 YML 里可查

## Commit

- message: "[L4 SHIPPED] feat(yml): session_memory_boot + session_memory_commit + governance_boot STEP 8.7 (last mile)"
- push origin main

## Notes

- Path B-lite: CTO 写 task card (本文件) + CEO 代 spawn Ryan/Leo (下 session 首轮)
- 此 task 完 = YML 真正 operational (从 library 变 system)
- 期望 output: session handoff 不再靠手动 memory/session_handoff.md，靠 YML decay-aware recall 自动

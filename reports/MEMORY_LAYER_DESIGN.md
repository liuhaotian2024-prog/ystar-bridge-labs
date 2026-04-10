# Y* Bridge Labs Memory Layer Design
**Research Mission Report — Kernel Engineer**  
**Date:** 2026-04-10  
**Status:** Design Complete, Ready for Implementation

---

## Executive Summary

Letta (formerly MemGPT) provides robust cross-session memory for AI agents but requires PostgreSQL + pgvector + Docker. For Y* Bridge Labs' Mac mini deployment, this is prohibitively heavy.

This design proposes **Y*gov Memory Layer (YML)** — a lightweight, SQLite-based memory system that integrates natively with Y*gov's governance infrastructure. It provides structured, decay-aware, per-agent memory with full CIEU audit trails.

**Key advantages over Letta:**
- Zero external dependencies (SQLite only)
- Gov-native: memory writes are automatically audited via Y*gov
- Simpler architecture: 300-400 lines vs. Letta's 50k+ LOC
- Optimized for Claude Code's session-per-subagent model
- Direct integration with existing OmissionEngine for memory decay and reminders

**Trade-offs:**
- No semantic search out of the box (can be added via embeddings later)
- No distributed memory (single-machine only)
- No built-in conversation history like Letta's archival storage

---

## 1. Current State Analysis

### 1.1 Existing Memory Infrastructure

**session_handoff.md** (209 lines)
- Human-curated markdown file
- Updated manually by CEO at session end
- Sections: Team Identity, Cases, Timeline, Architecture, Tasks
- **Pain points:**
  - Lossy: agents forget to update it
  - Unstructured: no schema, hard to query
  - No decay: old information never fades
  - No agent-specific views: everyone reads the same global state

**memory/INDEX.md**
- Catalog of memory files
- Currently only tracks session_handoff.md
- Protected by `.ystar_session.json` restricted_write_paths

**.ystar_session.json**
- Session-level config (not memory)
- Contains contract rules, obligation timing, agent scopes
- 148 lines of JSON

**Existing SQLite databases:**
- `.ystar_cieu.db` — CIEU audit records (208KB, actively written)
- `.ystar_omission.db` — Obligation tracking (69KB)
- `.ystar_retro_baseline.db` — Retroactive governance baseline

### 1.2 Y*gov Patterns We Can Reuse

From `ystar/governance/omission_store.py` and `omission_models.py`:

1. **Dual-layer architecture:**
   - `InMemoryOmissionStore` for tests
   - `OmissionStore` (SQLite) for production
   - Same interface, drop-in replacement

2. **Timestamp-based state management:**
   - `created_at`, `updated_at`, `last_event_at`
   - Used for decay and expiration logic

3. **Status state machines:**
   - `EntityStatus`, `ObligationStatus` enums
   - Clear state transitions with validation

4. **CIEU integration:**
   - OmissionEngine writes violations to `.ystar_cieu.db`
   - Provides audit trail for all governance events

5. **Gov-MCP tool pattern:**
   - 14 tools exposed via MCP server (port 7922)
   - Tools like `gov_check`, `gov_delegate`, `gov_escalate`
   - Same pattern can be used for `gov_remember`, `gov_recall`

---

## 2. Design: Y*gov Memory Layer (YML)

### 2.1 Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Claude Code                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   CEO    │  │   CTO    │  │eng-kernel│ ... agents   │
│  │  (Aiden) │  │          │  │          │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │             │                     │
│       └─────────────┴─────────────┘                     │
│                     │                                   │
│              gov_remember / gov_recall / gov_forget     │
│                     │                                   │
└─────────────────────┼───────────────────────────────────┘
                      │
         ┌────────────▼────────────┐
         │   GOV-MCP Server        │
         │   (port 7922)           │
         └────────────┬────────────┘
                      │
    ┌─────────────────┴──────────────────┐
    │                                    │
┌───▼───────────────┐        ┌───────────▼──────────┐
│ MemoryStore       │        │ OmissionEngine       │
│ (.ystar_memory.db)│        │ (.ystar_omission.db) │
│                   │        │                      │
│ - memories        │        │ - memory_obligations │
│ - agents          │◄───────┤ - decay reminders    │
│ - memory_types    │        │ - access violations  │
│ - access_log      │        │                      │
└───────┬───────────┘        └───────────┬──────────┘
        │                                │
        └────────────┬───────────────────┘
                     │
              ┌──────▼──────┐
              │ CIEUStore   │
              │ (audit log) │
              └─────────────┘
```

### 2.2 Database Schema

**File:** `.ystar_memory.db`

```sql
-- Per-agent memory entries
CREATE TABLE memories (
    memory_id         TEXT PRIMARY KEY,
    agent_id          TEXT NOT NULL,           -- 'ceo', 'cto', 'eng-kernel', etc.
    memory_type       TEXT NOT NULL,           -- 'decision', 'knowledge', 'obligation', 'lesson'
    content           TEXT NOT NULL,           -- Structured JSON or plain text
    relevance_score   REAL DEFAULT 1.0,        -- Decay score: 1.0 (fresh) → 0.0 (forgotten)
    context_tags      TEXT DEFAULT '[]',       -- JSON array: ['git', 'deployment', 'bug-fix']
    
    -- Temporal tracking
    created_at        REAL NOT NULL,
    last_accessed_at  REAL,
    access_count      INTEGER DEFAULT 0,
    
    -- Decay parameters
    half_life_days    REAL DEFAULT 30.0,       -- Memory decay half-life
    min_score         REAL DEFAULT 0.1,        -- Score threshold for pruning
    
    -- Reinforcement
    reinforced_by     TEXT,                    -- memory_id that reinforces this
    parent_memory_id  TEXT,                    -- For hierarchical memories
    
    -- Audit
    source_cieu_ref   TEXT,                    -- CIEU record that created this memory
    metadata_json     TEXT DEFAULT '{}'
);

-- Agent registry (for memory quotas and policies)
CREATE TABLE agents (
    agent_id          TEXT PRIMARY KEY,
    display_name      TEXT,
    memory_quota_mb   REAL DEFAULT 10.0,       -- Per-agent memory budget
    retention_policy  TEXT DEFAULT 'standard', -- 'standard', 'extended', 'minimal'
    created_at        REAL NOT NULL,
    last_session_at   REAL,
    session_count     INTEGER DEFAULT 0
);

-- Memory type catalog (defines decay behavior per type)
CREATE TABLE memory_types (
    memory_type       TEXT PRIMARY KEY,
    default_half_life REAL NOT NULL,          -- Days
    description       TEXT,
    schema_json       TEXT                    -- Optional JSON schema for content validation
);

-- Access log (who recalled what, when)
CREATE TABLE access_log (
    access_id         TEXT PRIMARY KEY,
    agent_id          TEXT NOT NULL,
    memory_id         TEXT NOT NULL,
    access_type       TEXT NOT NULL,          -- 'read', 'write', 'reinforce', 'forget'
    ts                REAL NOT NULL,
    cieu_ref          TEXT,                   -- CIEU audit reference
    context           TEXT DEFAULT '{}'       -- Why was this memory accessed?
);

-- Indexes
CREATE INDEX idx_mem_agent       ON memories(agent_id);
CREATE INDEX idx_mem_type        ON memories(memory_type);
CREATE INDEX idx_mem_score       ON memories(relevance_score);
CREATE INDEX idx_mem_created     ON memories(created_at);
CREATE INDEX idx_access_agent    ON access_log(agent_id);
CREATE INDEX idx_access_memory   ON access_log(memory_id);
```

### 2.3 Memory Types

Built-in types (inserted into `memory_types` on init):

| memory_type | half_life_days | description |
|-------------|----------------|-------------|
| `decision` | 90 | Strategic decisions (e.g., "chose SQLite over Postgres") |
| `knowledge` | 60 | Domain knowledge (e.g., "HN posts max 80 chars title") |
| `obligation` | 30 | Pending obligations (e.g., "must push commit after merge") |
| `lesson` | 180 | Learned lessons from Cases (e.g., CASE-001 fabrication) |
| `task_context` | 7 | Short-term task state (e.g., "analyzing bug in prefill.py") |
| `relationship` | 120 | Inter-agent dependencies (e.g., "CTO must notify CEO before merge") |

**Decay formula:**
```python
relevance_score = max(min_score, initial_score * (0.5 ** (days_since_create / half_life_days)))
```

Accessed memories get reinforcement: `access_count++`, `last_accessed_at = now`, and a small relevance boost.

---

## 3. API Design

### 3.1 Gov-MCP Tools

**gov_remember** — Store a memory
```python
{
  "agent_id": "ceo",
  "memory_type": "decision",
  "content": "Decided to use SQLite for memory layer instead of Letta/PostgreSQL. Rationale: Mac mini deployment, zero external deps.",
  "context_tags": ["architecture", "deployment", "dependencies"],
  "half_life_days": 90  # Optional override
}
```
Returns: `memory_id`, `created_at`, audit `cieu_ref`

**gov_recall** — Retrieve memories
```python
{
  "agent_id": "ceo",
  "memory_types": ["decision", "lesson"],  # Optional filter
  "context_tags": ["deployment"],          # Optional filter
  "min_relevance": 0.3,                    # Exclude faded memories
  "limit": 10,
  "sort_by": "relevance_desc"              # or "created_desc", "accessed_desc"
}
```
Returns: List of memory objects with `memory_id`, `content`, `relevance_score`, `created_at`, `access_count`

**gov_forget** — Explicitly delete a memory
```python
{
  "memory_id": "mem_abc123",
  "reason": "Superseded by new decision"
}
```
Returns: Success flag, writes deletion to CIEU for audit.

**gov_memory_summary** — Agent memory health report
```python
{
  "agent_id": "ceo"
}
```
Returns:
```json
{
  "agent_id": "ceo",
  "total_memories": 47,
  "active_memories": 32,   // relevance_score > 0.3
  "memory_quota_mb": 10.0,
  "usage_mb": 2.3,
  "oldest_memory": "2026-03-26",
  "most_accessed": [
    {"memory_id": "...", "content": "...", "access_count": 15}
  ],
  "pending_obligations": 3,
  "fading_memories": [  // relevance_score < 0.4
    {"memory_id": "...", "content": "...", "relevance_score": 0.35}
  ]
}
```

**gov_memory_decay** — Manual decay scan (usually runs automatically)
```python
{
  "prune_threshold": 0.1  // Delete memories below this score
}
```
Returns: Number of memories decayed, number pruned.

**gov_memory_reinforce** — Reinforce a memory (boost relevance)
```python
{
  "memory_id": "mem_abc123",
  "boost_factor": 1.2  // Multiply relevance_score by this
}
```
Use case: CEO sees a recurring mistake, reinforces the relevant lesson memory.

### 3.2 Python API (for kernel-level integration)

```python
from ystar.memory import MemoryStore, Memory

store = MemoryStore(db_path=".ystar_memory.db")

# Store memory
mem = Memory(
    agent_id="cto",
    memory_type="knowledge",
    content="pytest must pass 100% before commit",
    context_tags=["testing", "git"],
    half_life_days=60
)
store.remember(mem)

# Recall memories
results = store.recall(
    agent_id="cto",
    memory_types=["knowledge", "obligation"],
    min_relevance=0.3,
    limit=5
)

# Decay scan
decayed, pruned = store.decay_scan(prune_threshold=0.1)
```

---

## 4. Integration with Y*gov

### 4.1 Memory as Obligations

Memory operations trigger omission obligations:

| Memory Event | Obligation Created | Due Time | Severity |
|--------------|-------------------|----------|----------|
| `gov_remember(type='obligation')` | `MEMORY_FULFILL_REQUIRED` | As specified | medium |
| `gov_recall()` returns fading memory | `MEMORY_REINFORCE_SUGGESTED` | +7 days | low |
| Agent session ends | `SESSION_MEMORY_COMMIT_REQUIRED` | Immediate | high |
| Memory quota exceeded | `MEMORY_PRUNE_REQUIRED` | +1 day | medium |

**Example flow:**
1. CEO uses `gov_remember()` to store "Must publish blog post before 2026-04-15"
2. MemoryStore writes to `.ystar_memory.db`
3. MemoryStore calls `OmissionEngine.ingest_event(GovernanceEvent(type='MEMORY_STORED', ...))`
4. OmissionEngine creates `ObligationRecord(type='MEMORY_FULFILL_REQUIRED', due_at=2026-04-15)`
5. If deadline passes without fulfillment event, OmissionEngine detects violation
6. Violation written to CIEUStore for audit

### 4.2 CIEU Audit Trail

Every memory operation writes to `.ystar_cieu.db`:

```python
{
  "event": "memory.remember",
  "agent_id": "ceo",
  "memory_id": "mem_f4a2",
  "memory_type": "decision",
  "content_hash": "sha256:...",  # For verification
  "timestamp": 1712756400.0,
  "cieu_ref": "cieu_9a8b"
}
```

This enables:
- "Who stored what memory and when?"
- "Did agent X forget an obligation they previously acknowledged?"
- Retroactive audits: "Show me all decisions made in March"

### 4.3 Session Lifecycle Integration

**Session Start (boot protocol):**
```python
# In .claude/tasks/boot.py or session startup
agent_id = detect_current_agent()  # 'ceo', 'cto', etc.
recent_memories = store.recall(
    agent_id=agent_id,
    min_relevance=0.4,
    limit=20,
    sort_by="relevance_desc"
)
# Inject into agent context (e.g., prepend to prompt)
```

**Session End:**
```python
# CEO writes session summary to memory
store.remember(Memory(
    agent_id="ceo",
    memory_type="task_context",
    content=f"Session ended. Pending: {task_list}. Blocker: {blocker}.",
    half_life_days=7
))
```

**Autonomous decay (cron job):**
```bash
# Run every 6 hours
ystar memory-decay --prune-threshold 0.1
```

---

## 5. Comparison with Letta

### 5.1 What Letta Provides

Letta (v0.5+) architecture:
- **PostgreSQL + pgvector**: Semantic search over memories via embeddings
- **Tiered storage**: Working memory (4k tokens) + archival memory (SQL + embeddings)
- **Conversation history**: Automatic storage of full chat transcripts
- **Multi-agent memory sharing**: Agents can share memory pools
- **LLM-driven recall**: Agent decides what to recall via function calls

**Dependencies:**
- PostgreSQL server
- pgvector extension (requires build from source on some platforms)
- Docker (recommended deployment)
- 500+ MB memory footprint
- ~50k LOC Python codebase

### 5.2 What YML Provides

| Feature | Letta | YML | Notes |
|---------|-------|-----|-------|
| **Storage** | PostgreSQL + pgvector | SQLite | YML: zero external deps |
| **Semantic search** | ✅ (via embeddings) | ❌ (v1), ⚠️ (roadmap) | Can add sqlite-vss later |
| **Decay model** | ❌ (manual archival) | ✅ (automatic) | YML: time-based relevance |
| **Gov integration** | ❌ | ✅ (CIEU + OmissionEngine) | YML: memory ops are audited |
| **Per-agent isolation** | ✅ | ✅ | Both support |
| **Memory quotas** | ❌ | ✅ | YML: prevent runaway growth |
| **Conversation history** | ✅ (automatic) | ❌ (manual) | Letta stores full chat logs |
| **Cross-session state** | ✅ | ✅ | Both support |
| **Deployment** | Docker + Postgres | SQLite file | YML: 1 file, no servers |
| **Codebase size** | ~50k LOC | ~300-400 LOC (est.) | YML: minimal surface area |

### 5.3 Trade-offs

**We give up:**
- Semantic search: Can't do "recall memories related to [concept]" without embeddings
- Automatic chat history: Agent must explicitly `gov_remember()` important facts
- Distributed memory: Can't run YML across multiple machines

**We gain:**
- Zero deployment complexity: No Postgres, no Docker
- Gov-native: Memory writes are Y*gov events → full audit trail
- Simpler mental model: Decay happens automatically, no manual archival
- Lightweight: Runs on Mac mini with Ollama without resource contention

### 5.4 When to Choose YML vs. Letta

**Use YML if:**
- Single-machine deployment (like Y* Bridge Labs Mac mini)
- You already use Y*gov and want memory to be governed
- You want automatic decay instead of manual archival
- You need minimal dependencies

**Use Letta if:**
- You need semantic search over large knowledge bases
- You want automatic conversation history storage
- You need distributed multi-agent memory
- You don't mind running PostgreSQL

---

## 6. Implementation Plan

### 6.1 Phase 1: Core Memory Store (Day 1-2)
**Files to create:**
- `ystar/memory/__init__.py`
- `ystar/memory/models.py` — Memory, Agent, MemoryType dataclasses
- `ystar/memory/store.py` — MemoryStore, InMemoryMemoryStore
- `ystar/memory/decay.py` — Decay calculation and pruning logic

**Tests:**
- `tests/test_memory_store.py` — CRUD operations
- `tests/test_memory_decay.py` — Time-based relevance decay

**Acceptance:**
- Can store/retrieve memories by agent_id
- Relevance scores decay correctly based on half_life_days
- Access count increments on recall

### 6.2 Phase 2: Gov-MCP Integration (Day 3)
**Files to create:**
- `gov_mcp/memory_tools.py` — MCP tool definitions

**Add to `gov_mcp/server.py`:**
```python
@server.call_tool()
async def gov_remember(
    agent_id: str,
    memory_type: str,
    content: str,
    context_tags: list[str] | None = None,
    half_life_days: float | None = None
) -> str:
    store = MemoryStore()
    mem = Memory(...)
    store.remember(mem)
    # Write CIEU event
    return json.dumps({"memory_id": mem.memory_id, ...})
```

**Tests:**
- `tests/test_gov_memory_tools.py` — MCP tool invocations

**Acceptance:**
- `gov_remember`, `gov_recall`, `gov_forget` callable via MCP
- CIEU records written for each operation

### 6.3 Phase 3: OmissionEngine Integration (Day 4)
**Files to modify:**
- `ystar/governance/omission_rules.py` — Add memory-related rules

**New obligation types:**
- `MEMORY_FULFILL_REQUIRED` — Memory with due date not fulfilled
- `SESSION_MEMORY_COMMIT_REQUIRED` — Session ending without memory commit

**Tests:**
- `tests/test_memory_obligations.py` — Obligation creation and violation detection

**Acceptance:**
- Memory with `due_at` creates obligation
- Obligation expires if memory not marked fulfilled
- Violation written to CIEUStore

### 6.4 Phase 4: Session Lifecycle Hooks (Day 5)
**Files to create:**
- `scripts/session_memory_boot.py` — Load recent memories at session start
- `scripts/session_memory_commit.py` — Write session summary at end

**Hook into:**
- `.claude/agents/ceo/config.yaml` — Add pre-session hook
- Session end workflow (manual for now, auto later)

**Tests:**
- End-to-end: Start session → recall memories → do work → commit → end → start new session → verify recall

**Acceptance:**
- Agent can retrieve memories from previous session
- Session summary stored as memory

### 6.5 Phase 5: CLI and Monitoring (Day 6)
**Files to create:**
- `ystar/cli/memory_cmd.py` — CLI commands

**Commands:**
```bash
ystar memory recall ceo --type decision --limit 5
ystar memory decay --prune-threshold 0.1
ystar memory summary ceo
ystar memory init  # Initialize .ystar_memory.db
```

**Tests:**
- CLI invocation tests

**Acceptance:**
- Board can inspect agent memory via CLI
- Decay can be run manually for debugging

---

## 7. Code Sketches

### 7.1 Core Models (`ystar/memory/models.py`)

```python
from __future__ import annotations
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Memory:
    """Single memory entry."""
    memory_id: str = field(default_factory=lambda: f"mem_{uuid.uuid4().hex[:8]}")
    agent_id: str = ""
    memory_type: str = "knowledge"
    content: str = ""
    relevance_score: float = 1.0
    context_tags: list[str] = field(default_factory=list)
    
    created_at: float = field(default_factory=time.time)
    last_accessed_at: Optional[float] = None
    access_count: int = 0
    
    half_life_days: float = 30.0
    min_score: float = 0.1
    
    reinforced_by: Optional[str] = None
    parent_memory_id: Optional[str] = None
    
    source_cieu_ref: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def compute_relevance(self, now: float) -> float:
        """Decay relevance based on age."""
        age_days = (now - self.created_at) / 86400.0
        decay_factor = 0.5 ** (age_days / self.half_life_days)
        return max(self.min_score, self.relevance_score * decay_factor)

@dataclass
class Agent:
    """Agent metadata for memory management."""
    agent_id: str
    display_name: str = ""
    memory_quota_mb: float = 10.0
    retention_policy: str = "standard"
    created_at: float = field(default_factory=time.time)
    last_session_at: Optional[float] = None
    session_count: int = 0

@dataclass
class MemoryType:
    """Memory type definition."""
    memory_type: str
    default_half_life: float  # days
    description: str = ""
    schema_json: Optional[str] = None
```

### 7.2 Store Interface (`ystar/memory/store.py`)

```python
from __future__ import annotations
import json
import sqlite3
import time
from pathlib import Path
from typing import Optional
from .models import Memory, Agent, MemoryType

class MemoryStore:
    """SQLite-backed memory store."""
    
    def __init__(self, db_path: str = ".ystar_memory.db"):
        self.db_path = db_path
        self._init_schema()
    
    def _init_schema(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA_SQL)  # From schema in section 2.2
            self._seed_memory_types(conn)
    
    def _conn(self):
        return sqlite3.connect(self.db_path)
    
    def remember(self, mem: Memory) -> str:
        """Store a memory."""
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO memories (
                    memory_id, agent_id, memory_type, content,
                    relevance_score, context_tags, created_at,
                    half_life_days, min_score, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mem.memory_id, mem.agent_id, mem.memory_type, mem.content,
                mem.relevance_score, json.dumps(mem.context_tags), mem.created_at,
                mem.half_life_days, mem.min_score, json.dumps(mem.metadata)
            ))
            # Log access
            self._log_access(conn, mem.agent_id, mem.memory_id, "write")
        return mem.memory_id
    
    def recall(
        self,
        agent_id: str,
        memory_types: Optional[list[str]] = None,
        context_tags: Optional[list[str]] = None,
        min_relevance: float = 0.3,
        limit: int = 10,
        sort_by: str = "relevance_desc"
    ) -> list[Memory]:
        """Retrieve memories with filtering."""
        now = time.time()
        filters = ["agent_id = ?"]
        params = [agent_id]
        
        if memory_types:
            filters.append(f"memory_type IN ({','.join('?' * len(memory_types))})")
            params.extend(memory_types)
        
        # TODO: context_tags filtering (requires JSON query)
        
        query = f"SELECT * FROM memories WHERE {' AND '.join(filters)}"
        
        with self._conn() as conn:
            rows = conn.execute(query, params).fetchall()
            memories = [self._row_to_memory(r) for r in rows]
            
            # Compute current relevance and filter
            memories = [
                m for m in memories 
                if m.compute_relevance(now) >= min_relevance
            ]
            
            # Sort
            if sort_by == "relevance_desc":
                memories.sort(key=lambda m: m.compute_relevance(now), reverse=True)
            elif sort_by == "created_desc":
                memories.sort(key=lambda m: m.created_at, reverse=True)
            
            # Update access stats
            for mem in memories[:limit]:
                self._update_access(conn, mem.memory_id)
                self._log_access(conn, agent_id, mem.memory_id, "read")
            
            return memories[:limit]
    
    def forget(self, memory_id: str, reason: str = "") -> bool:
        """Delete a memory."""
        with self._conn() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
            if cursor.rowcount > 0:
                self._log_access(conn, "system", memory_id, "forget", {"reason": reason})
                return True
        return False
    
    def decay_scan(self, prune_threshold: float = 0.1) -> tuple[int, int]:
        """Scan all memories, decay relevance, prune below threshold."""
        now = time.time()
        decayed = 0
        pruned = 0
        
        with self._conn() as conn:
            rows = conn.execute("SELECT memory_id, relevance_score, created_at, half_life_days, min_score FROM memories").fetchall()
            
            for memory_id, score, created_at, half_life, min_score in rows:
                age_days = (now - created_at) / 86400.0
                decay_factor = 0.5 ** (age_days / half_life)
                new_score = max(min_score, score * decay_factor)
                
                if new_score < prune_threshold:
                    conn.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
                    pruned += 1
                elif new_score != score:
                    conn.execute("UPDATE memories SET relevance_score = ? WHERE memory_id = ?", (new_score, memory_id))
                    decayed += 1
        
        return decayed, pruned
    
    def _log_access(self, conn, agent_id: str, memory_id: str, access_type: str, context: dict = None):
        conn.execute("""
            INSERT INTO access_log (access_id, agent_id, memory_id, access_type, ts, context)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (f"acc_{uuid.uuid4().hex[:8]}", agent_id, memory_id, access_type, time.time(), json.dumps(context or {})))
    
    def _update_access(self, conn, memory_id: str):
        conn.execute("""
            UPDATE memories 
            SET access_count = access_count + 1, last_accessed_at = ?
            WHERE memory_id = ?
        """, (time.time(), memory_id))
    
    def _row_to_memory(self, row) -> Memory:
        # SQLite row tuple → Memory object
        # Implementation depends on column order from schema
        pass
```

### 7.3 Gov-MCP Tool (`gov_mcp/memory_tools.py`)

```python
from ystar.memory.store import MemoryStore
from ystar.memory.models import Memory
import json

def gov_remember(
    agent_id: str,
    memory_type: str,
    content: str,
    context_tags: list[str] | None = None,
    half_life_days: float | None = None
) -> str:
    """Store a memory and return memory_id."""
    store = MemoryStore()
    mem = Memory(
        agent_id=agent_id,
        memory_type=memory_type,
        content=content,
        context_tags=context_tags or [],
        half_life_days=half_life_days or 30.0
    )
    memory_id = store.remember(mem)
    
    # TODO: Write CIEU event
    # cieu_store.add_event(CIEUEvent(type="memory.remember", ...))
    
    return json.dumps({
        "memory_id": memory_id,
        "agent_id": agent_id,
        "created_at": mem.created_at
    })

def gov_recall(
    agent_id: str,
    memory_types: list[str] | None = None,
    min_relevance: float = 0.3,
    limit: int = 10
) -> str:
    """Retrieve memories for an agent."""
    store = MemoryStore()
    memories = store.recall(
        agent_id=agent_id,
        memory_types=memory_types,
        min_relevance=min_relevance,
        limit=limit
    )
    
    return json.dumps([{
        "memory_id": m.memory_id,
        "memory_type": m.memory_type,
        "content": m.content,
        "relevance_score": m.compute_relevance(time.time()),
        "created_at": m.created_at,
        "access_count": m.access_count
    } for m in memories])
```

---

## 8. Roadmap: Future Enhancements

### 8.1 Semantic Search (Phase 6)
- Add `embeddings` column to `memories` table
- Use `sqlite-vss` extension for vector search
- Generate embeddings via Ollama's `nomic-embed-text` model
- API: `gov_recall_semantic(query="deployment architecture", limit=5)`

### 8.2 Memory Graphs (Phase 7)
- Add `memory_edges` table for relationship tracking
- Types: `reinforces`, `contradicts`, `supersedes`, `depends_on`
- API: `gov_memory_graph(memory_id)` returns connected memories

### 8.3 Cross-Agent Memory Sharing (Phase 8)
- Add `shared_memories` table with ACL
- CTO can mark memory as "share with eng-kernel, eng-platform"
- Enforced by Y*gov contract: `only_agents: ["cto", "eng-kernel"]`

### 8.4 Memory Compression (Phase 9)
- Periodically summarize old, low-relevance memories
- Use LLM to generate compressed versions
- Store original in archive table, replace active with summary

---

## 9. Risk Analysis

### 9.1 Technical Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| SQLite file corruption | Medium | Regular backups, write-ahead logging (WAL mode) |
| Memory quota overflow | Low | Enforce quota in `gov_remember()`, auto-prune on quota hit |
| Decay parameter tuning | Low | Provide CLI tools for experimentation, document best practices |
| Context tag explosion | Low | Normalize tags, provide tag management tools |

### 9.2 Operational Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Agents forget to commit memory | High | OmissionEngine obligation on session end |
| Memory becomes stale | Medium | Automatic decay + reminder obligations for fading critical memories |
| Over-reliance on memory | Medium | Document when to use memory vs. files (e.g., code = files, context = memory) |

### 9.3 Gov-Specific Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Memory write bypasses gov_check | High | All writes go through gov-mcp tools, which enforce contracts |
| CIEU audit log out of sync | Medium | Atomic writes: memory + CIEU event in same transaction |
| Obligation spam from memory | Low | Throttle obligation creation, consolidate similar obligations |

---

## 10. Success Metrics

After deployment, measure:
1. **Cross-session recall rate**: % of sessions where agent successfully recalls prior context
2. **Memory decay accuracy**: Do faded memories match actual irrelevance?
3. **Quota compliance**: Are agents staying within memory budgets?
4. **CIEU coverage**: Are all memory ops audited?
5. **Performance**: Memory recall latency (target: <50ms for 100 memories)

Target: 90%+ cross-session recall, 100% CIEU coverage, <5% memory quota violations.

---

## 11. Board Decision Point

**Recommendation:** Proceed with YML implementation.

**Rationale:**
- Letta is too heavy for Mac mini deployment (PostgreSQL + Docker)
- YML provides 80% of Letta's value with 5% of the complexity
- Gov integration gives us unique audit trail capabilities
- Can always add semantic search later via sqlite-vss

**Estimated effort:** 6 engineering days (kernel engineer)

**Alternatives considered:**
1. Stay with markdown files → Rejected (too lossy, no structure)
2. Use Letta → Rejected (deployment complexity)
3. Build custom Postgres layer → Rejected (not lightweight enough)

**Next step:** Board approval → kernel engineer implements Phase 1-3 → iterate.

---

## Appendix A: File Paths

All code referenced in this design:

**New files to create:**
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/memory/__init__.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/memory/models.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/memory/store.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/memory/decay.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/gov_mcp/memory_tools.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/cli/memory_cmd.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/test_memory_store.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/test_memory_decay.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/test_gov_memory_tools.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/test_memory_obligations.py`

**Existing files referenced:**
- `/Users/haotianliu/.openclaw/workspace/ystar-company/memory/session_handoff.md`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/memory/INDEX.md`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_omission.db`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/omission_models.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/omission_store.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/omission_engine.py`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/gov_mcp/server.py`

---

**End of Design Document**

# Y* Bridge Labs Hybrid Architecture: OpenClaw + Claude Code
**Author:** CTO Ethan Wright
**Date:** 2026-04-11
**Status:** Architecture Proposal — Ready for CEO Review

---

## 1. Problem Statement

Claude Code (Opus) sessions restart frequently. Every restart = full amnesia. Current mitigations (session_handoff.md, continuation.json, governance_boot.sh) help, but:

- **continuation.json stales** — only updated at session close, not continuously
- **No one watches between sessions** — obligations go untracked, CIEU unaudited
- **Boot takes too long** — reading all state files, re-running daemons, 7-step verification
- **CSO intel protocol never executes** — protocol exists but no persistent executor
- **Board gets no alerts** — problems sit until next human check-in

The root cause: Claude Code is **ephemeral**. We need a **persistent** layer.

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Board (Haotian)                       │
│                    Telegram + CLI                        │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
     ┌───────▼──────────┐       ┌────────▼────────────┐
     │  OpenClaw / JinJin │       │  Claude Code / Opus  │
     │  (Persistent)     │◄─────►│  (Ephemeral)         │
     │                   │ files │                      │
     │  MiniMax M2.7     │       │  Opus 4.6 (1M ctx)   │
     │  LaunchAgent      │       │  Manual sessions      │
     │  24/7 daemon      │       │  High-cognition tasks │
     └───────────────────┘       └──────────────────────┘
             │
     Shared Workspace:
     /Users/haotianliu/.openclaw/workspace/ystar-company/
```

**Communication channel:** Shared filesystem (same directory). Both read/write to the same workspace. No extra infra needed.

---

## 3. What OpenClaw/JinJin Can Do (Verified)

### 3.1 Runtime Capabilities

| Capability | Status | Evidence |
|-----------|--------|---------|
| **24/7 daemon** | Running | LaunchAgent `ai.openclaw.gateway.plist`, confirmed via `openclaw daemon status` |
| **Cron scheduler** | Available | `openclaw cron add --every 10m --message "..."` — built-in, no extra infra |
| **Agent turns** | Available | `openclaw agent --message "..."` — programmatic agent invocation |
| **Telegram delivery** | Connected | Channel configured in openclaw.json, bot @K9newclaw_bot |
| **Discord delivery** | Configured | Token present, currently disabled |
| **File read/write** | Yes | Workspace is shared, AGENTS.md grants `file read/write, shell commands` |
| **Shell commands** | Yes | Permitted in AGENTS.md |
| **Web search** | Yes | Skill available (ai-news-oracle equivalent) |
| **Browser automation** | Yes | Permitted in AGENTS.md |
| **MiniMax M2.7 reasoning** | Yes | 200K context, reasoning-capable, $0.30/$1.20 per M tokens |
| **Ollama local models** | Yes | ystar-gemma, gemma4:e4b (free, 128K context) |
| **Direct API (no Telegram)** | Yes | `JinjinClient` in scripts/jinjin_client.py — 12s latency via OpenClaw gateway |

### 3.2 Scheduling Infrastructure

OpenClaw has a **native cron system** (`openclaw cron`) that runs jobs through the gateway:

```bash
# Example: run every 10 minutes
openclaw cron add --name "obligation-scan" --every 10m \
  --message "Scan .ystar_omission.db for overdue obligations. Report via Telegram if any found." \
  --agent main --timeout-seconds 120

# Example: run at specific times
openclaw cron add --name "daily-intel" --cron "0 7 * * *" --tz "America/New_York" \
  --message "Execute CSO intel protocol: scan arxiv, GitHub trending, HN, competitor updates." \
  --agent main --timeout-seconds 300

# One-shot with delivery
openclaw cron add --name "health-check" --every 30m \
  --message "Run: bash scripts/governance_boot.sh --verify-only. If FAILURES > 0, alert via Telegram." \
  --agent main --announce --channel telegram
```

### 3.3 Database Access

All three SQLite databases are in the shared workspace:

| Database | Path | JinJin Access |
|----------|------|--------------|
| `.ystar_memory.db` | Workspace root | Read/write via shell (sqlite3 CLI or Python) |
| `.ystar_cieu.db` | Workspace root | Read/write via shell |
| `.ystar_omission.db` | Workspace root | Read/write via shell |

JinJin can run `sqlite3 .ystar_cieu.db "SELECT * FROM ..."` or use Python scripts already in `scripts/`.

### 3.4 Gov-MCP Access

Gov-MCP is at `/Users/haotianliu/.openclaw/workspace/gov-mcp/`. JinJin **cannot** call MCP tools directly (MCP is a Claude Code protocol). However, JinJin can:

1. Run gov-mcp's Python code directly: `python3 -m gov_mcp.gov_check ...`
2. Use the CLI wrappers in `scripts/` that already exist
3. Read/write the same governance state files gov-mcp uses

This is sufficient for monitoring. Gov-MCP's enforcement tools are primarily needed during Claude Code execution anyway.

---

## 4. Responsibility Matrix

| Responsibility | Owner | Method | Rationale |
|---------------|-------|--------|-----------|
| **Write code** | Claude Code | Direct coding | Opus cognition required |
| **Write articles/content** | Claude Code | Direct writing | Opus quality required |
| **Strategic decisions** | Claude Code (CEO) | Read state -> decide -> execute | Opus reasoning required |
| **Architecture design** | Claude Code (CTO) | Analysis + design | Opus depth required |
| **Maintain continuation.json** | JinJin | Cron every 15min: check file ages, rebuild if stale | Persistent = always fresh |
| **Obligation tracking** | JinJin | Cron every 10min: scan omission.db, alert on overdue | Persistent = nothing missed |
| **CSO intel scanning** | JinJin | Cron daily 07:00: execute CSO_INTEL_PROTOCOL.md | MiniMax + web search sufficient |
| **Health monitoring** | JinJin | Cron every 30min: governance_boot.sh --verify-only | Persistent = continuous watch |
| **Board notifications** | JinJin | Telegram on any alert | Already connected |
| **Session bridge** | JinJin | Detect session end -> update continuation.json -> write bridge file | Persistent memory = no amnesia |
| **CIEU audit summary** | JinJin | Cron daily 21:00: summarize day's CIEU entries | MiniMax reasoning sufficient |
| **Competitor monitoring** | JinJin | Cron daily: GitHub trending + HN scan | Web search skill sufficient |

---

## 5. Session Bridge Protocol (Core Innovation)

This is the key mechanism that solves the amnesia problem.

### 5.1 When Claude Code Session Ends

JinJin detects session end via cron check:
```
Every 5 minutes:
  1. Check if scripts/.session_booted exists
  2. If it disappeared since last check -> session ended
  3. Run: python3 scripts/session_close_yml.py auto "Session ended (detected by JinJin)"
  4. Regenerate memory/continuation.json from latest DB state
  5. Write memory/bridge_status.json with timestamp
```

### 5.2 When Claude Code Session Starts

Claude Code's existing governance_boot.sh already reads continuation.json. The only change needed:

```bash
# Add to governance_boot.sh Step 2:
if [ -f "$YSTAR_DIR/memory/bridge_status.json" ]; then
  echo "[BRIDGE] JinJin last updated state at: $(jq -r '.last_update' $YSTAR_DIR/memory/bridge_status.json)"
  echo "[BRIDGE] State freshness: $(jq -r '.freshness' $YSTAR_DIR/memory/bridge_status.json)"
fi
```

### 5.3 bridge_status.json Schema

```json
{
  "last_update": "2026-04-11T23:15:00Z",
  "freshness": "2 minutes ago",
  "session_detected_end": "2026-04-11T23:10:00Z",
  "continuation_rebuilt": true,
  "obligations_overdue": 2,
  "cieu_entries_since_last_session": 47,
  "alerts_sent": ["obligation_overdue_pypi_release"],
  "intel_last_run": "2026-04-11T07:00:00Z",
  "health_last_check": "2026-04-11T23:00:00Z",
  "health_status": "ALL_SYSTEMS_GO"
}
```

---

## 6. Pain Points Solved

| Pain Point (Today) | Root Cause | Hybrid Solution |
|-------------------|-----------|----------------|
| Claude Code restarts -> full amnesia | Ephemeral sessions, stale continuation.json | JinJin keeps continuation.json fresh every 15min. On restart, state is at most 15min old. |
| CEO loses context every boot | Boot reads stale handoff, misses recent work | bridge_status.json tells CEO exactly what happened since last session, maintained by JinJin. |
| Nobody monitors between sessions | No persistent process | JinJin daemon runs 24/7. Cron jobs scan obligations, health, intel continuously. |
| CSO intel protocol never executes | Needs human to trigger, Claude Code too busy | JinJin cron runs it daily at 07:00. MiniMax + web search = sufficient for scanning. |
| Overdue obligations go unnoticed | Only checked during boot | JinJin scans every 10min, Telegram alerts Board on overdue items. |
| Health degradation undetected | governance_boot.sh only runs at session start | JinJin runs --verify-only every 30min, alerts on failures. |
| Board has no visibility between sessions | Board only sees when Claude Code is active | JinJin sends daily digest + real-time alerts via Telegram. |

---

## 7. Communication Mechanisms

### 7.1 File System (Primary — Already Working)

Both agents share `/Users/haotianliu/.openclaw/workspace/ystar-company/`. Communication files:

| File | Writer | Reader | Purpose |
|------|--------|--------|---------|
| `memory/continuation.json` | JinJin (cron) | Claude Code (boot) | Structured state for session recovery |
| `memory/bridge_status.json` | JinJin (cron) | Claude Code (boot) | What happened between sessions |
| `memory/session_handoff.md` | Claude Code (close) | Claude Code (boot) | Human-readable session summary |
| `.ystar_memory.db` | Both | Both | YML memory store |
| `.ystar_cieu.db` | Claude Code (primary) | JinJin (audit) | CIEU audit records |
| `.ystar_omission.db` | Claude Code (primary) | JinJin (scan) | Obligation tracking |
| `reports/intel/daily/` | JinJin | Claude Code (CEO/CSO) | Daily intel reports |
| `scripts/.session_booted` | Claude Code | JinJin (watch) | Session alive signal |

### 7.2 JinjinClient (Direct API — Already Built)

`scripts/jinjin_client.py` enables Claude Code to query JinJin directly:

```python
from scripts.jinjin_client import JinjinClient
jj = JinjinClient()
response = jj.ask("What's the current obligation status?")
```

Latency: ~12 seconds. Uses OpenClaw gateway at 127.0.0.1:18789. No Telegram needed.

### 7.3 Telegram (Board Notifications)

JinJin -> Board: Telegram @K9newclaw_bot (already configured)
Claude Code -> JinJin: `scripts/telegram_bridge.py` (already built, but JinjinClient is faster)

---

## 8. Implementation Plan

### Phase 1: Core Daemon (2-3 hours)

Create 5 OpenClaw cron jobs. Zero code changes, just configuration:

```bash
# 1. Session watchdog — detect session end, rebuild continuation
openclaw cron add --name "session-watchdog" --every 5m \
  --message "Check if scripts/.session_booted exists in /Users/haotianliu/.openclaw/workspace/ystar-company/. If it disappeared, run: cd /Users/haotianliu/.openclaw/workspace/ystar-company && python3 scripts/session_close_yml.py auto 'Session ended (JinJin detected)'. Then report status." \
  --agent main --timeout-seconds 120

# 2. Obligation scanner
openclaw cron add --name "obligation-scan" --every 10m \
  --message "Run: cd /Users/haotianliu/.openclaw/workspace/ystar-company && sqlite3 .ystar_omission.db 'SELECT content, created_at FROM obligations ORDER BY created_at DESC LIMIT 20'. Check for P0 items. If any look overdue, send alert via Telegram to Board." \
  --agent main --timeout-seconds 60

# 3. Health monitor
openclaw cron add --name "health-monitor" --every 30m \
  --message "Run: bash /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/governance_boot.sh --verify-only. Report result. If FAILURES > 0, alert via Telegram." \
  --agent main --timeout-seconds 120

# 4. Daily intel scan (CSO protocol)
openclaw cron add --name "daily-intel" --cron "0 7 * * *" --tz "America/New_York" \
  --message "Execute CSO intel protocol. Search for: AI governance news, AI agent security incidents, competitor updates (Lakera, NeMo Guardrails, Microsoft AGT). Write findings to /Users/haotianliu/.openclaw/workspace/ystar-company/reports/intel/daily/$(date +%%Y-%%m-%%d).md. Send TOP 5 items via Telegram." \
  --agent main --timeout-seconds 600

# 5. Daily CIEU digest
openclaw cron add --name "cieu-digest" --cron "0 21 * * *" --tz "America/New_York" \
  --message "Run: cd /Users/haotianliu/.openclaw/workspace/ystar-company && sqlite3 .ystar_cieu.db \"SELECT agent_id, action, timestamp FROM cieu WHERE date(timestamp, 'unixepoch') = date('now') ORDER BY timestamp DESC LIMIT 50\". Summarize today's governance activity. Write summary to reports/daily/cieu_digest.md." \
  --agent main --timeout-seconds 120
```

### Phase 2: Bridge Enhancement (1-2 hours)

1. **Create `scripts/jinjin_bridge.py`** — Python script JinJin runs to rebuild continuation.json from DB state (reuse logic from `session_close_yml.py::generate_continuation`)
2. **Create `memory/bridge_status.json`** — schema as defined in Section 5.3
3. **Patch `governance_boot.sh`** — add 3 lines to read bridge_status.json during boot

### Phase 3: Feedback Loop (1 hour)

1. **JinJin -> Claude Code task queue** — JinJin writes `memory/jinjin_inbox.json` with discovered items (overdue obligations, intel findings, health alerts). Claude Code reads this during boot and adds to action queue.
2. **Claude Code -> JinJin directives** — Claude Code writes `memory/jinjin_directives.json` with ad-hoc requests. JinJin picks up on next cron cycle.

### Total Implementation: ~4-6 hours

| Phase | Work | Time | Can Start Today? |
|-------|------|------|-----------------|
| Phase 1 | 5 cron commands | 2-3h | Yes — just CLI commands |
| Phase 2 | 1 Python script + 2 file schemas + 3-line patch | 1-2h | Yes |
| Phase 3 | 2 JSON schemas + convention doc | 1h | Yes |

---

## 9. Cost Analysis

| Component | Cost | Notes |
|-----------|------|-------|
| OpenClaw gateway | $0 | Already running as LaunchAgent |
| MiniMax M2.7 | ~$0.05/day | 5 cron jobs, ~50 agent turns/day, mostly cache hits |
| Claude Code (Opus) | $0 | Max subscription, already paying |
| Ollama (Gemma) | $0 | Local, free |
| Telegram | $0 | Free |
| **Total extra cost** | **~$1.50/month** | Effectively zero |

MiniMax M2.7 pricing: $0.30/M input, $1.20/M output. At ~2K tokens per cron turn, 50 turns/day = ~100K tokens/day = $0.03 input + $0.12 output = $0.15/day worst case. With cache hits, likely under $0.05/day.

If cost is a concern, swap to **Ollama ystar-gemma** for monitoring jobs (literally $0). Reserve MiniMax for intel scanning where web search quality matters.

---

## 10. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| JinJin hallucinates DB state | Medium | Cron messages include exact shell commands — JinJin executes, doesn't guess |
| Two agents write same file simultaneously | Low | Convention: JinJin owns bridge_status.json + intel reports. Claude Code owns handoff + CIEU. Clear ownership. |
| OpenClaw gateway crashes | Low | LaunchAgent auto-restarts. Also: `openclaw daemon status` in health check. |
| MiniMax API outage | Low | Fallback to Ollama gemma4:e4b (local, free, 128K context). Configure in models.json. |
| JinJin misinterprets cron message | Medium | Keep cron messages as explicit shell commands, not natural language requests |

---

## 11. Architecture Principles

1. **JinJin monitors, Claude Code decides.** JinJin's job is to watch, scan, alert, and maintain state. Strategic decisions remain with Opus-powered agents.

2. **File system is the API.** No new protocols. Both agents already share the workspace. JSON files with clear schemas are the contract.

3. **Explicit shell commands in cron messages.** Don't ask JinJin to "figure out" what to do. Give exact commands. JinJin's MiniMax brain interprets the output and decides what to alert on.

4. **Graceful degradation.** If JinJin is down, Claude Code still works normally (current behavior). JinJin is additive, not a dependency.

5. **Zero new infrastructure.** OpenClaw daemon already runs. Telegram already connected. Workspace already shared. We're wiring existing pieces together.

---

## 12. Next Steps (Recommended Sequence)

1. **CEO approves architecture** — this document
2. **CTO implements Phase 1** — 5 `openclaw cron add` commands (can do right now)
3. **Verify cron jobs running** — `openclaw cron list` + `openclaw cron runs`
4. **CTO implements Phase 2** — jinjin_bridge.py + governance_boot.sh patch
5. **Test session bridge** — deliberately restart Claude Code, verify JinJin detects it and rebuilds state
6. **CTO implements Phase 3** — inbox/directives JSON convention
7. **Run for 48 hours** — observe, tune cron intervals, fix edge cases
8. **Board review** — present results with actual CIEU evidence

---

## Appendix A: OpenClaw Capability Summary

From `/Users/haotianliu/.openclaw/openclaw.json` and `models.json`:

- **Gateway:** Local, port 18789, token-authenticated
- **Primary model:** MiniMax M2.5 (default), M2.7 available (reasoning-capable)
- **Local models:** ystar-gemma (fine-tuned), gemma4:e4b (base) — both free via Ollama
- **Codex models:** GPT-5.4, GPT-5.4-Mini, GPT-5.2 — available but $0 (likely subscription)
- **Channels:** Telegram (enabled), Discord (configured, disabled)
- **Skills:** 29/66 ready, includes web search, browser, shell, file ops
- **Cron:** Native scheduler, supports `--every`, `--cron`, `--at`, with agent message delivery
- **ClawFlows:** Multi-skill automation framework (capability-based, portable)
- **Max concurrency:** 4 agents, 8 subagents

## Appendix B: Existing Infrastructure We Leverage

| Component | Path | Status |
|-----------|------|--------|
| OpenClaw daemon | LaunchAgent | Running |
| JinjinClient | scripts/jinjin_client.py | Built, 12s latency |
| Telegram bridge | scripts/telegram_bridge.py | Built |
| Session close script | scripts/session_close_yml.py | Built, generates continuation.json |
| Governance boot | scripts/governance_boot.sh | Built, supports --verify-only |
| CSO intel protocol | governance/CSO_INTEL_PROTOCOL.md | Written, never executed |
| Obligation checker | scripts/check_obligations.py | Built |
| CIEU database | .ystar_cieu.db | Active |
| Memory database | .ystar_memory.db | Active |
| Omission database | .ystar_omission.db | Active |
| Gov-MCP server | /Users/haotianliu/.openclaw/workspace/gov-mcp/ | Built |

**Key insight:** Almost everything is already built. We're missing the glue — 5 cron jobs and 1 bridge script.

---
Y_star: "Board proposal (K9 always-watch CIEU + QA gate) gets a technically sound CTO opinion with empirical data"
Xt: "465 MB CIEU DB, 711K events, 52 events/min peak, 10 cieu_brain_daemon processes live, K9 audit runs daily"
U: "Gather empirical data, analyze feasibility, write focused opinion memo"
Yt_plus_1: "Memo delivered with single recommendation, Board can decide"
Rt_plus_1: "0 — memo complete, evidence-backed, single recommendation given"
tool_uses: 11
---

# CTO Opinion: K9 Always-Watches-CIEU + CIEU QA Gate

**From**: Ethan Wright, CTO  
**To**: Board (Haotian Liu), CC: Aiden (CEO)  
**Date**: 2026-04-23  
**Re**: Board proposal — K9 continuous CIEU monitoring + sub-task completion CIEU check as QA standard

## My Recommendation

**YES, but narrow scope: implement the QA gate (CIEU check at sub-task completion) immediately. Do NOT implement continuous K9 scan — the existing daemon fleet already covers that ground, and adding a hot-loop reader to a 465 MB SQLite database under concurrent write from 10 daemon processes will create I/O contention that degrades the very audit trail it is supposed to protect.**

## 1. Empirical State of CIEU Infrastructure

| Metric | Value | Source |
|--------|-------|--------|
| `.ystar_cieu.db` file size | **465 MB** | `ls -lh` |
| Total events | **711,650** | `SELECT COUNT(*)` |
| Average bytes per event | **685 bytes** | computed |
| Average write rate (13.8-day span) | **2,145 events/hour** | epoch range |
| Last-hour write rate | **3,122 events** (52/min) | epoch query |
| Active `cieu_brain_daemon` processes | **10** | `ps aux` |
| DB age | **13.8 days** | min/max `created_at` |
| Projected size at 30 days | **~1 GB** | linear extrapolation |

The database is already substantial. At current trajectory it will cross 1 GB within a month. SQLite handles this fine for append-only writes, but adding a continuous reader that scans recent events on a hot loop fundamentally changes the I/O profile.

## 2. "K9 Watches Always" — Technical Cost

The proposal's continuous monitoring component would require K9 to poll or subscribe to CIEU events in near-real-time. With 10 concurrent `cieu_brain_daemon` writers already holding WAL locks, a new persistent reader creates three problems:

**WAL checkpoint contention.** SQLite WAL mode allows concurrent reads and writes, but WAL checkpointing (merging WAL back into main DB) requires no active readers. A continuous K9 reader would delay WAL checkpoints, causing the WAL file to grow unbounded. The `.ystar_cieu.db-wal` file is already actively written — I observed the `-shm` and `-wal` files in dirty state in git status. A never-closing reader could push WAL past hundreds of MB, degrading all 10 daemon writers.

**Duplicate coverage.** The 10 `cieu_brain_daemon` processes already ingest CIEU events per-agent into brain databases. The `aiden_dream_production.py` does hourly synthesis. The daily `k9_repo_audit.py` does forensic scans. A continuous K9 watcher would be the fourth layer reading the same event stream. The incremental value over what cieu_brain_daemon already captures is marginal — the daemons already see every event within seconds.

**Blast radius ambiguity.** When K9 detects something in real-time, what happens? Today K9 audit writes a report file. Real-time detection implies real-time action: block the agent? Emit a warning event (which itself writes to the same CIEU DB, creating write amplification)? Alert a human who is AFK? Without a clear action path, continuous monitoring generates noise that nobody consumes.

## 3. "CIEU QA Gate at Sub-Task Completion" — This Part Is Sound

The second half of the proposal — every sub-task completion checks CIEU as a QA standard — is technically cheap and operationally valuable. Here is why:

- A single `SELECT COUNT(*) FROM cieu_events WHERE session_id = ? AND agent_id = ? AND created_at > ? AND passed = 0` per sub-task completion costs < 5 ms on a 465 MB database with proper indexing. Even at 50 dispatches/day, that is 250 ms total.
- For nested sub-tasks (sub-agent spawning sub-agent), the query scopes naturally by `session_id` + `agent_id` + time window. No explosion.
- This fills a real gap: today sub-agents self-report Rt+1=0, but nobody cross-checks that zero violations actually exist in CIEU during their execution window. The "hallucinated receipt" pattern (Ethan CZL-1 incident, per MEMORY.md) proves agents can claim completion while CIEU tells a different story.
- Implementation: one SQL query at sub-agent return, before CEO marks task complete. No daemon, no hot loop, no new process.

## 4. Hidden Risk Aiden Will Not See

**Schema evolution hygiene.** Ryan just encountered a `session_id NOT NULL` constraint violation from a caller that did not populate the field. If K9 itself becomes a CIEU writer (emitting audit events, alerting on detected issues), it becomes subject to the same schema contract that every other writer must obey. Today K9 is read-only against CIEU — it audits from the outside. The moment K9 writes events back (which "always watches + reports in real-time" implies), K9 becomes part of the system it audits. This is the observer-becomes-participant problem. Any future schema migration (adding columns, changing NOT NULL constraints, event_type taxonomy changes) must now coordinate with K9's write path too, multiplying the change coordination surface. Keep K9 as a pure reader of CIEU. Let it report via separate channels (files, logs), not by writing back into the audit database it monitors.

## Summary

| Component | Verdict | Reason |
|-----------|---------|--------|
| Continuous K9 CIEU scan | **NO** | WAL contention with 10 daemon writers, duplicates cieu_brain_daemon coverage, undefined blast radius |
| CIEU QA gate at sub-task completion | **YES** | Cheap (one SQL query), fills hallucinated-receipt gap, scopes naturally |
| K9 writing events back to CIEU | **NO** | Observer-becomes-participant anti-pattern, schema coupling risk |

Ship the QA gate. Skip the always-on watcher. The daemons already watch. What we lack is not detection — it is verification at the moment of claimed completion. That is what the QA gate delivers.

— Ethan Wright, CTO

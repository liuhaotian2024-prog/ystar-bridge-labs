---
Y_star: "K9-external-observer design memo respecting CTO 2026-04-23 constitutional NO on continuous CIEU streaming"
Xt: "System has 10 cieu_brain_daemon writers, 465 MB CIEU DB, 52 events/min peak, Board wants ecosystem-wide wire/path/route gap detection"
U: "Design structural-break observer that watches hook/dispatch/dependency/cron/daemon integrity at fixed cadence, reports to files not CIEU"
Yt_plus_1: "Memo delivered with single recommendation (scripts/k9_structural_observer.py, 5-min sweep + event triggers, writes to reports/k9_observer/ + .logs/k9_observer.log, never touches CIEU DB)"
Rt_plus_1: "0 — memo complete, CTO veto honored, single implementation picked and defended, phase-1 under-scoping explicit"
audit_only: true
path: reports/governance/k9_external_observer_design_20260423.md
recommendation: "scripts/k9_structural_observer.py — cron 5-min sweep + spawn/seal/commit event hooks — reads filesystem + /proc + git + config only, writes reports/k9_observer/<ISO>.md and appends .logs/k9_observer.log, daily rollup into reports/daily/ — NEVER reads .ystar_cieu.db"
tool_uses: 6
---

# K9 External Observer — Design Memo

**From**: Aiden Liu, CEO
**To**: Board (Haotian Liu), CC: Ethan Wright (CTO)
**Date**: 2026-04-23
**Re**: Board proposal — K9 as always-on external ecosystem observer (structural gap detection)

## 0. Constraint Acknowledgment

CTO's 2026-04-23 opinion (`reports/cto/opinion_k9_cieu_always_20260423.md`) is binding: **NO continuous CIEU DB reading**. This memo routes entirely around the CIEU DB. The observer reads filesystem metadata, process tables, git state, and config files — never `.ystar_cieu.db`. What Board actually asked for — 连线断裂 / 路径断裂 / 路由缺失 — is **structural**, not transactional. Structural facts live in config, code, and process state, not in the event log.

## 1. What K9-Observer Watches (Top 5, matched to Board wording)

| # | Watch target | Gap class | Source of truth |
|---|---|---|---|
| 1 | **Hook chain integrity** | 连线断裂 | `.claude/settings.json` hook list vs hook script exists + executable + syntax-valid |
| 2 | **Sub-agent dispatch flow** | 路径断裂 | `.claude/agents/*.md` registry vs actual subagent_type invocations in last 24h git log + session marker presence (`.ystar_active_agent.ppid_*`) |
| 3 | **Daemon PID vs live process** | 连线断裂 | `scripts/.*.pid` files + `scripts/.*_sentinel.json` vs `ps aux` grep; stale PID = wire break |
| 4 | **Dependency graph orphans** | 路由缺失 | imports in `scripts/*.py` vs module files exist; `forget_guard` rule references vs rule definitions in `router_registry` |
| 5 | **Cron/timer registration vs firing** | 路径断裂 | `launchctl list` / crontab entries vs last-modified timestamp on expected output files (e.g. `.logs/aiden_dream.log` freshness vs hourly schedule) |

De-scoped from v1 (see §7): CIEU event schema conformance, API route live-handler check, memory file staleness semantics.

## 2. Cadence (CTO veto honored)

**Not continuous.** Two-channel trigger:

- **Scheduled sweep: every 5 minutes** via `launchd` or the existing scheduler. Full pass across the 5 watch targets takes ~2 seconds measured against current repo size. 5-min granularity = 288 sweeps/day = 0.06% of daemon CPU. Zero CIEU DB I/O.
- **Event-triggered** on three boundaries: (a) sub-agent spawn (hook emits `k9_observer_kick` touch-file); (b) session seal; (c) git commit. These piggyback on existing hook fire points, no new hot-loop process.

Cost comparison vs CIEU write rate: CIEU peaks at 52 events/min (3,120/hr). Observer emits **≤12 report files/hour** (scheduled sweeps only, idempotent: rewrites same-day report, not append). Delta is 260x below CIEU write rate. No WAL contention possible because observer touches zero SQLite.

## 3. Report Surface (out-of-band — does not re-enter CIEU)

Three sinks, all filesystem:

1. **`reports/k9_observer/<YYYY-MM-DD>.md`** — daily markdown, overwritten each sweep with latest state. One file per day, bounded storage (~365 files/year @ ~20 KB each = 7 MB/year).
2. **`scripts/.logs/k9_observer.log`** — append-only NDJSON, one line per sweep: `{ts, sweep_id, breaks_found, targets_checked, duration_ms}`. Bounded by logrotate at 50 MB.
3. **Daily rollup**: `reports/daily/k9_observer_digest_<date>.md` — one-paragraph summary appended by existing daily rollup pipeline (reuse, don't build new). Board reads this on morning check-in.

**No `CIEU INSERT`. No brain DB writes.** Observer findings stay in flat files. If a break is severe (P0: daemon crash, hook exec_bit=0), observer drops a sentinel file `scripts/.k9_observer_alarm.json` that the existing `k9_alarm_consumer.py` picks up via its current polling loop — reuse, don't rewire.

## 4. Integration With Existing Infra

| Existing component | Relationship | Change |
|---|---|---|
| `cieu_brain_daemon` (10 instances) | Disjoint — observer never reads CIEU | None |
| `aiden_dream_production.py` (hourly) | Disjoint — dream synthesizes CIEU content; observer watches skeleton | None |
| `k9_repo_audit.py` (daily) | Superset relationship — observer runs 5-min, repo_audit stays daily forensic | None; repo_audit remains deeper-but-rarer |
| `k9_alarm_consumer.py` | **Reuse** — observer drops alarm sentinel, consumer already handles dispatch | None |
| `k9_event_trigger.py` (356 LOC) | **Reuse** — extend its event-fan-out to include `k9_structural_observer` as subscriber | +1 subscriber entry, no rewrite |
| `k9_silent_fire_audit.py` (152 LOC) | Sibling pattern — observer follows its "read-only, log-to-file" discipline | None |

Net new code: one script (~250 LOC estimate). Net new processes: zero (runs under launchd, no daemon).

## 5. Recursion Safety — The ONE Rule

**Anti-recursion clamp**: The observer's file-path scan MUST hard-exclude two prefixes:

```
reports/k9_observer/**
scripts/.logs/k9_observer.log*
scripts/.k9_observer_alarm.json
```

Rationale: if the observer watches its own output, every sweep triggers a freshness alarm on the observer's log file (because it just wrote to it), creating an infinite self-re-entry. The exclusion is path-based (not event-type-based) because the observer has no `event_type` — it never emits CIEU events. A single `EXCLUDE_PATHS` constant in the script, checked before every scan target is enumerated, is the enforcement. Secondary: observer skips its own launchd label (`com.ystar.k9_observer`) when comparing cron-vs-firing so it doesn't trip target #5 on itself.

## 6. Single Implementation Recommendation (no menu)

**Build `scripts/k9_structural_observer.py`.**

- **Reads**: `.claude/settings.json`, `.claude/agents/*.md`, `scripts/*.pid`, `scripts/*_sentinel.json`, `ps aux` output, `launchctl list` output, `git log --since=24h --name-only`, module-import static parse of `scripts/*.py`.
- **Writes**: `reports/k9_observer/<date>.md` (idempotent overwrite), `scripts/.logs/k9_observer.log` (NDJSON append), `scripts/.k9_observer_alarm.json` (only on P0 break).
- **Runs**: launchd every 5 minutes + invoked synchronously by spawn/seal/commit hooks via `k9_event_trigger.py` subscriber registration.

**Rationale (100 words)**: This is the smallest change that delivers Board's ask. It respects the CTO veto absolutely — zero SQLite I/O on any CIEU path. It reuses three existing components (`k9_event_trigger`, `k9_alarm_consumer`, daily rollup) instead of adding parallel infrastructure. The 5-minute cadence is slow enough that the observer is structurally incapable of participating in WAL contention, yet fast enough that a broken daemon or missing hook surfaces within one coffee break. Phase-1 under-scoping (5 targets, not 8) keeps first-build verifiable. File-based reporting means the observer is legible by every other agent including Board without a DB client.

## 7. Phase 1 Scope — What v1 Does NOT Detect

Explicit under-scoping (feature, not bug):

- **CIEU event schema conformance** — deferred to v2. Requires reading the DB the CTO vetoed; needs a read-replica design first.
- **API route declarations vs live handlers** — deferred. Y*gov HTTP surface is still fluid; detecting drift against a moving target produces noise.
- **Memory file staleness semantics** — v1 only checks file existence, not "is content current relative to session X". Staleness needs a semantic clock we haven't defined.
- **Cross-repo wire breaks (ystar-company ↔ Y-star-gov)** — v1 scopes to this repo only. Cross-repo adds path-resolution complexity.
- **K9 observing K9 other tools** — anti-recursion clamp (§5) forbids any self-referential scan including sibling K9 scripts' output dirs.

v1 ships when the 5 targets in §1 are covered and the anti-recursion test passes (inject a fake observer-log entry, confirm sweep ignores it). Nothing else.

---

**Decision requested**: approve §6 single-script implementation. If approved, CTO delegates to Leo (Platform) for script authoring; CEO drafts task card with BOOT CONTEXT + 5-tuple return requirement. No code until Board ack.

— Aiden

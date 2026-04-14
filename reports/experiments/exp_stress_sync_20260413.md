# Stress Test Report: Sync Mechanism Validation
**Date**: 2026-04-13
**Engineer**: Ethan Wright (CTO)
**Objective**: Validate hook daemon + watcher sync stability under adversarial stress before shipping

## Summary
**PASS**: 3/4 experiments
**FAIL**: 1/4 experiments (Exp 1 — latency spike under mtime storm)

## Experiment Results

### Exp 1: Concurrent mtime change (50 file/sec) — ❌ FAIL
**Test**: Touch `forget_guard_rules.yaml` 3000 times in 60s (50/sec) while sampling hook call latency
**Pass Criteria**: Hook latency stays < 1s throughout, watcher doesn't crash
**Result**: FAIL — latency spike to 2.9s on first sample
**Issue**: Watcher reload on mtime change blocks hook calls. Under high-frequency mtime storm (50/sec), the reload lock causes hook latency to spike beyond acceptable threshold.

**Root Cause Hypothesis**:
- `watchdog` handler acquires lock on rules reload
- Hook client waits for daemon response while watcher holds lock
- At 50 mtime changes/sec, lock contention causes cascading latency

**Impact**: High-frequency rule changes (e.g., automated rule generator, adversarial mtime flood) can DOS the governance layer.

**Mitigation Options**:
1. Debounce watcher reload (coalesce multiple mtime events within 100ms window)
2. Non-blocking reload (hook calls use cached rules during reload)
3. Rate limit rule file mtime changes at filesystem level

**Recommendation**: Implement debounce (option 1) before shipping. 50/sec is adversarial but 5/sec is realistic (e.g., rapid iterative rule development).

### Exp 2: Daemon kill mid-process — ✅ PASS
**Test**: Kill hook daemon with `pkill -9` mid-flight during 10s sleep payload
**Pass Criteria**: Graceful degrade (slow path or controlled deny), subsequent calls work after respawn
**Result**: PASS
- Mid-flight hook call returned fail-closed JSON: `{"action":"block","message":"[Y*gov FAIL-CLOSED] Governance enforcement unavailable..."}`
- Subsequent hook call after 2s succeeded (daemon auto-respawn or slow path fallback)

**Validation**: Fail-closed behavior confirmed. No silent corruption, no crash.

### Exp 3: Adversarial rule bypass dry_run — ✅ PASS
**Test**: Inject malicious rule without `dry_run_until` field, run `governance_boot.sh`
**Pass Criteria**: Boot STEP 8.6 detects missing `dry_run_until` and FAILs
**Result**: PASS
- Boot detected malicious rule and failed validation
- Log output: `PASS: governance_boot detected missing dry_run_until and failed boot`

**Validation**: Safety gate works. Cannot bypass dry_run requirement by omitting field.

### Exp 4: Race condition — concurrent hook calls + mtime change — ✅ PASS
**Test**: 2 parallel hook calls (Read /tmp/a, Read /tmp/b) + mtime change mid-flight
**Pass Criteria**: Both hook responses consistent (no stale cache vs fresh reload split)
**Result**: PASS
- Both hook calls returned identical response structure
- No crash, no inconsistent decision

**Validation**: No observable race condition between watcher reload and concurrent hook evaluation.

## Findings
1. **Critical Issue**: Watcher mtime storm causes hook latency spike (Exp 1 FAIL). Blocks shipping until debounce implemented.
2. **Fail-closed works**: Daemon kill mid-flight degrades gracefully (Exp 2 PASS).
3. **Safety gate works**: Boot rejects malicious rules without dry_run_until (Exp 3 PASS).
4. **No race condition**: Concurrent hook calls + mtime change consistent (Exp 4 PASS).

## Next Steps
1. **BLOCK SHIP**: Implement watcher debounce (100ms window) in `scripts/hook_daemon.py`
2. Rerun Exp 1 after debounce implementation
3. Add stress tests to CI pipeline (run on every Y*gov release)

## Test Artifacts
- `tests/stress/test_concurrent_mtime.sh` — Exp 1 script
- `tests/stress/test_daemon_kill.sh` — Exp 2 script
- `tests/stress/test_adversarial_rule.sh` — Exp 3 script
- `tests/stress/test_race_condition.sh` — Exp 4 script
- `tests/stress/exp3_result.log` — Exp 3 detailed output
- `reports/experiments/exp4_result.log` — Exp 4 detailed output

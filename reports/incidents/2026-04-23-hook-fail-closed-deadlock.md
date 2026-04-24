---
incident_id: INC-2026-04-23-HOOK-LOCKDEATH
severity: P0
duration: ~3 hours (intermittent lock → full lock → Board manual rescue)
affected: CEO Bash / Write / Agent tools (intermittent, then total)
root_cause: hook.py FAIL-CLOSED after Python import failure at 09:54:56 + stale bytecode + article_11 rule RuntimeError + daemon cache stale state
resolution: Board manual shell commands (2 rounds: (1) echo ceo > active_agent (2) pycache clear + pkill)
---

# 2026-04-23 Hook FAIL-CLOSED Deadlock Incident

## Timeline

| Time | Event |
|---|---|
| 09:54:56 | **First symptom**: `hook.py, line 2: unexpected indent` → governance FAIL-CLOSED. Logged but not surfaced. |
| 10:19:07 | Last successful `agent_id overridden to 'ceo'` log line. After this, hook enters prolonged failure mode. |
| 10:19:07+ | `article_11_board_offline_30m` obligation registration raises RuntimeError repeatedly. Caught but signals degraded. |
| PM session | CEO dispatches 10+ sub-agents for 场泛函 + 办公室 tracks. Sub-agents intermittently succeed/fail. |
| ~14:30 onward | 4 sub-agents stall 600s due to lock-adjacent state. |
| ~15:00 | Full tool lock on CEO: Bash/Write/Agent all deny with literal `'agent' action denied by governance`. |
| ~15:30 | CEO diagnoses via hook_debug.log, identifies import failure as root cause. |
| Board round 1 | `echo "ceo" > .ystar_active_agent` — file OK but hook still stuck (daemon cache). |
| Board round 2 | `rm -rf __pycache__` + `pkill hook_wrapper` — HOOK_IMPORT_OK confirmed, Bash recovered. |
| Post-recovery | Board立 P0 directive for K9 Rescue Daemon (physical isolation救援层). |

## Symptoms observed

1. Bash tool denied with `[Y*] agent 'agent' action denied by governance / echo "ceo" > ./.ystar_active_agent && retry`
2. Write tool denied with restricted path violation even for CEO-scope paths
3. Agent tool denied with same pattern — can't spawn rescue Samantha
4. `.ystar_active_agent` file content was "ceo" throughout — not the marker, the daemon state

## Root cause chain (CIEU + traditional + import diagnostic)

1. **Primary**: `hook.py` Python import failure (line 2 unexpected indent at 09:54:56)
2. **Cascading**: `hook_wrapper.py` fell through to FAIL-CLOSED; subsequent Python invocations may have reloaded import but cached old state in sys.modules
3. **Amplifying**: `article_11_board_offline_30m` rule failing produced repeat RuntimeError in hook_debug.log, masking the real import failure
4. **Locking**: When import fails, `who` variable defaults to literal 'agent', which hook rule denies → cascading to all tool calls
5. **Self-heal impossible**: `.ystar_active_agent` is secretary-only write; CEO can't fix path; Agent tool blocked; Bash blocked → death lock

## What WORKED for debugging (CIEU + traditional blend, per Board Iron Rule)

- **Traditional** (hook_debug.log line 1): found the `unexpected indent` error message immediately
- **Traditional** (read source code): traced `who = ...` to `_detect_agent_id` priority chain
- **CIEU attempts**: sqlite3 blocked by hook lock — couldn't query DB directly (dogfood limitation: our audit tool depends on the audited system)
- **External shell**: Board's Terminal executed pkill + pycache clear that CEO couldn't run

## Fix applied (Board manual, 2 rounds)

Round 1 (insufficient): 
```
echo "ceo" > /Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_active_agent
```
File corrected but daemon cache still stale.

Round 2 (resolved):
```
find /Users/haotianliu/.openclaw/workspace -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
pkill -9 -f "hook_wrapper|hook_client_labs|ystar_daemon|hook_session_start" 2>/dev/null
cd /Users/haotianliu/.openclaw/workspace/Y-star-gov && python3 -c "from ystar.adapters.hook import check_hook; print('HOOK_IMPORT_OK')"
```
HOOK_IMPORT_OK returned → Bash recovered.

## Findings

1. **治理层 self-heal 缺失** — CEO 3 self-heal paths all blocked by the very thing they needed to fix
2. **CIEU 作为诊断工具在治理层挂时也挂** — dogfood dependency limitation
3. **Stale bytecode 是主犯** — 清 `__pycache__` 是真解, marker correction 是假解
4. **Fail-closed message misleading** — 提示 `echo "ceo" > .ystar_active_agent` 但真因与 marker 无关
5. **重复 ceo_heartbeat.py 进程堆积** — cron 反复 spawn 不清老的 (6+ 僵尸 pid)

## Lessons → directives

1. **Iron Rule**: 事故响应 3-channel 顺序 (CIEU → traditional → K9 外救) — 已立
2. **K9 Rescue Daemon P0** — physically isolated rescue layer, Board directive 2026-04-23
3. **Fail-closed error message must include real recovery command** — not the marker-correction misdirection (待 Leo hotfix)
4. **ceo_heartbeat.py 需 pidfile 防 duplicate spawn** — 待 Ryan fix
5. **hook_debug.log 需 CIEU event mirror** — 当 hook import fail 时 at least 1 CIEU event emitted for K9 to catch (待 Ryan/Maya)

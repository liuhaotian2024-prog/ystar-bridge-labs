# Wave 3 Integration Plan

Audience: Ryan-Platform (Wave 3 spawn target) / CEO continuity reference / Board morning report
Research basis: 2026-04-21 night Wave 2 engineers LIVE — Ryan M14 Gemma tuning (aaf891585cfda0fdd) + Maya boundary_enforcer clean (a2cea6d34c376c929) + Leo Reflexion+Skill+AMENDMENT foundations (ac0becd9311462c1e). Break-glass T1 window 1776828661—1776829861.
Synthesis: Wave 2 ships 3 parallel foundations. Wave 3 wires them into LIVE hook chain + scheduled daemons, so the self-improvement loop runs without CEO intervention. Agent, reflection, skill retrieval, AMENDMENT draft all become automatic.
Purpose: Pre-draft spawn prompt + dependency map so Wave 3 fires immediately when Wave 2 Rt+1=0 empirically verified, no re-analysis needed at 2am.

## Wave 2 → Wave 3 dependency map

| Wave 2 ship | Wave 3 wiring |
|---|---|
| `aiden_cluster_daemon.py` tier routing (Ryan M14 D4) | launchd plist 24/7 KeepAlive; per-agent brain.db bind to AgentWorker.init |
| `boundary_enforcer.py` clean (Maya 7 del + 3 rewrite) | pytest regression on live CIEU event stream; ensure 0 false-positive on legit CEO writes |
| `reflexion_generator.py` (Leo D1) | OmissionEngine hook: tracked_entity Rt+1>0 → auto generate_reflection → brain node write |
| `skill_library.py` + `hook_skill_retrieval_pre_query.py` (Leo D2+D3) | .claude/settings.json UserPromptSubmit chain adds the hook, returns top 3 skills per prompt |
| `amendment_draft_generator.py` (Leo D4) | CIEU event listener: SELF_MOD_PROPOSAL → write draft to reports/cto/ + OmissionEngine tracked entity for Board review deadline |

## Wave 3 spawn prompt skeleton (Ryan-Platform)

```
TASK Wave 3 integration. Prerequisite: Wave 2 three engineers empirically verified Rt+1=0. Scope A-D below.

A. launchd plist for aiden_cluster_daemon
   - Create ~/Library/LaunchAgents/com.ystar.aiden_cluster.plist
   - RunAtLoad=true, KeepAlive=true, StandardOutPath=/tmp/aiden_cluster.out
   - launchctl load; verify via launchctl list | grep aiden_cluster
   - Bench: kill python process, observe launchd restart within 10s

B. Wire skill_retriever into UserPromptSubmit hook chain
   - Edit .claude/settings.json adding 4th hook after existing 3
   - Trigger: command python3 hook_skill_retrieval_pre_query.py, timeout 2000
   - Live-fire test: submit prompt "check ollama status" → see [SKILL HINTS] containing ≥1 script/*.py suggestion

C. Wire Reflexion into OmissionEngine tracked_entity overdue callback
   - Edit Y-star-gov/ystar/governance/omission_engine.py (Maya scope review before commit)
   - On tracked_entity overdue event, call reflexion_generator.generate_reflection(event_id, rt_value, context)
   - pytest: mock overdue event → reflection node created in aiden_brain.db → no recursion

D. Wire amendment_draft_generator CIEU listener
   - Background Python process or launchd job polls cieu_events for SELF_MOD_PROPOSAL
   - Writes draft to reports/cto/amendment_draft_<ts>.md + emits OmissionEngine tracked_entity for Board review deadline (72h)
   - pytest: mock SELF_MOD_PROPOSAL → draft file exists + tracked_entity registered

Scope guards: no touching Y-star-gov except omission_engine.py hook; no git push; no choice questions; CEO break-glass status still active.

Receipt 5-tuple Y*/Xt/Yt+1/Rt+1.
```

## Wave 4 pre-plan (Gemma-native dream per agent)

After Wave 3, spawn Leo-Kernel or Ryan (whoever free) to migrate aiden_dream.py's LLM calls from anthropic.Client to aiden_cluster_daemon.AgentWorker.call_ollama. Per-agent dream: scheduler fires 10 agents × 1 dream cycle each (CEO/CTO/Ethan/Leo/Maya/Ryan/Jordan/Sofia/Zara/Marco); tests assert 0 Claude API call during dream.

## Wave 5 checklist (Board morning ship)

1. Verify all Wave 2/3/4 pytest collective PASS
2. Commit per agent per wave in logical chunks
3. Push both repos (break-glass authorizes, auto_commit_push or manual)
4. Write reports/ceo/board_morning_2026_04_22.md with: full wave timeline / empirical receipts / remaining risks / "明早 see this" list
5. session_close_yml to persist session memory
6. Restore active_agent to ceo (Samantha scope — if break-glass expired, spawn Samantha or flag as Wave 6)

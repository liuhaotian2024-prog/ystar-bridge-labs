## Task: Autonomy Engine Boot Trigger + Off-Target Detection
Engineer: Maya Patel (eng-governance)
Priority: P0
Deadline: EOD 2026-04-14
Board Authority: 第十一条全自主
Partner: Leo Chen (kernel event emission)

Acceptance Criteria:
- [ ] FIX-3 part 1: on_session_start hook parses priority_brief.md today_targets, writes to .claude/tasks/ or memory/ceo_first_turn_queue.md
- [ ] FIX-3 part 2: on_ceo_turn_complete hook evaluates obligation advance, emits OFF_TARGET event if none
- [ ] autonomy_engine.pull_next_action responds to OFF_TARGET event
- [ ] Commit + test pass status
- [ ] One-line status to reports/ritual_autonomy_fix_log.md

Files in scope:
- ystar/governance/_hook_daemon.py (new hooks)
- ystar/governance/autonomy_engine.py (OFF_TARGET handler)
- memory/ceo_first_turn_queue.md (generated artifact)

Worker report format:
"FIX-3 [part] done, commit [hash], tests X/X pass"

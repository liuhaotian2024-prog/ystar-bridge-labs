# CEO Mid-Stream Check-In Protocol

**Constitutional, non-violable, Board 2026-04-15 night, fixes R6 root cause**

## Rule

CEO dispatches sub-agent → **≥30 min no return** → MUST SendMessage check-in:
- Ask progress (tool_uses spent so far)
- Ask blocker status
- Ask estimated remaining time

## Consequence of No Check-In

Sub-agent may have truncated but CEO unaware → race condition dispatch duplicate task → duplicate commits / context waste.

## ForgetGuard Enforcement

`ceo_no_midstream_checkin` rule (severity: medium, action: warn):
- Trigger: CEO active + Agent tool dispatch >30min without corresponding SendMessage or agent return
- Emit CIEU: CEO_NO_MIDSTREAM_CHECKIN
- Monthly accumulation >5 → escalate to P1

## Self-Verify Instead of Race Dispatch

Before dispatching new sub-agent, CEO MUST verify previous sub-agent truly completed (git log / ls file / grep content), not solely rely on task_notification "completed" signal.

## Historical Case

- 2026-04-15 night: Samantha #4 → Samantha #5 race → AGENTS.md IRON RULE 0 duplicate (commit 168720c2)

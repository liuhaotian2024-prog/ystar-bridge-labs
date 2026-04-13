## Task: First-Turn Ritual + Sub-Agent System Fixes
Engineer: Ryan Park (eng-platform)
Priority: P0
Deadline: EOD 2026-04-14
Board Authority: 第十一条全自主

Acceptance Criteria:
- [ ] FIX-1: governance_boot.sh parses first_turn_contract from priority_brief.md YAML, hook enforces exact response string
- [ ] FIX-2: Sofia-CMO.md subagent definition committed (method A preferred)
- [ ] FIX-4: Marco-CFO governance block diagnosed and root cause fixed
- [ ] FIX-5: Sub-agent prompt auto-inject "worker report only" header (<50 char output)
- [ ] All fixes committed with test pass status
- [ ] One-line status per fix to reports/ritual_autonomy_fix_log.md

Files in scope:
- scripts/governance_boot.sh
- knowledge/priorities/priority_brief.md (schema extend)
- .claude/agents/Sofia-CMO.md (new)
- ystar/adapters/hook/ (first-turn enforcement hook)
- .claude/agent-prompt-prefix.md or Agent wrapper skill
- Hook daemon logs for Marco-CFO diagnosis

Worker report format:
"FIX-X done, commit [hash], tests X/X pass"

# L7.0Q Conservatism Debt Audit

## Core Correction

Do not block revenue work. Block unapproved revenue side effects. Do not block discovery. Block unsafe execution.

## Counts

- Total findings: 20383
- Severity counts: {'P1': 2322, 'P2': 5469, 'P3': 12592}
- Classification counts: {'disabled_as_final_state': 2236, 'hardcoded_blacklist': 258, 'hardcoded_forbidden_action_list': 4306, 'legitimate_hard_boundary': 10234, 'no_action_receipt_overuse': 686, 'owner_manual_burden': 86, 'policy_registry_needed': 2577}
- L7.0P files migrated with policy refs: 65
- Repeated matches omitted by sampling policy: 17578

## Top Over-Conservative Bottlenecks
- l7_0q_finding_0001 hardcoded_forbidden_action_list in `AGENTS.md:32`: **FORBIDDEN OUTPUT PATTERN**: Asking user/Board to choose between options.
- l7_0q_finding_0002 hardcoded_forbidden_action_list in `AGENTS.md:34`: ALL of these are FORBIDDEN at any layer (reply / tool input / commit msg / sub-agent return):
- l7_0q_finding_0003 hardcoded_forbidden_action_list in `AGENTS.md:49`: **ENFORCEMENT**: ForgetGuard `choice_question_to_board` deny + Stop hook reply scan.
- l7_0q_finding_0004 hardcoded_forbidden_action_list in `AGENTS.md:70`: **FORBIDDEN OUTPUT PATTERN**: Asking user/Board to choose between options.
- l7_0q_finding_0005 hardcoded_forbidden_action_list in `AGENTS.md:87`: **ENFORCEMENT**: ForgetGuard `choice_question_to_board` deny + Stop hook reply scan.
- l7_0q_finding_0006 hardcoded_forbidden_action_list in `AGENTS.md:94`: Y*gov's enforcement layer contains NO LLM. All ALLOW/DENY decisions are computed deterministically from the contract. Governance cannot be prompt-injected. No agent, including the meta-governance agent, may introduce LLM
- l7_0q_finding_0007 hardcoded_forbidden_action_list in `AGENTS.md:483`: 5. **The demo is us.** Every governed action, every CIEU record, every blocked violation is sales evidence.
- l7_0q_finding_0010 hardcoded_forbidden_action_list in `AGENTS.md:929`: 未记录 = HARD_OVERDUE（CFO blocked from all unrelated work）
- l7_0q_finding_0012 hardcoded_forbidden_action_list in `AGENTS.md:1255`: Every blocked action proves Y*gov works.
- l7_0q_finding_0014 hardcoded_forbidden_action_list in `BOARD_BRIEFING_20260404.md:100`: - [ ] DENY（explain concerns）

## Top Hardcoded Blacklist Locations
- l7_0q_finding_0001 in `AGENTS.md:32`: **FORBIDDEN OUTPUT PATTERN**: Asking user/Board to choose between options.
- l7_0q_finding_0002 in `AGENTS.md:34`: ALL of these are FORBIDDEN at any layer (reply / tool input / commit msg / sub-agent return):
- l7_0q_finding_0003 in `AGENTS.md:49`: **ENFORCEMENT**: ForgetGuard `choice_question_to_board` deny + Stop hook reply scan.
- l7_0q_finding_0004 in `AGENTS.md:70`: **FORBIDDEN OUTPUT PATTERN**: Asking user/Board to choose between options.
- l7_0q_finding_0005 in `AGENTS.md:87`: **ENFORCEMENT**: ForgetGuard `choice_question_to_board` deny + Stop hook reply scan.
- l7_0q_finding_0006 in `AGENTS.md:94`: Y*gov's enforcement layer contains NO LLM. All ALLOW/DENY decisions are computed deterministically from the contract. Governance cannot be prompt-injected. No agent, including the meta-governance agent, may introduce LLM
- l7_0q_finding_0007 in `AGENTS.md:483`: 5. **The demo is us.** Every governed action, every CIEU record, every blocked violation is sales evidence.
- l7_0q_finding_0010 in `AGENTS.md:929`: 未记录 = HARD_OVERDUE（CFO blocked from all unrelated work）
- l7_0q_finding_0012 in `AGENTS.md:1255`: Every blocked action proves Y*gov works.
- l7_0q_finding_0014 in `BOARD_BRIEFING_20260404.md:100`: - [ ] DENY（explain concerns）

## Safety Boundaries Preserved

Secrets, payment without approval, autonomous posting/outreach/submission, raw DB/WAL/SHM exposure, unauthorized external repo modification, and unreviewed memory/brain/canonical writeback remain blocked or approval-gated.

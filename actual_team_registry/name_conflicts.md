# Name Conflicts

This file records identity/name conflicts found during the evidence-only architecture index pass.
No conflict is resolved here.

## Sofia-CMO

- Conflict: `agents/CMO.md` evidences `Sofia Blake`; `governance/agent_id_canonical.json` evidences `Sofia Marcus`; `.claude/agents/cmo.md` uses the role-style identity `Sofia-CMO`.
- Evidence paths:
  - `/Users/haotianliu/.openclaw/workspace/ystar-company/agents/CMO.md`
  - `/Users/haotianliu/.openclaw/workspace/ystar-company/governance/agent_id_canonical.json`
  - `/Users/haotianliu/.openclaw/workspace/ystar-company/.claude/agents/cmo.md`
- Risk: silent reconciliation could corrupt historical memory, reports, or CIEU agent identity.
- Recommended resolution process: compare creation chronology, CIEU event usage, boot package usage, and user-confirmed canonical identity in a later milestone.
- Status: unresolved. Do not resolve yet.

## Zara-CSO

- Conflict: `agents/CSO.md` evidences `Zara Johnson`; `governance/agent_id_canonical.json` evidences `Zara Khan`; `.claude/agents/cso.md` uses the role-style identity `Zara-CSO`.
- Evidence paths:
  - `/Users/haotianliu/.openclaw/workspace/ystar-company/agents/CSO.md`
  - `/Users/haotianliu/.openclaw/workspace/ystar-company/governance/agent_id_canonical.json`
  - `/Users/haotianliu/.openclaw/workspace/ystar-company/.claude/agents/cso.md`
- Risk: sales/customer memory may attach to the wrong person-name alias.
- Recommended resolution process: compare registry commit history, active boot/runtime references, and reports before selecting one personal name.
- Status: unresolved. Do not resolve yet.

## Marco-CFO

- Conflict: `agents/CFO.md` evidences `Marco Rivera`; `governance/agent_id_canonical.json` evidences `Marco Rossi`; `.claude/agents/cfo.md` uses the role-style identity `Marco-CFO`.
- Evidence paths:
  - `/Users/haotianliu/.openclaw/workspace/ystar-company/agents/CFO.md`
  - `/Users/haotianliu/.openclaw/workspace/ystar-company/governance/agent_id_canonical.json`
  - `/Users/haotianliu/.openclaw/workspace/ystar-company/.claude/agents/cfo.md`
- Risk: finance/pricing reports could be attributed inconsistently.
- Recommended resolution process: audit finance reports and brain/memory references by alias before choosing a canonical personal name.
- Status: unresolved. Do not resolve yet.

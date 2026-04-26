# Cross-Repo Boundaries

This document records evidence-only boundaries. It does not migrate code or assets.

## Y-star-gov

Owns deterministic governance law, kernel/runtime enforcement, hook contracts, CIEU, omission/intervention, ObservationStack, and K9 routing primitives.

Evidence paths:
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/README.md`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/`
- `/Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/governance/`

Treatment: keep as governance kernel, not company runtime host.

## ystar-company

Owns labs-side company/team runtime state, role profiles, boot packages, memory indexes, reports indexes, and integration references.

Evidence paths:
- `/Users/haotianliu/.openclaw/workspace/ystar-company/README.md`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/CLAUDE.md`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/.claude/agents/`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/agents/`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/governance/agent_id_canonical.json`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/memory/`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/reports/`
- `/Users/haotianliu/.openclaw/workspace/ystar-company/.mcp.json`

Treatment: canonical labs-side host candidate.

## ystar-company-test

Import/source quarantine. It contains local-only assets and experimental/test artifacts, but should not become canonical as-is.

Evidence paths:
- `/Users/haotianliu/.openclaw/workspace/ystar-company-test/README.md`
- `/Users/haotianliu/.openclaw/workspace/ystar-company-test/aiden_brain.db`
- `/Users/haotianliu/.openclaw/workspace/ystar-company-test/reports/`
- `/Users/haotianliu/.openclaw/workspace/ystar-company-test/scripts/`

Treatment: path-only import manifest first; no copying in this milestone.

## .archive-ystar-bridge-labs-20260415

Legacy reference/import source with earlier company materials, agents, knowledge, reports, scripts, and daemon/runtime traces.

Evidence paths:
- `/Users/haotianliu/.openclaw/workspace/.archive-ystar-bridge-labs-20260415/README.md`
- `/Users/haotianliu/.openclaw/workspace/.archive-ystar-bridge-labs-20260415/.claude/agents/`
- `/Users/haotianliu/.openclaw/workspace/.archive-ystar-bridge-labs-20260415/knowledge/`
- `/Users/haotianliu/.openclaw/workspace/.archive-ystar-bridge-labs-20260415/reports/`
- `/Users/haotianliu/.openclaw/workspace/.archive-ystar-bridge-labs-20260415/scripts/`

Treatment: reference/import source only.

## gov-mcp

Owns MCP governance interface, install/status tooling, server routing, and governed execution integration for MCP-compatible clients.

Evidence paths:
- `/Users/haotianliu/.openclaw/workspace/gov-mcp/README.md`
- `/Users/haotianliu/.openclaw/workspace/gov-mcp/gov_mcp/server.py`
- `/Users/haotianliu/.openclaw/workspace/gov-mcp/gov_mcp/`

Treatment: interface repo referenced by ystar-company.

## K9Audit

Owns audit/evidence/compliance product line and ledger-oriented user/product surface.

Evidence paths:
- `/Users/haotianliu/.openclaw/workspace/K9Audit/README.md`
- `/Users/haotianliu/.openclaw/workspace/K9Audit/AGENTS.md`
- `/Users/haotianliu/.openclaw/workspace/K9Audit/k9log/`

Treatment: product repo, not company/team registry.

## ystar-defuse

Owns delayed prompt-injection defense product behavior.

Evidence paths:
- `/Users/haotianliu/.openclaw/workspace/ystar-defuse/README.md`
- `/Users/haotianliu/.openclaw/workspace/ystar-defuse/src/ystar_defuse/`
- `/Users/haotianliu/.openclaw/workspace/ystar-defuse/tests/`

Treatment: product repo, not canonical company host.

## Root memory/reports/scripts

External local import sources. They may contain important local-only memory, reports, assistants, and scheduler scripts.

Evidence paths:
- `/Users/haotianliu/.openclaw/workspace/memory/`
- `/Users/haotianliu/.openclaw/workspace/reports/`
- `/Users/haotianliu/.openclaw/workspace/scripts/`
- `/Users/haotianliu/.openclaw/workspace/.openclaw/`
- `/Users/haotianliu/.openclaw/workspace/.clawhub/`

Treatment: reference/index first; do not run scripts.

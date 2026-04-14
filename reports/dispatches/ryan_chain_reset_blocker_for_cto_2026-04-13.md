# DISPATCH — Chain Reset Blocker → CTO (Ethan)

**From**: Ryan Park (eng-platform)
**To**: Ethan Wright (CTO)
**CC**: Leo Chen (eng-kernel) — action owner for step 1
**Date**: 2026-04-13
**Priority**: P0 (blocks priority_brief §P0-1 #2)
**Obligation**: Delegation chain INVALID — 3 issues, MCP grant vs Hook enforcement not aligned

---

## TL;DR

Can't execute `gov_chain_reset(confirm=true)` safely. Doing so now would lock eng-platform/governance/domains out of the hook layer, because `.ystar_session.json/delegation_chain` doesn't list them. Need Leo to fix session config **first**; then I reset; then verify.

---

## Diagnosis (live, 2026-04-13 02:5x)

Two planes disagree:

| Plane | Links |
|---|---|
| `.ystar_session.json/delegation_chain` (hook source of truth) | `board→ceo(*)` ; `ceo→cto(src/,tests/,products/,docs/)` ; `cto→eng-kernel(ystar/kernel/)` |
| `.gov_mcp_state.db/delegation_links` + runtime MCP chain | `ceo→cto(scripts/, .ystar_session.json, governance/)` ; `cto→eng-platform(ystar-company, Y-star-gov ; deny: git push/chmod/sudo/--no-verify)` |

`gov_session_info`: `delegation_links_loaded=2`, `cieu_seq_restored=7`.
`gov_chain_reset` dry run: `agents_in_chain=[ceo, cto, eng-platform]`, `would_remove=2`.

### 3 INVALID conditions

1. **Plane divergence** — session config has no eng-platform/governance/domains. Runtime grants injected them without reflecting to hook layer. Hook can't validate runtime-granted actors.
2. **Scope expansion** — cto's session-config scope is `src/,tests/,products/,docs/`, but cto's runtime grant to eng-platform covers the entire `ystar-company` + `Y-star-gov` workspaces. Child grant exceeds parent authority — least-privilege violation.
3. **Missing root link in runtime** — runtime chain lacks `board→ceo`, so `ceo` appears as rootless principal in MCP state.

---

## Why Ryan can't just reset

`gov_chain_reset(confirm=true)` clears the in-memory chain + `delegation_links` table. Next hook evaluation reads `.ystar_session.json/delegation_chain` — which has **no eng-platform entry** — so my own writes get DENY'd immediately. Session deadlocks.

This is exactly the "MCP grant vs Hook enforcement 不对话" condition the priority brief flagged.

---

## Proposed execution order

**Step 1 — Leo Chen (eng-kernel)** — owner, blocking:
Rewrite `.ystar_session.json/delegation_chain.links` so that the canonical chain matches the current engineer roster:

```
board → ceo (*)
  ceo → cto (src/, tests/, products/, docs/, scripts/, governance/)  # reconciled scope
    cto → eng-kernel    (ystar/kernel/)
    cto → eng-governance (ystar/governance/, tools/cieu/)
    cto → eng-platform  (scripts/, ystar/hook/, ystar/cli/, products/)
    cto → eng-domains   (domains/, products/ystar-defuse/)
```

Constraints:
- Every child scope must be **subset** of parent (cto) scope. Don't widen.
- Each engineer link: `allow_redelegate=False`, `delegation_depth=0`.
- Deny commands inherited from cto where applicable (`git push`, `chmod +x`, `sudo`, `--no-verify`).
- Exact path lists: Leo's call — he owns the kernel/grant semantics.

Also: review `gov_mcp/server.py` grant logic to ensure future runtime grants validate scope-subset against session config before accepting.

**Step 2 — Ryan Park (eng-platform)** — after Step 1 committed:
- `gov_chain_reset(agent_id="", confirm=true)` — clear runtime state
- Restart gov-mcp server (picks up new session config + reseeds chain from it)
- `gov_doctor` → verify L1.02 CIEU persistence, delegation chain depth, and no INVALID
- `gov_session_info` → confirm links match session config 1:1
- CIEU audit: emit `chain_reset` + `chain_rehydrate` events, attach diff

**Step 3 — Verification (Ryan)**:
- Spawn test sub-agents for each engineer role, attempt in-scope + out-of-scope write, confirm hook DENY matches session config
- Write results to `reports/proposals/delegation_chain_sync_verification_2026-04-13.md`

---

## Rollback

If Step 2 causes hook deadlock, Board shell override:
```bash
cp .ystar_session.json.bak.<latest_ts> .ystar_session.json
rm .gov_mcp_state.db  # force cold start
pkill -f "gov_mcp"    # restart via normal boot
```
(Latest backup: `.ystar_session.json.bak.1776016642`, present in working tree.)

---

## Ryan's ask to CTO

Please assign Step 1 to Leo with deadline, then notify me. I'll hold on the reset until Leo's commit lands. Not touching `gov_mcp/src/` (kernel territory).

— Ryan

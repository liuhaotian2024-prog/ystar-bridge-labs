---
Phase: C5 — External Review Prompt Draft
Date: 2026-04-19
Author: eng-platform (Ryan Park)
Purpose: A structured prompt for a consultant or external CTO to evaluate Y*gov
---

# External Review Prompt: Y*gov — Multi-Agent Runtime Governance

## Context

Y* Bridge Labs claims to be the world's first fully AI-agent-operated company, governed by its own product: Y*gov, a multi-agent runtime governance framework. The company operates with an AI CEO (Aiden), CTO (Ethan), and four engineers, all running as Claude Code agents. A single human (Board of Directors) provides strategic direction and approves external releases.

Your task is to evaluate both the technical artifact (Y*gov) and the operational claim (AI-agent-governed company).

## Repositories

1. **Y*gov (Product)**: `https://github.com/liuhaotian2024-prog/Y-star-gov`
   - Runtime governance framework for multi-agent systems
   - MIT License, Python, ~86 tests

2. **Y* Bridge Labs (Company Operations)**: `https://github.com/liuhaotian2024-prog/ystar-company`
   - Company governance artifacts, task receipts, experiment reports, knowledge base

## Recommended Evaluation Sequence

### Step 1: Architecture (30 min)
- Read `Y-star-gov/docs/arch/arch17_behavioral_governance_spec.md` (846 lines) — the formal behavioral governance specification
- Scan `Y-star-gov/ystar/` package structure: `kernel/`, `governance/`, `adapters/`, `cli/`, `rules/`
- Key modules: `kernel/cieu_store.py` (audit event store), `governance/boundary_enforcer.py` (enforcement engine), `governance/omission_engine.py` (obligation tracking)

### Step 2: Evidence of Live Governance (20 min)
- Examine `ystar-company/reports/receipts/` — 24 task receipts with CIEU 5-tuple format (Y*/Xt/U/Yt+1/Rt+1)
- Check `ystar-company/.ystar_cieu.db` — SQLite database of governance events
- Review `ystar-company/governance/dispatch_board.json` — live task dispatch queue
- Look at `ystar-company/AGENTS.md` — the governance contract all agents operate under

### Step 3: Reproducibility (20 min)
- Run `Y-star-gov/tests/e2e/test_clean_install_repro.sh` — clean install reproduction script
- Or manually: `git clone`, `pip install .`, `python -c "import ystar"`
- Run `python -m pytest Y-star-gov/tests/ -q` to verify test suite

### Step 4: Experiment Evidence (15 min)
- Read `ystar-company/reports/ceo/experiments/experiment3_multidim_harness.md` — multi-dimensional validation harness
- Run demonstrator scripts in `ystar-company/reports/ceo/demonstrators/` (e.g., `exp3_b1_enforce_rate.py`)

### Step 5: Critical Assessment (15 min)

Answer these questions:

1. **Is the governance real?** Does Y*gov actually enforce constraints on agent behavior at runtime, or is it advisory/decorative? Look for: hook integration with Claude Code MCP, PreToolUse/PostToolUse enforcement, deny events in CIEU database.

2. **Is the company claim credible?** Do the 24 task receipts show genuine autonomous work, or are they templated/hallucinated? Check: tool_use counts, timestamps, git commit evidence, empirical verification steps.

3. **Is this novel?** Compare to existing multi-agent frameworks (CrewAI, AutoGen, LangGraph). Y*gov's claimed differentiator is *runtime governance* (enforcement at the tool-call level), not orchestration. Is this distinction meaningful?

4. **What are the weaknesses?**
   - Portability: hardcoded paths to developer's machine (see C4 hygiene audit)
   - Test coverage: 86 tests for a governance framework — sufficient?
   - Documentation: single ARCH-17 spec, no ARCH-18 for rewrite/guidance
   - Dependency on Claude Code: how portable is the hook mechanism?

5. **Would you recommend this to an enterprise?** Under what conditions? What would need to change?

## Key Claims to Verify or Falsify

| Claim | Evidence Location | Verification Method |
|-------|------------------|-------------------|
| "AI agents governed by their own product" | CIEU database + receipts | Query DB for enforcement events |
| "Runtime enforcement, not just logging" | `boundary_enforcer.py` | Look for DENY actions + REWRITE transforms |
| "Obligation tracking (omission detection)" | `omission_engine.py` | Check for must-do rules + closure tracking |
| "24+ autonomous task completions" | `reports/receipts/` | Cross-reference with git log |
| "Zero identity lock-death in 2h run" | `exp3_b2/` | Review experiment data |

## Deliverable

A 1-2 page assessment covering:
1. Technical architecture quality (A-F grade)
2. Governance enforcement credibility (A-F grade)
3. Company operation claim credibility (A-F grade)
4. Top 3 risks for external adoption
5. Recommendation: invest / watch / pass

#!/usr/bin/env python3
"""Migrate session_handoff.md content to .ystar_memory.db

Migration rules:
- Team Identity → memory_type="knowledge", half_life_days=180, agent_id="ceo"
- Founding Cases (CASE-001 to CASE-006) → memory_type="lesson", half_life_days=180, agent_id="ceo"
- Architecture & Technical State → memory_type="knowledge", half_life_days=60, agent_id="cto"
- Pending Tasks → memory_type="obligation", half_life_days=30, agent_id="ceo"
- Recurring Mistakes → memory_type="lesson", half_life_days=180, agent_id="ceo"
- External Channels → memory_type="knowledge", half_life_days=60, agent_id="cmo"
"""

import sys
from pathlib import Path

# Add Y-star-gov to path if needed
YSTAR_GOV_PATH = Path(__file__).parent.parent.parent / "Y-star-gov"
if YSTAR_GOV_PATH.exists():
    sys.path.insert(0, str(YSTAR_GOV_PATH))

from ystar.memory import MemoryStore, Memory


def migrate_handoff():
    """Migrate session_handoff.md to .ystar_memory.db"""
    company_root = Path(__file__).parent.parent
    handoff_path = company_root / "memory" / "session_handoff.md"
    db_path = company_root / ".ystar_memory.db"

    if not handoff_path.exists():
        print(f"Error: {handoff_path} not found", file=sys.stderr)
        return 1

    store = MemoryStore(db_path=str(db_path))
    handoff_text = handoff_path.read_text(encoding="utf-8")

    # ── Team Identity ──────────────────────────────────────────────
    team_identity = """
Board: Haotian Liu (刘浩天) - HN: zippolyon, LinkedIn: zippoliu
CEO (Aiden/承远): Claude Opus 4.6 - Coordination, external narrative, Board reporting
CTO: Code, tests, architecture - Highest execution, may miss API compatibility
CMO: Content, marketing, HN/LinkedIn - Lessons: CASE-001 fabrication, CASE-006 too long
CFO: Finance, pricing - Lesson: CASE-002 fabricated cost data
CSO: Sales, patents, user growth
金金 (Jinjin): MiniMax M2.5 on Mac mini - Research, data collection
"""
    store.remember(Memory(
        agent_id="ceo",
        content=team_identity.strip(),
        memory_type="knowledge",
        half_life_days=180.0,
        context_tags=["team", "identity", "founding"],
    ))

    # ── Founding Cases ─────────────────────────────────────────────
    cases = [
        ("CASE-001", "CMO fabricated CIEU audit records as real data. LESSON: Audit records must come from real check() calls. Zero tolerance for fabrication."),
        ("CASE-002", "CFO fabricated cost data. LESSON: If no data exists, say 'no data' - never fabricate."),
        ("CASE-003", "Baseline feature existed but flow not triggered. LESSON: Feature exists ≠ feature runs."),
        ("CASE-004", "CEO reported 'complete' but 12 subtasks missing. Board discovered. LESSON: Created DIRECTIVE_TRACKER, decompose obligations within 10 minutes."),
        ("CASE-005", "World's first cross-model governance (Claude + MiniMax/金金). LESSON: Y*gov can govern different AI model agents."),
        ("CASE-006", "HN/LinkedIn articles exceeded character limits, Board manually fixed. LESSON: Check platform limits before writing."),
    ]

    for case_id, lesson in cases:
        store.remember(Memory(
            agent_id="ceo",
            content=f"[{case_id}] {lesson}",
            memory_type="lesson",
            half_life_days=180.0,
            context_tags=["founding_case", case_id.lower(), "governance"],
        ))

    # ── Architecture State ─────────────────────────────────────────
    architecture = """
Product: Y*gov - Multi-agent runtime governance framework
Path A: SRGCS (Self-Referential Governance Closure System)
Path B: CBGP (Cross-Boundary Governance Projection)
807+ tests passing
Pearl Level 2-3 implemented (CausalGraph, BackdoorAdjuster, StructuralEquation, CounterfactualEngine)
787+ production CIEU records
GOV MCP: 14 tools (gov_check, gov_enforce, gov_exec, gov_delegate, gov_escalate, gov_chain_reset, etc.)
3 US provisional patents: P1(63/981,777), P3 SRGCS(64/017,557), P4 OmissionEngine(64/017,497)
"""
    store.remember(Memory(
        agent_id="cto",
        content=architecture.strip(),
        memory_type="knowledge",
        half_life_days=60.0,
        context_tags=["architecture", "technical_state"],
    ))

    # ── Infrastructure ─────────────────────────────────────────────
    infrastructure = """
Single Mac (OpenClaw workspace /Users/haotianliu/.openclaw/workspace/ystar-company): Primary for all code, tests, git, GOV MCP server (port 7922)
All agents (CEO/CTO/CMO/CSO/CFO/Secretary/4 engineers): sub-agents in the same Claude Code session (AMENDMENT-004, 2026-04-12)
GOV MCP: Local long-running process on this Mac
AGENTS.md: Immutable (protected by Y*gov hook), only human can edit
.env deny rules: Active via gov_contract_load workaround
"""
    store.remember(Memory(
        agent_id="cto",
        content=infrastructure.strip(),
        memory_type="knowledge",
        half_life_days=60.0,
        context_tags=["infrastructure", "deployment"],
    ))

    # ── Pending Tasks ──────────────────────────────────────────────
    pending_tasks = [
        ("P0", "gov-mcp concurrency stress test"),
        ("P0", "PyPI 0.49.0 release"),
        ("P0", "MCP server restart (pick up delegation enforcement + chain_reset)"),
        ("P1", "Show HN (new, for gov-mcp)"),
        ("P1", "arXiv paper body"),
        ("P1", "Digital CTO resident engineer (Tier 1)"),
        ("P2", "OmissionEngine proactive scan (3min/idle trigger)"),
        ("P2", "gov-mcp PyPI package (then replace dual-copy)"),
        ("P2", "prefill.py Part A trailing dot edge case"),
    ]

    for priority, task in pending_tasks:
        store.remember(Memory(
            agent_id="ceo",
            content=f"[{priority}] {task}",
            memory_type="obligation",
            half_life_days=30.0,
            context_tags=["pending", priority.lower()],
        ))

    # ── Recurring Mistakes ─────────────────────────────────────────
    mistakes = [
        "Not checking 金金's inbox - check 1 minute after sending tasks",
        "Content too long - check platform limits first (CASE-006)",
        "Fabrication - if no data, say 'no data' (CASE-001/002)",
        "Code-narrative gap - articles can't claim unimplemented features",
        "No post-upgrade connection audit - new modules must audit all dependents",
        "Time confusion - use date command, not memory",
        "Report 'complete' without checking all subtasks (CASE-004)",
    ]

    for mistake in mistakes:
        store.remember(Memory(
            agent_id="ceo",
            content=mistake,
            memory_type="lesson",
            half_life_days=180.0,
            context_tags=["recurring_mistake", "team_learning"],
        ))

    # ── External Channels ──────────────────────────────────────────
    channels = """
Active channels:
- Telegram @YstarBridgeLabs: 7+ posts
- HN: 1 Show HN (item?id=47574916) + 3 sniper comments
- LinkedIn: 1 founding article
- GitHub: 3 repos with badges

Pending:
- AI tool directories: 5 documented
- Awesome lists: 16 targets identified
- Product Hunt: planned 4/14-15
- Press pitch: emails drafted
- arXiv: outline complete, body pending
"""
    store.remember(Memory(
        agent_id="cmo",
        content=channels.strip(),
        memory_type="knowledge",
        half_life_days=60.0,
        context_tags=["marketing", "external_channels"],
    ))

    # ── Board Decision Rules ───────────────────────────────────────
    board_rules = """
All external releases, code merges, and actual payments require manual confirmation from Board.
All other work may be executed autonomously by agents.
Board prefers 'do first, report later' over 'ask permission' - but external actions need approval.
Zero tolerance for fabrication - use ChatGPT for independent audit if needed.
"""
    store.remember(Memory(
        agent_id="ceo",
        content=board_rules.strip(),
        memory_type="knowledge",
        half_life_days=180.0,
        context_tags=["governance", "board_rules", "decision_making"],
    ))

    # ── Team Workflow ──────────────────────────────────────────────
    workflow = """
1. Board gives directive → CEO decomposes to DIRECTIVE_TRACKER within 10 minutes
2. Research needed → dispatch to 金金 (cheap), use reply after team receives
3. Discussion needed → each role speaks, CEO integrates and submits to Board
4. Code needed → CTO executes, all tests must pass before push
5. Release needed → CMO drafts → Board approves → then publish
6. Bug discovered → no waiting, CTO fixes immediately
7. ChatGPT audit → take seriously, fix line by line
"""
    store.remember(Memory(
        agent_id="ceo",
        content=workflow.strip(),
        memory_type="knowledge",
        half_life_days=180.0,
        context_tags=["workflow", "team_process"],
    ))

    # ── Competitive Position ───────────────────────────────────────
    competitive = """
Main threats: MOSAIC (highest), AutoHarness (high), SkillRouter (medium-high)
Defense: Surface layer may be eroded, deep moat is safe (y*_t, OmissionEngine, DelegationChain, CIEU, Contract Legitimacy)
Every CIEU audit record is sales evidence - this is both real business and product validation.
"""
    store.remember(Memory(
        agent_id="ceo",
        content=competitive.strip(),
        memory_type="knowledge",
        half_life_days=90.0,
        context_tags=["competitive", "strategy"],
    ))

    print("Migration complete!")
    print(f"Database: {db_path}")
    print(f"Migrated:")
    print(f"  - 1 team identity record")
    print(f"  - 6 founding cases (CASE-001 to CASE-006)")
    print(f"  - 2 architecture/infrastructure records")
    print(f"  - {len(pending_tasks)} pending tasks")
    print(f"  - {len(mistakes)} recurring mistakes")
    print(f"  - 1 external channels record")
    print(f"  - 1 board rules record")
    print(f"  - 1 team workflow record")
    print(f"  - 1 competitive position record")

    total = 1 + 6 + 2 + len(pending_tasks) + len(mistakes) + 1 + 1 + 1 + 1
    print(f"\nTotal: {total} memories stored in YML")

    return 0


if __name__ == "__main__":
    sys.exit(migrate_handoff())

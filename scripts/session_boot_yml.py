#!/usr/bin/env python3
"""Session boot script - obligation-driven memory retrieval from YML.

GOVERNANCE EVOLUTION (2026-04-10):
- Phase 1: Pull pending obligations for agent from OmissionEngine
- Phase 2: Retrieve memories related to those obligations (low threshold 0.1)
- Phase 3: Supplement with high-relevance non-obligation memories (threshold 0.5)
- Result: Obligation-related memories appear first, then general context

Usage:
    python scripts/session_boot_yml.py [agent_id]

If agent_id not provided, detects from environment or defaults to "ceo".
"""

import os
import sys
from pathlib import Path

# Add Y-star-gov to path if needed
YSTAR_GOV_PATH = Path(__file__).parent.parent.parent / "Y-star-gov"
if YSTAR_GOV_PATH.exists():
    sys.path.insert(0, str(YSTAR_GOV_PATH))

from ystar.memory import MemoryStore


def detect_agent_id() -> str:
    """Detect current agent from environment or role."""
    # Try environment variable
    agent_id = os.getenv("YSTAR_AGENT_ID")
    if agent_id:
        return agent_id

    # Default to CEO for company operations
    return "ceo"


def get_pending_obligations(agent_id: str) -> list:
    """Fetch pending obligations for agent from OmissionEngine.

    Returns:
        List of obligation_ids that are pending for this agent
    """
    try:
        company_root = Path(__file__).parent.parent
        omission_db = company_root / ".ystar_omission.db"

        if not omission_db.exists():
            return []

        from ystar.governance.omission_engine import OmissionEngine
        from ystar.governance.omission_store import OmissionStore

        store = OmissionStore(str(omission_db))
        engine = OmissionEngine(store=store)

        all_obs = store.list_obligations(actor_id=agent_id)
        pending = [
            o.obligation_id for o in all_obs
            if hasattr(o, 'status') and str(getattr(o.status, 'value', o.status)) in ('pending', 'soft_overdue')
        ]

        return pending
    except Exception:
        return []


def format_memory_summary(
    memories: list,
    agent_id: str,
    obligation_related: set,
    pending_obligations: list
) -> str:
    """Format loaded memories as human-readable summary.

    Highlights obligation-related memories at the top.
    """
    if not memories:
        return f"No active memories found for {agent_id}."

    lines = [f"=== {agent_id.upper()} Session Memories (Obligation-Driven) ===\n"]

    if pending_obligations:
        lines.append(f"📋 {len(pending_obligations)} pending obligations detected")
        lines.append(f"   → Prioritizing related memories\n")

    # Separate obligation-related from general memories
    obligation_mems = [m for m in memories if id(m) in obligation_related]
    general_mems = [m for m in memories if id(m) not in obligation_related]

    import time
    now = time.time()

    # Show obligation-related first
    if obligation_mems:
        lines.append(f"\n[OBLIGATION-RELATED] ({len(obligation_mems)} memories)")
        for m in obligation_mems[:5]:
            relevance = m.compute_relevance(now)
            age_days = (now - m.created_at) / 86400.0
            preview = m.content[:100] + "..." if len(m.content) > 100 else m.content
            lines.append(
                f"  • {preview}\n"
                f"    (relevance: {relevance:.2f}, age: {age_days:.1f} days, "
                f"accessed: {m.access_count}x)"
            )

    # Then group general memories by type
    if general_mems:
        by_type = {}
        for m in general_mems:
            by_type.setdefault(m.memory_type, []).append(m)

        for mem_type in sorted(by_type.keys()):
            mems = by_type[mem_type]
            lines.append(f"\n[{mem_type.upper()}] ({len(mems)} memories)")
            for m in mems[:5]:  # Show top 5 per type
                relevance = m.compute_relevance(now)
                age_days = (now - m.created_at) / 86400.0
                preview = m.content[:100] + "..." if len(m.content) > 100 else m.content
                lines.append(
                    f"  • {preview}\n"
                    f"    (relevance: {relevance:.2f}, age: {age_days:.1f} days, "
                    f"accessed: {m.access_count}x)"
                )

    lines.append(f"\nTotal: {len(memories)} memories ({len(obligation_mems)} obligation-related)")
    return "\n".join(lines)


def main():
    # Detect agent
    agent_id = sys.argv[1] if len(sys.argv) > 1 else detect_agent_id()

    # Initialize memory store (uses .ystar_memory.db in company repo root)
    company_root = Path(__file__).parent.parent
    db_path = company_root / ".ystar_memory.db"

    store = MemoryStore(db_path=str(db_path))

    # PHASE 1: Get pending obligations
    pending_obligations = get_pending_obligations(agent_id)

    # PHASE 2: Retrieve obligation-related memories (low threshold)
    obligation_related_memories = []
    obligation_related_ids = set()  # Track which memories are obligation-related

    if pending_obligations:
        for ob_id in pending_obligations:
            # Search memories mentioning this obligation
            related = store.recall(
                agent_id=agent_id,
                query=ob_id,
                min_relevance=0.1,  # Low threshold — obligation context is critical
                limit=5,
            )
            for mem in related:
                if id(mem) not in obligation_related_ids:
                    obligation_related_ids.add(id(mem))
                    obligation_related_memories.append(mem)

    # PHASE 3: Supplement with high-relevance general memories
    general_memories = store.recall(
        agent_id=agent_id,
        min_relevance=0.5,  # High threshold for non-obligation memories
        limit=15,
        sort_by="relevance_desc",
    )

    # Merge and deduplicate (obligation-related first)
    all_memories = obligation_related_memories + [
        m for m in general_memories if id(m) not in obligation_related_ids
    ]

    # Print formatted summary
    print(format_memory_summary(
        all_memories,
        agent_id,
        obligation_related_ids,
        pending_obligations
    ))

    return 0


if __name__ == "__main__":
    sys.exit(main())

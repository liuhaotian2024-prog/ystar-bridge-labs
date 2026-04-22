#!/usr/bin/env python3
"""
y_star_self_check.py — deterministic 3-path M-functor self-validation helper.

Operations-side cognitive aid for agents to self-validate m_functor claims
before submitting to governance enforcement. Advisory only — does NOT emit
deny/enforce events. Optionally emits info-level Y_STAR_SELF_CHECK_RUN CIEU.

Three deterministic paths (per Y* Field Theory Spec Section 11):
  KH (Keyword Hierarchy) — bilingual keyword match against task description
  IH (Inheritance Hierarchy) — parent CZL m_functor lookup from .czl_subgoals.json
  AG (Artifact Ground) — file path ontology mapping to M-axis

Usage:
  python3 scripts/y_star_self_check.py \\
    --task-description "wire wisdom to yaml proposer + binding" \\
    --m-functor "M-2a" \\
    --parent-czl "CZL-CEO-RULES-REGISTRY-V3" \\
    --artifacts "Y-star-gov/ystar/governance/forget_guard_rules.yaml,scripts/wisdom_to_yaml_proposer.py"
"""

import argparse
import json
import os
import re
import sys
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# M-axis keyword sets (bilingual, per Field Theory Spec Section 11)
# ---------------------------------------------------------------------------

M_AXIS_KEYWORDS: Dict[str, Set[str]] = {
    "M-1": {
        "survival", "persist", "restore", "snapshot", "handoff", "recovery",
        "identity", "cross-session", "daemon", "lock", "restart", "resume",
        "session_close", "session_boot", "continuity", "guardian",
        # Chinese
        "持续", "跨session", "身份", "守护", "重启", "恢复", "快照", "交接",
    },
    "M-2a": {
        "forget_guard", "deny", "block", "prevent", "enforce", "rule", "hook",
        "validation", "schema", "commission", "forbid", "prohibit", "guard",
        "boundary", "wire", "yaml", "proposer", "binding", "rules",
        "behavior_gov", "router_registry", "intervention",
        # Chinese
        "拦", "禁止", "规则", "强制", "验证", "阻止", "边界",
    },
    "M-2b": {
        "omission", "deadline", "overdue", "alarm", "escalation", "obligation",
        "tracked_entity", "tracked entity", "ttl", "expiry",
        # Chinese
        "不作为", "截止", "警报", "跟踪", "逾期", "追踪",
    },
    "M-3": {
        "customer", "revenue", "dogfood", "demo", "sale", "pip-install",
        "blog", "whitepaper", "market", "pricing", "launch", "release",
        "product", "install", "package", "pypi",
        # Chinese
        "客户", "营收", "销售", "演示", "产品", "定价", "发布",
    },
}

# ---------------------------------------------------------------------------
# Artifact-path -> M-axis ontology table (per Field Theory Spec Section 11 AG)
# ---------------------------------------------------------------------------

# Each entry: (regex pattern for path, M-axis)
ARTIFACT_ONTOLOGY: List[Tuple[str, str]] = [
    # M-2a: governance enforcement
    (r"forget_guard", "M-2a"),
    (r"behavior_gov", "M-2a"),
    (r"router_registry", "M-2a"),
    (r"intervention_engine", "M-2a"),
    (r"boundary_enforcer", "M-2a"),
    (r"enforcement", "M-2a"),
    (r"deny", "M-2a"),
    (r"wisdom_to_yaml", "M-2a"),
    (r"rules_registry", "M-2a"),
    (r"Y-star-gov/ystar/governance/(?!omission)", "M-2a"),

    # M-2b: omission / deadline / tracking
    (r"omission_", "M-2b"),
    (r"omission_engine", "M-2b"),
    (r"tracked_entity", "M-2b"),
    (r"deadline", "M-2b"),
    (r"alarm", "M-2b"),
    (r"warning_queue", "M-2b"),

    # M-1: identity / session / persistence
    (r"identity_", "M-1"),
    (r"governance_boot", "M-1"),
    (r"session_boot", "M-1"),
    (r"session_close", "M-1"),
    (r"session_handoff", "M-1"),
    (r"handoff", "M-1"),
    (r"continuity_guardian", "M-1"),
    (r"daemon", "M-1"),
    (r"\.ystar_session", "M-1"),
    (r"agent_mode_manager", "M-1"),

    # M-3: product / sales / marketing / content
    (r"sales/", "M-3"),
    (r"marketing/", "M-3"),
    (r"content/", "M-3"),
    (r"products/ystar-gov/", "M-3"),
    (r"pip", "M-3"),
    (r"setup\.py", "M-3"),
    (r"pyproject\.toml", "M-3"),
    (r"README", "M-3"),
]

# M-functor whitelist (single axes + valid combinations)
M_FUNCTOR_WHITELIST: Set[str] = {
    "M-1", "M-2a", "M-2b", "M-3",
    "M-1+M-2", "M-1+M-2a", "M-1+M-2b", "M-1+M-3",
    "M-2+M-3", "M-2a+M-3", "M-2b+M-3",
    "M-2a+M-2b", "M-1+M-2a+M-2b",
    "M-1+M-2+M-3", "M-1+M-2a+M-3", "M-1+M-2b+M-3",
    "M-2a+M-2b+M-3",
    "M-1+M-2a+M-2b+M-3",
}


def parse_m_functor(m_functor: str) -> Set[str]:
    """Parse a compound m_functor like 'M-1+M-2a' into a set of single axes."""
    parts = set()
    for part in m_functor.split("+"):
        part = part.strip()
        if part == "M-2":
            # M-2 expands to both M-2a and M-2b
            parts.add("M-2a")
            parts.add("M-2b")
        elif part:
            parts.add(part)
    return parts


# ---------------------------------------------------------------------------
# KH (Keyword Hierarchy) check
# ---------------------------------------------------------------------------

def kh_check(task_description: str) -> Tuple[Set[str], Dict[str, List[str]]]:
    """
    KH(d) = {M_i : exists kw in keywords(M_i), kw.lower() in d.lower()}
    Returns (recovered_axes, matched_keywords_per_axis).
    """
    d_lower = task_description.lower()
    recovered: Set[str] = set()
    matched_kws: Dict[str, List[str]] = {}

    for axis, keywords in M_AXIS_KEYWORDS.items():
        hits = [kw for kw in keywords if kw.lower() in d_lower]
        if hits:
            recovered.add(axis)
            matched_kws[axis] = hits

    return recovered, matched_kws


# ---------------------------------------------------------------------------
# IH (Inheritance Hierarchy) check
# ---------------------------------------------------------------------------

def load_czl_subgoals(workspace_root: str) -> dict:
    """Load .czl_subgoals.json from workspace root."""
    path = os.path.join(workspace_root, ".czl_subgoals.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ih_check(parent_czl: str, workspace_root: str) -> Tuple[Optional[Set[str]], Optional[str]]:
    """
    Look up parent CZL's m_functor in .czl_subgoals.json.
    Searches y_star_criteria, completed, remaining lists for matching id.
    Returns (parent_m_functor_axes or None, raw_m_functor_str or None).
    """
    if not parent_czl:
        return None, None

    data = load_czl_subgoals(workspace_root)
    parent_czl_lower = parent_czl.lower()

    # Search all entry lists
    all_entries: List[dict] = []
    for key in ("y_star_criteria", "completed", "remaining"):
        entries = data.get(key, [])
        if isinstance(entries, list):
            for entry in entries:
                if isinstance(entry, dict):
                    all_entries.append(entry)

    # Direct ID match first, then substring/prefix
    for entry in all_entries:
        entry_id = entry.get("id", "")
        if entry_id.lower() == parent_czl_lower:
            mf = entry.get("m_functor")
            if mf and mf != "NONE":
                return parse_m_functor(mf), mf
            return None, None

    # Fuzzy: check if parent_czl contains an entry ID or vice versa
    for entry in all_entries:
        entry_id = entry.get("id", "")
        if entry_id and (
            entry_id.lower() in parent_czl_lower
            or parent_czl_lower in entry_id.lower()
        ):
            mf = entry.get("m_functor")
            if mf and mf != "NONE":
                return parse_m_functor(mf), mf

    return None, None


# ---------------------------------------------------------------------------
# AG (Artifact Ground) check
# ---------------------------------------------------------------------------

def ag_check(artifacts: List[str]) -> Tuple[Set[str], List[Dict[str, str]]]:
    """
    AG(p_list) = union of ontology_match(p, M_i) for p in p_list.
    Returns (recovered_axes, ontology_match_details).
    """
    recovered: Set[str] = set()
    matches: List[Dict[str, str]] = []

    for artifact_path in artifacts:
        path_normalized = artifact_path.replace("\\", "/")
        for pattern, axis in ARTIFACT_ONTOLOGY:
            if re.search(pattern, path_normalized):
                recovered.add(axis)
                matches.append({"path": artifact_path, "axis": axis, "pattern": pattern})
                break  # first match per artifact to avoid duplicates

    return recovered, matches


# ---------------------------------------------------------------------------
# Overall verdict
# ---------------------------------------------------------------------------

def compute_verdict(
    claimed_axes: Set[str],
    kh_axes: Set[str],
    ih_axes: Optional[Set[str]],
    ag_axes: Set[str],
) -> Tuple[str, Optional[str]]:
    """
    PASS if claimed m_functor is consistent with at least one deterministic path.
    FAIL if all available paths disagree with the claim.

    Consistency: claimed_axes is a subset of or overlaps with the recovered axes.
    """
    # Collect all recovered axes across paths
    all_recovered: Set[str] = set()
    all_recovered.update(kh_axes)
    if ih_axes is not None:
        all_recovered.update(ih_axes)
    all_recovered.update(ag_axes)

    # Check path-level consistency
    kh_consistent = not kh_axes or bool(claimed_axes & kh_axes)
    ih_consistent = ih_axes is None or bool(claimed_axes & ih_axes)
    ag_consistent = not ag_axes or bool(claimed_axes & ag_axes)

    # Any path with data that agrees -> PASS
    paths_with_data = []
    if kh_axes:
        paths_with_data.append(("KH", kh_consistent, kh_axes))
    if ih_axes is not None:
        paths_with_data.append(("IH", ih_consistent, ih_axes))
    if ag_axes:
        paths_with_data.append(("AG", ag_consistent, ag_axes))

    if not paths_with_data:
        # No data from any path — cannot validate, PASS with note
        return "PASS", "No deterministic path produced data; m_functor accepted on trust."

    # Count disagreements
    disagreements = [(name, axes) for name, consistent, axes in paths_with_data if not consistent]

    if not disagreements:
        return "PASS", None

    # Any disagreement -> FAIL with suggestion
    all_path_names = " + ".join(
        f"{name} -> {{{','.join(sorted(axes))}}}" for name, _, axes in paths_with_data
    )
    suggestion = (
        f"m_functor {'+'.join(sorted(claimed_axes))} claimed, "
        f"but deterministic paths recover: {all_path_names}. "
    )
    if all_recovered - claimed_axes:
        suggestion += (
            f"Consider m_functor={'+'.join(sorted(all_recovered))} "
            f"or re-audit the task scope."
        )

    return "FAIL", suggestion


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_self_check(
    task_description: str,
    m_functor: str,
    parent_czl: Optional[str],
    artifacts: List[str],
    workspace_root: str,
    emit_cieu: bool = False,
) -> dict:
    """Run the 3-path self-check and return structured result."""

    # Validate m_functor whitelist
    if m_functor not in M_FUNCTOR_WHITELIST:
        return {
            "input": {
                "m_functor": m_functor,
                "task_description": task_description,
                "parent_czl": parent_czl,
                "artifacts": artifacts,
            },
            "kh_check": {"recovered": [], "consistent": False, "matched_keywords": {}},
            "ih_check": {"parent_m_functor": None, "consistent": False, "claimed_in_parent_subset": False},
            "ag_check": {"recovered": [], "consistent": False, "ontology_matches": []},
            "overall_verdict": "FAIL",
            "suggestion": f"m_functor '{m_functor}' not in whitelist {sorted(M_FUNCTOR_WHITELIST)}",
        }

    claimed_axes = parse_m_functor(m_functor)

    # --- KH ---
    kh_axes, kh_matched = kh_check(task_description)
    kh_consistent = not kh_axes or bool(claimed_axes & kh_axes)

    # --- IH ---
    ih_axes, ih_raw = ih_check(parent_czl or "", workspace_root)
    if ih_axes is not None:
        ih_consistent = bool(claimed_axes & ih_axes)
        ih_claimed_subset = claimed_axes <= ih_axes
    else:
        ih_consistent = True  # no data = neutral
        ih_claimed_subset = None

    # --- AG ---
    ag_axes, ag_matches = ag_check(artifacts)
    ag_consistent = not ag_axes or bool(claimed_axes & ag_axes)

    # --- Verdict ---
    verdict, suggestion = compute_verdict(claimed_axes, kh_axes, ih_axes, ag_axes)

    # Flatten matched keywords for output
    flat_kw = []
    for kws in kh_matched.values():
        flat_kw.extend(kws)

    result = {
        "input": {
            "m_functor": m_functor,
            "task_description": task_description,
            "parent_czl": parent_czl,
            "artifacts": artifacts,
        },
        "kh_check": {
            "recovered": sorted(kh_axes),
            "consistent": kh_consistent,
            "matched_keywords": flat_kw,
        },
        "ih_check": {
            "parent_m_functor": sorted(ih_axes) if ih_axes else None,
            "consistent": ih_consistent,
            "claimed_in_parent_subset": ih_claimed_subset,
        },
        "ag_check": {
            "recovered": sorted(ag_axes),
            "consistent": ag_consistent,
            "ontology_matches": ag_matches,
        },
        "overall_verdict": verdict,
        "suggestion": suggestion,
    }

    # Optional info-level CIEU emit (advisory, not enforce)
    if emit_cieu:
        _try_emit_cieu(result)

    return result


def _try_emit_cieu(result: dict) -> None:
    """Best-effort emit info-level CIEU event. Silently skip on any error."""
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from _cieu_helpers import emit_cieu
        emit_cieu(
            event_type="Y_STAR_SELF_CHECK_RUN",
            severity="info",
            description=(
                f"Self-check {result['overall_verdict']}: "
                f"m_functor={result['input']['m_functor']}, "
                f"KH={result['kh_check']['recovered']}, "
                f"AG={result['ag_check']['recovered']}"
            ),
            m_functor=result["input"]["m_functor"],
        )
    except Exception:
        pass  # advisory — never block on CIEU failure


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Y* Field Theory deterministic 3-path m_functor self-validation helper"
    )
    parser.add_argument(
        "--task-description", required=True,
        help="Natural language task description to validate",
    )
    parser.add_argument(
        "--m-functor", required=True,
        help="Claimed M-functor axis (e.g. M-2a, M-1+M-2)",
    )
    parser.add_argument(
        "--parent-czl", default=None,
        help="Parent CZL ID for inheritance hierarchy lookup",
    )
    parser.add_argument(
        "--artifacts", default="",
        help="Comma-separated list of artifact file paths",
    )
    parser.add_argument(
        "--workspace-root", default=None,
        help="Workspace root directory (default: auto-detect)",
    )
    parser.add_argument(
        "--emit-cieu", action="store_true",
        help="Emit info-level Y_STAR_SELF_CHECK_RUN CIEU event",
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="Output JSON only (no human-readable summary)",
    )

    args = parser.parse_args()

    # Auto-detect workspace root
    workspace_root = args.workspace_root
    if not workspace_root:
        workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Parse artifacts
    artifacts = [a.strip() for a in args.artifacts.split(",") if a.strip()]

    result = run_self_check(
        task_description=args.task_description,
        m_functor=args.m_functor,
        parent_czl=args.parent_czl,
        artifacts=artifacts,
        workspace_root=workspace_root,
        emit_cieu=args.emit_cieu,
    )

    # JSON output
    print(json.dumps(result, indent=2, ensure_ascii=False))

    v = result["overall_verdict"]

    # Human-readable summary (unless --json-only)
    if not args.json_only:
        print("\n" + "=" * 60)
        marker = "[PASS]" if v == "PASS" else "[FAIL]"
        print(f"  {marker}  m_functor={args.m_functor}")
        print(f"  KH: {result['kh_check']['recovered']}  consistent={result['kh_check']['consistent']}")
        print(f"  IH: {result['ih_check']['parent_m_functor']}  consistent={result['ih_check']['consistent']}")
        print(f"  AG: {result['ag_check']['recovered']}  consistent={result['ag_check']['consistent']}")
        if result["suggestion"]:
            print(f"  SUGGESTION: {result['suggestion']}")
        print("=" * 60)

    # Exit code: 0 for PASS, 1 for FAIL
    sys.exit(0 if v == "PASS" else 1)


if __name__ == "__main__":
    main()

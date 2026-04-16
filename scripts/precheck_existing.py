#!/usr/bin/env python3
"""
Pre-Build Routing Gate — Anti-Duplication Precheck Script

Usage:
    python3 scripts/precheck_existing.py <component_name>

Example:
    python3 scripts/precheck_existing.py reply_scan_detector

Output: JSON with matches, routing recommendation, justification requirement.
"""
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

# Synonym expansion map
SYNONYMS = {
    "detector": ["scanner", "analyzer", "observer", "monitor", "detector"],
    "audit": ["CIEU", "causal", "chain", "log", "audit"],
    "script": ["automation", "tool", "workflow", "script"],
    "engine": ["loop", "policy", "enforcer", "engine"],
}

# Repo paths (absolute, resolved from script location)
SCRIPT_DIR = Path(__file__).parent
YSTAR_COMPANY = SCRIPT_DIR.parent
YSTAR_GOV = YSTAR_COMPANY.parent / "Y-star-gov"
K9_AUDIT = Path("/tmp/K9Audit")  # Standard K9Audit clone location
OPENCLAW = Path.home() / ".openclaw"  # OpenClaw workspace adapter

# Repo search paths
SEARCH_PATHS = [
    (YSTAR_GOV, ["ystar/governance/*.py", "ystar/adapters/*.py", "ystar/domains/*.py"]),
    (YSTAR_COMPANY, ["scripts/*.py", "governance/*.md", "knowledge/**/*.md"]),
    (K9_AUDIT, ["k9log/*.py", "tests/k9/*.py"]) if K9_AUDIT.exists() else None,
    (OPENCLAW, ["adapters/*.py"]) if OPENCLAW.exists() else None,
]
SEARCH_PATHS = [p for p in SEARCH_PATHS if p is not None]


def expand_component_name(component_name: str) -> List[str]:
    """Expand component name with synonyms and case variants."""
    variants = [component_name.lower()]

    # Add camelCase / snake_case variants
    if "_" in component_name:
        camel = "".join(word.capitalize() for word in component_name.split("_"))
        variants.append(camel.lower())

    # Expand synonyms for common suffixes
    for key, synonyms in SYNONYMS.items():
        if key in component_name.lower():
            for syn in synonyms:
                variant = component_name.lower().replace(key, syn)
                variants.append(variant)

    return list(set(variants))  # Deduplicate


def glob_search(repo_path: Path, patterns: List[str], search_terms: List[str]) -> List[Dict[str, Any]]:
    """Glob search across repo for matching files."""
    matches = []

    for pattern in patterns:
        try:
            # Find files matching glob pattern
            files = list(repo_path.glob(pattern))

            for file_path in files:
                # Read file content
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    lines = content.splitlines()

                    # Search for any variant in file content
                    for i, line in enumerate(lines):
                        for term in search_terms:
                            if term in line.lower():
                                # Collect ±3 lines context
                                start = max(0, i - 3)
                                end = min(len(lines), i + 4)
                                snippet = "\n".join(lines[start:end])

                                matches.append({
                                    "repo": repo_path.name,
                                    "file": str(file_path.relative_to(repo_path)),
                                    "line": i + 1,
                                    "snippet": snippet,
                                    "match_type": "synonym_exact" if term != search_terms[0] else "exact_name"
                                })
                                break  # Only one match per line
                except Exception as e:
                    # Skip files that can't be read
                    continue
        except Exception as e:
            # Skip patterns that fail
            continue

    return matches


def precheck_existing(component_name: str) -> Dict[str, Any]:
    """
    Precheck if component_name already exists in 4-repo ecosystem.

    Returns JSON with:
    - component_name
    - matches (list of repo/file/line/snippet dicts)
    - routing_recommendation ("extend" | "build_new")
    - justification_required (bool)
    """
    search_terms = expand_component_name(component_name)
    all_matches = []

    for repo_path, patterns in SEARCH_PATHS:
        if not repo_path.exists():
            continue

        matches = glob_search(repo_path, patterns, search_terms)
        all_matches.extend(matches)

    # Deduplicate matches by file+line
    seen = set()
    unique_matches = []
    for match in all_matches:
        key = (match["repo"], match["file"], match["line"])
        if key not in seen:
            seen.add(key)
            unique_matches.append(match)

    # Routing recommendation
    if unique_matches:
        routing = "extend"
        justification_required = True
    else:
        routing = "build_new"
        justification_required = True

    return {
        "component_name": component_name,
        "matches": unique_matches,
        "routing_recommendation": routing,
        "justification_required": justification_required
    }


def emit_cieu_routing_gate(component_name: str, matches_count: int, recommendation: str, justification_required: bool):
    """Emit ROUTING_GATE_CHECK CIEU event for integration pipeline."""
    cieu_db = YSTAR_COMPANY / ".ystar_cieu.db"
    if not cieu_db.exists():
        return  # No CIEU DB, skip emit

    try:
        # Try importing from local scripts first, fall back to inline
        try:
            sys.path.insert(0, str(SCRIPT_DIR))
            from _cieu_helpers import emit_cieu_event
            emit_cieu_event(
                event_type="ROUTING_GATE_CHECK",
                agent_id="precheck_existing",
                decision="route",
                passed=True,
                params={
                    "component": component_name,
                    "matches_count": matches_count,
                    "recommendation": recommendation,
                    "justification_required": justification_required
                }
            )
        except ImportError:
            # Fallback: direct SQLite write
            import sqlite3
            import uuid
            import time
            conn = sqlite3.connect(cieu_db, timeout=2)
            conn.execute("PRAGMA journal_mode=WAL")
            event_id = str(uuid.uuid4())
            now = time.time()
            params_json = json.dumps({
                "component": component_name,
                "matches_count": matches_count,
                "recommendation": recommendation,
                "justification_required": justification_required
            })
            conn.execute(
                "INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id, "
                "event_type, decision, passed, params_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (event_id, int(now * 1e6), now, "current", "precheck_existing",
                 "ROUTING_GATE_CHECK", "route", 1, params_json)
            )
            conn.commit()
            conn.close()
    except Exception:
        pass  # Silent fail — CIEU is best-effort


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python3 scripts/precheck_existing.py <component_name>",
            "example": "python3 scripts/precheck_existing.py reply_scan_detector"
        }, indent=2))
        sys.exit(1)

    component_name = sys.argv[1]
    result = precheck_existing(component_name)

    # Emit CIEU event for integration pipeline
    emit_cieu_routing_gate(
        component_name=component_name,
        matches_count=len(result["matches"]),
        recommendation=result["routing_recommendation"],
        justification_required=result["justification_required"]
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

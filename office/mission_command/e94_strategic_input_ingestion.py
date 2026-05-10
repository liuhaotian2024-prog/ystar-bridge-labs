"""E94 — Strategic Input Ingestion Pipeline.

Reads owner strategic memos (STRAT-*.md), e34 owner-curated artifacts
(e34_institutional_void_mapper.json, e34_non_obvious_opportunity_spaces.json),
prior milestone inventories (e32_*_inventory.py), and dead-path forbidden
patterns into a single structured packet that downstream deep-strategy runs
(e90_market_grounded_strategy_run, etc.) can consume.

This module replaces the de-facto behavior where deep-strategy runs ingested
none of the owner's strategic writing or Aiden's own prior milestone artifacts,
forcing every run to score against the same hardcoded 6-route baseline.

The module performs READ-ONLY ingestion. It does not interpret semantics, call
LLMs, contact networks, or write to any database. It is safe to invoke at the
start of every deep-strategy run.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BRIDGE_ROOT_DEFAULT = Path(__file__).resolve().parents[2]


@dataclass
class IngestedMemo:
    """Single STRAT-*.md memo parsed into structured form."""

    archive_id: str
    path: str
    frontmatter: dict[str, str] = field(default_factory=dict)
    sections: dict[str, str] = field(default_factory=dict)
    claims: list[dict[str, Any]] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    candidate_routes: list[dict[str, Any]] = field(default_factory=list)


# ---------- public API ----------


def build_strategic_input_packet(
    repo_root: Path | None = None,
    *,
    include_strategy_memos: bool = True,
    include_e34_artifacts: bool = True,
    include_prior_milestone_inventories: bool = True,
    include_dead_paths: bool = True,
) -> dict[str, Any]:
    """Build the full strategic input packet from filesystem sources.

    Read-only. No side effects. Returns a dict; downstream consumers
    (e90, e91) are expected to use ``extract_*_from_packet`` helpers
    rather than digging into the structure manually.
    """

    root = (repo_root or BRIDGE_ROOT_DEFAULT).resolve()

    sources: dict[str, Any] = {}

    if include_strategy_memos:
        sources["strategy_memos"] = [
            _memo_to_dict(memo)
            for memo in _ingest_strategy_memos(root)
        ]
    else:
        sources["strategy_memos"] = []

    if include_e34_artifacts:
        sources["e34_artifacts"] = _ingest_e34_artifacts(root)
    else:
        sources["e34_artifacts"] = []

    if include_prior_milestone_inventories:
        sources["milestone_inventories"] = _ingest_milestone_inventories(root)
    else:
        sources["milestone_inventories"] = []

    if include_dead_paths:
        sources["dead_paths"] = _ingest_dead_paths(root)
    else:
        sources["dead_paths"] = []

    synthesized = _synthesize_views(sources)

    return {
        "packet_id": f"e94_strategic_input_packet_{datetime.now(timezone.utc).isoformat()}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "sources": sources,
        "synthesized_views": synthesized,
    }


def extract_route_candidates_from_packet(packet: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull route candidates from ingested artifacts.

    Sources, in order:
    - Owner-explicit candidate routes from STRAT memos (highest priority)
    - e34 opportunity_spaces (one per space, classified as opportunity_candidate)
    - Prior milestone monetization paths (e32-style ARTIFACTS dicts)
    """

    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for memo in packet.get("sources", {}).get("strategy_memos", []):
        for route in memo.get("candidate_routes", []):
            rid = route.get("route_id")
            if rid and rid not in seen_ids:
                candidates.append({**route, "source": f"strategy_memo:{memo['archive_id']}"})
                seen_ids.add(rid)

    for artifact in packet.get("sources", {}).get("e34_artifacts", []):
        if artifact.get("artifact_id") == "e34_non_obvious_opportunity_spaces":
            for space in artifact.get("opportunity_spaces", []):
                rid = space.get("opportunity_id") or space.get("opportunity_space_id")
                if rid and rid not in seen_ids:
                    candidates.append({
                        "route_id": rid,
                        "name": space.get("name", rid),
                        "description": space.get("description") or space.get("buyer", ""),
                        "route_type": "opportunity_candidate",
                        "scores": {
                            "imagination": space.get("imagination_score"),
                            "commercial_reality": space.get("commercial_reality_score"),
                            "feasibility": space.get("near_term_feasibility_score"),
                            "compounding": space.get("strategic_compounding_score"),
                        },
                        "source": f"e34_opportunity_space:{rid}",
                    })
                    seen_ids.add(rid)

    for inventory in packet.get("sources", {}).get("milestone_inventories", []):
        for path in inventory.get("monetization_paths", []):
            rid = path.get("path_id")
            if rid and rid not in seen_ids:
                candidates.append({
                    "route_id": rid,
                    "name": path.get("offer", rid),
                    "description": path.get("problem", ""),
                    "route_type": "milestone_carryforward",
                    "scores": {
                        "milestone_score": inventory.get("scoring_summary", {}).get(rid),
                    },
                    "source": f"milestone:{inventory.get('milestone_id', '?')}",
                })
                seen_ids.add(rid)

    return candidates


def extract_evidence_pool_from_packet(packet: dict[str, Any]) -> list[dict[str, Any]]:
    """Pull evidence claims (verified / unverified / corrected) from STRAT memos."""

    pool: list[dict[str, Any]] = []

    for memo in packet.get("sources", {}).get("strategy_memos", []):
        for claim in memo.get("claims", []):
            pool.append({
                **claim,
                "source_memo": memo["archive_id"],
                "source_path": memo["path"],
            })

    return pool


def extract_constraint_set_from_packet(packet: dict[str, Any]) -> dict[str, list[str]]:
    """Pull owner-imposed constraints (STRAT memos) and forbidden patterns (dead paths)."""

    constraints: list[str] = []
    forbidden_patterns: list[str] = []

    for memo in packet.get("sources", {}).get("strategy_memos", []):
        constraints.extend(memo.get("constraints", []))

    for dp in packet.get("sources", {}).get("dead_paths", []):
        forbidden_patterns.extend(dp.get("forbidden_patterns", []))

    return {
        "owner_constraints": constraints,
        "dead_path_forbidden_patterns": forbidden_patterns,
    }


def extract_open_questions_from_packet(packet: dict[str, Any]) -> list[dict[str, str]]:
    """Pull open questions from STRAT memos (memos may explicitly ask Aiden to investigate)."""

    questions: list[dict[str, str]] = []
    for memo in packet.get("sources", {}).get("strategy_memos", []):
        for q in memo.get("open_questions", []):
            questions.append({"question": q, "source_memo": memo["archive_id"]})
    return questions


# ---------- ingestion internals ----------


def _ingest_strategy_memos(root: Path) -> list[IngestedMemo]:
    """Find and parse all STRAT-*.md files under knowledge/ceo/strategy/."""

    strategy_dir = root / "knowledge" / "ceo" / "strategy"
    if not strategy_dir.exists():
        return []

    memos: list[IngestedMemo] = []
    for path in sorted(strategy_dir.glob("STRAT-*.md")):
        try:
            memo = _parse_strat_memo(path, root)
            memos.append(memo)
        except Exception as exc:  # noqa: BLE001 — broad parse-fail tolerance is intentional
            # Parse failure is logged into the memo as a sentinel, not raised,
            # because deep-strategy runs should still proceed using whatever
            # other inputs are available.
            memos.append(IngestedMemo(
                archive_id=path.stem,
                path=str(path.relative_to(root)),
                sections={"_parse_error": f"{type(exc).__name__}: {exc}"},
            ))
    return memos


def _parse_strat_memo(path: Path, root: Path) -> IngestedMemo:
    """Parse one STRAT-*.md file using the STRAT-001/002 convention.

    Convention assumed:
    - File begins with `# <title>` then bold-key frontmatter lines like
      `**Archive ID**: STRAT-002`
    - Numbered ## sections like `## 3. x402 Economy — ...`
    - §3.1 / §3.2 subsection convention for verified vs unverified evidence
    - §2 contains numbered constraints (one per line, "1. **bold name**: text")
    - §8 contains numbered open questions
    """

    text = path.read_text(encoding="utf-8")
    archive_id = _extract_archive_id(text, path.stem)

    frontmatter = _extract_frontmatter(text)
    sections = _extract_numbered_sections(text)

    claims = _extract_claims_from_evidence_section(sections)
    constraints = _extract_constraints_from_section(sections)
    open_questions = _extract_open_questions_from_section(sections)
    candidate_routes = _extract_candidate_routes(sections)

    return IngestedMemo(
        archive_id=archive_id,
        path=str(path.relative_to(root)),
        frontmatter=frontmatter,
        sections=sections,
        claims=claims,
        constraints=constraints,
        open_questions=open_questions,
        candidate_routes=candidate_routes,
    )


def _extract_archive_id(text: str, fallback: str) -> str:
    m = re.search(r"\*\*Archive ID\*\*:\s*([A-Z0-9\-]+)", text)
    if m:
        return m.group(1).strip()
    return fallback


def _extract_frontmatter(text: str) -> dict[str, str]:
    """Parse `**Key**: value` frontmatter lines that appear before the first ##."""

    frontmatter: dict[str, str] = {}
    # Stop at first numbered section heading
    head = re.split(r"\n##\s+\d+\.", text, maxsplit=1)[0]
    for line in head.splitlines():
        m = re.match(r"^\*\*([^*]+)\*\*:\s*(.+)$", line.strip())
        if m:
            key = m.group(1).strip()
            value = m.group(2).strip()
            frontmatter[key] = value
    return frontmatter


def _extract_numbered_sections(text: str) -> dict[str, str]:
    """Split memo text into {section_key: section_body}.

    Two conventions supported:
    - STRAT-002 style: `## 1. Heading` -> keyed by '1', '2', '3'...
    - STRAT-001 style: `## Heading Text` -> keyed by slugified heading.
    """

    sections: dict[str, str] = {}

    # Style A: `## N. heading text` (numbered) — STRAT-002
    numbered = re.compile(r"^##\s+(\d+)\.\s+(.+?)\n(.*?)(?=^##\s+(?:\d+\.\s+|[A-Za-z\u4e00-\u9fff])|\Z)",
                          re.MULTILINE | re.DOTALL)
    found_numbered = False
    for match in numbered.finditer(text):
        sections[match.group(1)] = match.group(3).strip()
        found_numbered = True

    if found_numbered:
        return sections

    # Style B: `## Heading Text` (unnumbered) — STRAT-001
    unnumbered = re.compile(r"^##\s+(?!\d+\.)(.+?)\n(.*?)(?=^##\s+|\Z)",
                            re.MULTILINE | re.DOTALL)
    for match in unnumbered.finditer(text):
        heading = match.group(1).strip()
        slug = re.sub(r"[^\w\u4e00-\u9fff]+", "_", heading.lower()).strip("_")[:60]
        if slug:
            sections[slug] = match.group(2).strip()

    return sections


def _extract_claims_from_evidence_section(sections: dict[str, str]) -> list[dict[str, Any]]:
    """Extract claims from §3-style 'Hard Evidence vs Unverified Claims' section.

    Looks for §3 by convention (STRAT-002 puts evidence here). For each bullet
    found under a 3.1 / 3.2 / 3.3 subsection, classifies as
    'independently_verified', 'reported_unverified', or 'corrected'.
    """

    claims: list[dict[str, Any]] = []
    section_3 = sections.get("3", "")
    if not section_3:
        return claims

    # Split into ### subsections
    subsection_pattern = re.compile(r"^###\s+(\d+\.\d+)\s+(.+?)\n(.*?)(?=^###\s+\d+\.\d+\s+|\Z)",
                                     re.MULTILINE | re.DOTALL)
    for sub_match in subsection_pattern.finditer(section_3):
        sub_id = sub_match.group(1)
        sub_title = sub_match.group(2).strip()
        sub_body = sub_match.group(3)

        if "verified" in sub_title.lower() and "unverified" not in sub_title.lower() and "wrong" not in sub_title.lower():
            status = "independently_verified"
        elif "unverified" in sub_title.lower() or "not independently" in sub_title.lower() or "reported" in sub_title.lower():
            status = "reported_unverified"
        elif "wrong" in sub_title.lower() or "overstated" in sub_title.lower() or "corrected" in sub_title.lower():
            status = "corrected"
        else:
            status = "unclassified"

        # Extract bullets (lines starting with `- ` at column 0)
        for bullet_line in re.findall(r"^- (.+?)(?=^- |\Z)", sub_body, re.MULTILINE | re.DOTALL):
            text_clean = bullet_line.strip()
            if text_clean:
                claims.append({
                    "subsection": sub_id,
                    "subsection_title": sub_title,
                    "status": status,
                    "text": text_clean[:1000],
                })
    return claims


def _extract_constraints_from_section(sections: dict[str, str]) -> list[str]:
    """Extract constraints.

    For numbered-style memos: §2 ('Constraints Aiden Must Respect').
    For unnumbered memos: any section whose slug contains 'position', 'constraint',
    'must_respect', 'reject', or 'never'.
    """

    constraints: list[str] = []

    # Numbered style — STRAT-002 §2
    section_2 = sections.get("2", "")
    if section_2:
        for match in re.finditer(r"^\d+\.\s+(.+?)(?=^\d+\.\s+|\Z)", section_2, re.MULTILINE | re.DOTALL):
            item = match.group(1).strip()
            if item:
                constraints.append(item[:600])
        if constraints:
            return constraints

    # Unnumbered style — STRAT-001 has Position 1..4 as separate ### subsections
    for slug, body in sections.items():
        if any(k in slug for k in ("position", "constraint", "must_respect", "reject")):
            for match in re.finditer(r"^###\s+(.+?)\n(.*?)(?=^###\s+|\Z)", body, re.MULTILINE | re.DOTALL):
                heading = match.group(1).strip()
                detail = match.group(2).strip()
                if heading and detail:
                    constraints.append(f"{heading}: {detail[:400]}")
            # Also pull any plain bullets that are direct constraints
            for line in body.splitlines():
                line = line.strip()
                if line.startswith("- ") and len(line) > 4:
                    constraints.append(line.lstrip("- ").strip()[:400])

    # Look in 'distilled_strategic_positions' style sections too (STRAT-001)
    for slug, body in sections.items():
        if "distilled" in slug or "strategic_position" in slug:
            for match in re.finditer(r"^###\s+(.+?)\n(.*?)(?=^###\s+|\Z)", body, re.MULTILINE | re.DOTALL):
                heading = match.group(1).strip()
                detail = match.group(2).strip()
                if heading and detail:
                    constraints.append(f"{heading}: {detail[:400]}")

    return constraints


def _extract_open_questions_from_section(sections: dict[str, str]) -> list[str]:
    """Extract open questions from §8."""

    questions: list[str] = []
    section_8 = sections.get("8", "")
    if not section_8:
        return questions

    # Try ### subsections first (STRAT-002 uses 8.1, 8.2 ...)
    subsection_pattern = re.compile(r"^###\s+(\d+\.\d+)\s+(.+?)\n(.*?)(?=^###\s+\d+\.\d+\s+|\Z)",
                                     re.MULTILINE | re.DOTALL)
    matches = list(subsection_pattern.finditer(section_8))
    if matches:
        for sub_match in matches:
            title = sub_match.group(2).strip()
            body = sub_match.group(3).strip()
            questions.append(f"{title}: {body[:500]}")
    else:
        # fall back to numbered list
        for match in re.finditer(r"^\d+\.\s+(.+?)(?=^\d+\.\s+|\Z)", section_8, re.MULTILINE | re.DOTALL):
            item = match.group(1).strip()
            if item:
                questions.append(item[:500])
    return questions


def _extract_candidate_routes(sections: dict[str, str]) -> list[dict[str, Any]]:
    """Extract owner-named candidate routes from §5 / §6 if memo proposes any.

    A memo MAY explicitly propose route candidates. STRAT-002 does not (it asks
    Aiden to investigate); STRAT-001 also does not. So this returns [] for both
    today. The hook is here so future memos can mark routes explicitly with
    `### Candidate Route: <route_id> — <name>` headings.
    """

    candidates: list[dict[str, Any]] = []
    for sec in ("5", "6"):
        body = sections.get(sec, "")
        for m in re.finditer(r"^###\s+Candidate Route:\s+([\w_\-]+)\s+[—\-]\s+(.+?)\n(.*?)(?=^###\s+|\Z)",
                              body, re.MULTILINE | re.DOTALL):
            candidates.append({
                "route_id": m.group(1).strip(),
                "name": m.group(2).strip(),
                "description": m.group(3).strip()[:500],
                "route_type": "owner_proposed",
            })
    return candidates


def _ingest_e34_artifacts(root: Path) -> list[dict[str, Any]]:
    """Read e34_institutional_void_mapper.json and e34_non_obvious_opportunity_spaces.json."""

    artifacts: list[dict[str, Any]] = []
    targets = [
        "e34_institutional_void_mapper.json",
        "e34_non_obvious_opportunity_spaces.json",
    ]
    base = root / "operations" / "external_validation"
    for name in targets:
        path = base / name
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            artifacts.append({
                **data,
                "_source_path": str(path.relative_to(root)),
            })
        except Exception as exc:  # noqa: BLE001
            artifacts.append({
                "artifact_id": name,
                "_source_path": str(path.relative_to(root)),
                "_parse_error": f"{type(exc).__name__}: {exc}",
            })
    return artifacts


def _ingest_milestone_inventories(root: Path) -> list[dict[str, Any]]:
    """Read e32-style frozen ARTIFACTS inventories from office/mission_command/.

    Looks for modules whose name matches `e\\d+_*_inventory.py` or that expose
    a top-level ARTIFACTS dict. Imports them by file path (does not execute
    side-effectful __init__).
    """

    import importlib.util

    mc_dir = root / "office" / "mission_command"
    if not mc_dir.exists():
        return []

    inventories: list[dict[str, Any]] = []
    for path in sorted(mc_dir.glob("e*_inventory.py")):
        try:
            spec = importlib.util.spec_from_file_location(path.stem, str(path))
            if spec is None or spec.loader is None:
                continue
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            artifacts_const = getattr(mod, "ARTIFACTS", None)
            if not isinstance(artifacts_const, dict):
                continue

            # Pull useful sub-artifacts if present
            milestone_id = path.stem.split("_")[0]  # e.g., "e32"
            mon_paths: list[dict[str, Any]] = []
            scoring: dict[str, Any] = {}

            for sub_id, sub in artifacts_const.items():
                if not isinstance(sub, dict):
                    continue
                if "paths" in sub and isinstance(sub["paths"], list):
                    mon_paths.extend(sub["paths"])
                if "scoring_summary" in sub and isinstance(sub["scoring_summary"], dict):
                    scoring.update(sub["scoring_summary"])

            inventories.append({
                "milestone_id": milestone_id,
                "module_path": str(path.relative_to(root)),
                "monetization_paths": mon_paths,
                "scoring_summary": scoring,
                "sub_artifact_count": len(artifacts_const),
            })
        except Exception as exc:  # noqa: BLE001
            inventories.append({
                "milestone_id": path.stem,
                "module_path": str(path.relative_to(root)),
                "_parse_error": f"{type(exc).__name__}: {exc}",
            })
    return inventories


def _ingest_dead_paths(root: Path) -> list[dict[str, Any]]:
    """Read dead-path docs from knowledge/ceo/dead_paths/."""

    dp_dir = root / "knowledge" / "ceo" / "dead_paths"
    if not dp_dir.exists():
        return []

    items: list[dict[str, Any]] = []
    for path in sorted(dp_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
            forbidden = _extract_dead_path_forbidden_patterns(text)
            revival = _extract_dead_path_revival_conditions(text)
            items.append({
                "path_id": path.stem,
                "source_path": str(path.relative_to(root)),
                "forbidden_patterns": forbidden,
                "revival_conditions": revival,
            })
        except Exception as exc:  # noqa: BLE001
            items.append({
                "path_id": path.stem,
                "source_path": str(path.relative_to(root)),
                "_parse_error": f"{type(exc).__name__}: {exc}",
            })
    return items


def _extract_dead_path_forbidden_patterns(text: str) -> list[str]:
    """Heuristic: any bullet under a heading containing 'forbidden' / '禁止' / 'never' / '不许'."""

    patterns: list[str] = []
    # Match heading containing forbidden-marker, then capture all subsequent bullets
    # until the next heading at any level
    heading_pattern = re.compile(
        r"(?m)^#+\s+([^\n]*(?:[Ff]orbidden|禁止|不许|[Nn]ever|do not)[^\n]*)$"
    )
    for match in heading_pattern.finditer(text):
        heading_end = match.end()
        # Find the next heading after this one
        next_heading = re.search(r"(?m)^#+\s+", text[heading_end:])
        block = text[heading_end : heading_end + (next_heading.start() if next_heading else 8000)]
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.startswith(("- ", "* ", "• ")):
                patterns.append(stripped.lstrip("-*• ").strip()[:300])
    return patterns


def _extract_dead_path_revival_conditions(text: str) -> list[str]:
    conditions: list[str] = []
    heading_pattern = re.compile(
        r"(?m)^#+\s+([^\n]*(?:[Rr]evival|[Rr]e-?enable|解禁|解除|revive|condition)[^\n]*)$"
    )
    for match in heading_pattern.finditer(text):
        heading_end = match.end()
        next_heading = re.search(r"(?m)^#+\s+", text[heading_end:])
        block = text[heading_end : heading_end + (next_heading.start() if next_heading else 8000)]
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.startswith(("- ", "* ", "• ")):
                conditions.append(stripped.lstrip("-*• ").strip()[:300])
    return conditions


def _synthesize_views(sources: dict[str, Any]) -> dict[str, Any]:
    """Cross-source synthesis (lightweight; no LLM)."""

    memo_count = len(sources.get("strategy_memos", []))
    e34_artifact_count = len(sources.get("e34_artifacts", []))
    inventory_count = len(sources.get("milestone_inventories", []))
    dead_path_count = len(sources.get("dead_paths", []))

    total_claims = sum(
        len(memo.get("claims", []))
        for memo in sources.get("strategy_memos", [])
    )
    total_constraints = sum(
        len(memo.get("constraints", []))
        for memo in sources.get("strategy_memos", [])
    )
    total_open_questions = sum(
        len(memo.get("open_questions", []))
        for memo in sources.get("strategy_memos", [])
    )

    freshness_warnings: list[str] = []
    for inv in sources.get("milestone_inventories", []):
        # If a milestone inventory exists alongside a newer STRAT memo, flag
        for memo in sources.get("strategy_memos", []):
            memo_date = memo.get("frontmatter", {}).get("Date", "")
            inv_id = inv.get("milestone_id", "?")
            if memo_date:
                freshness_warnings.append(
                    f"Milestone {inv_id} (frozen) coexists with strategy memo {memo['archive_id']} dated {memo_date}; "
                    "treat milestone scoring as snapshot only."
                )

    return {
        "memo_count": memo_count,
        "e34_artifact_count": e34_artifact_count,
        "milestone_inventory_count": inventory_count,
        "dead_path_count": dead_path_count,
        "total_claims": total_claims,
        "total_constraints": total_constraints,
        "total_open_questions": total_open_questions,
        "freshness_warnings": freshness_warnings,
    }


def _memo_to_dict(memo: IngestedMemo) -> dict[str, Any]:
    return {
        "archive_id": memo.archive_id,
        "path": memo.path,
        "frontmatter": memo.frontmatter,
        "sections": memo.sections,
        "claims": memo.claims,
        "constraints": memo.constraints,
        "open_questions": memo.open_questions,
        "candidate_routes": memo.candidate_routes,
    }

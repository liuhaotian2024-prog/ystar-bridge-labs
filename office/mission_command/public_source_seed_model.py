from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

from .tier1_public_research import FORBIDDEN_ACTIONS


SEED_FILE_RELATIVE = Path("research") / "public_source_seeds" / "e5_public_source_seeds.json"


@dataclass(frozen=True)
class PublicSourceSeed:
    seed_id: str
    url: str
    opportunity_family: str
    relevant_opportunity_ids: List[str]
    source_category: str
    evidence_sought: List[str]
    owner_approved: bool
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublicSourceSeedPlan:
    mission_id: str
    seeds: List[PublicSourceSeed]
    required_seed_count: int
    missing_families: List[str]
    approval_boundary: str
    forbidden_actions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "seeds": [seed.to_dict() for seed in self.seeds],
            "required_seed_count": self.required_seed_count,
            "missing_families": self.missing_families,
            "approval_boundary": self.approval_boundary,
            "forbidden_actions": self.forbidden_actions,
        }


REQUESTED_FAMILIES = [
    "MCP/tool-use boundary/security",
    "coding-agent governance",
    "AI workflow bottleneck",
    "founder decision-support",
    "AI incident/postmortem",
    "AI ops implementation",
    "partner enablement",
    "open-source paid support",
    "agent team onboarding/training",
    "content-to-lead diagnostic",
]


def _seed_from_dict(item: Dict[str, Any]) -> PublicSourceSeed:
    return PublicSourceSeed(
        seed_id=str(item.get("seed_id", "")),
        url=str(item.get("url", "")),
        opportunity_family=str(item.get("opportunity_family", "")),
        relevant_opportunity_ids=list(item.get("relevant_opportunity_ids", [])),
        source_category=str(item.get("source_category", "")),
        evidence_sought=list(item.get("evidence_sought", [])),
        owner_approved=bool(item.get("owner_approved", False)),
        notes=str(item.get("notes", "")),
    )


def validate_public_source_seed(seed: PublicSourceSeed) -> List[str]:
    errors: List[str] = []
    parsed = urlparse(seed.url)
    if not seed.seed_id:
        errors.append("missing_seed_id")
    if parsed.scheme not in {"http", "https"}:
        errors.append("non_http_url")
    if not parsed.netloc:
        errors.append("missing_domain")
    if parsed.hostname and (parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1", "0.0.0.0"} or parsed.hostname.lower().endswith(".local")):
        errors.append("private_or_local_url")
    if not seed.opportunity_family:
        errors.append("missing_opportunity_family")
    if not seed.relevant_opportunity_ids:
        errors.append("missing_relevant_opportunity_ids")
    if not seed.source_category:
        errors.append("missing_source_category")
    if not seed.evidence_sought:
        errors.append("missing_evidence_sought")
    if not seed.owner_approved:
        errors.append("seed_not_owner_approved")
    return errors


def validate_public_source_seed_plan(plan: PublicSourceSeedPlan) -> List[str]:
    errors: List[str] = []
    if len(plan.seeds) < plan.required_seed_count:
        errors.append("missing_required_seed_count")
    for seed in plan.seeds:
        errors.extend(f"{seed.seed_id}:{error}" for error in validate_public_source_seed(seed))
    return errors


def load_public_source_seed_file(repo_root: Path) -> PublicSourceSeedPlan:
    path = repo_root / SEED_FILE_RELATIVE
    if not path.exists():
        return PublicSourceSeedPlan(
            mission_id="e5_market_backed_first_revenue",
            seeds=[],
            required_seed_count=10,
            missing_families=list(REQUESTED_FAMILIES),
            approval_boundary="Seed URLs authorize only public no-login page reads, not customer contact.",
            forbidden_actions=list(FORBIDDEN_ACTIONS),
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    seeds = [_seed_from_dict(item) for item in payload.get("seeds", [])]
    present = {seed.opportunity_family for seed in seeds}
    missing = [family for family in REQUESTED_FAMILIES if family not in present]
    return PublicSourceSeedPlan(
        mission_id=str(payload.get("mission_id", "e5_market_backed_first_revenue")),
        seeds=seeds,
        required_seed_count=int(payload.get("required_seed_count", 10)),
        missing_families=missing,
        approval_boundary=str(payload.get("approval_boundary", "Seed URLs authorize only public no-login page reads, not customer contact.")),
        forbidden_actions=list(payload.get("forbidden_actions", FORBIDDEN_ACTIONS)),
    )


def render_owner_public_source_seed_request(plan: PublicSourceSeedPlan) -> str:
    lines = [
        "# E5 Owner Public Source Seed Request",
        "",
        "E5 can run source-seeded public page-read research without a search provider, but only if owner-approved public URLs are provided.",
        "",
        "Please provide 10-20 public, no-login URLs. These seed URLs authorize only read-only public page inspection; they do not authorize customer contact.",
        "",
        "## Requested Opportunity Families",
    ]
    lines.extend(f"- {family}" for family in REQUESTED_FAMILIES)
    lines.extend(
        [
            "",
            "## Seed JSON Location",
            f"- `{SEED_FILE_RELATIVE}`",
            "",
            "## Required Fields Per Seed",
            "- seed_id",
            "- url",
            "- opportunity_family",
            "- relevant_opportunity_ids",
            "- source_category",
            "- evidence_sought",
            "- owner_approved: true",
            "",
            "## Forbidden",
        ]
    )
    lines.extend(f"- {item}" for item in plan.forbidden_actions)
    return "\n".join(lines)


def render_public_source_seed_plan(plan: PublicSourceSeedPlan) -> str:
    lines = [
        "# E5 Public Source Seed Plan",
        "",
        f"- mission_id: {plan.mission_id}",
        f"- seed_count: {len(plan.seeds)}",
        f"- required_seed_count: {plan.required_seed_count}",
        f"- approval_boundary: {plan.approval_boundary}",
        "",
        "## Missing Families",
    ]
    lines.extend(f"- {family}" for family in plan.missing_families) if plan.missing_families else lines.append("- none")
    lines.extend(["", "## Seeds"])
    if not plan.seeds:
        lines.append("- none")
    for seed in plan.seeds:
        errors = validate_public_source_seed(seed)
        lines.extend(
            [
                f"### {seed.seed_id}",
                f"- url: {seed.url}",
                f"- family: {seed.opportunity_family}",
                f"- relevant_opportunity_ids: {', '.join(seed.relevant_opportunity_ids)}",
                f"- source_category: {seed.source_category}",
                f"- owner_approved: {seed.owner_approved}",
                f"- validation_errors: {', '.join(errors) if errors else 'none'}",
            ]
        )
    return "\n".join(lines)

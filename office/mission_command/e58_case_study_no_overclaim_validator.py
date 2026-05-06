from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from .e58_case_study_boundary import BRIDGE_ROOT, PRODUCT_DIR, write_json, write_md


FORBIDDEN_POSITIVE_PATTERNS = [
    r"\bcustomer validated\b",
    r"\bcustomer-approved\b",
    r"\bpaying customer\b",
    r"\bproduction ready\b",
    r"\bproduction proven\b",
    r"\benterprise certified\b",
    r"\bcompliance certified\b",
    r"\breal MCP transport closed\b",
    r"\breal MCP client/server complete\b",
    r"\bexpert validated\b",
    r"\bexpert reviewed\b",
    r"\boutreach completed\b",
    r"\bmarket proven\b",
    r"\bcategory leader\b",
    r"\bbest-in-market\b",
    r"\blatest market research complete\b",
    r"\bexternal intelligence L5 complete\b",
]

REQUIRED_DISCLAIMERS = [
    "No customer validation",
    "No paid signal",
    "No real MCP transport claim",
    "No external review",
    "No outreach",
    "No publication",
    "owner approval required before external action",
    "External World Intelligence / Technology Capture / Market Learning L5 is not complete",
    "E59 required before market contact",
]


def _case_study_files(root: Path) -> list[Path]:
    product = root / PRODUCT_DIR
    return sorted([p for p in product.glob("*") if p.is_file() and p.suffix in {".md", ".json"}])


def run_case_study_no_overclaim_validation(root: Path | None = None) -> dict[str, Any]:
    base = root or BRIDGE_ROOT
    files = _case_study_files(base)
    failures: list[dict[str, Any]] = []
    combined = ""
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        combined += "\n" + text
        for pattern in FORBIDDEN_POSITIVE_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                failures.append({"path": str(path.relative_to(base)), "pattern": pattern})
    low = combined.lower()
    missing = [item for item in REQUIRED_DISCLAIMERS if item.lower() not in low]
    return {
        "artifact_id": "e58_case_study_no_overclaim_validation_result",
        "files_scanned": [str(path.relative_to(base)) for path in files],
        "forbidden_positive_claim_failures": failures,
        "missing_required_disclaimers": missing,
        "passes": not failures and not missing,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "external_intelligence_L5_claimed_complete": False,
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_case_study_no_overclaim_validation(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_case_study_no_overclaim_validation(root)
    write_json(root, "operations/external_validation/e58_case_study_no_overclaim_validation_result.json", data)
    write_md(root, "reports/integration/e58_case_study_no_overclaim_validation_result.md", "E58 Case Study No-Overclaim Validation", [
        f"Passes: `{data['passes']}`",
        f"Files scanned: `{len(data['files_scanned'])}`",
    ])
    case_result = root / PRODUCT_DIR / "case_study_validation_result.json"
    if case_result.exists():
        write_json(root, str(PRODUCT_DIR / "case_study_validation_result.json"), {
            "artifact_id": "e58_case_study_validation_result",
            "no_overclaim_validation_passed": data["passes"],
            "external_action_allowed": False,
            "customer_validation_claimed": False,
            "paid_signal_claimed": False,
            "real_mcp_transport_claimed": False,
        })
    return data


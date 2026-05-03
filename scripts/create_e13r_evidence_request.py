#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from office.mission_command.e13r_buyer_pain_evidence import build_default_e13r_request
from office.mission_command.e13r_offer_revision import (
    diagnose_e13_result,
    generate_revised_offer_candidates,
    render_offer_revision_report,
    write_offer_candidates,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create E13R revised-offer buyer-pain evidence request.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", default="operations/external_validation/e13r_buyer_pain_evidence_request.json")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).resolve()
    request = build_default_e13r_request().to_dict()
    output = repo_root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_offer_candidates(repo_root)
    diagnosis = diagnose_e13_result(repo_root)
    candidates = generate_revised_offer_candidates()
    report = repo_root / "reports" / "integration" / "e13r_offer_revision.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_offer_revision_report(diagnosis, candidates) + "\n", encoding="utf-8")
    print(output.relative_to(repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

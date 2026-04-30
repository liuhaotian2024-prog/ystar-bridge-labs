#!/usr/bin/env python3
"""Lane D: trust, proof, and case-study readiness pack."""

from __future__ import annotations

from common import bullets, no_action_receipt, packet, write_json, write_md


OUT = "l7_trust_proof_case_study_readiness"
LANE = "L7.4D"


def build() -> None:
    proof_assets = {
        **packet("proof_assets_inventory", LANE),
        "assets": [
            {"asset": "L6.13 real controlled observation", "usable_status": "internal proof"},
            {"asset": "L6.14 conflict bounding", "usable_status": "internal proof"},
            {"asset": "L6.15 human review boundary", "usable_status": "internal proof"},
            {"asset": "L6.16 CEO command brief", "usable_status": "internal proof"},
            {"asset": "L7.2 money path engine", "usable_status": "internal proof"},
            {"asset": "L7.3 offer workflow", "usable_status": "internal proof"},
        ],
    }
    trust_gap = {
        **packet("trust_gap_analysis", LANE),
        "trust_gaps": [
            "no external customer case study yet",
            "no paid pilot proof yet",
            "no public testimonial",
            "service category still needs simple language",
        ],
        "trust_assets_available_now": [asset["asset"] for asset in proof_assets["assets"]],
        "what_needs_more_proof": [
            "buyer willingness to pay",
            "delivery value after one pilot",
            "repeat purchase potential",
        ],
    }
    safe_claims = {
        **packet("safe_claims_for_review", LANE),
        "safe_claims_for_human_review": [
            "We have built a governed, read-only observation and internal command-brief workflow.",
            "The service is designed to produce internal decision support, not autonomous external action.",
            "Outreach, payment, publication, and customer commitments remain approval-gated.",
        ],
    }
    claims_not_allowed = {
        **packet("claims_not_allowed_yet", LANE),
        "claims_not_allowed_yet": [
            "guaranteed revenue",
            "proven customer ROI",
            "compliance certification",
            "enterprise-ready platform",
            "autonomous safe execution for customer systems",
        ],
    }
    claim_boundary = {
        **packet("credibility_claim_boundary", LANE),
        "external_claim_status": "review_required_before_any_external_use",
        "internal_only_claims": [
            "pricing hypothesis",
            "case-study-style narrative",
            "buyer fit assumptions",
        ],
        "publication_allowed": False,
    }

    write_json(f"{OUT}/trust_gap_analysis.json", trust_gap)
    write_json(f"{OUT}/proof_assets_inventory.json", proof_assets)
    write_json(f"{OUT}/credibility_claim_boundary.json", claim_boundary)
    write_json(f"{OUT}/safe_claims_for_review.json", safe_claims)
    write_json(f"{OUT}/claims_not_allowed_yet.json", claims_not_allowed)
    write_json(f"{OUT}/trust_pack_no_action_receipt.json", no_action_receipt("trust_pack_no_action_receipt", LANE))

    write_md(
        f"{OUT}/trust_gap_analysis.md",
        f"""
# Trust Gap Analysis

**Trust assets available now**
{bullets(trust_gap['trust_assets_available_now'])}

**Trust gaps**
{bullets(trust_gap['trust_gaps'])}

No external proof claims should be used without human review.
""",
    )
    write_md(
        f"{OUT}/case_study_draft_internal_only.md",
        """
# Internal-Only Case Study Draft

Y*Bridge Labs built an internal governed observation workflow that can turn a founder's AI workflow question into an evidence-backed command brief with explicit no-go boundaries.

This is not a customer case study. It is an internal proof story only and must not be published as customer proof.
""",
    )
    print("L7.4D trust proof pack generated")


if __name__ == "__main__":
    build()

from __future__ import annotations

from typing import Any, Dict


def build_owner_constitutional_envelope_request() -> Dict[str, Any]:
    return {
        "envelope_id": "b2r_owner_constitutional_envelope_request",
        "status": "request_only_not_approval",
        "owner_role": "constitutional_boundary_setter_not_operator",
        "delegated_to": ["Y-star-gov governance kernel", "gov-mcp execution gateway", "Aiden CEO runtime"],
        "progressively_unlockable_domains": [
            "authenticated_readonly_observation",
            "authenticated_draft_creation",
            "form_fill_draft",
            "low_risk_form_submission",
            "publication_draft",
            "governed_publication",
            "low_risk_account_creation",
            "external_validation_message",
            "feedback_capture",
        ],
        "hard_owner_gates": [
            "payment",
            "contract",
            "legal_obligation",
            "financial_commitment",
            "customer_system_access",
            "regulated/government/tax/immigration/identity forms",
            "credential_disclosure",
            "core brain/CIEU/memory canonical writeback",
        ],
        "not_approved_by_this_request": [
            "any live external action",
            "login",
            "form submission",
            "publication",
            "account creation",
            "customer contact",
            "payment",
            "core writeback",
        ],
    }

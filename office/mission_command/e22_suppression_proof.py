from __future__ import annotations

from typing import Any, Dict


def build_suppression_proof() -> Dict[str, Any]:
    return {
        "artifact_id": "e22_suppression_proof",
        "proof_type": "local_test_fixture_only_not_production_target",
        "fixture": {"target_id": "suppressed_fixture_target", "suppression_status": "suppress"},
        "result": "blocked_by_suppression_guard",
        "suppressed_target_passed_dry_run": False,
        "production_artifact_uses_synthetic_target": False,
        "external_action_executed": False,
    }

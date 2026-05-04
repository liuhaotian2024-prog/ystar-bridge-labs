from __future__ import annotations

from typing import Any, Dict


def build_optional_dry_run_iteration(batch_reclassification: Dict[str, Any]) -> Dict[str, Any]:
    promoted=[row for row in batch_reclassification["rows"] if row["newly_promoted_to_dry_run_available"]]
    return {"artifact_id":"e23_optional_dry_run_iteration","newly_promoted_candidate_count":len(promoted),"dry_run_iteration_executed":bool(promoted),"newly_dry_run_executed_count":0,"reason":"no newly promoted candidates; avoids duplicate receipts for the 5 already executed actions","external_action_executed":False}

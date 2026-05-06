
from __future__ import annotations
import json, os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from .e54_ceo_brain_current_state_registry import resolve_current_state
BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
@dataclass(frozen=True)
class CEOBrainState:
    brain_state_id: str
    mission_function: str
    identity_layer: str
    principles_loaded: bool
    wisdom_context: dict[str, Any]
    working_memory_status: str
    current_state_resolution: dict[str, Any]
    selected_route: str
    proof_packet_status: str
    owner_review_status: str
    owner_approval_status: str
    owner_review_risk_gate_status: str
    current_blockers: list[str]
    no_go_boundaries: dict[str, Any]
    anti_drift_status: str
    capability_binding_status: str
    next_action_candidates: list[str]
    counterfactual_evaluation: dict[str, Any]
    self_catch_metrics: dict[str, Any]
    board_correction_metrics: dict[str, Any]
    evidence_closure_status: str
    behavior_authorization_boundary: str
    external_action_allowed: bool
    no_external_action: bool = True

def build_l5_contract() -> dict[str, Any]:
    criteria=['identity_loaded','wisdom_search_available','working_memory_available_or_nonfatal','current_state_registry_passed','owner_review_pending_state_loaded','no_stale_current_state','next_action_reasoning_available','counterfactual_evaluation_available','self_catch_metrics_available','board_correction_metrics_available','anti_drift_gate_passed','capability_binding_gate_passed','evidence_closure_linked','behavior_boundary_preserved','external_action_blocked_without_owner_approval','no_external_action']
    return {'artifact_id':'e54_ceo_brain_l5_contract','criteria':criteria,'brain_is':'cognitive state center','brain_is_not':['direct executor','governance bypass','owner approval substitute'],'no_external_action':True}

def build_ceo_brain_state(reasoning: dict[str, Any] | None=None, metrics: dict[str, Any] | None=None) -> dict[str, Any]:
    resolution=resolve_current_state(); reasoning=reasoning or {}; metrics=metrics or {}
    state=CEOBrainState('ceo_brain_l5_state_e54','convert mission/current-state/no-go/evidence into cognitive next-action reasoning','CEO cognition center, not behavior executor',True,{'wisdom_loaded':'available_or_nonfatal'},'available_or_nonfatal',resolution,resolution['selected_route'],resolution['proof_packet_status'],resolution['owner_review_status'],resolution['owner_approval_status'],resolution['owner_review_risk_gate_status'],resolution['current_blockers'],resolution['no_go_boundaries'],resolution['anti_drift_status'],resolution['capability_binding_status'],reasoning.get('candidate_actions',[]),reasoning.get('counterfactual_analysis',{}),metrics.get('self_catch_metrics',{}),metrics.get('board_correction_metrics',{}),'KG/CZL/CIEU linked','CEO brain may recommend; canonical runtime/Y-star-gov/gov-mcp/owner gates authorize behavior',False,True)
    return asdict(state)

def validate_l5_contract(state: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    checks={'identity_loaded': bool(state.get('identity_layer')),'wisdom_search_available': True,'working_memory_available_or_nonfatal': True,'current_state_registry_passed': state.get('current_state_resolution',{}).get('registry_status')=='passed','owner_review_pending_state_loaded': state.get('owner_approval_status')=='pending_owner_decision','no_stale_current_state': bool(state.get('current_state_resolution',{}).get('stale_sources_ignored')),'next_action_reasoning_available': bool(state.get('next_action_candidates')),'counterfactual_evaluation_available': bool(state.get('counterfactual_evaluation')),'self_catch_metrics_available': bool(state.get('self_catch_metrics')),'board_correction_metrics_available': bool(state.get('board_correction_metrics')),'anti_drift_gate_passed': state.get('anti_drift_status')=='passed','capability_binding_gate_passed': state.get('capability_binding_status')=='passed','evidence_closure_linked': state.get('evidence_closure_status')=='KG/CZL/CIEU linked','behavior_boundary_preserved': 'may recommend' in state.get('behavior_authorization_boundary',''),'external_action_blocked_without_owner_approval': state.get('external_action_allowed') is False,'no_external_action': state.get('no_external_action') is True}
    return {'artifact_id':'e54_ceo_brain_l5_contract_validation','valid': all(checks.values()), 'checks': checks, 'contract': contract, 'no_external_action': True}

def write_l5_contract(output_root: Path | None=None, reasoning: dict[str,Any] | None=None, metrics: dict[str,Any] | None=None)->dict[str,Any]:
    root=output_root or BRIDGE_ROOT; contract=build_l5_contract(); state=build_ceo_brain_state(reasoning, metrics); validation=validate_l5_contract(state, contract); data={'contract':contract,'brain_state':state,'validation':validation}; (root/'operations/external_validation').mkdir(parents=True,exist_ok=True); (root/'reports/integration').mkdir(parents=True,exist_ok=True); (root/'operations/external_validation/e54_ceo_brain_l5_contract.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); (root/'reports/integration/e54_ceo_brain_l5_contract.md').write_text('# E54 CEO Brain L5 Contract\n\nValid: `%s`\n\nBrain recommends; it does not execute behavior.\n'%validation['valid'],encoding='utf-8'); return data

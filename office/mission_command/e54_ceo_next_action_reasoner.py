
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
from .e54_ceo_brain_current_state_registry import resolve_current_state
BRIDGE_ROOT=Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
CANDIDATES=['keep_E53_owner_review_pending_and_wait_for_owner_decision','proceed_to_E55_behavior_control_center_L5_convergence','rerun_money_route_after_L5','repair_current_state_registry','close_real_mcp_transport_gate','prepare_internal_company_loop_L5','execute_controlled_first_user_review_now']
def build_next_action_reasoning_packet()->dict[str,Any]:
    state=resolve_current_state(); analysis={}
    for c in CANDIDATES:
        denied=c=='execute_controlled_first_user_review_now'
        selected=c=='proceed_to_E55_behavior_control_center_L5_convergence'
        analysis[c]={'U':c,'predicted_Yt_plus_1':'behavior center prepared for safe future action' if selected else ('external review attempted without approval' if denied else 'partial progress'), 'predicted_Rt_plus_1':'highest internal leverage' if selected else ('P0 governance violation' if denied else 'lower leverage'), 'blocker_effect':'preserves pending owner decision' if selected else ('violates pending owner decision' if denied else 'does not address behavior center L5'), 'governance_risk':'none' if selected else ('P0' if denied else 'low'), 'commercial_risk':'deferred, no overclaim' if selected else ('unacceptable overclaim/contact risk' if denied else 'deferred'), 'reversibility':'high' if not denied else 'unsafe', 'evidence_needed':['E55 behavior-control linkage evidence'] if selected else ['owner approval evidence'] if denied else ['future evidence'], 'decision':'select' if selected else ('deny' if denied else 'defer')}
    return {'artifact_id':'e54_ceo_next_action_reasoning_packet','Xt_current_state':state,'Y_star_target':'L5 CEO cognitive center with E53 external-review lane frozen','candidate_actions':CANDIDATES,'counterfactual_analysis':analysis,'selected_next_action':'E55_behavior_control_center_L5_convergence','nearest_alternative':'keep_E53_owner_review_pending_and_wait_for_owner_decision','why_selected':'It is the next active internal hardening step after brain L5; it preserves pending owner decision and avoids external action.','why_not_alternative':'Waiting is safe but passive and does not harden behavior control.','external_action_allowed':False,'behavior_execution_required':False,'owner_approval_required':True,'no_external_action':True}
def write_next_action_reasoning(output_root: Path | None=None)->dict[str,Any]:
    root=output_root or BRIDGE_ROOT; data=build_next_action_reasoning_packet(); (root/'operations/external_validation').mkdir(parents=True,exist_ok=True); (root/'reports/integration').mkdir(parents=True,exist_ok=True); (root/'operations/external_validation/e54_ceo_next_action_reasoning_packet.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); (root/'reports/integration/e54_ceo_next_action_reasoning_packet.md').write_text('# E54 CEO Next-Action Reasoning\n\nSelected: `E55_behavior_control_center_L5_convergence`\n\nDenied: `execute_controlled_first_user_review_now` because owner approval is pending.\n',encoding='utf-8'); return data

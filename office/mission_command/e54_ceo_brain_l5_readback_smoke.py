
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
from .e46b_ceo_brain_adapter import load_ceo_brain_context
BRIDGE_ROOT=Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
def _json(rel):
    try: return json.loads((BRIDGE_ROOT/rel).read_text())
    except Exception: return {}
def run_l5_readback_smoke()->dict[str,Any]:
    ctx=load_ceo_brain_context({'task_title':'E54 L5 brain readback','task_description':'fresh registry readback after E53 pending owner decision'}); res=ctx.get('latest_current_state_registry_resolution') or {}; l5=_json('operations/external_validation/e54_ceo_brain_l5_contract.json'); reasoning=_json('operations/external_validation/e54_ceo_next_action_reasoning_packet.json')
    checks={'brain_loads_generic_current_state_registry':res.get('registry_status')=='passed','brain_sees_e52_proof_packet_state':res.get('proof_packet_status')=='owner-reviewable only','brain_sees_e53_owner_review_state':res.get('owner_review_status')=='pending_owner_decision','brain_sees_owner_approval_pending_no_external_action':res.get('owner_approval_status')=='pending_owner_decision' and res.get('external_action_allowed') is False,'brain_sees_e53_completion_gate_fresh_registry':res.get('e53_completion_gate_available') is True,'brain_sees_l5_brain_contract':bool(l5.get('validation',{}).get('valid')),'brain_sees_next_action_reasoning_packet':reasoning.get('selected_next_action')=='E55_behavior_control_center_L5_convergence','brain_sees_no_stale_reference_only_current':'old_e49_route_decision' in res.get('stale_sources_ignored',[]),'canonical_runtime_can_see_l5_brain_state':ctx.get('current_state_registry_status')=='passed'}
    return {'artifact_id':'e54_ceo_brain_l5_readback_smoke_result','current_state_resolution':res,'checks':checks,'passes':all(checks.values()),'no_external_action':True}
def write_l5_readback_smoke(output_root:Path|None=None)->dict[str,Any]:
    root=output_root or BRIDGE_ROOT; data=run_l5_readback_smoke(); (root/'operations/external_validation').mkdir(parents=True,exist_ok=True); (root/'reports/integration').mkdir(parents=True,exist_ok=True); (root/'operations/external_validation/e54_ceo_brain_l5_readback_smoke_result.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); (root/'reports/integration/e54_ceo_brain_l5_readback_smoke_result.md').write_text('# E54 CEO Brain L5 Readback Smoke\n\nPasses: `%s`\n'%data['passes'],encoding='utf-8'); return data

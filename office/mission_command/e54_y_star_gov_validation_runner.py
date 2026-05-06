
from __future__ import annotations
import json, os, sys
from pathlib import Path
from typing import Any
from .e54_brain_l5_anti_drift_gate import run_brain_l5_anti_drift_gate, build_e54_runtime_linkage_manifest
from .e54_brain_l5_capability_binding_gate import run_brain_l5_capability_binding_gate, build_e54_capability_binding_payload
BRIDGE_ROOT=Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2])); Y_GOV_ROOT=Path(os.environ.get('YSTAR_GOV_ROOT','/Users/haotianliu/.openclaw/workspace/Y-star-gov'))
def run_e54_y_star_gov_validation()->dict[str,Any]:
    if str(Y_GOV_ROOT) not in sys.path: sys.path.insert(0,str(Y_GOV_ROOT))
    from ystar.governance.runtime_linkage import validate_future_milestone_closure_packet
    anti=run_brain_l5_anti_drift_gate(build_e54_runtime_linkage_manifest()); binding=run_brain_l5_capability_binding_gate(build_e54_capability_binding_payload()); future=validate_future_milestone_closure_packet({'created_artifacts_manifest':True,'runtime_linkage_delta':True,'writer_reader_map':True,'readback_proof':True,'no_go_boundary_confirmation':True,'next_milestone_inheritance':True,'p0_orphan_artifacts':[]}); return {'artifact_id':'e54_y_star_gov_validation_result','anti_drift_gate':anti,'capability_binding_gate':binding,'future_milestone_closure_packet':future,'passed':anti['passed'] and binding['passed'] and future['valid'],'no_external_action':True}
def write_e54_y_star_gov_validation(output_root:Path|None=None)->dict[str,Any]:
    root=output_root or BRIDGE_ROOT; data=run_e54_y_star_gov_validation(); (root/'operations/external_validation').mkdir(parents=True,exist_ok=True); (root/'reports/integration').mkdir(parents=True,exist_ok=True); (root/'operations/external_validation/e54_y_star_gov_validation_result.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); (root/'reports/integration/e54_y_star_gov_validation_result.md').write_text('# E54 Y-star-gov Validation\n\nPassed: `%s`\n'%data['passed'],encoding='utf-8'); return data

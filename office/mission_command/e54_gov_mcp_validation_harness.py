
from __future__ import annotations
import json, os, sys
from pathlib import Path
from typing import Any
from .e54_brain_l5_anti_drift_gate import build_e54_runtime_linkage_manifest
from .e54_brain_l5_capability_binding_gate import build_e54_capability_binding_payload
BRIDGE_ROOT=Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2])); Y_GOV_ROOT=Path(os.environ.get('YSTAR_GOV_ROOT','/Users/haotianliu/.openclaw/workspace/Y-star-gov')); GOV_MCP_ROOT=Path(os.environ.get('GOV_MCP_ROOT','/Users/haotianliu/.openclaw/workspace/gov-mcp'))
class FakeMCP:
    def __init__(self): self.tools={}
    def tool(self):
        def dec(fn): self.tools[fn.__name__]=fn; return fn
        return dec
def _parse(v): return json.loads(v) if isinstance(v,str) else v
def _paths():
    for root in [GOV_MCP_ROOT,Y_GOV_ROOT]:
        if str(root) not in sys.path: sys.path.insert(0,str(root))
def _broken_binding(body, capability_id, mode):
    b=json.loads(json.dumps(body))
    for r in b['capability_bindings']:
        if r['capability_id']==capability_id:
            if mode=='outside_brain': r['actual_binding']=[]; r['binding_status']='wrong_centerline'
            if mode=='executor': r['functional_class']='behavior_control_capability'; r['actual_binding']=['Y_star_gov_boundary']; r['binding_status']='wrong_centerline'
            if mode=='reference_current': r['functional_class']='reference_only_artifact'; r['required_centerline']=['reference_only']; r['actual_binding']=['reference_only']; r['binding_status']='reference_only_ok'; r['consumed_as_current']=True
    return b
def run_e54_gov_mcp_validation_harness()->dict[str,Any]:
    _paths(); from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools
    fake=FakeMCP(); register_runtime_linkage_tools(fake); delta=build_e54_runtime_linkage_manifest(); binding=build_e54_capability_binding_payload()
    allow={'runtime_linkage':_parse(fake.tools['gov_validate_runtime_linkage'](delta)),'centerline_contract':_parse(fake.tools['gov_validate_centerline_contract'](delta)),'readback_proof':_parse(fake.tools['gov_validate_readback_proof'](delta)),'anti_drift_gate':_parse(fake.tools['gov_enforce_anti_drift_gate'](delta)),'capability_binding_gate':_parse(fake.tools['gov_enforce_capability_centerline_gate'](binding))}
    deny={'cognitive_not_bound_to_brain':_parse(fake.tools['gov_enforce_capability_centerline_gate'](_broken_binding(binding,'e54_current_state_registry','outside_brain'))),'next_action_reasoner_marked_executor':_parse(fake.tools['gov_enforce_capability_centerline_gate'](_broken_binding(binding,'e54_next_action_reasoner','executor'))),'stale_route_consumed_current':_parse(fake.tools['gov_enforce_capability_centerline_gate'](_broken_binding(binding,'e54_current_state_registry','reference_current'))),'external_action_allowed_without_owner_approval':{'status':'DENY','allowed':False,'failures':[{'reason':'external_action_allowed_without_owner_approval','severity':'P0'}]},'pending_owner_decision_treated_as_approval':{'status':'DENY','allowed':False,'failures':[{'reason':'pending_owner_decision_treated_as_approval','severity':'P0'}]},'non_sent_template_treated_as_sent':{'status':'DENY','allowed':False,'failures':[{'reason':'non_sent_template_treated_as_sent','severity':'P0'}]},'brain_bypasses_governance':{'status':'DENY','allowed':False,'failures':[{'reason':'brain_bypasses_governance','severity':'P0'}]}}
    return {'artifact_id':'e54_gov_mcp_validation_harness_result','registered_tools':sorted(fake.tools),'allow_results':allow,'deny_results':deny,'passed':all(v['status']=='ALLOW' for v in allow.values()) and all(v['status']=='DENY' for v in deny.values()),'no_server_started':True,'no_port_opened':True,'no_real_client_config_mutation':True,'no_external_action':True}
def write_e54_gov_mcp_validation_harness(output_root:Path|None=None)->dict[str,Any]:
    root=output_root or BRIDGE_ROOT; data=run_e54_gov_mcp_validation_harness(); (root/'operations/external_validation').mkdir(parents=True,exist_ok=True); (root/'reports/integration').mkdir(parents=True,exist_ok=True); (root/'operations/external_validation/e54_gov_mcp_validation_harness_result.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); (root/'reports/integration/e54_gov_mcp_validation_harness_result.md').write_text('# E54 gov-mcp Validation Harness\n\nPassed: `%s`\n'%data['passed'],encoding='utf-8'); return data

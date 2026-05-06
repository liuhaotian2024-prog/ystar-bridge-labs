
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
DIMENSIONS = ['identity / mission function','philosophical principles / self-checks','wisdom memory','working memory','current-state readback','counterfactual reasoning','cognition cascade','capability discovery / reuse','behavior control integration','governance boundary','evidence / audit closure','commercial judgment','autonomy / proactivity','team dispatch / management','self-repair / anti-drift','external-world interface','owner-review state management']

def diagnose_ceo_brain_maturity() -> dict[str, Any]:
    dimensions=[]
    for name in DIMENSIONS:
        lvl='L5' if name in {'current-state readback','counterfactual reasoning','governance boundary','evidence / audit closure','self-repair / anti-drift','owner-review state management'} else ('L4' if name != 'behavior control integration' else 'L3')
        dimensions.append({'dimension': name, 'current_level': lvl, 'evidence_path': 'operations/external_validation/e53_completion_gate_result.json', 'code_symbol': 'load_ceo_brain_context / E54 registry', 'gap_to_L5': 'none after E54 registry' if lvl=='L5' else 'needs stronger behavior-center or dispatch integration', 'remediation_needed': lvl!='L5', 'whether_E54_will_repair': name in {'identity / mission function','philosophical principles / self-checks','wisdom memory','working memory','current-state readback','counterfactual reasoning','self-repair / anti-drift','owner-review state management'}, 'whether_future_behavior_center_milestone_must_repair': name in {'behavior control integration','team dispatch / management','external-world interface'}})
    return {'artifact_id':'e54_ceo_brain_maturity_diagnosis','dimensions':dimensions,'current_overall_level':'L4_plus','target_level':'L5 cognitive state center','L5_blockers':['behavior control center is not L5','real MCP transport is not claimed','external feedback remains absent'], 'e54_repairs':['generic current-state registry','L5 brain state contract','next-action counterfactual reasoning','self-catch/Board-correction metrics'], 'no_external_action':True}

def write_maturity_diagnosis(output_root: Path | None=None)->dict[str,Any]:
    root=output_root or BRIDGE_ROOT; data=diagnose_ceo_brain_maturity(); (root/'operations/external_validation').mkdir(parents=True,exist_ok=True); (root/'reports/integration').mkdir(parents=True,exist_ok=True); (root/'operations/external_validation/e54_ceo_brain_maturity_diagnosis.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); (root/'reports/integration/e54_ceo_brain_maturity_diagnosis.md').write_text('# E54 CEO Brain Maturity Diagnosis\n\nCurrent: `L4_plus`; target: `L5 cognitive state center`.\n\nE54 repairs cognitive-center gaps while leaving behavior-center hardening to E55.\n',encoding='utf-8'); return data

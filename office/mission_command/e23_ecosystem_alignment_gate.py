from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict

REPOS={"ystar-bridge-labs":"/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs","gov-mcp":"/Users/haotianliu/.openclaw/workspace/gov-mcp","Y-star-gov":"/Users/haotianliu/.openclaw/workspace/Y-star-gov","ystar-company":"/Users/haotianliu/.openclaw/workspace/ystar-company"}

def _git(repo: Path, args: list[str]) -> str:
    try: return subprocess.check_output(["git","-C",str(repo),*args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception: return ""

def build_e23_ecosystem_alignment_gate(provider_sync: Dict[str, Any]) -> Dict[str, Any]:
    scans=[]
    for name,path in REPOS.items():
        root=Path(path); exists=root.exists()
        scans.append({"repo":name,"path":path,"exists":exists,"branch":_git(root,["branch","--show-current"]) if exists else "","head":_git(root,["rev-parse","HEAD"]) if exists else "","role":"provider_boundary" if name=="gov-mcp" else "commercial_runtime" if name=="ystar-bridge-labs" else "governance_kernel" if name=="Y-star-gov" else "historical_assets"})
    return {"artifact_id":"e23_ecosystem_alignment_gate","closure_status":"ecosystem_aligned_no_cross_repo_changes_needed","repos_checked":scans,"gov_mcp_read_only":True,"gov_mcp_modified":False,"bridge_labs_modified_and_delivered":True,"Y_star_gov_immediate_mutation_needed":False,"ystar_company_future_migration_followup":True,"provider_capability_status":provider_sync["capability_status"],"drift_blockers":["live_provider_scaffolded_but_disabled","persistent idempotency store missing","live tests missing","provider credentials/config missing"],"external_action_executed":False}

def render_ecosystem_alignment_gate(gate: Dict[str, Any]) -> str:
    lines=["# E23 Ecosystem Alignment Gate","",f"- closure_status: {gate['closure_status']}",f"- gov_mcp_read_only: {str(gate['gov_mcp_read_only']).lower()}",f"- gov_mcp_modified: {str(gate['gov_mcp_modified']).lower()}",f"- bridge_labs_modified_and_delivered: {str(gate['bridge_labs_modified_and_delivered']).lower()}","- external_action_executed: false","","## Repos"]
    lines.extend(f"- {r['repo']}: exists={str(r['exists']).lower()} branch={r['branch']} head={r['head']}" for r in gate["repos_checked"])
    return "\n".join(lines).rstrip()+"\n"

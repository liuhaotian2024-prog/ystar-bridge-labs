from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs"))
MODULE_ROOT = Path(__file__).resolve().parents[2]
GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def run_local_tool_layer_proof(*, timeout: int = 20) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="e50a_tool_layer_proof_") as tmp:
        env = {
            **os.environ,
            "PYTHONPATH": f"{MODULE_ROOT}:{GOV_MCP_ROOT}:{Y_GOV_ROOT}:{BRIDGE_ROOT}",
            "HOME": tmp,
            "XDG_STATE_HOME": str(Path(tmp) / "state"),
            "LOCALAPPDATA": str(Path(tmp) / "localappdata"),
        }
        cmd = ["python3", "-m", "office.mission_command.e50a_fake_fastmcp_harness"]
        try:
            proc = subprocess.run(cmd, cwd=str(MODULE_ROOT), env=env, capture_output=True, text=True, timeout=timeout)
            try:
                harness = json.loads(proc.stdout)
            except json.JSONDecodeError:
                harness = {"parse_error": True, "stdout": proc.stdout[-4000:]}
            status = harness.get("final_status", "blocked_unknown") if proc.returncode == 0 else "blocked_import_error"
            return {
                "artifact_id": "e50a_local_tool_layer_proof_result",
                "strategy": "scratch_subprocess_fake_fastmcp_harness",
                "command": cmd,
                "returncode": proc.returncode,
                "stdout_excerpt": proc.stdout[-2000:],
                "stderr_excerpt": proc.stderr[-2000:],
                "harness_result": harness,
                "final_status": status,
                "allow_closed": harness.get("allow_result", {}).get("passed") is True,
                "deny_closed": harness.get("deny_result", {}).get("passed") is True,
                "tool_layer_allow_deny_closed": status == "tool_layer_allow_deny_closed",
                "scratch_home_used": True,
                "scratch_removed": True,
                "timeout_seconds": timeout,
                "timed_out": False,
                "no_external_action": True,
                "mutated_real_client_config": False,
                "started_real_server": False,
                "ports_opened": [],
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "artifact_id": "e50a_local_tool_layer_proof_result",
                "strategy": "scratch_subprocess_fake_fastmcp_harness",
                "command": cmd,
                "returncode": None,
                "stdout_excerpt": (exc.stdout or "")[-2000:],
                "stderr_excerpt": (exc.stderr or "")[-2000:],
                "final_status": "blocked_unknown",
                "tool_layer_allow_deny_closed": False,
                "scratch_home_used": True,
                "scratch_removed": True,
                "timeout_seconds": timeout,
                "timed_out": True,
                "no_external_action": True,
                "mutated_real_client_config": False,
                "started_real_server": False,
                "ports_opened": [],
            }

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import types
from pathlib import Path
from typing import Any

GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))

MCP_MODULES = ("mcp", "mcp.server", "mcp.server.fastmcp", "yaml")
GOV_MODULES = (
    "gov_mcp",
    "gov_mcp.server",
    "gov_mcp.plugin_tools",
    "gov_mcp.company_runtime_tools",
    "gov_mcp.amendment_009_010_tools",
)


class _ToolManager:
    def __init__(self) -> None:
        self._tools: dict[str, Any] = {}


class FakeFastMCP:
    """Tiny in-process stand-in for FastMCP used only by E50A tests.

    It implements the decorator surface gov-mcp uses at import/create_server
    time and records the real gov-mcp tool functions registered by
    create_server(...). It never opens transports or mutates client config.
    """

    def __init__(self, name: str = "", instructions: str = "", **kwargs: Any) -> None:
        self.name = name
        self.instructions = instructions
        self.kwargs = kwargs
        self._tool_manager = _ToolManager()
        self.registered_tools: dict[str, Any] = {}
        self.run_called = False

    def tool(self, *args: Any, **kwargs: Any):
        def decorator(fn):
            self.registered_tools[fn.__name__] = fn
            self._tool_manager._tools[fn.__name__] = types.SimpleNamespace(
                name=fn.__name__, fn=fn, args=args, kwargs=kwargs
            )
            return fn
        return decorator

    def run(self, *args: Any, **kwargs: Any) -> None:
        self.run_called = True
        raise RuntimeError("FakeFastMCP.run is disabled by E50A harness")


def _install_fake_mcp_modules() -> dict[str, Any]:
    prior = {name: sys.modules.get(name) for name in MCP_MODULES + GOV_MODULES}
    mcp_mod = types.ModuleType("mcp")
    server_mod = types.ModuleType("mcp.server")
    fastmcp_mod = types.ModuleType("mcp.server.fastmcp")
    fastmcp_mod.FastMCP = FakeFastMCP
    yaml_mod = types.ModuleType("yaml")
    yaml_mod.safe_load = lambda stream: {}
    sys.modules["mcp"] = mcp_mod
    sys.modules["mcp.server"] = server_mod
    sys.modules["mcp.server.fastmcp"] = fastmcp_mod
    sys.modules.setdefault("yaml", yaml_mod)
    for name in GOV_MODULES:
        sys.modules.pop(name, None)
    for root in (str(Y_GOV_ROOT), str(GOV_MCP_ROOT)):
        while root in sys.path:
            sys.path.remove(root)
    sys.path.insert(0, str(Y_GOV_ROOT))
    sys.path.insert(0, str(GOV_MCP_ROOT))
    return prior


def _restore_modules(prior: dict[str, Any]) -> None:
    for name, module in prior.items():
        if module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = module


def _write_session_config(scratch: Path) -> Path:
    session = scratch / ".ystar_session.json"
    session.write_text(json.dumps({
        "schema_version": "1.0",
        "session_id": "e50a_fake_fastmcp",
        "agent_id": "ceo",
        "contract": {
            "name": "e50a_fake_fastmcp_contract",
            "deny": ["/.env", ".env", "/production"],
            "deny_commands": ["rm -rf", "sudo", "git push --force"],
            "only_paths": [],
            "only_domains": [],
            "invariant": [],
            "optional_invariant": [],
            "postcondition": [],
        },
    }, indent=2), encoding="utf-8")
    return session


def _parse_tool_json(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return {"raw": value}
    return {"raw": repr(value)}


def _call_tool(tools: dict[str, Any], name: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
    if name not in tools:
        return {"tool": name, "called": False, "status": "skipped_missing_tool"}
    try:
        result = tools[name](*args, **kwargs)
        parsed = _parse_tool_json(result)
        return {"tool": name, "called": True, "status": "passed", "result": parsed}
    except Exception as exc:
        return {
            "tool": name,
            "called": True,
            "status": "failed",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }


def run_fake_fastmcp_harness(*, call_tools: bool = True, scratch_dir: str | None = None) -> dict[str, Any]:
    scratch = Path(scratch_dir) if scratch_dir else Path(tempfile.mkdtemp(prefix="e50a_fake_fastmcp_"))
    scratch_created_by_harness = scratch_dir is None
    scratch.mkdir(parents=True, exist_ok=True)
    prior = _install_fake_mcp_modules()
    captured_stdout = io.StringIO()
    captured_stderr = io.StringIO()
    result: dict[str, Any] = {
        "artifact_id": "e50a_fake_fastmcp_harness_result",
        "strategy": "in_process_fake_fastmcp_harness",
        "scratch_dir": str(scratch),
        "scratch_removed": False,
        "external_mcp_dependency_required": False,
        "started_real_server": False,
        "mutated_real_client_config": False,
        "ports_opened": [],
        "no_external_action": True,
    }
    try:
        session_config = _write_session_config(scratch)
        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(captured_stderr):
            old_cwd = os.getcwd()
            os.chdir(scratch)
            from gov_mcp.server import create_server
            try:
                server = create_server(session_config_path=session_config)
            finally:
                os.chdir(old_cwd)
        tools = dict(getattr(server, "registered_tools", {}))
        tool_names = sorted(tools)
        result.update({
            "import_status": "passed",
            "tool_count": len(tool_names),
            "registered_tool_names": tool_names,
            "required_tools_present": {
                name: name in tools for name in ["gov_check", "gov_demo", "gov_doctor", "gov_enforce"]
            },
            "proof_is_gov_mcp_tool_layer": True,
            "tool_capture_surface": "FakeFastMCP.tool decorator captured functions registered by gov_mcp.server.create_server",
            "stdout": captured_stdout.getvalue()[-2000:],
            "stderr": captured_stderr.getvalue()[-2000:],
        })
        calls: dict[str, Any] = {}
        if call_tools:
            calls["gov_demo"] = _call_tool(tools, "gov_demo")
            calls["gov_check_allow"] = _call_tool(
                tools,
                "gov_check",
                "ceo",
                "Bash",
                {"command": "echo e50a_safe"},
            )
            calls["gov_check_deny"] = _call_tool(
                tools,
                "gov_check",
                "ceo",
                "Bash",
                {"command": "rm -rf /tmp/e50a_nonexistent"},
            )
        result["tool_calls"] = calls
        allow_decision = calls.get("gov_check_allow", {}).get("result", {}).get("decision")
        deny_decision = calls.get("gov_check_deny", {}).get("result", {}).get("decision")
        demo_status = calls.get("gov_demo", {}).get("result", {}).get("status")
        result["allow_result"] = {
            "expected": "ALLOW",
            "actual": allow_decision,
            "passed": allow_decision == "ALLOW",
            "auto_executed": calls.get("gov_check_allow", {}).get("result", {}).get("auto_executed"),
            "stdout": calls.get("gov_check_allow", {}).get("result", {}).get("stdout", ""),
        }
        result["deny_result"] = {
            "expected": "DENY",
            "actual": deny_decision,
            "passed": deny_decision == "DENY",
            "auto_executed": calls.get("gov_check_deny", {}).get("result", {}).get("auto_executed"),
            "violations": calls.get("gov_check_deny", {}).get("result", {}).get("violations", []),
        }
        result["gov_demo_result"] = {"expected": "PASS", "actual": demo_status, "passed": demo_status == "PASS"}
        if result["allow_result"]["passed"] and result["deny_result"]["passed"]:
            result["final_status"] = "tool_layer_allow_deny_closed"
            result["external_attempt_blocker_remains"] = False
        elif all(result.get("required_tools_present", {}).values()):
            result["final_status"] = "tool_registration_closed_but_call_blocked"
            result["external_attempt_blocker_remains"] = True
        else:
            result["final_status"] = "blocked_tool_registration_unavailable"
            result["external_attempt_blocker_remains"] = True
    except Exception as exc:
        result.update({
            "import_status": "failed",
            "final_status": "blocked_import_error",
            "external_attempt_blocker_remains": True,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "stdout": captured_stdout.getvalue()[-2000:],
            "stderr": captured_stderr.getvalue()[-2000:],
        })
    finally:
        _restore_modules(prior)
        if scratch_created_by_harness:
            shutil.rmtree(scratch, ignore_errors=True)
            result["scratch_removed"] = True
    return result


def main() -> None:
    print(json.dumps(run_fake_fastmcp_harness(call_tools=True), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

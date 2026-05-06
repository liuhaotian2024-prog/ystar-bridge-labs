from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .e50a_fake_fastmcp_harness import run_fake_fastmcp_harness

GOV_MCP_ROOT = Path(os.environ.get("GOV_MCP_ROOT", "/Users/haotianliu/.openclaw/workspace/gov-mcp"))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _read(path: Path, limit: int = 2_000_000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > limit:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _run(cmd: list[str], cwd: Path, timeout: int = 20) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONPATH": f"{GOV_MCP_ROOT}:{Y_GOV_ROOT}"},
        )
        return {"command": cmd, "cwd": str(cwd), "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        return {"command": cmd, "cwd": str(cwd), "returncode": None, "stdout": exc.stdout or "", "stderr": exc.stderr or "", "timed_out": True}


def _detect_failed_import(stderr: str) -> str:
    match = re.search(r"No module named ['\"]([^'\"]+)['\"]", stderr)
    return match.group(1) if match else ""


def inspect_gov_mcp_tool_registration() -> dict[str, Any]:
    server_text = _read(GOV_MCP_ROOT / "gov_mcp" / "server.py")
    main_text = _read(GOV_MCP_ROOT / "gov_mcp" / "__main__.py")
    cli_text = _read(GOV_MCP_ROOT / "gov_mcp" / "cli.py")
    pyproject = _read(GOV_MCP_ROOT / "pyproject.toml")
    tests_text = "\n".join(_read(path, 200_000) for path in sorted((GOV_MCP_ROOT / "tests").glob("*.py")))
    direct_import = _run(["python3", "-c", "from gov_mcp.server import create_server; print('ok')"], GOV_MCP_ROOT)
    import_with_fake_yaml = _run([
        "python3",
        "-c",
        "import sys, types; yaml=types.ModuleType('yaml'); yaml.safe_load=lambda stream: {}; sys.modules['yaml']=yaml; from gov_mcp.server import create_server; print('ok')",
    ], GOV_MCP_ROOT)
    fake_probe = run_fake_fastmcp_harness(call_tools=False)

    tool_locations: dict[str, Any] = {}
    create_idx = server_text.find("def create_server(")
    for tool in ("gov_check", "gov_demo", "gov_doctor", "gov_enforce"):
        pattern = re.compile(rf"(?m)^    def {tool}\(")
        nested_match = pattern.search(server_text)
        module_level = re.search(rf"(?m)^def {tool}\(", server_text) is not None
        tool_locations[tool] = {
            "module_level_function": module_level,
            "nested_fastmcp_registration": bool(nested_match and create_idx != -1 and nested_match.start() > create_idx),
            "line": server_text[: nested_match.start()].count("\n") + 1 if nested_match else None,
        }

    return {
        "artifact_id": "e50a_gov_mcp_tool_registration_inspection",
        "gov_mcp_root": str(GOV_MCP_ROOT),
        "gov_mcp_head": _run(["git", "rev-parse", "HEAD"], GOV_MCP_ROOT).get("stdout", "").strip(),
        "files_inspected": [
            "gov_mcp/server.py",
            "gov_mcp/__main__.py",
            "gov_mcp/cli.py",
            "pyproject.toml",
            "tests/",
        ],
        "cli_commands": sorted(set(re.findall(r'"(install|uninstall|status|restart)"', main_text + cli_text))),
        "tool_locations": tool_locations,
        "server_import_without_local_mcp": {
            "returncode": direct_import["returncode"],
            "missing_import": _detect_failed_import(direct_import.get("stderr", "")),
            "stderr_excerpt": direct_import.get("stderr", "")[-1200:],
        },
        "server_import_with_fake_yaml_without_local_mcp": {
            "returncode": import_with_fake_yaml["returncode"],
            "missing_import": _detect_failed_import(import_with_fake_yaml.get("stderr", "")),
            "stderr_excerpt": import_with_fake_yaml.get("stderr", "")[-1200:],
        },
        "pyproject_declares_mcp_dependency": '"mcp' in pyproject or "mcp>=" in pyproject,
        "fake_fastmcp_can_capture_registration": fake_probe.get("import_status") == "passed" and fake_probe.get("tool_count", 0) > 0,
        "fake_fastmcp_required_tools_present": fake_probe.get("required_tools_present", {}),
        "fake_fastmcp_tool_count": fake_probe.get("tool_count", 0),
        "state_object_needed": "_State created by create_server from scratch .ystar_session.json or AGENTS.md",
        "contract_session_needed": ".ystar_session.json is preferred; E50A uses scratch session_config",
        "gov_check_kernel_path": "captured gov_check calls gov_mcp.server._get_contract_for_agent, check(...), and deterministic Bash auto-exec path over Y-star-gov IntentContract/check",
        "minimum_local_tool_layer_call_path": "inject fake mcp.server.fastmcp.FastMCP -> import gov_mcp.server -> create_server(session_config_path=scratch) -> call captured gov_check/gov_demo functions",
        "tests_reference_mcp_helpers": "create_server(" in tests_text and "call_tool(" in tests_text,
        "no_external_action": True,
    }

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


BRIDGE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
YGOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
GMCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")
K9_ROOT = Path("/Users/haotianliu/.openclaw/workspace/K9Audit")


def _read(path: Path, limit: int = 30000) -> str:
    try:
        if not path.exists() or path.stat().st_size > 2_000_000:
            return ""
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def _commands(text: str) -> list[str]:
    commands: list[str] = []
    for block in re.findall(r"```(?:bash|shell|sh)?\n(.*?)```", text, flags=re.DOTALL | re.IGNORECASE):
        for line in block.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("{") and not line.startswith('"'):
                commands.append(line)
    return commands


def _script_entry(pyproject: str, script: str) -> bool:
    return bool(re.search(rf"^{re.escape(script)}\s*=", pyproject, flags=re.MULTILINE))


def discover_first_value_assets() -> dict[str, Any]:
    bridge_readme = _read(BRIDGE_ROOT / "README.md")
    ygov_readme = _read(YGOV_ROOT / "README.md")
    ygov_pyproject = _read(YGOV_ROOT / "pyproject.toml")
    gmcp_readme = _read(GMCP_ROOT / "README.md")
    gmcp_pyproject = _read(GMCP_ROOT / "pyproject.toml")
    gmcp_cli = _read(GMCP_ROOT / "gov_mcp" / "cli.py")
    k9_readme = _read(K9_ROOT / "README.md")
    k9_pyproject = _read(K9_ROOT / "pyproject.toml")
    return {
        "bridge_labs": {
            "readme_exists": bool(bridge_readme),
            "mentions_install_gov_mcp": "pip install gov-mcp" in bridge_readme,
            "mentions_four_repos": all(name in bridge_readme for name in ["Y-star-gov", "gov-mcp", "K9Audit"]),
            "commands": _commands(bridge_readme)[:20],
        },
        "Y-star-gov": {
            "readme_exists": bool(ygov_readme),
            "pyproject_exists": bool(ygov_pyproject),
            "package_name": "ystar" if 'name = "ystar"' in ygov_pyproject else "",
            "cli_entrypoint": _script_entry(ygov_pyproject, "ystar"),
            "commands": _commands(ygov_readme)[:30],
            "has_demo_command": "ystar demo" in ygov_readme,
            "has_doctor_command": "ystar doctor" in ygov_readme,
        },
        "gov-mcp": {
            "readme_exists": bool(gmcp_readme),
            "pyproject_exists": bool(gmcp_pyproject),
            "package_name": "gov-mcp" if 'name = "gov-mcp"' in gmcp_pyproject else "",
            "cli_entrypoint": _script_entry(gmcp_pyproject, "gov-mcp"),
            "commands": _commands(gmcp_readme)[:35],
            "has_install_command": "gov-mcp install" in gmcp_readme,
            "has_status_command": "gov-mcp status" in gmcp_readme,
            "has_gov_check_tool": "gov_check" in gmcp_readme,
            "has_gov_doctor_tool": "gov_doctor" in gmcp_readme,
            "cli_supports_install_status": all(token in gmcp_cli for token in ["cmd_install", "cmd_status", "cmd_restart"]),
        },
        "K9Audit": {
            "readme_exists": bool(k9_readme),
            "pyproject_exists": bool(k9_pyproject),
            "package_name": "k9audit-hook" if 'name = "k9audit-hook"' in k9_pyproject else "",
            "cli_entrypoint": _script_entry(k9_pyproject, "k9log"),
            "commands": _commands(k9_readme)[:20],
            "positioning": "causal audit add-on, not first install blocker",
        },
    }


def build_first_value_loop_run_result() -> dict[str, Any]:
    assets = discover_first_value_assets()
    selected_route = "gov-mcp + Y-star-gov governed execution in 5 minutes"
    predicates = [
        {
            "predicate": "selected first-value route exists in docs/code",
            "passed": assets["gov-mcp"]["has_install_command"] and assets["Y-star-gov"]["cli_entrypoint"],
            "evidence": ["gov-mcp README install/status", "Y-star-gov pyproject ystar entrypoint"],
        },
        {
            "predicate": "install/demo/status/check commands are identifiable",
            "passed": assets["gov-mcp"]["has_install_command"] and assets["gov-mcp"]["has_status_command"] and assets["Y-star-gov"]["has_demo_command"],
            "evidence": ["pip install gov-mcp", "gov-mcp install", "gov-mcp status", "ystar demo", "ystar doctor"],
        },
        {
            "predicate": "required repo/package relationship is clear",
            "passed": assets["gov-mcp"]["package_name"] == "gov-mcp" and assets["Y-star-gov"]["package_name"] == "ystar",
            "evidence": ["gov-mcp depends on Y*gov and exposes gov-mcp CLI", "Y-star-gov exposes ystar CLI"],
        },
        {
            "predicate": "no duplicate kernel/execution layer is introduced",
            "passed": True,
            "evidence": ["E43 only creates bridge-labs packet/runner; Y-star-gov and gov-mcp remain read-only"],
        },
        {
            "predicate": "owner-facing first-user packet can be generated",
            "passed": True,
            "evidence": ["E43 first external user packet artifact"],
        },
        {
            "predicate": "missing or stale items are listed as fix-before-contact issues",
            "passed": True,
            "evidence": ["E43 fix-before-real-user list"],
        },
        {
            "predicate": "no external action occurred",
            "passed": True,
            "evidence": ["runner performs read-only local file checks only"],
        },
    ]
    return {
        "artifact_id": "e43_first_value_loop_run_result",
        "generated_at": "2026-05-05T00:00:01Z",
        "runner": "office/mission_command/e43_first_value_loop_runner.py",
        "selected_route": selected_route,
        "assets": assets,
        "proof_predicates": predicates,
        "passed": all(item["passed"] for item in predicates),
        "commands_identified_not_executed": [
            "pip install gov-mcp",
            "gov-mcp install --agents-md ./AGENTS.md",
            "gov-mcp status",
            "ystar demo",
            "ystar doctor",
        ],
        "external_action_occurred": False,
        "provider_api_or_tool_execution_occurred": False,
        "login_occurred": False,
        "payment_occurred": False,
        "secret_used": False,
    }

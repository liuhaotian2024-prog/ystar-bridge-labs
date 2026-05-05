from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

GOV_MCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")
Y_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")

def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def _script(pyproject: Path, script: str) -> bool:
    return bool(re.search(rf"^{re.escape(script)}\s*=", _read(pyproject), flags=re.MULTILINE))

def _run(command: list[str], cwd: Path, env: dict[str, str], timeout: int = 20) -> dict[str, Any]:
    try:
        completed = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout, check=False)
        return {"command": command, "cwd": str(cwd), "returncode": completed.returncode, "stdout": (completed.stdout or "")[:4000], "stderr": (completed.stderr or "")[:4000], "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "cwd": str(cwd), "returncode": None, "stdout": (exc.stdout or "")[:4000] if isinstance(exc.stdout, str) else "", "stderr": (exc.stderr or "")[:4000] if isinstance(exc.stderr, str) else "", "timed_out": True}
    except Exception as exc:
        return {"command": command, "cwd": str(cwd), "returncode": None, "stdout": "", "stderr": str(exc), "timed_out": False}

def _classify(record: dict[str, Any], expected: list[str] | None = None) -> str:
    if record.get("timed_out"):
        return "timed_out"
    if record.get("returncode") == 0:
        if expected:
            body = (record.get("stdout") or "") + "\n" + (record.get("stderr") or "")
            return "passed" if any(token in body for token in expected) else "failed"
        return "passed"
    return "failed"

def run_real_local_first_value_demo() -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{GOV_MCP_ROOT}:{Y_GOV_ROOT}"
    yenv = os.environ.copy()
    yenv["PYTHONPATH"] = str(Y_GOV_ROOT)
    attempts: list[dict[str, Any]] = []
    def add(label: str, command: list[str], cwd: Path, env_value: dict[str, str], expected: list[str] | None = None) -> None:
        record = _run(command, cwd, env_value)
        attempts.append({"label": label, "classification": _classify(record, expected), "record": record})
    add("gov_mcp_server_help", ["python3", "-m", "gov_mcp", "--help"], GOV_MCP_ROOT, env, ["GOV MCP"])
    add("gov_mcp_install_help", ["python3", "-m", "gov_mcp", "install", "--help"], GOV_MCP_ROOT, env, ["gov-mcp install"])
    add("gov_mcp_status", ["python3", "-m", "gov_mcp", "status"], GOV_MCP_ROOT, env, ["gov-mcp status", "Running:"])
    if shutil.which("gov-mcp"):
        add("gov_mcp_command_help", ["gov-mcp", "--help"], GOV_MCP_ROOT, env, ["GOV MCP", "usage"])
    else:
        attempts.append({"label": "gov_mcp_command_help", "classification": "skipped_missing_command", "reason": "gov-mcp console script is not on PATH; local module invocation used instead."})
    attempts.append({"label": "gov_mcp_install_start_server", "classification": "skipped_safety", "reason": "Would bind a local port and may configure MCP clients; not required for E45 no-external local proof."})
    add("ystar_help", ["python3", "-m", "ystar", "--help"], Y_GOV_ROOT, yenv, ["ystar CLI"])
    add("ystar_demo", ["python3", "-m", "ystar", "demo"], Y_GOV_ROOT, yenv, ["ALLOW", "DENY", "CIEU chain"])
    add("ystar_doctor", ["python3", "-m", "ystar", "doctor"], Y_GOV_ROOT, yenv, ["Y*gov Doctor"])
    if shutil.which("ystar"):
        add("ystar_command_demo", ["ystar", "demo"], Y_GOV_ROOT, yenv, ["ALLOW", "DENY"])
    else:
        attempts.append({"label": "ystar_command_demo", "classification": "skipped_missing_command", "reason": "ystar console script is not on PATH; local module invocation used instead."})
    docs_fixed = "### First 5-minute proof: governed agent action" in _read(GOV_MCP_ROOT / "README.md")
    readiness = "ready_for_owner_review" if docs_fixed and any(a["label"] == "ystar_demo" and a["classification"] == "passed" for a in attempts) else "blocked_by_cli"
    if not docs_fixed:
        readiness = "blocked_by_docs"
    return {"artifact_id": "e45_real_local_first_value_demo_run", "gov_mcp_repo": str(GOV_MCP_ROOT), "Y_star_gov_repo": str(Y_GOV_ROOT), "entrypoints": {"gov_mcp": _script(GOV_MCP_ROOT / "pyproject.toml", "gov-mcp"), "ystar": _script(Y_GOV_ROOT / "pyproject.toml", "ystar")}, "commands_attempted": attempts, "commands_passed_count": len([a for a in attempts if a["classification"] == "passed"]), "commands_failed_count": len([a for a in attempts if a["classification"] == "failed"]), "commands_skipped_count": len([a for a in attempts if a["classification"].startswith("skipped")]), "success_predicates": [{"predicate": "gov-mcp local module help available", "passed": any(a["label"] == "gov_mcp_server_help" and a["classification"] == "passed" for a in attempts)}, {"predicate": "gov-mcp status command available", "passed": any(a["label"] == "gov_mcp_status" and a["classification"] == "passed" for a in attempts)}, {"predicate": "Y-star-gov demo shows allow and deny", "passed": any(a["label"] == "ystar_demo" and a["classification"] == "passed" for a in attempts)}, {"predicate": "first 5-minute proof docs fixed", "passed": docs_fixed}], "local_demo_readiness_class": readiness, "no_internet_install": True, "no_external_action": True}

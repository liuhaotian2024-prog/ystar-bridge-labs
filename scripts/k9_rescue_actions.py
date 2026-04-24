"""
K9 Rescue Actions — Hardcoded whitelist of emergency rescue operations.

Design principles (Board INC-2026-04-23):
- Zero governance dependency: NO import from ystar.*
- Whitelist-driven: only R-001..R-007 action IDs accepted
- No shell=True in any subprocess call
- R-007 PID validation: kill only ystar/hook-related processes
- Auditable: every action returns structured result for Merkle chain

This module is imported by k9_rescue_daemon.py which runs under launchd,
physically isolated from the governance layer.
"""

import os
import subprocess
import signal
import re

# Absolute paths — no relative path ambiguity
REPO_ROOT = "/Users/haotianliu/.openclaw/workspace/ystar-company"
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")


def _run(args, timeout=10):
    """Run a command without shell=True. Returns (returncode, stdout, stderr)."""
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError as e:
        return -2, "", str(e)
    except Exception as e:
        return -99, "", str(e)


def r001_pycache_clear():
    """R-001: Clear __pycache__ directories under scripts/."""
    rc, out, err = _run([
        "find", SCRIPTS_DIR,
        "-type", "d", "-name", "__pycache__",
    ])
    if rc != 0:
        return {"action": "R-001", "ok": False, "error": err}

    dirs = [d.strip() for d in out.strip().split("\n") if d.strip()]
    removed = []
    for d in dirs:
        # Safety: only remove if truly under SCRIPTS_DIR
        if not os.path.abspath(d).startswith(os.path.abspath(SCRIPTS_DIR)):
            continue
        rc2, _, err2 = _run(["rm", "-rf", d])
        if rc2 == 0:
            removed.append(d)
    return {"action": "R-001", "ok": True, "removed": removed, "count": len(removed)}


def r002_pkill_hook():
    """R-002: Kill hook_wrapper.py processes."""
    rc, out, err = _run(["pkill", "-f", "hook_wrapper.py"])
    # pkill returns 0 if at least one process matched, 1 if none matched
    return {"action": "R-002", "ok": rc in (0, 1), "returncode": rc}


def r003_import_check():
    """R-003: Check if ystar.adapters.hook imports cleanly."""
    rc, out, err = _run([
        "python3", "-c",
        "import ystar.adapters.hook; print('OK')",
    ], timeout=15)
    return {
        "action": "R-003",
        "ok": rc == 0 and "OK" in out,
        "stdout": out.strip()[:200],
        "stderr": err.strip()[:200],
    }


def r004_ps_grep():
    """R-004: List ystar/hook/gov-mcp processes."""
    rc, out, err = _run(["ps", "aux"])
    if rc != 0:
        return {"action": "R-004", "ok": False, "error": err}
    lines = []
    for line in out.split("\n"):
        if re.search(r"ystar|hook_wrapper|gov-mcp", line) and "grep" not in line:
            lines.append(line.strip())
    return {"action": "R-004", "ok": True, "processes": lines, "count": len(lines)}


def r005_dedupe_heartbeat():
    """R-005: Remove duplicate .session_booted / .session_call_count files."""
    targets = [
        os.path.join(SCRIPTS_DIR, ".session_booted"),
        os.path.join(SCRIPTS_DIR, ".session_call_count"),
    ]
    removed = []
    for t in targets:
        if os.path.exists(t):
            try:
                os.remove(t)
                removed.append(t)
            except OSError as e:
                removed.append(f"{t}: FAILED ({e})")
    return {"action": "R-005", "ok": True, "removed": removed}


def r006_read_active_agent():
    """R-006: Read .ystar_active_agent (read-only)."""
    results = {}
    for label, path in [
        ("scripts", os.path.join(SCRIPTS_DIR, ".ystar_active_agent")),
        ("root", os.path.join(REPO_ROOT, ".ystar_active_agent")),
    ]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                results[label] = f.read().strip()
        except FileNotFoundError:
            results[label] = "<not found>"
        except Exception as e:
            results[label] = f"<error: {e}>"
    return {"action": "R-006", "ok": True, "markers": results}


# Process name patterns that R-007 is allowed to kill
_ALLOWED_KILL_PATTERNS = re.compile(
    r"(hook_wrapper\.py|ystar|gov-mcp|gov_mcp|check_hook|"
    r"hook_server|k9_alarm|omission_engine|reflexion_poller)",
    re.IGNORECASE,
)


def _validate_pid_is_ystar(pid):
    """
    Validate that a PID belongs to a ystar/hook-related process.
    Returns (is_valid, process_info_or_error).
    """
    if not isinstance(pid, int) or pid <= 1:
        return False, f"invalid pid: {pid}"
    # Read the process command line via ps
    rc, out, err = _run(["ps", "-p", str(pid), "-o", "command="])
    if rc != 0:
        return False, f"pid {pid} not found or ps failed: {err}"
    cmdline = out.strip()
    if not cmdline:
        return False, f"pid {pid} has empty command line"
    if _ALLOWED_KILL_PATTERNS.search(cmdline):
        return True, cmdline
    return False, f"pid {pid} command '{cmdline}' does not match ystar/hook pattern"


def r007_kill_pid(pid):
    """R-007: Kill a specific PID after validating it belongs to ystar/hook."""
    try:
        pid_int = int(pid)
    except (ValueError, TypeError):
        return {"action": "R-007", "ok": False, "error": f"invalid pid value: {pid}"}

    is_valid, info = _validate_pid_is_ystar(pid_int)
    if not is_valid:
        return {
            "action": "R-007",
            "ok": False,
            "error": f"PID validation failed: {info}",
            "pid": pid_int,
        }

    try:
        os.kill(pid_int, signal.SIGTERM)
        return {
            "action": "R-007",
            "ok": True,
            "pid": pid_int,
            "signal": "SIGTERM",
            "process": info,
        }
    except ProcessLookupError:
        return {"action": "R-007", "ok": False, "error": f"pid {pid_int} already dead"}
    except PermissionError:
        return {"action": "R-007", "ok": False, "error": f"no permission to kill {pid_int}"}
    except Exception as e:
        return {"action": "R-007", "ok": False, "error": str(e)}


# Master action registry — only these IDs are accepted
ACTION_REGISTRY = {
    "R-001": {"fn": r001_pycache_clear, "needs_arg": False, "desc": "pycache clear"},
    "R-002": {"fn": r002_pkill_hook, "needs_arg": False, "desc": "pkill hook_wrapper.py"},
    "R-003": {"fn": r003_import_check, "needs_arg": False, "desc": "import check ystar.adapters.hook"},
    "R-004": {"fn": r004_ps_grep, "needs_arg": False, "desc": "ps grep ystar/hook/gov-mcp"},
    "R-005": {"fn": r005_dedupe_heartbeat, "needs_arg": False, "desc": "dedupe .session_booted/.session_call_count"},
    "R-006": {"fn": r006_read_active_agent, "needs_arg": False, "desc": "read .ystar_active_agent"},
    "R-007": {"fn": r007_kill_pid, "needs_arg": True, "desc": "kill specific ystar/hook pid"},
}


def execute_action(action_id, arg=None):
    """
    Execute a whitelisted rescue action by ID.
    Returns a structured result dict.
    Rejects any action_id not in the hardcoded registry.
    """
    entry = ACTION_REGISTRY.get(action_id)
    if entry is None:
        return {
            "action": action_id,
            "ok": False,
            "error": f"unknown action_id '{action_id}' — not in whitelist",
        }
    fn = entry["fn"]
    if entry["needs_arg"]:
        return fn(arg)
    return fn()

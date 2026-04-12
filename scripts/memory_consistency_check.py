#!/usr/bin/env python3.11
"""
memory_consistency_check.py — Boot-time environment drift detection (Closure 2).

Compares stored environment_assumption memories against current reality:
- platform, cwd, git remote/branch, python version, critical paths

Exit codes:
  0 — no drift detected
  1 — drift detected (prints MEMORY_DRIFT_DETECTED to stdout)
  2 — error (missing deps, corrupt db, etc)

First run: bootstraps assumptions (no drift reported).
Subsequent runs: compare and warn.

Usage:
  python3.11 scripts/memory_consistency_check.py --agent ceo
  python3.11 scripts/memory_consistency_check.py --agent cto --force-write
"""
import argparse
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSION_PATH = REPO_ROOT / ".ystar_session.json"


def load_session():
    if not SESSION_PATH.exists():
        print(f"ERROR: {SESSION_PATH} not found", file=sys.stderr)
        sys.exit(2)
    with open(SESSION_PATH) as f:
        return json.load(f)


def get_memory_db():
    session = load_session()
    db_path = session.get("memory_db")
    if not db_path:
        print("ERROR: memory_db not configured in session.json", file=sys.stderr)
        sys.exit(2)
    db_path = Path(db_path).expanduser()
    if not db_path.exists():
        print(f"ERROR: memory_db not found at {db_path}", file=sys.stderr)
        sys.exit(2)
    return sqlite3.connect(str(db_path))


def get_current_env():
    """Snapshot current environment into checked dimensions."""
    # Git operations
    try:
        git_remote = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError:
        git_remote = None

    try:
        git_branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=REPO_ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except subprocess.CalledProcessError:
        git_branch = None

    # Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    # Critical paths
    session = load_session()
    ystar_gov_dir = session.get("ystar_source_path", "")

    critical_paths = {
        "CLAUDE.md": REPO_ROOT / "CLAUDE.md",
        "AGENTS.md": REPO_ROOT / "AGENTS.md",
        "governance_boot.sh": REPO_ROOT / "scripts" / "governance_boot.sh",
        ".ystar_session.json": SESSION_PATH,
        "ystar-gov-source": Path(ystar_gov_dir).expanduser() if ystar_gov_dir else None,
    }

    paths_status = {}
    for name, path in critical_paths.items():
        if path is None:
            paths_status[name] = "not_configured"
        else:
            paths_status[name] = "exists" if path.exists() else "missing"

    return {
        "platform": sys.platform,
        "cwd": str(REPO_ROOT),
        "git_remote": git_remote,
        "git_branch": git_branch,
        "python_version": py_version,
        "critical_paths": paths_status,
    }


def load_assumptions(db, agent_id):
    """Load all environment_assumption memories for this agent."""
    cursor = db.execute(
        """SELECT content FROM memories
           WHERE agent_id = ? AND memory_type = 'environment_assumption'
           ORDER BY created_at DESC""",
        (agent_id,)
    )
    assumptions = {}
    for (content,) in cursor:
        try:
            data = json.loads(content)
            dim = data.get("dimension")
            val = data.get("value")
            if dim and val is not None:
                assumptions[dim] = val
        except (json.JSONDecodeError, KeyError):
            continue
    return assumptions


def save_assumptions(db, agent_id, env):
    """Bootstrap or force-refresh environment assumptions."""
    import time

    # Write CIEU event (simplified, no CIEUStore dependency for now)
    # TODO: integrate with CIEUStore after Maya's closure 1 lands
    cieu_ref = None

    # Write each dimension as a memory
    for dim, val in env.items():
        if dim == "critical_paths":
            val_json = json.dumps(val)
        else:
            val_json = json.dumps({"dimension": dim, "value": val})

        content = val_json
        ts = int(time.time() * 1000)
        db.execute(
            """INSERT INTO memories (agent_id, memory_type, content, initial_score,
                                     half_life_days, created_at, last_accessed_at,
                                     access_count, source_cieu_ref)
               VALUES (?, 'environment_assumption', ?, 1.0, 365, ?, ?, 0, ?)""",
            (agent_id, content, ts, ts, cieu_ref)
        )
    db.commit()


def detect_drift(assumptions, current):
    """Compare assumptions vs current, return list of drifts."""
    drifts = []

    for dim in ["platform", "cwd", "git_remote", "git_branch", "python_version"]:
        if dim not in assumptions:
            continue  # first run, no baseline yet

        old = assumptions[dim]
        new = current[dim]

        if old != new:
            drifts.append(f"{dim}={old}→{new}")

    # Check critical paths
    if "critical_paths" in assumptions:
        try:
            old_paths = json.loads(assumptions["critical_paths"]) if isinstance(assumptions["critical_paths"], str) else assumptions["critical_paths"]
            new_paths = current["critical_paths"]

            for name, status in new_paths.items():
                old_status = old_paths.get(name)
                if old_status and old_status != status:
                    drifts.append(f"critical_path[{name}]={old_status}→{status}")
        except (json.JSONDecodeError, KeyError):
            pass

    return drifts


def main():
    parser = argparse.ArgumentParser(description="Memory consistency check for boot")
    parser.add_argument("--agent", required=True, help="Agent ID (ceo, cto, etc)")
    parser.add_argument("--force-write", action="store_true",
                       help="Force refresh all assumptions to current env")
    args = parser.parse_args()

    db = get_memory_db()
    current = get_current_env()
    assumptions = load_assumptions(db, args.agent)

    # First run or force-write: bootstrap
    if not assumptions or args.force_write:
        save_assumptions(db, args.agent, current)
        if args.force_write:
            print(f"FORCE_WRITE: refreshed {len(current)} assumptions", file=sys.stderr)
        return 0

    # Drift detection
    drifts = detect_drift(assumptions, current)

    if drifts:
        print(f"MEMORY_DRIFT_DETECTED: {'; '.join(drifts)}")
        # Set flag for agent to acknowledge
        flag_file = REPO_ROOT / ".ystar_session_flags"
        with open(flag_file, "a") as f:
            f.write("MEMORY_DRIFT_PENDING_ACK=1\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

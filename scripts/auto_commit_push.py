#!/usr/bin/env python3
"""
auto_commit_push.py — Milestone 13 production implementation.

Per Ethan CTO ruling CZL-AUTO-COMMIT-PUSH (2026-04-19):
- CLI: --mode {once|daemon} --repo {ystar-company|y-star-gov|both}
- Mtime gate: skip if last run <10min AND no file changed
- Hash dedupe: skip if git diff HEAD hash unchanged since last run
- Sanity gates: no .ystar_cieu.db, no >50MB files, no leaked secrets
- Commit message: [auto] WIP checkpoint YYYY-MM-DD HH:MM -- N files changed
- Push gated by env YSTAR_AUTO_PUSH_ENABLED=1
- Sentinel: scripts/.auto_commit_push_sentinel.json
- CIEU event AUTO_COMMIT_PUSH_CYCLE per invocation

Author: Ethan Wright (CTO) — M13 implementation
Date: 2026-04-21
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Paths ──────────────────────────────────────────────────────────
COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
YSTAR_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
SENTINEL_PATH = COMPANY_ROOT / "scripts" / ".auto_commit_push_sentinel.json"
LOG_DIR = COMPANY_ROOT / "scripts" / ".logs"
LOG_FILE = LOG_DIR / "auto_commit_push.log"

REPO_MAP = {
    "ystar-company": COMPANY_ROOT,
    "y-star-gov": YSTAR_GOV_ROOT,
}

# ── Safety exclusions (never staged) ──────────────────────────────
EXCLUDE_PATTERNS = [
    ".ystar_cieu.db",
    ".ystar_cieu_omission.db",
    ".ystar_memory.db",
    "aiden_brain.db",
    ".env",
    ".ystar_session.json",
    ".ystar_active_agent",
    ".k9_subscriber_state.json",
    ".ystar_warning_queue_archive.json",
    "scripts/.session_booted",
    "scripts/.session_call_count",
    "scripts/.logs/",
    "scripts/.ystar_",
    "scripts/.k9_",
    "scripts/.brain_",
    "__pycache__",
    ".pyc",
    ".whl",
    ".egg-info",
    ".bak",
    ".swp",
    ".venv/",
    ".venv\\",
    "_brain.db",
    ".lock",
    ".ppid_",
    ".commit_msg",
    ".commit_msgs/",
    "bench_out",
]

# Files that must never be staged (exact basename match)
EXCLUDE_BASENAMES = {
    ".ystar_cieu.db", ".ystar_cieu.db-shm", ".ystar_cieu.db-wal",
    ".ystar_cieu_omission.db", ".ystar_cieu_omission.db-shm", ".ystar_cieu_omission.db-wal",
    ".ystar_memory.db", ".ystar_memory.db-shm", ".ystar_memory.db-wal",
    "aiden_brain.db", "aiden_brain.db-shm", "aiden_brain.db-wal",
    "ethan_brain.db", "leo_brain.db", "maya_brain.db", "ryan_brain.db",
    "jordan_brain.db", "sofia_brain.db", "zara_brain.db", "marco_brain.db",
    "samantha_brain.db",
    ".env",
}

# Secret patterns (simple string scan)
SECRET_PATTERNS = [
    re.compile(r"ANTHROPIC_API_KEY\s*=\s*sk-"),
    re.compile(r"OPENAI_API_KEY\s*=\s*sk-"),
    re.compile(r"sk-ant-[a-zA-Z0-9]{20,}"),
    re.compile(r"password\s*=\s*['\"][^'\"]{8,}"),
]

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB
MTIME_GATE_SECONDS = 600  # 10 minutes


# ── Helpers ────────────────────────────────────────────────────────

def log(msg: str) -> None:
    """Append timestamped line to log file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line)
    except OSError:
        pass
    print(line.rstrip(), file=sys.stderr)


def load_sentinel() -> Dict[str, Any]:
    """Load sentinel JSON or return empty dict."""
    if SENTINEL_PATH.exists():
        try:
            return json.loads(SENTINEL_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_sentinel(data: Dict[str, Any]) -> None:
    """Persist sentinel JSON."""
    SENTINEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SENTINEL_PATH.write_text(json.dumps(data, indent=2) + "\n")


def git_run(repo: Path, args: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a git command in the given repo."""
    return subprocess.run(
        ["git", "-C", str(repo)] + args,
        capture_output=True, text=True, timeout=timeout,
    )


def get_porcelain(repo: Path) -> str:
    """Return git status --porcelain output."""
    r = git_run(repo, ["status", "--porcelain"])
    return r.stdout.strip() if r.returncode == 0 else ""


def get_diff_hash(repo: Path) -> str:
    """Compute hash of git diff HEAD (content-based dedupe)."""
    r = git_run(repo, ["diff", "HEAD"])
    content = r.stdout if r.returncode == 0 else ""
    # Also include untracked files list
    u = git_run(repo, ["ls-files", "--others", "--exclude-standard"])
    untracked = u.stdout if u.returncode == 0 else ""
    combined = content + "\n---UNTRACKED---\n" + untracked
    return hashlib.sha256(combined.encode()).hexdigest()


def get_changed_files(repo: Path) -> List[str]:
    """Get list of modified + untracked files (for staging)."""
    files = []
    # Modified/deleted tracked files
    r = git_run(repo, ["diff", "--name-only", "HEAD"])
    if r.returncode == 0 and r.stdout.strip():
        files.extend(r.stdout.strip().split("\n"))
    # Untracked files
    r = git_run(repo, ["ls-files", "--others", "--exclude-standard"])
    if r.returncode == 0 and r.stdout.strip():
        files.extend(r.stdout.strip().split("\n"))
    return [f for f in files if f]


def is_excluded(filepath: str) -> bool:
    """Check if a file should be excluded from auto-commit."""
    basename = Path(filepath).name
    if basename in EXCLUDE_BASENAMES:
        return True
    for pat in EXCLUDE_PATTERNS:
        if pat in filepath:
            return True
    return False


def check_file_size(repo: Path, filepath: str) -> bool:
    """Return True if file is under 50MB limit."""
    full = repo / filepath
    if full.exists() and full.stat().st_size > MAX_FILE_SIZE_BYTES:
        return False
    return True


def check_no_secrets(repo: Path, filepath: str) -> bool:
    """Return True if file does not contain secret patterns."""
    full = repo / filepath
    if not full.exists() or not full.is_file():
        return True
    # Skip binary files
    try:
        content = full.read_text(errors="ignore")
    except OSError:
        return True
    for pat in SECRET_PATTERNS:
        if pat.search(content):
            return False
    return True


# ── Core logic ─────────────────────────────────────────────────────

def process_repo(
    repo_name: str,
    repo_path: Path,
    sentinel: Dict[str, Any],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Process one repo: check gates, commit, optionally push.

    Returns a result dict for CIEU event payload.
    """
    result: Dict[str, Any] = {
        "repo": repo_name,
        "action": "skip",
        "reason": "",
        "files_committed": 0,
        "files_skipped": 0,
        "commit_hash": None,
        "pushed": False,
        "errors": [],
    }

    # 1. Check if repo exists
    if not repo_path.exists():
        result["reason"] = "repo_not_found"
        result["errors"].append(f"{repo_path} does not exist")
        return result

    # 2. git status --porcelain: if empty, nothing to do
    porcelain = get_porcelain(repo_path)
    if not porcelain:
        result["reason"] = "clean_working_tree"
        log(f"[{repo_name}] SKIP: clean working tree")
        return result

    # 3. Mtime gate: skip if last run <10min ago
    repo_sentinel = sentinel.get(repo_name, {})
    last_run_ts = repo_sentinel.get("last_run_ts", 0)
    now = time.time()
    if now - last_run_ts < MTIME_GATE_SECONDS:
        # But still check if content actually changed via hash
        current_hash = get_diff_hash(repo_path)
        last_hash = repo_sentinel.get("last_hash", "")
        if current_hash == last_hash:
            result["reason"] = "mtime_gate_and_hash_unchanged"
            log(f"[{repo_name}] SKIP: within 10min window and hash unchanged")
            return result
        # Hash changed within 10min -- proceed (new content worth committing)

    # 4. Hash dedupe: compute diff hash, compare to sentinel
    current_hash = get_diff_hash(repo_path)
    last_hash = repo_sentinel.get("last_hash", "")
    if current_hash == last_hash:
        result["reason"] = "hash_unchanged"
        log(f"[{repo_name}] SKIP: diff hash unchanged")
        return result

    # 5. Get changed files and filter
    all_files = get_changed_files(repo_path)
    safe_files = []
    skipped_files = []

    for f in all_files:
        if is_excluded(f):
            skipped_files.append(f"excluded:{f}")
            continue
        if not check_file_size(repo_path, f):
            skipped_files.append(f"too_large:{f}")
            result["errors"].append(f"File > 50MB: {f}")
            continue
        if not check_no_secrets(repo_path, f):
            skipped_files.append(f"secret_detected:{f}")
            result["errors"].append(f"Secret pattern in: {f}")
            continue
        safe_files.append(f)

    if not safe_files:
        result["reason"] = "no_safe_files_after_filter"
        result["files_skipped"] = len(skipped_files)
        log(f"[{repo_name}] SKIP: {len(skipped_files)} files filtered, 0 safe")
        return result

    # 6. Commit
    ts_str = time.strftime("%Y-%m-%d %H:%M")
    commit_msg = f"[auto] WIP checkpoint {ts_str} -- {len(safe_files)} files changed"

    if dry_run:
        log(f"[{repo_name}] DRY-RUN: would commit {len(safe_files)} files")
        result["action"] = "dry_run"
        result["files_committed"] = len(safe_files)
        result["files_skipped"] = len(skipped_files)
        return result

    # Stage specific files (never git add -A)
    try:
        git_run(repo_path, ["add", "--"] + safe_files, timeout=30)
    except Exception as e:
        result["errors"].append(f"git add failed: {e}")
        result["reason"] = "git_add_failed"
        return result

    # Commit
    try:
        r = git_run(repo_path, ["commit", "-m", commit_msg], timeout=30)
        if r.returncode != 0:
            result["errors"].append(f"git commit failed: {r.stderr.strip()}")
            result["reason"] = "git_commit_failed"
            return result
    except Exception as e:
        result["errors"].append(f"git commit exception: {e}")
        result["reason"] = "git_commit_failed"
        return result

    # Get commit hash
    r = git_run(repo_path, ["rev-parse", "HEAD"], timeout=10)
    commit_hash = r.stdout.strip() if r.returncode == 0 else "unknown"

    result["action"] = "committed"
    result["commit_hash"] = commit_hash
    result["files_committed"] = len(safe_files)
    result["files_skipped"] = len(skipped_files)
    log(f"[{repo_name}] COMMITTED {commit_hash[:12]} ({len(safe_files)} files)")

    # 7. Push gate: env var YSTAR_AUTO_PUSH_ENABLED must be "1"
    push_enabled = os.environ.get("YSTAR_AUTO_PUSH_ENABLED", "0") == "1"
    if push_enabled:
        try:
            pr = git_run(repo_path, ["push", "origin", "main"], timeout=120)
            if pr.returncode == 0:
                result["pushed"] = True
                log(f"[{repo_name}] PUSHED to origin/main")
            else:
                result["errors"].append(f"git push failed: {pr.stderr.strip()}")
                log(f"[{repo_name}] PUSH FAILED: {pr.stderr.strip()}")
        except Exception as e:
            result["errors"].append(f"git push exception: {e}")
            log(f"[{repo_name}] PUSH EXCEPTION: {e}")
    else:
        log(f"[{repo_name}] PUSH SKIPPED: YSTAR_AUTO_PUSH_ENABLED != 1")

    # 8. Update sentinel
    sentinel[repo_name] = {
        "last_run_ts": now,
        "last_hash": current_hash,
        "last_commit_hash": commit_hash,
    }

    return result


def emit_cieu_event(results: List[Dict[str, Any]]) -> None:
    """Write AUTO_COMMIT_PUSH_CYCLE event to CIEU database (best-effort)."""
    try:
        import sqlite3
        db_path = COMPANY_ROOT / ".ystar_cieu.db"
        if not db_path.exists():
            return
        conn = sqlite3.connect(str(db_path), timeout=5)
        conn.execute("CREATE TABLE IF NOT EXISTS cieu_events ("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "timestamp REAL, event_type TEXT, agent_id TEXT,"
                     "payload TEXT)")
        payload = json.dumps({
            "repos": results,
            "sentinel_path": str(SENTINEL_PATH),
            "push_env": os.environ.get("YSTAR_AUTO_PUSH_ENABLED", "0"),
        })
        conn.execute(
            "INSERT INTO cieu_events (timestamp, event_type, agent_id, payload) "
            "VALUES (?, ?, ?, ?)",
            (time.time(), "AUTO_COMMIT_PUSH_CYCLE", "auto_commit_push", payload),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log(f"[CIEU] emit failed (non-fatal): {e}")


def run_once(repos: List[str], dry_run: bool = False) -> int:
    """Single pass over specified repos. Returns 0 on success."""
    sentinel = load_sentinel()
    results = []

    for repo_name in repos:
        repo_path = REPO_MAP.get(repo_name)
        if repo_path is None:
            log(f"Unknown repo: {repo_name}")
            continue
        r = process_repo(repo_name, repo_path, sentinel, dry_run=dry_run)
        results.append(r)

    save_sentinel(sentinel)
    emit_cieu_event(results)

    # Print summary
    for r in results:
        action = r["action"]
        repo = r["repo"]
        if action == "committed":
            print(f"[{repo}] committed {r['files_committed']} files -> {r['commit_hash'][:12]}"
                  f"{' (pushed)' if r['pushed'] else ''}")
        elif action == "skip":
            print(f"[{repo}] skipped: {r['reason']}")
        elif action == "dry_run":
            print(f"[{repo}] dry-run: would commit {r['files_committed']} files")

    return 0


def run_daemon(repos: List[str], interval: int = 1800) -> int:
    """Loop forever, running once every interval seconds."""
    log(f"[daemon] starting with interval={interval}s repos={repos}")
    while True:
        try:
            run_once(repos)
        except Exception as e:
            log(f"[daemon] cycle error: {e}")
        time.sleep(interval)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Auto-commit-push for Y* Bridge Labs repos (M13)"
    )
    parser.add_argument(
        "--mode", choices=["once", "daemon"], default="once",
        help="once: single pass; daemon: loop every --interval seconds"
    )
    parser.add_argument(
        "--repo", choices=["ystar-company", "y-star-gov", "both"], default="both",
        help="Which repo(s) to process"
    )
    parser.add_argument(
        "--interval", type=int, default=1800,
        help="Daemon loop interval in seconds (default 1800 = 30min)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview without executing any git operations"
    )
    args = parser.parse_args()

    repos = list(REPO_MAP.keys()) if args.repo == "both" else [args.repo]

    if args.mode == "daemon":
        return run_daemon(repos, interval=args.interval)
    else:
        return run_once(repos, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())

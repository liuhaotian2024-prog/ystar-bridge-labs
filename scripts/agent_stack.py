"""
CZL-P1-e: Agent Stack — push/pop for subagent identity management.

When a subagent is spawned, push the current agent onto a stack and write
the subagent name to the active agent marker. When the subagent completes,
pop the stack and restore the previous agent.

This prevents the "identity pollution" lock-death where CEO's main thread
gets stuck with a subagent's identity after the subagent exits.

Stack file: scripts/.agent_stack.json (JSON list, last = most recent push)
Marker file: scripts/.ystar_active_agent (flat text, single agent name)

CZL-MARKER-PER-SESSION-ISOLATION (2026-04-19):
  Per-session marker isolation. Each Claude Code session gets its own
  marker file (.ystar_active_agent.<session_id>) and stack file
  (.agent_stack.<session_id>.json) to prevent race conditions when N
  parallel sub-agents write concurrently. Fallback chain for reads:
    1. Per-session marker: .ystar_active_agent.<session_id>
    2. Global marker: .ystar_active_agent (backward compat)
    3. DEFAULT_AGENT ("ceo")

Author: Ryan Park (eng-platform)
"""
import json
import os
import fcntl
from pathlib import Path
from typing import Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
STACK_FILE = SCRIPTS_DIR / ".agent_stack.json"
MARKER_FILE = SCRIPTS_DIR / ".ystar_active_agent"  # global fallback
LOCK_FILE = SCRIPTS_DIR / ".agent_stack.lock"
DEFAULT_AGENT = "ceo"


def _get_session_id() -> Optional[str]:
    """
    Get a session-unique identifier for per-session marker isolation.

    Priority:
    1. CLAUDE_SESSION_ID env var (set by Claude Code per session)
    2. PPID (parent process ID — unique per terminal/session)
    3. None (fallback to global marker)
    """
    sid = os.environ.get("CLAUDE_SESSION_ID", "").strip()
    if sid:
        # Sanitize: only keep alphanumeric, dash, underscore to prevent
        # path injection
        sanitized = "".join(c for c in sid if c.isalnum() or c in "-_")
        if sanitized:
            return sanitized
    # Fallback: PPID
    ppid = os.environ.get("PPID", "")
    if not ppid:
        try:
            ppid = str(os.getppid())
        except Exception:
            pass
    if ppid and ppid != "1":  # PID 1 is init, not useful
        return f"ppid_{ppid}"
    return None


def _session_marker_file() -> Path:
    """
    Return the per-session marker file path if a session ID is available,
    otherwise return the global marker file path.
    """
    sid = _get_session_id()
    if sid:
        return SCRIPTS_DIR / f".ystar_active_agent.{sid}"
    return MARKER_FILE


def _session_stack_file() -> Path:
    """
    Return the per-session stack file path if a session ID is available,
    otherwise return the global stack file path.
    """
    sid = _get_session_id()
    if sid:
        return SCRIPTS_DIR / f".agent_stack.{sid}.json"
    return STACK_FILE


def _session_lock_file() -> Path:
    """
    Return the per-session lock file path if a session ID is available,
    otherwise return the global lock file path.
    """
    sid = _get_session_id()
    if sid:
        return SCRIPTS_DIR / f".agent_stack.{sid}.lock"
    return LOCK_FILE


class _StackLock:
    """File-based lock for atomic read-modify-write of stack + marker.

    CZL-MARKER-PER-SESSION-ISOLATION: Uses per-session lock file so
    concurrent sessions don't contend on the same lock.
    """

    def __init__(self, lock_path: Optional[Path] = None):
        self._fd = None
        self._lock_path = lock_path or _session_lock_file()

    def __enter__(self):
        self._fd = open(self._lock_path, "w")
        try:
            fcntl.flock(self._fd, fcntl.LOCK_EX)
        except Exception:
            self._fd.close()
            self._fd = None
        return self

    def __exit__(self, *args):
        if self._fd is not None:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
            except Exception:
                pass
            self._fd.close()
            self._fd = None


def _read_stack() -> list:
    """Read the agent stack from disk. Uses per-session stack file."""
    stack_file = _session_stack_file()
    try:
        with open(stack_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def _write_stack(stack: list) -> None:
    """Write the agent stack to disk atomically. Uses per-session stack file."""
    stack_file = _session_stack_file()
    tmp = str(stack_file) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(stack, f)
    os.replace(tmp, str(stack_file))


def _read_marker() -> str:
    """Read the current active agent from the marker file.

    CZL-MARKER-PER-SESSION-ISOLATION fallback chain:
    1. Per-session marker (.ystar_active_agent.<session_id>)
    2. Global marker (.ystar_active_agent)
    3. DEFAULT_AGENT ("ceo")
    """
    # 1. Per-session marker
    session_marker = _session_marker_file()
    if session_marker != MARKER_FILE:  # only if we have a real session ID
        try:
            content = session_marker.read_text(encoding="utf-8").strip()
            if content:
                return content
        except FileNotFoundError:
            pass
    # 2. Global marker (backward compat)
    try:
        content = MARKER_FILE.read_text(encoding="utf-8").strip()
        return content if content else DEFAULT_AGENT
    except FileNotFoundError:
        return DEFAULT_AGENT


def _write_marker(agent: str) -> None:
    """Write agent name to both per-session and global marker files.

    Per-session marker is the primary target. Global marker is also
    written for backward compatibility with callers that don't yet
    understand per-session isolation.
    """
    session_marker = _session_marker_file()
    session_marker.write_text(agent + "\n", encoding="utf-8")
    # Also write global marker for backward compat
    try:
        MARKER_FILE.write_text(agent + "\n", encoding="utf-8")
    except Exception:
        pass  # Non-fatal: per-session marker is the source of truth


def push_agent(subagent_name: str) -> str:
    """
    Push current agent onto stack and write subagent name to marker.

    Uses file lock to prevent race conditions between concurrent hook processes.
    Returns the previous agent name (the one that was pushed).
    """
    with _StackLock():
        current = _read_marker()
        stack = _read_stack()
        stack.append(current)
        _write_stack(stack)
        _write_marker(subagent_name.strip())
        return current


def pop_agent() -> str:
    """
    Pop the stack and restore the previous agent to the marker.

    Uses file lock to prevent race conditions.
    Returns the restored agent name.
    If stack is empty, restores to DEFAULT_AGENT ("ceo").
    """
    with _StackLock():
        stack = _read_stack()
        if stack:
            previous = stack.pop()
            _write_stack(stack)
            _write_marker(previous)
            return previous
        else:
            _write_marker(DEFAULT_AGENT)
            return DEFAULT_AGENT


def current_agent() -> str:
    """Read the current active agent from marker file."""
    return _read_marker()


def stack_depth() -> int:
    """Return the number of entries in the agent stack."""
    return len(_read_stack())


def reset_stack() -> None:
    """Clear the stack and reset marker to default. For emergency recovery."""
    _write_stack([])
    _write_marker(DEFAULT_AGENT)


def cleanup_session_files() -> int:
    """
    Remove per-session marker, stack, and lock files for the current session.
    Call this when a session ends to avoid file accumulation.
    Returns the number of files removed.
    """
    sid = _get_session_id()
    if not sid:
        return 0
    removed = 0
    for pattern in [
        f".ystar_active_agent.{sid}",
        f".agent_stack.{sid}.json",
        f".agent_stack.{sid}.json.tmp",
        f".agent_stack.{sid}.lock",
    ]:
        target = SCRIPTS_DIR / pattern
        try:
            target.unlink()
            removed += 1
        except FileNotFoundError:
            pass
    return removed


def get_session_id() -> Optional[str]:
    """Public accessor for the current session ID. Returns None if no
    session-level isolation is active."""
    return _get_session_id()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_push = sub.add_parser("push-agent")
    p_push.add_argument("agent_id")
    sub.add_parser("pop-agent")
    sub.add_parser("peek")
    args = parser.parse_args()
    if args.cmd == "push-agent":
        push_agent(args.agent_id)
    elif args.cmd == "pop-agent":
        pop_agent()
    elif args.cmd == "peek":
        print(current_agent() or "")

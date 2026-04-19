"""
CZL-P1-e: Agent Stack — push/pop for subagent identity management.

When a subagent is spawned, push the current agent onto a stack and write
the subagent name to the active agent marker. When the subagent completes,
pop the stack and restore the previous agent.

This prevents the "identity pollution" lock-death where CEO's main thread
gets stuck with a subagent's identity after the subagent exits.

Stack file: scripts/.agent_stack.json (JSON list, last = most recent push)
Marker file: scripts/.ystar_active_agent (flat text, single agent name)

Author: Ryan Park (eng-platform)
"""
import json
import os
import fcntl
from pathlib import Path
from typing import Optional

SCRIPTS_DIR = Path(__file__).resolve().parent
STACK_FILE = SCRIPTS_DIR / ".agent_stack.json"
MARKER_FILE = SCRIPTS_DIR / ".ystar_active_agent"
LOCK_FILE = SCRIPTS_DIR / ".agent_stack.lock"
DEFAULT_AGENT = "ceo"


class _StackLock:
    """File-based lock for atomic read-modify-write of stack + marker."""

    def __init__(self):
        self._fd = None

    def __enter__(self):
        self._fd = open(LOCK_FILE, "w")
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
    """Read the agent stack from disk. Returns empty list if not found."""
    try:
        with open(STACK_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return []


def _write_stack(stack: list) -> None:
    """Write the agent stack to disk atomically."""
    tmp = str(STACK_FILE) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(stack, f)
    os.replace(tmp, str(STACK_FILE))


def _read_marker() -> str:
    """Read the current active agent from the marker file."""
    try:
        content = MARKER_FILE.read_text(encoding="utf-8").strip()
        return content if content else DEFAULT_AGENT
    except FileNotFoundError:
        return DEFAULT_AGENT


def _write_marker(agent: str) -> None:
    """Write agent name to the marker file."""
    MARKER_FILE.write_text(agent + "\n", encoding="utf-8")


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

#!/usr/bin/env python3
"""
V3-Jordan — PostToolUse Hook: memory/feedback_*.md -> yaml proposal pipeline

Purpose: After any Write tool completes targeting memory/feedback_*.md,
  trigger the wisdom-to-yaml pipeline (wisdom_to_yaml_proposer.py) to
  auto-generate a candidate governance rule in governance/proposed_rules/.
  This closes the loop: new Board feedback -> automatic yaml proposal -> CTO review.

Wiring: .claude/settings.json hooks.PostToolUse entry with matcher "Write".
  Registration example (CTO adds to settings.json):
  {
    "matcher": "Write",
    "hooks": [{
      "type": "command",
      "command": "python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_posttool_feedback_to_yaml.py",
      "timeout": 10000
    }]
  }

Advisory hook — never blocks Write. Fail-open on all errors.
"""
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
import uuid
from pathlib import Path

REPO_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = REPO_ROOT / ".ystar_cieu.db"
PROPOSER_SCRIPT = REPO_ROOT / "scripts" / "wisdom_to_yaml_proposer.py"
PROPOSED_RULES_DIR = REPO_ROOT / "governance" / "proposed_rules"

# Pattern: memory/feedback_*.md (absolute or relative)
FEEDBACK_FILE_PATTERN = re.compile(r"memory/feedback_[^/]+\.md$")


def _emit_cieu(event_type: str, metadata: dict) -> None:
    """Emit a CIEU event. Fail-open: never crashes on DB errors."""
    try:
        conn = sqlite3.connect(str(CIEU_DB), timeout=2.0)
        conn.execute(
            "INSERT INTO cieu_events "
            "(event_id, seq_global, created_at, session_id, agent_id, "
            "event_type, decision, passed, task_description) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                0,
                time.time(),
                "feedback_to_yaml_hook",
                "eng-domains",
                event_type,
                "info",
                1,
                json.dumps(metadata, ensure_ascii=False)[:500],
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[V3-Jordan] CIEU emit failed: {e}", file=sys.stderr)


def hook_posttool_feedback_to_yaml(
    tool_name: str, tool_input: dict, tool_result: dict
) -> dict:
    """
    PostToolUse hook: fires after Write tool completes.
    If file_path matches memory/feedback_*.md, triggers yaml proposal generation.

    Args:
        tool_name: The tool that was invoked (e.g. "Write", "Read", "Bash")
        tool_input: The input dict passed to the tool (contains file_path for Write)
        tool_result: The result dict returned by the tool

    Returns:
        dict with status key. Always "ok" — this hook is advisory (never blocks).
    """
    # Gate 1: Only fire on Write tool
    if tool_name != "Write":
        return {"status": "ok", "fired": False, "reason": "not_write_tool"}

    # Gate 2: Check file path matches memory/feedback_*.md
    file_path = tool_input.get("file_path", "")
    if not FEEDBACK_FILE_PATTERN.search(file_path):
        return {"status": "ok", "fired": False, "reason": "path_no_match"}

    # --- Hook fires: feedback file was written ---
    feedback_filename = Path(file_path).name
    proposer_available = PROPOSER_SCRIPT.exists()
    proposer_result = None
    proposer_error = None

    if proposer_available:
        # Call the wisdom-to-yaml proposer
        try:
            result = subprocess.run(
                [sys.executable, str(PROPOSER_SCRIPT), file_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(REPO_ROOT),
            )
            proposer_result = {
                "returncode": result.returncode,
                "stdout": result.stdout[:200] if result.stdout else "",
                "stderr": result.stderr[:200] if result.stderr else "",
            }
        except subprocess.TimeoutExpired:
            proposer_error = "proposer_timeout_30s"
        except Exception as e:
            proposer_error = f"proposer_subprocess_error: {e}"
    else:
        print(
            "[SKIP] wisdom_to_yaml_proposer.py not yet available (Maya V3 pending)",
            file=sys.stderr,
        )

    # Emit CIEU event
    cieu_payload = {
        "file_path": file_path,
        "feedback_filename": feedback_filename,
        "proposer_available": proposer_available,
        "proposer_result": proposer_result,
        "proposer_error": proposer_error,
    }
    _emit_cieu("FEEDBACK_TO_YAML_HOOK_FIRED", cieu_payload)

    return {
        "status": "ok",
        "fired": True,
        "file_path": file_path,
        "proposer_available": proposer_available,
        "proposer_result": proposer_result,
        "proposer_error": proposer_error,
    }


def main():
    """Entry point when invoked as PostToolUse hook from Claude Code."""
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:
        payload = {}

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    tool_result = payload.get("tool_result", {})

    result = hook_posttool_feedback_to_yaml(tool_name, tool_input, tool_result)

    # PostToolUse hooks must output JSON with "action" key
    output = {"action": "allow"}
    output.update(result)
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()

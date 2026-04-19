#!/usr/bin/env python3
"""
PreToolUse Hook — CEO Pre-Output U-Workflow Enforcement

Authority: CTO Ethan Wright, Board-authorized CZL-159 P0
Purpose: Block CEO Write to external-facing paths without U-workflow evidence.

Checks Write tool calls targeting reports/, content/, knowledge/ceo/strategy/.
Scans the written content for 3 compliance signals:
  1. Research evidence (source/cite/per/according/search/found)
  2. Synthesis evidence (therefore/because/analysis/conclude/lesson/insight)
  3. Audience/purpose framing (audience/purpose/for Board/stakeholder/reader)

If ANY signal missing -> block with actionable message.
If all present -> allow.

Called by: ~/.claude/settings.json hooks.PreToolUse[Write]
Stdin: {"tool_name":"Write","tool_input":{"file_path":"...","content":"..."}}
Stdout: Claude Code hookSpecificOutput format (permissionDecision: allow|deny)
"""

import sys
import json
import re

ENFORCED_PREFIXES = ("reports/", "content/", "knowledge/ceo/strategy/")

RESEARCH_PATTERNS = re.compile(
    r"(source[s]?[:\s]|cite[ds]?[\s:]|per\s+\w|according\s+to|"
    r"search|found\s+that|reference[ds]?|evidence|data\s+show|"
    r"based\s+on|research|study|paper|article|empirical)",
    re.IGNORECASE,
)

SYNTHESIS_PATTERNS = re.compile(
    r"(therefore|because|analysis|conclude[ds]?|lesson[s]?|"
    r"insight[s]?|implication|root\s+cause|pattern|takeaway|"
    r"diagnosis|framework|principle|synthesis|assessment)",
    re.IGNORECASE,
)

AUDIENCE_PATTERNS = re.compile(
    r"(audience|purpose|for\s+board|stakeholder|reader[s]?|"
    r"目标受众|目的|面向|intended\s+for|context\s+for|"
    r"decision\s+maker|consumer|recipient)",
    re.IGNORECASE,
)


def is_enforced_path(file_path: str) -> bool:
    """Check if path falls under CEO external-facing enforcement."""
    for prefix in ENFORCED_PREFIXES:
        if prefix in file_path:
            return True
    return False


def check_compliance(content: str) -> dict:
    """Return {signal: bool} for each U-workflow requirement."""
    return {
        "research": bool(RESEARCH_PATTERNS.search(content)),
        "synthesis": bool(SYNTHESIS_PATTERNS.search(content)),
        "audience": bool(AUDIENCE_PATTERNS.search(content)),
    }


def _cc_output(decision: str, reason: str = ""):
    """Output in Claude Code hookSpecificOutput format."""
    out = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
        }
    }
    if reason:
        out["hookSpecificOutput"]["permissionDecisionReason"] = reason
    print(json.dumps(out))


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print("{}")
        return

    tool = payload.get("tool_name", "") or payload.get("tool", "")
    if tool != "Write":
        print("{}")
        return

    inp = payload.get("tool_input", {}) or payload.get("input", {})
    file_path = inp.get("file_path", "")

    if not is_enforced_path(file_path):
        print("{}")
        return

    content = inp.get("content", "")
    signals = check_compliance(content)
    missing = [k for k, v in signals.items() if not v]

    if missing:
        msg = (
            f"[CZL-159] CEO PRE-OUTPUT BLOCK: Write to {file_path} missing "
            f"U-workflow signals: {', '.join(missing)}. "
            f"Do research/synthesis/audience framing before writing."
        )
        _cc_output("deny", msg)
    else:
        print("{}")


if __name__ == "__main__":
    main()

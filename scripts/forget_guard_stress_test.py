#!/usr/bin/env python3
"""
forget_guard_stress_test.py - Campaign v3 Phase 1 W4 stress test

10 cases covering all 4 deny rules:
- defer_language (defer_001, defer_002, defer_003)
- choice_question_to_board (choice_001, choice_002)
- defer_language_in_commit_msg (commit_001, commit_002)
- defer_language_in_echo (echo_001)
- safe cases (safe_001, safe_002)

Expected: 8 deny, 2 allow, 10/10 pass.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GUARD_SCRIPT = REPO_ROOT / "scripts" / "forget_guard.py"

# Test cases: (id, payload, expected_action, description)
# Payload format: flat PreToolUse schema {"tool": "X", "command": "...", "file_path": "...", "content": "..."}
CASES = [
    # defer_language rules — trigger on Edit/Write tools (3 cases)
    ("defer_001", {
        "tool": "Write",
        "file_path": "reports/test.md",
        "content": "We can defer this to next session"
    }, "deny", "defer in Write content"),

    ("defer_002", {
        "tool": "Edit",
        "file_path": "src/test.py",
        "old_string": "old",
        "new_string": "Let's push this to tomorrow"
    }, "deny", "push-to-tomorrow in Edit"),

    ("defer_003", {
        "tool": "Write",
        "file_path": "docs/plan.md",
        "content": "Will handle later"
    }, "deny", "later in Write content"),

    # choice_question_to_board — trigger on Edit/Write (2 cases)
    ("choice_001", {
        "tool": "Write",
        "file_path": "reports/decision.md",
        "content": "Board请选择：1) Plan A 2) Plan B"
    }, "deny", "numbered choice question in Write"),

    ("choice_002", {
        "tool": "Edit",
        "file_path": "reports/status.md",
        "old_string": "status",
        "new_string": "老大选择方案一还是方案二？"
    }, "deny", "Chinese choice question in Edit"),

    # defer_language_in_commit_msg — trigger on Bash + git commit (2 cases)
    # Keywords from rule: ["明日", "明早", "tomorrow", "next session", "queued for", "wait for", "稍后", "later"]
    ("commit_001", {
        "tool": "Bash",
        "command": "git commit -m 'queued for next session'"
    }, "deny", "queued-for-next-session in commit message"),

    ("commit_002", {
        "tool": "Bash",
        "command": "git commit -m 'will handle later'"
    }, "deny", "later in commit message"),

    # defer_language_in_echo — trigger on Bash + echo (1 case)
    # Keywords from rule: ["明日", "明早", "tomorrow", "next session", "queued for", "wait for", "稍后", "later"]
    ("echo_001", {
        "tool": "Bash",
        "command": "echo '明日处理'"
    }, "deny", "明日 in echo command"),

    # safe cases (2 cases)
    ("safe_001", {
        "tool": "Bash",
        "command": "pytest tests/"
    }, "allow", "normal pytest command"),

    ("safe_002", {
        "tool": "Write",
        "file_path": "src/feature_x.py",
        "content": "def feature_x(): pass"
    }, "allow", "normal Write file"),
]


def run_test(case_id, payload, expected_action, description):
    """Run single test case through forget_guard.py."""
    try:
        result = subprocess.run(
            [sys.executable, str(GUARD_SCRIPT)],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return False, f"non-zero exit: {result.returncode}"

        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            return False, f"invalid JSON output: {result.stdout[:100]}"

        actual_action = response.get("action", "").strip()

        if actual_action == expected_action:
            return True, None
        else:
            return False, f"expected {expected_action}, got {actual_action}"

    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)


def main():
    print("=== ForgetGuard Stress Test (Campaign v3 W4) ===\n")

    passed = 0
    failed = 0

    for case_id, payload, expected, desc in CASES:
        ok, err = run_test(case_id, payload, expected, desc)

        if ok:
            print(f"✅ {case_id}: {desc}")
            passed += 1
        else:
            print(f"❌ {case_id}: {desc} — {err}")
            failed += 1

    total = passed + failed
    pct = (passed / total * 100) if total > 0 else 0

    print(f"\n{'='*50}")
    print(f"Result: {passed}/{total} ({pct:.0f}%) {'✅ 全部通过' if failed == 0 else '❌ 存在失败'}")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

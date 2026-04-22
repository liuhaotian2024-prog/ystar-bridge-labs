"""
CZL-WHO-I-AM-SYSTEM-BINDING tests.

Verifies:
1. governance_boot.sh contains cat WHO_I_AM line
2. UserPromptSubmit hook output contains v0.4 key content
3. WHO_I_AM file missing -> hook graceful degradation (no crash)
"""
import json
import os
import subprocess
import sys
import tempfile

YSTAR_DIR = "/Users/haotianliu/.openclaw/workspace/ystar-company"
BOOT_SH = os.path.join(YSTAR_DIR, "scripts", "governance_boot.sh")
HOOK_WRAPPER = os.path.join(YSTAR_DIR, "scripts", "hook_wrapper.py")
WHO_I_AM = os.path.join(YSTAR_DIR, "knowledge", "ceo", "wisdom", "WHO_I_AM.md")


def test_boot_sh_contains_cat_whoiam():
    """governance_boot.sh must contain a cat command for WHO_I_AM.md."""
    with open(BOOT_SH, "r", encoding="utf-8") as f:
        content = f.read()
    # Verify cat command targeting WHO_I_AM.md exists
    assert "cat " in content and "WHO_I_AM.md" in content, (
        "governance_boot.sh must contain 'cat ...WHO_I_AM.md'"
    )
    # Verify it's conditional on CEO agent
    assert 'AGENT_ID" = "ceo"' in content or "AGENT_ID = ceo" in content, (
        "WHO_I_AM cat should be conditional on CEO agent_id"
    )


def test_user_prompt_submit_injects_whoiam_v04():
    """UserPromptSubmit hook must inject WHO_I_AM v0.4 section content."""
    # Simulate a UserPromptSubmit event
    payload = {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "test message",
    }

    env = os.environ.copy()
    env["PYTHONPATH"] = "/Users/haotianliu/.openclaw/workspace/Y-star-gov"

    proc = subprocess.run(
        [sys.executable, HOOK_WRAPPER],
        input=json.dumps(payload).encode(),
        capture_output=True,
        timeout=10,
        cwd=YSTAR_DIR,
        env=env,
    )

    # Should not crash
    assert proc.returncode == 0, f"Hook crashed: {proc.stderr.decode()[:500]}"

    # Parse output
    stdout = proc.stdout.decode().strip()
    assert stdout, "Hook produced no output for UserPromptSubmit"

    result = json.loads(stdout)

    # Verify v0.4 content injection
    hook_output = result.get("hookSpecificOutput", {})
    additional = hook_output.get("additionalSystemPrompt", "")

    # Key neutral terms from v0.4 section that should be present
    assert "WHO_I_AM active framing" in additional, (
        "Missing WHO_I_AM framing wrapper"
    )
    # Check for content from L3 framing section (neutral keywords)
    assert any(kw in additional for kw in ["上帝视角", "治理层两分", "L3 Framing"]), (
        f"L3 framing key content not found in injection. Got: {additional[:200]}"
    )


def test_whoiam_missing_graceful_degradation():
    """If WHO_I_AM.md does not exist, hook must not crash."""
    # Create a modified hook script that points to nonexistent file
    # We'll test by temporarily using a payload and monkeypatching the path

    # Simpler: invoke hook_wrapper with a UserPromptSubmit event
    # but from a directory where the relative path won't resolve.
    # The hook uses os.path.dirname(os.path.dirname(__file__)) which is stable.

    # Instead, let's just verify the code handles FileNotFoundError.
    # We'll invoke the hook from a temp dir where the knowledge/ tree doesn't exist.
    payload = {
        "hook_event_name": "UserPromptSubmit",
        "prompt": "test",
    }

    # Create a copy of hook_wrapper that references a nonexistent path
    with open(HOOK_WRAPPER, "r", encoding="utf-8") as f:
        hook_code = f.read()

    # Replace the WHO_I_AM path construction with a guaranteed-missing path
    modified_code = hook_code.replace(
        '"knowledge", "ceo", "wisdom", "WHO_I_AM.md"',
        '"NONEXISTENT_DIR_12345", "WHO_I_AM.md"',
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="/tmp"
    ) as tmp:
        tmp.write(modified_code)
        tmp_path = tmp.name

    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = "/Users/haotianliu/.openclaw/workspace/Y-star-gov"

        proc = subprocess.run(
            [sys.executable, tmp_path],
            input=json.dumps(payload).encode(),
            capture_output=True,
            timeout=10,
            cwd=YSTAR_DIR,
            env=env,
        )

        # Must not crash (returncode 0)
        assert proc.returncode == 0, (
            f"Hook crashed when WHO_I_AM missing: rc={proc.returncode}, "
            f"stderr={proc.stderr.decode()[:300]}"
        )

        # Output should be valid JSON (empty {} is acceptable)
        stdout = proc.stdout.decode().strip()
        result = json.loads(stdout)
        assert isinstance(result, dict), "Output must be valid JSON dict"

    finally:
        os.unlink(tmp_path)

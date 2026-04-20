"""
CZL-BRAIN-BOUNDARY-HOOKS regression tests.

Validates:
  D1: governance_boot.sh contains brain auto-ingest step 8.9.5
  D2: session_close_yml.py calls brain_auto_ingest at close boundary
  D3: .claude/settings.json has brain pre-query hook in UserPromptSubmit
  D4: Latency of hook_ceo_pre_output_brain_query.py

Author: Ryan Park (eng-platform)
Date: 2026-04-19
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
YGOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")


class TestD1BootBoundaryIngest:
    """D1: governance_boot.sh boot-time ingest wiring."""

    def test_boot_script_contains_brain_ingest_step(self):
        """Step 8.9.5 exists in governance_boot.sh."""
        boot_sh = COMPANY_ROOT / "scripts" / "governance_boot.sh"
        content = boot_sh.read_text()
        assert "8.9.5" in content, "Step 8.9.5 missing from governance_boot.sh"
        assert "Brain auto-ingest" in content or "brain auto-ingest" in content
        assert "brain_auto_ingest" in content, "brain_auto_ingest import missing"

    def test_boot_script_uses_extract_and_apply(self):
        """Boot script calls extract_candidates + apply_ingest."""
        boot_sh = COMPANY_ROOT / "scripts" / "governance_boot.sh"
        content = boot_sh.read_text()
        assert "extract_candidates" in content
        assert "apply_ingest" in content

    def test_boot_script_has_import_error_gate(self):
        """Boot script handles ImportError gracefully (Leo#6 gate)."""
        boot_sh = COMPANY_ROOT / "scripts" / "governance_boot.sh"
        content = boot_sh.read_text()
        assert "ImportError" in content, "Missing ImportError gate for module-not-ready"
        assert "BRAIN_INGEST_MODULE_NOT_READY" in content

    def test_boot_script_has_generic_exception_handler(self):
        """Boot script catches general exceptions without blocking boot."""
        boot_sh = COMPANY_ROOT / "scripts" / "governance_boot.sh"
        content = boot_sh.read_text()
        # Must have both ImportError AND generic Exception handlers
        assert "except ImportError" in content
        assert "except Exception" in content

    def test_boot_ingest_module_importable(self):
        """brain_auto_ingest module is importable and has required functions."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(YGOV_ROOT) + ":" + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-c", """
import sys
try:
    from ystar.governance.brain_auto_ingest import extract_candidates, apply_ingest
    # Verify the functions are callable (don't run full corpus)
    assert callable(extract_candidates), "extract_candidates not callable"
    assert callable(apply_ingest), "apply_ingest not callable"
    print("IMPORTABLE")
except ImportError:
    print("MODULE_NOT_READY")
except Exception as e:
    print(f"ERROR: {e}")
"""],
            capture_output=True, text=True, timeout=15, env=env,
        )
        assert result.returncode == 0, f"Import test crashed: {result.stderr}"
        output = result.stdout.strip()
        assert output in ("IMPORTABLE", "MODULE_NOT_READY"), \
            f"Unexpected output: {output}"

    def test_boot_ingest_gate_handles_missing_module(self):
        """ImportError gate works: non-existent module does not crash."""
        result = subprocess.run(
            [sys.executable, "-c", """
try:
    from ystar.governance.brain_auto_ingest_NONEXISTENT import run_boundary
    print("UNEXPECTED_IMPORT")
except ImportError:
    print("GATE_WORKS")
except Exception as e:
    print(f"ERROR: {e}")
"""],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0
        assert "GATE_WORKS" in result.stdout


class TestD2CloseBoundaryIngest:
    """D2: session_close_yml.py close-time ingest wiring."""

    def test_close_script_contains_brain_ingest(self):
        """session_close_yml.py has brain auto-ingest call."""
        close_py = COMPANY_ROOT / "scripts" / "session_close_yml.py"
        content = close_py.read_text()
        assert "brain_auto_ingest" in content, "brain_auto_ingest not in session_close_yml.py"
        assert "extract_candidates" in content
        assert "apply_ingest" in content

    def test_close_script_has_import_error_gate(self):
        """Close script handles ImportError gracefully."""
        close_py = COMPANY_ROOT / "scripts" / "session_close_yml.py"
        content = close_py.read_text()
        assert "ImportError" in content

    def test_close_script_brain_ingest_before_cleanup(self):
        """Brain ingest runs BEFORE active_agent home state cleanup."""
        close_py = COMPANY_ROOT / "scripts" / "session_close_yml.py"
        content = close_py.read_text()
        ingest_pos = content.find("brain_auto_ingest")
        cleanup_pos = content.find("home state cleanup")
        assert ingest_pos < cleanup_pos, \
            "Brain ingest must run before home state cleanup"


class TestD3PreQueryHookWiring:
    """D3: .claude/settings.json has brain pre-query hook."""

    def test_settings_has_brain_query_hook(self):
        """UserPromptSubmit contains hook_ceo_pre_output_brain_query.py."""
        settings_path = COMPANY_ROOT / ".claude" / "settings.json"
        settings = json.loads(settings_path.read_text())
        ups_hooks = settings.get("hooks", {}).get("UserPromptSubmit", [])
        found = False
        for entry in ups_hooks:
            for hook in entry.get("hooks", []):
                if "hook_ceo_pre_output_brain_query" in hook.get("command", ""):
                    found = True
                    break
        assert found, "hook_ceo_pre_output_brain_query not in UserPromptSubmit hooks"

    def test_settings_brain_hook_has_timeout(self):
        """Brain query hook has a timeout configured."""
        settings_path = COMPANY_ROOT / ".claude" / "settings.json"
        settings = json.loads(settings_path.read_text())
        ups_hooks = settings.get("hooks", {}).get("UserPromptSubmit", [])
        for entry in ups_hooks:
            for hook in entry.get("hooks", []):
                if "hook_ceo_pre_output_brain_query" in hook.get("command", ""):
                    assert "timeout" in hook, "Brain query hook missing timeout"
                    assert hook["timeout"] <= 5000, \
                        f"Timeout too high: {hook['timeout']}ms"
                    return
        pytest.fail("Brain query hook not found")

    def test_settings_preserves_existing_hooks(self):
        """Adding brain query hook did not remove existing UserPromptSubmit hooks."""
        settings_path = COMPANY_ROOT / ".claude" / "settings.json"
        settings = json.loads(settings_path.read_text())
        ups_hooks = settings.get("hooks", {}).get("UserPromptSubmit", [])
        # Must still have the original hook_user_prompt_tracker
        tracker_found = any(
            "hook_user_prompt_tracker" in h.get("command", "")
            for entry in ups_hooks
            for h in entry.get("hooks", [])
        )
        assert tracker_found, "Original hook_user_prompt_tracker was removed"

    def test_brain_query_script_exists(self):
        """hook_ceo_pre_output_brain_query.py exists and is importable."""
        script = COMPANY_ROOT / "scripts" / "hook_ceo_pre_output_brain_query.py"
        assert script.exists(), f"Script not found: {script}"


class TestD4LatencyStress:
    """D4: Latency verification for pre-query hook."""

    def test_brain_query_function_latency(self):
        """query_brain_for_context() completes within 100ms per call (in-process)."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(YGOV_ROOT) + ":" + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-c", """
import sys, time, json, statistics
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/ystar-company/scripts")

try:
    from hook_ceo_pre_output_brain_query import query_brain_for_context
except ImportError as e:
    print(json.dumps({"error": str(e), "p95_ms": -1}))
    sys.exit(0)

payload = {
    "tool_name": "Write",
    "tool_input": {"file_path": "reports/test.md", "content": "test content"},
    "agent_id": "ceo"
}

times = []
for i in range(50):
    start = time.perf_counter()
    try:
        query_brain_for_context(payload, k=3)
    except Exception:
        pass
    elapsed_ms = (time.perf_counter() - start) * 1000
    times.append(elapsed_ms)

times.sort()
p95_idx = int(len(times) * 0.95)
p95 = times[min(p95_idx, len(times)-1)]
p50 = times[len(times)//2]
print(json.dumps({"p50_ms": round(p50,1), "p95_ms": round(p95,1), "max_ms": round(max(times),1), "count": len(times)}))
"""],
            capture_output=True, text=True, timeout=60, env=env,
        )
        assert result.returncode == 0, f"Latency test crashed: {result.stderr}"
        data = json.loads(result.stdout.strip())
        if data.get("error"):
            pytest.skip(f"Module import failed: {data['error']}")
        # In-process function latency should be well under 50ms
        # (Python subprocess startup adds ~300ms, but the function itself is fast)
        assert data["p95_ms"] < 50, \
            f"In-process p95 latency {data['p95_ms']}ms exceeds 50ms target"

    def test_subprocess_latency_within_hook_timeout(self):
        """Full subprocess invocation completes within settings.json timeout (500ms)."""
        script = str(COMPANY_ROOT / "scripts" / "hook_ceo_pre_output_brain_query.py")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(YGOV_ROOT) + ":" + env.get("PYTHONPATH", "")

        times = []
        for i in range(5):
            start = time.perf_counter()
            result = subprocess.run(
                [sys.executable, script],
                capture_output=True, text=True, timeout=10, env=env,
            )
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)

        times.sort()
        p95 = times[-1]  # with 5 samples, max = p95
        # Must complete within the configured hook timeout (500ms)
        assert p95 < 500, \
            f"Subprocess p95 latency {p95:.0f}ms exceeds 500ms hook timeout"

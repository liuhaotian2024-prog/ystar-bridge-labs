#!/usr/bin/env python3
"""
Campaign v4 R2 — Canonical Hash Guard Drift Cycle Stress Test

Test matrix:
1. 4 clean files: governance/WORKING_STYLE.md:783-884, :889-947, AGENTS.md:408-423, forget_guard_rules.yaml
2. Each file: baseline → pollute → detect → restore → verify
3. Boundary cases: incomplete restore, meta-check
"""

import subprocess
import hashlib
import sqlite3
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
CIEU_DB = WORKSPACE / ".ystar_cieu.db"

# Files to test (excluding already-drifted czl_boot_inject.py)
TEST_FILES = [
    "governance/WORKING_STYLE.md:783-884",
    "governance/WORKING_STYLE.md:889-947",
    "AGENTS.md:408-423",
    "governance/forget_guard_rules.yaml",
]

def run_wire_check():
    """Run wire_integrity_check.py and capture stderr"""
    result = subprocess.run(
        ["python3", "scripts/wire_integrity_check.py"],
        capture_output=True,
        text=True,
        cwd=WORKSPACE
    )
    return result.stderr

def query_cieu_drift_events():
    """Query CIEU DB for recent CANONICAL_HASH_DRIFT events"""
    try:
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_id, created_at, event_type, task_description
            FROM cieu_events
            WHERE event_type = 'CANONICAL_HASH_DRIFT'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        return f"ERROR: {e}"

def pollute_file(file_spec):
    """Append single space to file (minimal change)"""
    if ":" in file_spec and "-" in file_spec.split(":")[-1]:
        # Line range spec — pollute WITHIN the range
        file_path = WORKSPACE / file_spec.split(":")[0]
        range_spec = file_spec.split(":")[-1]
        start, end = map(int, range_spec.split("-"))

        original_content = file_path.read_text()
        lines = original_content.split('\n')

        # Pollute last line of the range by appending space
        if end <= len(lines):
            lines[end - 1] = lines[end - 1] + " "  # Append space to line `end`

        polluted_content = '\n'.join(lines)
        file_path.write_text(polluted_content)
        return original_content
    else:
        # Full file — pollute EOF
        file_path = WORKSPACE / file_spec
        original_content = file_path.read_text()
        file_path.write_text(original_content + " ")
        return original_content

def restore_file(file_spec, original_content):
    """Restore file to original content"""
    if ":" in file_spec and "-" in file_spec.split(":")[-1]:
        file_path = WORKSPACE / file_spec.split(":")[0]
    else:
        file_path = WORKSPACE / file_spec

    file_path.write_text(original_content)

def incomplete_restore_file(file_spec, original_content):
    """Restore file but missing 1 byte (boundary case)"""
    if ":" in file_spec and "-" in file_spec.split(":")[-1]:
        # Line range spec — restore but corrupt one line in range
        file_path = WORKSPACE / file_spec.split(":")[0]
        range_spec = file_spec.split(":")[-1]
        start, end = map(int, range_spec.split("-"))

        lines = original_content.split('\n')
        # Corrupt last line of range by removing 1 char
        if end <= len(lines) and len(lines[end - 1]) > 0:
            lines[end - 1] = lines[end - 1][:-1]

        file_path.write_text('\n'.join(lines))
    else:
        # Full file — restore but remove last byte
        file_path = WORKSPACE / file_spec
        file_path.write_text(original_content[:-1])

def test_drift_cycle(file_spec, test_num):
    """Test full drift cycle for one file"""
    print(f"\n{'='*80}")
    print(f"TEST {test_num}: {file_spec}")
    print(f"{'='*80}")

    results = {}

    # 1. Baseline
    print("\n[1/5] BASELINE CHECK...")
    baseline_output = run_wire_check()
    results["baseline_has_drift"] = file_spec in baseline_output
    print(f"  Drift in baseline: {results['baseline_has_drift']}")

    # 2. Pollute
    print("\n[2/5] POLLUTE (append 1 space)...")
    original_content = pollute_file(file_spec)
    print(f"  File polluted: +1 byte")

    # 3. Detect
    print("\n[3/5] DETECT DRIFT...")
    polluted_output = run_wire_check()
    results["polluted_has_drift"] = "CANONICAL_HASH_DRIFT" in polluted_output and file_spec.split(":")[0] in polluted_output
    print(f"  Drift detected: {results['polluted_has_drift']}")
    if results["polluted_has_drift"]:
        # Extract drift details from output
        for line in polluted_output.split('\n'):
            if file_spec.split(":")[0] in line:
                print(f"  Details: {line.strip()}")

    # 4. Restore
    print("\n[4/5] RESTORE (git checkout equivalent)...")
    restore_file(file_spec, original_content)
    print(f"  File restored")

    # 5. Verify clean
    print("\n[5/5] VERIFY CLEAN...")
    restored_output = run_wire_check()
    results["restored_is_clean"] = file_spec not in restored_output or "CANONICAL_HASH_DRIFT" not in restored_output
    print(f"  Clean after restore: {results['restored_is_clean']}")

    # Pass criteria
    passed = (
        not results["baseline_has_drift"] and
        results["polluted_has_drift"] and
        results["restored_is_clean"]
    )

    results["passed"] = passed
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'}")

    return results

def test_boundary_incomplete_restore():
    """Boundary case: incomplete restore should still show drift"""
    print(f"\n{'='*80}")
    print(f"BOUNDARY TEST 1: Incomplete Restore")
    print(f"{'='*80}")

    file_spec = "governance/forget_guard_rules.yaml"

    # Pollute
    print("\n[1/3] POLLUTE...")
    original_content = pollute_file(file_spec)

    # Incomplete restore (missing 1 byte)
    print("\n[2/3] INCOMPLETE RESTORE (missing last byte)...")
    incomplete_restore_file(file_spec, original_content)

    # Detect — should still drift
    print("\n[3/3] DETECT (should still drift)...")
    output = run_wire_check()
    still_drifts = "CANONICAL_HASH_DRIFT" in output

    # Clean up
    restore_file(file_spec, original_content)

    passed = still_drifts
    print(f"\n{'✅ PASS' if passed else '❌ FAIL'} — Incomplete restore detected: {still_drifts}")

    return {"passed": passed, "detected_incomplete_restore": still_drifts}

def test_boundary_meta_check():
    """Boundary case: can canonical_hashes.json itself be checked?"""
    print(f"\n{'='*80}")
    print(f"BOUNDARY TEST 2: Meta-Check (canonical_hashes.json)")
    print(f"{'='*80}")

    canonical_file = WORKSPACE / "governance/canonical_hashes.json"
    original_content = canonical_file.read_text()

    # Pollute canonical_hashes.json itself
    print("\n[1/2] POLLUTE canonical_hashes.json...")
    canonical_file.write_text(original_content + " ")

    # Detect
    print("\n[2/2] DETECT (meta-check support?)...")
    output = run_wire_check()
    meta_detected = "canonical_hashes.json" in output

    # Restore
    canonical_file.write_text(original_content)

    print(f"\n{'✅ META-CHECK SUPPORTED' if meta_detected else '⚠️  META-CHECK NOT IMPLEMENTED'}")
    print(f"  (This is acceptable — canonical_hashes.json is protected by git)")

    return {"meta_check_supported": meta_detected}

def main():
    print("="*80)
    print("Campaign v4 R2 — Canonical Hash Guard Stress Test")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*80)

    # Test drift cycles for 4 clean files
    drift_results = []
    for i, file_spec in enumerate(TEST_FILES, 1):
        result = test_drift_cycle(file_spec, i)
        drift_results.append({"file": file_spec, **result})

    # Boundary tests
    boundary_results = []
    boundary_results.append({
        "test": "incomplete_restore",
        **test_boundary_incomplete_restore()
    })
    boundary_results.append({
        "test": "meta_check",
        **test_boundary_meta_check()
    })

    # Query CIEU events
    print(f"\n{'='*80}")
    print("CIEU EVENT QUERY")
    print(f"{'='*80}")
    events = query_cieu_drift_events()
    if isinstance(events, str):
        print(f"Error: {events}")
    else:
        print(f"\nRecent CANONICAL_HASH_DRIFT events (last 10):")
        for event_id, created_at, event_type, task_desc in events:
            dt = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
            print(f"  [{dt}] {event_type}")
            try:
                details = json.loads(task_desc)
                print(f"    Issues: {details.get('total_issues', 'N/A')}")
            except:
                pass

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")

    drift_pass_count = sum(1 for r in drift_results if r["passed"])
    print(f"\nDrift Cycle Tests: {drift_pass_count}/{len(drift_results)} PASS")
    for r in drift_results:
        status = "✅" if r["passed"] else "❌"
        print(f"  {status} {r['file']}")

    boundary_pass_count = sum(1 for r in boundary_results if r.get("passed", r.get("meta_check_supported", False)))
    print(f"\nBoundary Tests: {len(boundary_results)} completed")
    for r in boundary_results:
        print(f"  • {r['test']}: {r}")

    # Overall
    total_tests = len(drift_results) + len(boundary_results)
    total_pass = drift_pass_count + boundary_pass_count
    overall_pass_rate = total_pass / total_tests if total_tests > 0 else 0

    print(f"\n{'='*80}")
    print(f"OVERALL: {drift_pass_count}/{len(drift_results)} drift cycles + {len(boundary_results)} boundary tests")
    print(f"Drift detection rate: {drift_pass_count}/{len(drift_results)} ({100*drift_pass_count/len(drift_results):.0f}%)")
    print(f"{'='*80}")

    return drift_results, boundary_results, events

if __name__ == "__main__":
    main()

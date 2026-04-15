#!/usr/bin/env python3
"""
[L2→L3] Wire Integrity Check — Verify governance wiring is complete

Scans for:
1. Hook scripts in scripts/hook_*.py vs settings.json registration
2. Cron scripts (@cron docstring) vs crontab -l
3. Whitelist YAML files vs forget_guard_rules.yaml references

Always exits 0 (fail-open), emits WIRE_BROKEN CIEU on mismatches
"""

import sys
import json
import subprocess
import time
import uuid
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
SETTINGS_JSON = WORKSPACE_ROOT / ".claude/settings.json"
WHITELIST_DIR = WORKSPACE_ROOT / "governance/whitelist"
FORGET_GUARD_RULES = WORKSPACE_ROOT / "governance/forget_guard_rules.yaml"
CIEU_DB = WORKSPACE_ROOT / ".ystar_cieu.db"


def emit_cieu(event_type, details):
    """Emit CIEU event to audit log using proper CIEU schema"""
    try:
        import sqlite3
        import time
        import uuid

        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()

        # Use proper CIEU schema (cieu_events table)
        cursor.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, task_description
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),                      # event_id
            int(time.time() * 1_000_000),           # seq_global (microseconds)
            time.time(),                            # created_at (Unix timestamp)
            "wire_integrity_cron",                  # session_id
            "platform",                             # agent_id
            event_type,                             # event_type
            "escalate",                             # decision
            0,                                      # passed (0=failed)
            details                                 # task_description (JSON string)
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        # Fail-open but log to stderr for debugging
        print(f"[CIEU EMIT FAILED] {e}", file=sys.stderr)
        pass


def check_hook_wiring():
    """Check hook scripts vs settings.json registration"""
    broken = []

    # Find all hook_*.py scripts
    hook_scripts = list(WORKSPACE_ROOT.glob("scripts/hook_*.py"))
    hook_script_basenames = {s.name for s in hook_scripts}

    # Load settings.json hooks
    try:
        with open(SETTINGS_JSON) as f:
            settings = json.load(f)
            registered_hooks = settings.get("hooks", {})
    except Exception as e:
        return [f"Cannot read settings.json: {e}"]

    # Extract all registered hook script basenames from settings.json
    registered_basenames = set()
    for event_name, event_hooks in registered_hooks.items():
        for hook_entry in event_hooks:
            for hook_def in hook_entry.get("hooks", []):
                command = hook_def.get("command", "")
                # Extract basename from command (handles both absolute paths and script names)
                parts = command.split()
                for part in parts:
                    if part.endswith(".py") or part.endswith(".sh"):
                        # Get basename (last path component)
                        basename = Path(part).name
                        registered_basenames.add(basename)

    # Check each hook script is registered
    for script_basename in hook_script_basenames:
        if script_basename not in registered_basenames:
            broken.append(f"Hook script {script_basename} not registered in settings.json")

    return broken


def check_cron_wiring():
    """Check @cron docstring scripts vs crontab -l"""
    broken = []

    # Find all scripts with @cron marker
    cron_scripts = []
    for script in WORKSPACE_ROOT.glob("scripts/*.py"):
        try:
            content = script.read_text()
            if "@cron" in content or "cron_" in script.stem:
                cron_scripts.append(script)
        except Exception:
            pass

    # Get current crontab
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True,
            text=True,
            timeout=5
        )
        crontab_content = result.stdout if result.returncode == 0 else ""
    except Exception:
        crontab_content = ""

    # Check each cron script is in crontab
    for script in cron_scripts:
        if str(script) not in crontab_content and script.name not in crontab_content:
            broken.append(f"Cron script {script.name} not in crontab")

    return broken


def check_whitelist_wiring():
    """Check whitelist YAML files vs forget_guard_rules.yaml references"""
    broken = []

    # Find all whitelist/*.yaml files
    if not WHITELIST_DIR.exists():
        return broken

    whitelist_files = list(WHITELIST_DIR.glob("*.yaml"))

    # Load forget_guard_rules.yaml
    try:
        forget_guard_content = FORGET_GUARD_RULES.read_text()
    except Exception:
        return [f"Cannot read {FORGET_GUARD_RULES}"]

    # Check each whitelist file is referenced
    for wl_file in whitelist_files:
        if wl_file.stem not in forget_guard_content:
            broken.append(f"Whitelist {wl_file.name} not referenced in forget_guard_rules.yaml")

    return broken


def check_canonical_hashes():
    """
    Check canonical file hashes against genesis tag expectations.

    W6 Phase 2: Detects drift in immutable CZL files.
    Prevents "Article 11 slogan-ization" and other canonical drift.
    """
    import hashlib

    broken = []

    canonical_hashes_file = WORKSPACE_ROOT / "governance/canonical_hashes.json"
    if not canonical_hashes_file.exists():
        return [f"Missing {canonical_hashes_file} — cannot verify canonical files"]

    try:
        with open(canonical_hashes_file) as f:
            canonical_data = json.load(f)
        # W6.1: Schema v1.1 splits static_frozen vs live_tracked
        schema_version = canonical_data.get("schema_version", "1.0")
        if schema_version == "1.1":
            static_frozen = canonical_data.get("static_frozen", {})
            live_tracked = canonical_data.get("live_tracked", {})
        else:
            # Legacy v1.0: treat all as static (backward compat)
            static_frozen = canonical_data
            live_tracked = {}
    except Exception as e:
        return [f"Cannot read canonical_hashes.json: {e}"]

    def get_file_hash(path, start_line=None, end_line=None):
        """Get SHA256 hash of file or specific line range"""
        try:
            full_path = WORKSPACE_ROOT / path if not Path(path).is_absolute() else Path(path)
            content = full_path.read_text()
            if start_line and end_line:
                lines = content.split('\n')
                content = '\n'.join(lines[start_line-1:end_line])
            return hashlib.sha256(content.encode()).hexdigest()
        except Exception as e:
            return f"ERROR:{e}"

    # W6.1: Check static_frozen (P0 severity) and live_tracked (INFO severity) separately
    def check_files(file_dict, category):
        """Check files and return broken list with category label"""
        broken_in_category = []
        for file_spec, expected_hash in file_dict.items():
            if ":schema_fields" in file_spec:
                # Special case: .czl_subgoals.json schema fields
                czl_file = WORKSPACE_ROOT / ".czl_subgoals.json"
                try:
                    with open(czl_file) as f:
                        czl_data = json.load(f)
                    actual_fields = sorted(czl_data.keys())
                    actual_hash = hashlib.sha256(json.dumps(actual_fields).encode()).hexdigest()
                except Exception as e:
                    broken_in_category.append(f"[{category}] {file_spec}: cannot read file ({e})")
                    continue
            elif ":" in file_spec:
                # Parse file:range or file:tag specification
                parts = file_spec.rsplit(":", 1)
                file_path = parts[0]
                range_or_tag = parts[1]

                if "-" in range_or_tag and range_or_tag.replace("-", "").isdigit():
                    # Line range specification (e.g., "file.md:100-200")
                    start, end = map(int, range_or_tag.split("-"))
                    actual_hash = get_file_hash(file_path, start, end)
                else:
                    # Tag specification (e.g., "AGENTS.md:Memory&Continuity") — treat as full file
                    # The tag is just a label, hash the full file
                    actual_hash = get_file_hash(file_path)
            else:
                # Full file hash
                actual_hash = get_file_hash(file_spec)

            if actual_hash.startswith("ERROR:"):
                broken_in_category.append(f"[{category}] {file_spec}: {actual_hash}")
            elif actual_hash != expected_hash:
                if category == "STATIC":
                    # P0 severity: static frozen files must never drift
                    broken_in_category.append(
                        f"[P0 CANONICAL_HASH_DRIFT] {file_spec}: "
                        f"(expected {expected_hash[:16]}..., got {actual_hash[:16]}...)"
                    )
                    # Emit CIEU event for static drift
                    emit_cieu("CANONICAL_HASH_DRIFT", json.dumps({
                        "file": file_spec,
                        "expected": expected_hash[:16],
                        "actual": actual_hash[:16],
                        "severity": "P0"
                    }))
                else:
                    # INFO severity: live files expected to change
                    broken_in_category.append(
                        f"[INFO LIVE_FILE_CHANGED] {file_spec}: "
                        f"(expected {expected_hash[:16]}..., got {actual_hash[:16]}...)"
                    )
                    # Emit CIEU event for live change
                    emit_cieu("LIVE_FILE_CHANGED", json.dumps({
                        "file": file_spec,
                        "expected": expected_hash[:16],
                        "actual": actual_hash[:16],
                        "severity": "INFO"
                    }))
        return broken_in_category

    # Check both categories
    broken.extend(check_files(static_frozen, "STATIC"))
    broken.extend(check_files(live_tracked, "LIVE"))

    return broken


def main():
    """Run all wire integrity checks"""
    print("=== Wire Integrity Check ===", file=sys.stderr)

    all_broken = []

    hook_broken = check_hook_wiring()
    if hook_broken:
        all_broken.extend(hook_broken)
        print(f"[HOOK WIRING] {len(hook_broken)} issues found", file=sys.stderr)
        for issue in hook_broken:
            print(f"  - {issue}", file=sys.stderr)

    cron_broken = check_cron_wiring()
    if cron_broken:
        all_broken.extend(cron_broken)
        print(f"[CRON WIRING] {len(cron_broken)} issues found", file=sys.stderr)
        for issue in cron_broken:
            print(f"  - {issue}", file=sys.stderr)

    whitelist_broken = check_whitelist_wiring()
    if whitelist_broken:
        all_broken.extend(whitelist_broken)
        print(f"[WHITELIST WIRING] {len(whitelist_broken)} issues found", file=sys.stderr)
        for issue in whitelist_broken:
            print(f"  - {issue}", file=sys.stderr)

    # W6 Phase 2: Canonical hash checks
    canonical_broken = check_canonical_hashes()
    if canonical_broken:
        all_broken.extend(canonical_broken)
        print(f"[CANONICAL HASHES] {len(canonical_broken)} issues found", file=sys.stderr)
        for issue in canonical_broken:
            print(f"  - {issue}", file=sys.stderr)

    if all_broken:
        categories = {
            "hooks": len(hook_broken),
            "cron": len(cron_broken),
            "whitelist": len(whitelist_broken),
            "canonical_hashes": len(canonical_broken) if canonical_broken else 0
        }
        emit_cieu("WIRE_BROKEN", json.dumps({
            "total_issues": len(all_broken),
            "categories": categories,
            "details": all_broken
        }))
        print(f"\n[WIRE_BROKEN] {len(all_broken)} total issues", file=sys.stderr)
    else:
        print("[OK] All wires intact", file=sys.stderr)

    # Always exit 0 (fail-open)
    sys.exit(0)


if __name__ == "__main__":
    main()

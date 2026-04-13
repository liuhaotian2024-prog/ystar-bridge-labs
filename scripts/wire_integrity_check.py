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
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
SETTINGS_JSON = WORKSPACE_ROOT / ".claude/settings.json"
WHITELIST_DIR = WORKSPACE_ROOT / "governance/whitelist"
FORGET_GUARD_RULES = WORKSPACE_ROOT / "governance/forget_guard_rules.yaml"
CIEU_DB = WORKSPACE_ROOT / ".ystar_cieu.db"


def emit_cieu(event_type, details):
    """Emit CIEU event to audit log"""
    try:
        import sqlite3
        conn = sqlite3.connect(CIEU_DB)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cieu_events (timestamp, event_type, details)
            VALUES (?, ?, ?)
        """, (datetime.now().isoformat(), event_type, details))
        conn.commit()
        conn.close()
    except Exception:
        pass  # Fail-open


def check_hook_wiring():
    """Check hook scripts vs settings.json registration"""
    broken = []

    # Find all hook_*.py scripts
    hook_scripts = list(WORKSPACE_ROOT.glob("scripts/hook_*.py"))
    hook_names = {s.stem.replace('hook_', ''): s for s in hook_scripts}

    # Load settings.json hooks
    try:
        with open(SETTINGS_JSON) as f:
            settings = json.load(f)
            registered_hooks = settings.get("hooks", {})
    except Exception as e:
        return [f"Cannot read settings.json: {e}"]

    # Check each hook script is registered
    for hook_name, script_path in hook_names.items():
        # Normalize hook name to event name (e.g., user_prompt_tracker → UserPromptSubmit)
        # This is heuristic; may need manual mapping
        event_candidates = [
            hook_name,
            ''.join(word.capitalize() for word in hook_name.split('_')),
            hook_name.replace('_', '').capitalize()
        ]

        registered = False
        for event_name in registered_hooks.keys():
            if any(cand.lower() in event_name.lower() for cand in event_candidates):
                # Check if script path is in command
                event_hooks = registered_hooks[event_name]
                for hook_entry in event_hooks:
                    for hook_def in hook_entry.get("hooks", []):
                        if str(script_path) in hook_def.get("command", ""):
                            registered = True
                            break

        if not registered:
            broken.append(f"Hook script {script_path.name} not registered in settings.json")

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

    if all_broken:
        emit_cieu("WIRE_BROKEN", json.dumps({
            "total_issues": len(all_broken),
            "categories": {
                "hooks": len(hook_broken),
                "cron": len(cron_broken),
                "whitelist": len(whitelist_broken)
            },
            "details": all_broken
        }))
        print(f"\n[WIRE_BROKEN] {len(all_broken)} total issues", file=sys.stderr)
    else:
        print("[OK] All wires intact", file=sys.stderr)

    # Always exit 0 (fail-open)
    sys.exit(0)


if __name__ == "__main__":
    main()

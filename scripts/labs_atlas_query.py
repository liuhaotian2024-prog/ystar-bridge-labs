#!/usr/bin/env python3
"""
Labs Atlas Query CLI — Query subsystem inventory

Usage:
    python3 scripts/labs_atlas_query.py list
    python3 scripts/labs_atlas_query.py who_calls <module>
    python3 scripts/labs_atlas_query.py dormant
    python3 scripts/labs_atlas_query.py dead
"""

import sys
import re
from pathlib import Path
from typing import List, Dict

YSTAR_COMPANY = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
INDEX_PATH = YSTAR_COMPANY / "SUBSYSTEM_INDEX.md"


def parse_index() -> Dict[str, List[Dict]]:
    """Parse SUBSYSTEM_INDEX.md into structured data."""
    if not INDEX_PATH.exists():
        print(f"❌ Index not found: {INDEX_PATH}")
        print("Run: python3 scripts/labs_atlas_scan.py")
        sys.exit(1)

    with open(INDEX_PATH, 'r') as f:
        content = f.read()

    subsystems = {}
    current_subsystem = None

    for line in content.split('\n'):
        # Detect subsystem header
        if line.startswith("## ") and not line.startswith("## Summary") and not line.startswith("## Dead"):
            current_subsystem = line[3:].strip()
            subsystems[current_subsystem] = []
            continue

        # Parse module line
        if current_subsystem and line.startswith("| `") and not line.startswith("| Module"):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                module = {
                    'name': parts[1].strip('`'),
                    'status': parts[2].strip(),
                    'last_invoked': parts[3].strip(),
                    'callers': int(parts[4].strip()),
                    'api': parts[5].strip()
                }
                subsystems[current_subsystem].append(module)

    return subsystems


def cmd_list():
    """List all modules."""
    data = parse_index()

    print("\n=== Labs Atlas — Full Inventory ===\n")
    for subsystem, modules in data.items():
        print(f"## {subsystem} ({len(modules)} modules)")
        for mod in modules:
            print(f"  {mod['status'][:2]} {mod['name']} — {mod['api']}, {mod['callers']} callers, last: {mod['last_invoked']}")
        print()


def cmd_who_calls(module_name: str):
    """Find who calls a module."""
    # This is a simplified version - full implementation would need to
    # parse the caller graph from the scanner directly
    data = parse_index()

    print(f"\n=== Who Calls: {module_name} ===\n")

    found = False
    for subsystem, modules in data.items():
        for mod in modules:
            if module_name in mod['name']:
                print(f"Module: {mod['name']}")
                print(f"Subsystem: {subsystem}")
                print(f"Callers: {mod['callers']}")
                print(f"Status: {mod['status']}")
                found = True

    if not found:
        print(f"❌ Module '{module_name}' not found")


def cmd_dormant():
    """List dormant modules (7d+ no invoke)."""
    data = parse_index()

    print("\n=== Dormant Modules (7d+) ===\n")

    count = 0
    for subsystem, modules in data.items():
        dormant = [m for m in modules if 'dormant' in m['status'].lower()]
        if dormant:
            print(f"## {subsystem}")
            for mod in dormant:
                print(f"  ⚠️  {mod['name']} — last: {mod['last_invoked']}, {mod['callers']} callers")
            print()
            count += len(dormant)

    print(f"Total dormant: {count}")


def cmd_dead():
    """List dead modules (30d+ no invoke, no callers)."""
    data = parse_index()

    print("\n=== Dead Modules (30d+, no callers) ===\n")

    count = 0
    for subsystem, modules in data.items():
        dead = [m for m in modules if 'dead' in m['status'].lower()]
        if dead:
            print(f"## {subsystem}")
            for mod in dead:
                print(f"  💀 {mod['name']} — last: {mod['last_invoked']}")
            print()
            count += len(dead)

    print(f"Total dead: {count}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        cmd_list()
    elif command == "who_calls":
        if len(sys.argv) < 3:
            print("Usage: labs_atlas_query.py who_calls <module>")
            sys.exit(1)
        cmd_who_calls(sys.argv[2])
    elif command == "dormant":
        cmd_dormant()
    elif command == "dead":
        cmd_dead()
    else:
        print(f"❌ Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

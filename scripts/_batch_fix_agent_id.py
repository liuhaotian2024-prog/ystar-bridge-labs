#!/usr/bin/env python3
"""
W23 Batch Fix: Inject _get_current_agent() into all CIEU emit scripts.
Replaces hardcoded agent_id with fresh read from .ystar_active_agent.
"""
import re
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
TARGET_FILES = [
    "article_11_tracker.py",
    "forget_guard.py",
    "forget_guard_summary.py",
    "hook_user_prompt_tracker.py",
    "idle_pulse.py",
    "precheck_review.py",
    "priority_brief_validator.py",
    "session_close_yml.py",
    "session_health_watchdog.py",
    "twin_evolution.py",
]

def inject_import(content: str) -> str:
    """Inject import _get_current_agent if not present."""
    if "_get_current_agent" in content:
        return content

    # Find first import block
    lines = content.split("\n")
    last_import_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            last_import_idx = i

    if last_import_idx == -1:
        # No imports, inject after shebang/docstring
        insert_idx = 0
        if lines[0].startswith("#!"):
            insert_idx = 1
        if lines[insert_idx].startswith('"""') or lines[insert_idx].startswith("'''"):
            # Find end of docstring
            for j in range(insert_idx + 1, len(lines)):
                if lines[j].strip().endswith('"""') or lines[j].strip().endswith("'''"):
                    insert_idx = j + 1
                    break
        lines.insert(insert_idx, "\nsys.path.insert(0, str(Path(__file__).parent))")
        lines.insert(insert_idx + 1, "from _cieu_helpers import _get_current_agent\n")
    else:
        lines.insert(last_import_idx + 1, "sys.path.insert(0, str(Path(__file__).parent))")
        lines.insert(last_import_idx + 2, "from _cieu_helpers import _get_current_agent")

    return "\n".join(lines)

def fix_agent_id_in_inserts(content: str) -> str:
    """Replace hardcoded agent_id values with _get_current_agent() calls."""

    # Pattern 1: agent_id in VALUES tuple with string literal
    # Example: VALUES (?, ?, "ceo", ?, ...) → VALUES (?, ?, _get_current_agent(), ?, ...)
    content = re.sub(
        r'VALUES\s*\([^)]*?["\'](?:ceo|unknown|agent|hook_pipeline|system)["\'][^)]*?\)',
        lambda m: m.group(0).replace('"ceo"', '_get_current_agent()').replace("'ceo'", '_get_current_agent()')
                           .replace('"unknown"', '_get_current_agent()').replace("'unknown'", '_get_current_agent()')
                           .replace('"agent"', '_get_current_agent()').replace("'agent'", '_get_current_agent()')
                           .replace('"hook_pipeline"', '_get_current_agent()').replace("'hook_pipeline'", '_get_current_agent()')
                           .replace('"system"', '_get_current_agent()').replace("'system'", '_get_current_agent()'),
        content
    )

    # Pattern 2: agent_id=variable assignment in dict/tuple construction
    # Example: agent_id="ceo" → agent_id=_get_current_agent()
    content = re.sub(
        r'agent_id\s*=\s*["\'](?:ceo|unknown|agent|hook_pipeline|system)["\']',
        'agent_id=_get_current_agent()',
        content
    )

    # Pattern 3: Tuple/list with positional agent_id
    # Example: (timestamp, "ceo", event_type, ...) → (timestamp, _get_current_agent(), event_type, ...)
    # This is harder, manual inspection preferred, but try common patterns

    return content

def process_file(file_path: Path) -> tuple[bool, str]:
    """Process a single file. Returns (changed, message)."""
    try:
        content = file_path.read_text()
        original = content

        # Step 1: Inject import
        content = inject_import(content)

        # Step 2: Fix agent_id
        content = fix_agent_id_in_inserts(content)

        if content == original:
            return False, "no changes needed"

        file_path.write_text(content)
        return True, "✓ fixed"
    except Exception as e:
        return False, f"error: {e}"

def main():
    print("W23 Batch Fix: Injecting _get_current_agent() into CIEU emit scripts\n")

    results = []
    for filename in TARGET_FILES:
        file_path = SCRIPTS_DIR / filename
        if not file_path.exists():
            results.append((filename, False, "not found"))
            continue

        changed, msg = process_file(file_path)
        results.append((filename, changed, msg))

    print("Results:")
    for filename, changed, msg in results:
        status = "✓" if changed else "·"
        print(f"  {status} {filename}: {msg}")

    total_changed = sum(1 for _, changed, _ in results if changed)
    print(f"\n{total_changed}/{len(TARGET_FILES)} files modified")

if __name__ == "__main__":
    main()

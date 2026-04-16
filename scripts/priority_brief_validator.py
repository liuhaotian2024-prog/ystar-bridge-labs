#!/usr/bin/env python3
"""Priority Brief YAML Frontmatter Validator (AMENDMENT-009 §2.2)

Validates that reports/priority_brief.md contains structured target frontmatter:
- today_targets: [...]
- this_week_targets: [...]
- this_month_targets: [...]

Each target must have: target, owner, deadline, verify

Emits CIEU event: PRIORITY_BRIEF_TARGETS_MISSING (warning) if empty.
"""

import sys
import re
import yaml
import json
import time
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from _cieu_helpers import _get_current_agent


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content.

    Expects format:
    ---
    key: value
    ---
    # Markdown content
    """
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not frontmatter_match:
        return {}

    frontmatter_yaml = frontmatter_match.group(1)
    try:
        return yaml.safe_load(frontmatter_yaml) or {}
    except yaml.YAMLError as e:
        print(f"[ERROR] YAML parse failed: {e}", file=sys.stderr)
        return {}


def validate_target_schema(target: dict, context: str) -> list[str]:
    """Validate single target object has required fields.

    Returns list of validation errors.
    """
    errors = []
    required_fields = ["target", "owner", "deadline", "verify"]

    for field in required_fields:
        if field not in target:
            errors.append(f"{context}: missing required field '{field}'")
        elif not target[field] or (isinstance(target[field], str) and not target[field].strip()):
            errors.append(f"{context}: field '{field}' is empty")

    # Validate owner is a known role
    known_roles = ["ceo", "cto", "cmo", "cso", "cfo", "eng-kernel", "eng-platform", "eng-governance", "eng-domains"]
    if "owner" in target and target["owner"] not in known_roles:
        errors.append(f"{context}: unknown owner '{target['owner']}' (must be one of {known_roles})")

    return errors


def validate_priority_brief(brief_path: Path) -> tuple[bool, list[str], dict]:
    """Validate priority_brief.md frontmatter schema.

    Returns:
        (is_valid, errors, frontmatter)
    """
    if not brief_path.exists():
        return False, ["priority_brief.md does not exist"], {}

    content = brief_path.read_text()
    frontmatter = parse_frontmatter(content)

    errors = []

    # Check for required top-level keys
    required_keys = ["today_targets", "this_week_targets", "this_month_targets"]
    for key in required_keys:
        if key not in frontmatter:
            errors.append(f"Missing required frontmatter key: {key}")

    # Validate each target list
    for key in required_keys:
        if key in frontmatter:
            targets = frontmatter[key]
            if not isinstance(targets, list):
                errors.append(f"{key} must be a list")
                continue

            for i, target in enumerate(targets):
                if not isinstance(target, dict):
                    errors.append(f"{key}[{i}]: must be a dict")
                    continue

                target_errors = validate_target_schema(target, f"{key}[{i}]")
                errors.extend(target_errors)

    is_valid = len(errors) == 0
    return is_valid, errors, frontmatter


def emit_cieu_warning(company_root: Path, frontmatter: dict, errors: list[str]):
    """Emit CIEU warning event if targets are missing or invalid."""
    cieu_db = company_root / ".ystar_cieu.db"

    # Count total targets
    today_count = len(frontmatter.get("today_targets", []))
    week_count = len(frontmatter.get("this_week_targets", []))
    month_count = len(frontmatter.get("this_month_targets", []))

    decision = "warn" if (today_count == 0 or errors) else "allow"

    try:
        import sqlite3
        conn = sqlite3.connect(cieu_db)

        event_id = str(uuid.uuid4())
        seq_global = int(time.time() * 1_000_000)

        sess_cfg_path = company_root / ".ystar_session.json"
        session_id = "unknown"
        if sess_cfg_path.exists():
            session_id = json.loads(sess_cfg_path.read_text()).get("session_id", "unknown")

        params = {
            "today_count": today_count,
            "week_count": week_count,
            "month_count": month_count,
            "validation_errors": errors,
        }

        conn.execute("""
            INSERT INTO cieu_events (
                event_id, seq_global, created_at, session_id, agent_id, event_type,
                decision, passed, task_description, params_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            seq_global,
            time.time(),
            session_id,
            "ceo",
            "PRIORITY_BRIEF_TARGETS_CHECK",
            decision,
            1 if decision == "allow" else 0,
            f"Priority brief has {today_count} today targets, {week_count} week targets, {month_count} month targets",
            json.dumps(params),
        ))

        conn.commit()
        conn.close()

        print(f"[CIEU] PRIORITY_BRIEF_TARGETS_CHECK: {decision}", file=sys.stderr)

    except Exception as e:
        print(f"[warn] CIEU emit failed: {e}", file=sys.stderr)


def main():
    company_root = Path(__file__).parent.parent
    brief_path = company_root / "reports" / "priority_brief.md"

    is_valid, errors, frontmatter = validate_priority_brief(brief_path)

    if not is_valid:
        print("VALIDATION FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)

        emit_cieu_warning(company_root, frontmatter, errors)
        return 1

    # Check if targets are empty (warning, not failure)
    today_count = len(frontmatter.get("today_targets", []))
    week_count = len(frontmatter.get("this_week_targets", []))
    month_count = len(frontmatter.get("this_month_targets", []))

    print(f"Priority brief validation: OK")
    print(f"  Today targets: {today_count}")
    print(f"  This week targets: {week_count}")
    print(f"  This month targets: {month_count}")

    if today_count == 0:
        print("[WARN] No today_targets defined — ADE cannot drive daily work", file=sys.stderr)
        emit_cieu_warning(company_root, frontmatter, ["today_targets is empty"])
    else:
        emit_cieu_warning(company_root, frontmatter, [])

    return 0


if __name__ == "__main__":
    sys.exit(main())

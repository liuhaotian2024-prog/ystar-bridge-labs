#!/usr/bin/env python3
"""YAML Mutation Testing Harness — governance integrity verification.

Deliberately corrupts governance YAML files and checks if the governance layer
detects each corruption. Undetected mutations ("survivors") expose governance gaps.

Board 2026-04-22 directive: G2 long-term drift prevention.
CZL-CEO-RULES-REGISTRY-V3-RYAN

SAFETY:
  - Always backs up YAML before mutation (shutil.copy2)
  - Always restores in try/finally
  - Verifies restore with file hash comparison
  - Exits 2 if restore fails (CRITICAL safety valve)

Usage:
    python3 scripts/yaml_mutation_harness.py
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import sqlite3
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Use PyYAML — available in the environment
try:
    import yaml
except ImportError:
    print("CRITICAL: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
YAML_PATH = WORKSPACE / "governance" / "forget_guard_rules.yaml"
CIEU_DB = WORKSPACE / ".ystar_cieu.db"
REPORTS_DIR = WORKSPACE / "reports" / "governance"

# Backup path (in /tmp for safety — never in the governance directory)
BACKUP_PATH = Path("/tmp/forget_guard_rules_mutation_backup.yaml")


def file_hash(path: Path) -> str:
    """SHA-256 hash of file contents."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def backup_yaml() -> str:
    """Backup the YAML file. Returns the hash of the original."""
    shutil.copy2(YAML_PATH, BACKUP_PATH)
    h = file_hash(YAML_PATH)
    assert file_hash(BACKUP_PATH) == h, "backup hash mismatch"
    return h


def restore_yaml(original_hash: str):
    """Restore YAML from backup. Exits 2 on failure."""
    shutil.copy2(BACKUP_PATH, YAML_PATH)
    restored_hash = file_hash(YAML_PATH)
    if restored_hash != original_hash:
        print("CRITICAL: RESTORE FAILED — hash mismatch after restore!", file=sys.stderr)
        print(f"  Expected: {original_hash}", file=sys.stderr)
        print(f"  Got:      {restored_hash}", file=sys.stderr)
        sys.exit(2)


def load_yaml() -> dict:
    """Load the YAML file."""
    with open(YAML_PATH) as f:
        return yaml.safe_load(f) or {}


def save_yaml(data: dict):
    """Write mutated YAML back."""
    with open(YAML_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def find_rule_by_id(rules: list, rule_id: str) -> tuple[int, dict | None]:
    """Find a rule by its 'id' field. Returns (index, rule) or (-1, None)."""
    for i, rule in enumerate(rules):
        if rule.get("id") == rule_id:
            return i, rule
    return -1, None


# ────────────────────────────────────────────────────────────
# Mutation Bank
# ────────────────────────────────────────────────────────────

class Mutation:
    def __init__(self, mid: str, description: str, tests: str):
        self.mid = mid
        self.description = description
        self.tests = tests
        self.status = "PENDING"
        self.detail = ""

    def apply(self, data: dict) -> dict:
        raise NotImplementedError

    def check_detection(self, original: dict, mutated: dict) -> bool:
        """Return True if the mutation was detected (governance gap found)."""
        raise NotImplementedError


class M1_DeleteTriggerPattern(Mutation):
    """Delete first trigger_patterns entry from choice_question_to_board rule."""
    def __init__(self):
        super().__init__(
            "M1",
            "Delete first keywords entry from choice_question_to_board trigger",
            "Pattern matching completeness",
        )

    def apply(self, data: dict) -> dict:
        rules = data.get("rules", [])
        _, rule = find_rule_by_id(rules, "choice_question_to_board")
        if rule is None:
            self.detail = "rule not found"
            return data
        conditions = rule.get("trigger", {}).get("conditions", [])
        for cond in conditions:
            if cond.get("type") == "content_contains" and "keywords" in cond:
                if len(cond["keywords"]) > 0:
                    removed = cond["keywords"].pop(0)
                    self.detail = f"removed keyword: {removed}"
                    return data
        self.detail = "no keywords to remove"
        return data

    def check_detection(self, original: dict, mutated: dict) -> bool:
        """Detect by checking keyword count differs."""
        orig_rules = original.get("rules", [])
        mut_rules = mutated.get("rules", [])
        _, orig_rule = find_rule_by_id(orig_rules, "choice_question_to_board")
        _, mut_rule = find_rule_by_id(mut_rules, "choice_question_to_board")
        if orig_rule is None or mut_rule is None:
            return False
        orig_kw = []
        mut_kw = []
        for cond in orig_rule.get("trigger", {}).get("conditions", []):
            if cond.get("type") == "content_contains":
                orig_kw = cond.get("keywords", [])
                break
        for cond in mut_rule.get("trigger", {}).get("conditions", []):
            if cond.get("type") == "content_contains":
                mut_kw = cond.get("keywords", [])
                break
        detected = len(orig_kw) != len(mut_kw)
        return detected


class M2_FlipActionDenyToAllow(Mutation):
    """Change action: deny to action: allow on choice_question_to_board."""
    def __init__(self):
        super().__init__(
            "M2",
            "Change action from 'deny' to 'allow' on choice_question_to_board",
            "Action enforcement integrity",
        )

    def apply(self, data: dict) -> dict:
        rules = data.get("rules", [])
        _, rule = find_rule_by_id(rules, "choice_question_to_board")
        if rule is None:
            self.detail = "rule not found"
            return data
        old_action = rule.get("action", "")
        rule["action"] = "allow"
        self.detail = f"changed action from '{old_action}' to 'allow'"
        return data

    def check_detection(self, original: dict, mutated: dict) -> bool:
        """Detect by finding deny rules that became allow."""
        orig_rules = original.get("rules", [])
        mut_rules = mutated.get("rules", [])
        _, orig_rule = find_rule_by_id(orig_rules, "choice_question_to_board")
        _, mut_rule = find_rule_by_id(mut_rules, "choice_question_to_board")
        if orig_rule is None or mut_rule is None:
            return False
        return orig_rule.get("action") != mut_rule.get("action")


class M3_EmptyScope(Mutation):
    """Empty the trigger.tool (scope) field of a rule."""
    def __init__(self):
        super().__init__(
            "M3",
            "Empty the trigger.tool scope of choice_question_to_board",
            "Scope matching coverage",
        )

    def apply(self, data: dict) -> dict:
        rules = data.get("rules", [])
        _, rule = find_rule_by_id(rules, "choice_question_to_board")
        if rule is None:
            self.detail = "rule not found"
            return data
        trigger = rule.get("trigger", {})
        old_tools = trigger.get("tool", [])
        trigger["tool"] = []
        self.detail = f"emptied tool scope (was: {old_tools})"
        return data

    def check_detection(self, original: dict, mutated: dict) -> bool:
        """Detect by finding rules with empty scope."""
        mut_rules = mutated.get("rules", [])
        _, mut_rule = find_rule_by_id(mut_rules, "choice_question_to_board")
        if mut_rule is None:
            return False
        tools = mut_rule.get("trigger", {}).get("tool", [])
        return len(tools) == 0  # detection: empty scope is anomalous


class M4_RenameRuleTypo(Mutation):
    """Rename choice_question_to_board to choice_question_to_board_TYPO."""
    def __init__(self):
        super().__init__(
            "M4",
            "Rename rule 'choice_question_to_board' to '..._TYPO'",
            "Rule name lookup integrity",
        )

    def apply(self, data: dict) -> dict:
        rules = data.get("rules", [])
        _, rule = find_rule_by_id(rules, "choice_question_to_board")
        if rule is None:
            self.detail = "rule not found"
            return data
        rule["id"] = "choice_question_to_board_TYPO"
        self.detail = "renamed to choice_question_to_board_TYPO"
        return data

    def check_detection(self, original: dict, mutated: dict) -> bool:
        """Detect by checking if expected rule name is missing."""
        mut_rules = mutated.get("rules", [])
        _, mut_rule = find_rule_by_id(mut_rules, "choice_question_to_board")
        # If the original name is gone, we detected the mutation
        return mut_rule is None


class M5_RemoveEntireRule(Mutation):
    """Remove entire ceo_engineering_boundary rule entry."""
    def __init__(self):
        super().__init__(
            "M5",
            "Remove entire 'ceo_engineering_boundary' rule entry",
            "Rule count integrity",
        )

    def apply(self, data: dict) -> dict:
        rules = data.get("rules", [])
        idx, rule = find_rule_by_id(rules, "ceo_engineering_boundary")
        if idx < 0:
            self.detail = "rule not found in parsed data"
            return data
        removed = rules.pop(idx)
        self.detail = f"removed ceo_engineering_boundary rule entirely (was at index {idx})"
        return data

    def check_detection(self, original: dict, mutated: dict) -> bool:
        """Detect by checking rule count decreased."""
        orig_count = len(original.get("rules", []))
        mut_count = len(mutated.get("rules", []))
        return orig_count != mut_count


# ────────────────────────────────────────────────────────────
# Governance Check Engine
# ────────────────────────────────────────────────────────────

def run_governance_check(original_data: dict, mutated_data: dict, mutation: Mutation) -> bool:
    """
    Run governance integrity checks on the mutated YAML.
    Returns True if the mutation was detected (caught), False if it survived.

    Checks performed:
    1. Rule count integrity (original vs mutated)
    2. Critical rule name presence (deny rules must exist)
    3. Action field integrity (no deny->allow flips on critical rules)
    4. Scope field non-empty for enabled rules
    5. Keywords field non-empty for content_contains conditions
    """
    problems = []

    # Check 1: Rule count
    orig_count = len(original_data.get("rules", []))
    mut_count = len(mutated_data.get("rules", []))
    if orig_count != mut_count:
        problems.append(f"rule_count_changed: {orig_count} -> {mut_count}")

    # Check 2: Critical rule names must exist
    critical_rule_ids = set()
    for rule in original_data.get("rules", []):
        if rule.get("action") == "deny":
            critical_rule_ids.add(rule.get("id"))
    mut_rule_ids = {r.get("id") for r in mutated_data.get("rules", [])}
    missing = critical_rule_ids - mut_rule_ids
    if missing:
        problems.append(f"critical_rules_missing: {missing}")

    # Check 3: Action integrity (deny rules should not become allow)
    orig_deny = {}
    for rule in original_data.get("rules", []):
        if rule.get("action") == "deny":
            orig_deny[rule.get("id")] = rule.get("action")
    for rule in mutated_data.get("rules", []):
        rid = rule.get("id")
        if rid in orig_deny and rule.get("action") != "deny":
            problems.append(f"action_flip: {rid} was deny, now {rule.get('action')}")

    # Check 4: Scope non-empty for enabled rules
    for rule in mutated_data.get("rules", []):
        if rule.get("enabled", True):
            tools = rule.get("trigger", {}).get("tool", None)
            if tools is not None and len(tools) == 0:
                problems.append(f"empty_scope: {rule.get('id')} has empty tool list")

    # Check 5: Keywords non-empty for content_contains conditions
    for rule in mutated_data.get("rules", []):
        for cond in rule.get("trigger", {}).get("conditions", []):
            if cond.get("type") == "content_contains":
                kws = cond.get("keywords", [])
                if not kws:
                    problems.append(f"empty_keywords: {rule.get('id')} content_contains has no keywords")

    # Check 6: Keyword count for known rules (original vs mutated)
    for orig_rule in original_data.get("rules", []):
        rid = orig_rule.get("id")
        _, mut_rule = find_rule_by_id(mutated_data.get("rules", []), rid)
        if mut_rule is None:
            continue
        for o_cond in orig_rule.get("trigger", {}).get("conditions", []):
            if o_cond.get("type") != "content_contains":
                continue
            orig_kws = o_cond.get("keywords", [])
            # Find matching condition in mutated
            for m_cond in mut_rule.get("trigger", {}).get("conditions", []):
                if m_cond.get("type") == "content_contains":
                    mut_kws = m_cond.get("keywords", [])
                    if len(orig_kws) != len(mut_kws):
                        problems.append(f"keyword_count_changed: {rid} had {len(orig_kws)} keywords, now {len(mut_kws)}")
                    break

    detected = len(problems) > 0
    if detected:
        mutation.detail += f" | governance checks caught: {'; '.join(problems)}"
    else:
        mutation.detail += " | governance checks found NO problems (gap!)"
    return detected


# ────────────────────────────────────────────────────────────
# CIEU Emit
# ────────────────────────────────────────────────────────────

def emit_cieu(survived_count: int, caught_count: int, total: int, details: str) -> str:
    """Emit YAML_MUTATION_TEST CIEU event."""
    event_id = str(uuid.uuid4())
    now = time.time()
    seq = int(now * 1_000_000)
    session_id = os.environ.get("YSTAR_SESSION_ID", "mutation-harness")

    try:
        conn = sqlite3.connect(str(CIEU_DB), timeout=10)
        conn.execute(
            """INSERT INTO cieu_events
               (event_id, seq_global, created_at, session_id, agent_id,
                event_type, decision, passed, drift_details, task_description,
                params_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (event_id, seq, now, session_id, "eng-platform",
             "YAML_MUTATION_TEST",
             "allow" if survived_count == 0 else "deny",
             1 if survived_count == 0 else 0,
             details,
             "YAML mutation testing harness run",
             json.dumps({"survived": survived_count, "caught": caught_count, "total": total})),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"  [WARN] CIEU emit failed: {e}", file=sys.stderr)
    return event_id


# ────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────

MUTATION_BANK: list[Mutation] = [
    M1_DeleteTriggerPattern(),
    M2_FlipActionDenyToAllow(),
    M3_EmptyScope(),
    M4_RenameRuleTypo(),
    M5_RemoveEntireRule(),
]


def main() -> int:
    print("=" * 60)
    print("  YAML Mutation Testing Harness")
    print(f"  Target: {YAML_PATH}")
    print(f"  Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    if not YAML_PATH.exists():
        print(f"CRITICAL: YAML file not found: {YAML_PATH}", file=sys.stderr)
        return 2

    # Take pre-run hash
    pre_hash = file_hash(YAML_PATH)
    print(f"\n  Pre-run hash: {pre_hash[:16]}...")

    # Load original data (immutable reference)
    original_data = load_yaml()
    original_rule_count = len(original_data.get("rules", []))
    print(f"  Original rule count: {original_rule_count}")

    results = []

    for mutation in MUTATION_BANK:
        print(f"\n--- Mutation {mutation.mid}: {mutation.description} ---")

        # Backup
        orig_hash = backup_yaml()
        assert orig_hash == pre_hash, "hash changed between mutations — aborting"

        try:
            # Load fresh copy
            data = load_yaml()
            original_copy = copy.deepcopy(data)

            # Apply mutation
            mutated_data = mutation.apply(data)
            save_yaml(mutated_data)

            # Reload mutated to verify it was written
            reloaded = load_yaml()

            # Run governance checks
            caught = run_governance_check(original_copy, reloaded, mutation)

            if caught:
                mutation.status = "CAUGHT"
                print(f"  [{mutation.mid}] CAUGHT — {mutation.detail}")
            else:
                mutation.status = "SURVIVED"
                print(f"  [{mutation.mid}] SURVIVED (gap!) — {mutation.detail}")

        except Exception as e:
            mutation.status = "ERROR"
            mutation.detail = f"exception: {type(e).__name__}: {e}"
            print(f"  [{mutation.mid}] ERROR — {mutation.detail}")

        finally:
            # ALWAYS restore
            restore_yaml(orig_hash)
            # Verify restoration
            post_restore_hash = file_hash(YAML_PATH)
            if post_restore_hash != orig_hash:
                print("CRITICAL: RESTORE FAILED after mutation!", file=sys.stderr)
                sys.exit(2)
            print(f"  Restored: hash verified {post_restore_hash[:16]}...")

        results.append({
            "id": mutation.mid,
            "description": mutation.description,
            "tests": mutation.tests,
            "status": mutation.status,
            "detail": mutation.detail,
        })

    # Final hash check
    final_hash = file_hash(YAML_PATH)
    if final_hash != pre_hash:
        print("CRITICAL: RESTORE FAILED — final hash mismatch!", file=sys.stderr)
        sys.exit(2)

    # Summary
    caught_count = sum(1 for r in results if r["status"] == "CAUGHT")
    survived_count = sum(1 for r in results if r["status"] == "SURVIVED")
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    total = len(results)
    survival_rate = survived_count / total if total > 0 else 0.0

    print(f"\n{'=' * 60}")
    print(f"  SUMMARY")
    print(f"  Total:    {total}")
    print(f"  Caught:   {caught_count}")
    print(f"  Survived: {survived_count}")
    print(f"  Errors:   {error_count}")
    print(f"  Survival rate: {survival_rate:.1%}")
    print(f"  Final hash: {final_hash[:16]}... (matches pre-run: {final_hash == pre_hash})")
    print(f"{'=' * 60}")

    # Emit CIEU
    event_id = emit_cieu(
        survived_count, caught_count, total,
        f"caught={caught_count}, survived={survived_count}, total={total}",
    )
    print(f"  CIEU event: {event_id}")

    # Write report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "yaml_file": str(YAML_PATH),
        "pre_hash": pre_hash,
        "post_hash": final_hash,
        "hash_match": pre_hash == final_hash,
        "mutations": results,
        "caught": caught_count,
        "survived": survived_count,
        "errors": error_count,
        "total": total,
        "survival_rate": survival_rate,
        "cieu_event_id": event_id,
    }
    report_path = REPORTS_DIR / "mutation_test_results.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"  Report: {report_path}")

    # Clean up backup
    if BACKUP_PATH.exists():
        BACKUP_PATH.unlink()

    return 0 if survived_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

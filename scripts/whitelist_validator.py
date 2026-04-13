#!/usr/bin/env python3
"""
Whitelist YAML Validator
AMENDMENT-018 §2.2 Unified Entry Schema Enforcement

Validates governance/whitelist/*.yaml files against schema:
- schema_version: "1.0"
- corpus: one of 7 valid corpus names
- entries: list of whitelist entries with required fields

Usage:
    python3 scripts/whitelist_validator.py [corpus_name]
    # If no corpus_name, validates all .yaml files in governance/whitelist/

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File not found or parsing error
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple

VALID_CORPORA = {
    "constitutional",
    "role_mandate",
    "inter_role_sop",
    "project_procedure",
    "event_workflow",
    "rapid_matrix",
    "escape_hatch",
}

REQUIRED_SCHEMA_FIELDS = {
    "schema_version": str,
    "corpus": str,
    "last_updated": str,
    "source_files": list,
    "entries": list,
}

REQUIRED_ENTRY_FIELDS = {
    "id": str,
    "who": str,
    "what": str,
    "when_trigger": str,
    "when_complete": str,
    "prerequisites": list,
    "observable_signal": dict,
    "source_ref": dict,
}


def validate_schema_top_level(data: Dict[str, Any], file_path: Path) -> List[str]:
    """Validate top-level schema fields."""
    errors = []

    for field, expected_type in REQUIRED_SCHEMA_FIELDS.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(data[field], expected_type):
            errors.append(
                f"Field '{field}' must be {expected_type.__name__}, got {type(data[field]).__name__}"
            )

    if "schema_version" in data and data["schema_version"] != "1.0":
        errors.append(f"schema_version must be '1.0', got '{data['schema_version']}'")

    if "corpus" in data and data["corpus"] not in VALID_CORPORA:
        errors.append(
            f"corpus '{data['corpus']}' not in valid set: {VALID_CORPORA}"
        )

    if "source_files" in data and not data["source_files"]:
        errors.append("source_files list is empty (must have at least one source)")

    return errors


def validate_entry(entry: Dict[str, Any], entry_idx: int) -> List[str]:
    """Validate a single whitelist entry."""
    errors = []

    for field, expected_type in REQUIRED_ENTRY_FIELDS.items():
        if field not in entry:
            errors.append(f"Entry [{entry_idx}] missing required field: {field}")
        elif not isinstance(entry[field], expected_type):
            errors.append(
                f"Entry [{entry_idx}] field '{field}' must be {expected_type.__name__}, "
                f"got {type(entry[field]).__name__}"
            )

    # Validate 'id' format (corpus_NNN or escape_NNN, etc.)
    if "id" in entry:
        entry_id = entry["id"]
        if "_" not in entry_id:
            errors.append(
                f"Entry [{entry_idx}] id '{entry_id}' must follow format 'prefix_NNN'"
            )
        else:
            prefix, suffix = entry_id.rsplit("_", 1)
            if not suffix.isdigit():
                errors.append(
                    f"Entry [{entry_idx}] id '{entry_id}' suffix must be numeric"
                )

    # Validate 'observable_signal' structure
    if "observable_signal" in entry and isinstance(entry["observable_signal"], dict):
        obs_sig = entry["observable_signal"]
        if "cieu_event" not in obs_sig:
            errors.append(
                f"Entry [{entry_idx}] observable_signal missing 'cieu_event' field"
            )
        # 'must_contain' is optional but if present must be dict
        if "must_contain" in obs_sig and not isinstance(obs_sig["must_contain"], dict):
            errors.append(
                f"Entry [{entry_idx}] observable_signal.must_contain must be dict"
            )

    # Validate 'source_ref' structure
    if "source_ref" in entry and isinstance(entry["source_ref"], dict):
        source_ref = entry["source_ref"]
        required_ref_fields = {"file", "section"}
        for ref_field in required_ref_fields:
            if ref_field not in source_ref:
                errors.append(
                    f"Entry [{entry_idx}] source_ref missing '{ref_field}' field"
                )

    # Validate non-empty 'what' (core description)
    if "what" in entry and not entry["what"].strip():
        errors.append(f"Entry [{entry_idx}] 'what' field is empty")

    return errors


def validate_entries(entries: List[Dict[str, Any]]) -> List[str]:
    """Validate all entries in the corpus."""
    errors = []

    if not entries:
        errors.append("entries list is empty (must have at least one entry)")
        return errors

    seen_ids = set()
    for idx, entry in enumerate(entries):
        entry_errors = validate_entry(entry, idx)
        errors.extend(entry_errors)

        # Check for duplicate IDs
        if "id" in entry:
            entry_id = entry["id"]
            if entry_id in seen_ids:
                errors.append(f"Duplicate entry id: {entry_id}")
            seen_ids.add(entry_id)

    return errors


def validate_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate a single YAML file.
    Returns (success: bool, errors: List[str])
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return False, [f"File not found: {file_path}"]
    except yaml.YAMLError as e:
        return False, [f"YAML parse error: {e}"]

    if not isinstance(data, dict):
        return False, ["Root element must be a YAML dictionary"]

    errors = []

    # Validate top-level schema
    errors.extend(validate_schema_top_level(data, file_path))

    # Validate entries
    if "entries" in data and isinstance(data["entries"], list):
        errors.extend(validate_entries(data["entries"]))

    return len(errors) == 0, errors


def main():
    workspace_root = Path(__file__).parent.parent
    whitelist_dir = workspace_root / "governance" / "whitelist"

    if not whitelist_dir.exists():
        print(f"ERROR: Whitelist directory not found: {whitelist_dir}")
        sys.exit(2)

    # Determine which files to validate
    if len(sys.argv) > 1:
        corpus_name = sys.argv[1]
        files_to_validate = [whitelist_dir / f"{corpus_name}.yaml"]
    else:
        files_to_validate = sorted(whitelist_dir.glob("*.yaml"))

    if not files_to_validate:
        print("No YAML files found to validate.")
        sys.exit(2)

    total_files = 0
    total_entries = 0
    failed_files = []

    for file_path in files_to_validate:
        if not file_path.exists():
            print(f"\n❌ FAIL: {file_path.name}")
            print(f"   File not found: {file_path}")
            failed_files.append(file_path.name)
            continue

        success, errors = validate_file(file_path)
        total_files += 1

        if success:
            # Count entries for stats
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                entry_count = len(data.get("entries", []))
                total_entries += entry_count

            print(f"✅ PASS: {file_path.name} ({entry_count} entries)")
        else:
            print(f"\n❌ FAIL: {file_path.name}")
            for error in errors:
                print(f"   • {error}")
            failed_files.append(file_path.name)

    print("\n" + "=" * 60)
    print(f"Validation Summary:")
    print(f"  Files validated: {total_files}")
    print(f"  Total entries: {total_entries}")
    print(f"  Passed: {total_files - len(failed_files)}")
    print(f"  Failed: {len(failed_files)}")

    if failed_files:
        print(f"\nFailed files: {', '.join(failed_files)}")
        sys.exit(1)
    else:
        print("\n✅ All validations passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Whitelist YAML Validator v2
AMENDMENT-018 Phase 1 - Permissive Core + Extension Support

Validates governance/whitelist/*.yaml files with permissive schema:
- Accepts multiple field name variants (id/flow_id/decision_type_id)
- Normalizes to core fields (entry_id, entry_what, entry_who, etc.)
- Extension fields allowed (task_type, legacy_level, cieu_markers, etc.)
- Top-level metadata optional (schema_version, corpus, etc.)

Usage:
    python3 scripts/whitelist_validator.py [corpus_name]
    # If no corpus_name, validates all .yaml files in governance/whitelist/

    Add --verbose or -v to see normalized entries
    Add --dump-first to dump first normalized entry per file

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: File not found or parsing error
"""

import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

VALID_CORPORA = {
    "constitutional",
    "role_mandate",
    "inter_role_sop",
    "project_procedure",
    "event_workflow",
    "rapid_matrix",
    "escape_hatch",
}

# Permissive top-level - these are now OPTIONAL
OPTIONAL_SCHEMA_FIELDS = {
    "schema_version": str,
    "corpus": str,
    "last_updated": str,
    "source_files": list,
    "version": (str, int, float),
    "schema": str,
    "generated_at": str,
    "source": str,
}


def validate_schema_top_level(data: Dict[str, Any], file_path: Path) -> List[str]:
    """Validate top-level schema fields (permissive - all optional)."""
    errors = []

    # Check entries or procedures is required (normalize procedures → entries)
    # Prioritize 'procedures' if it's a list (some files use 'entries' as metadata int)
    entries_list = None
    if "procedures" in data and isinstance(data["procedures"], list):
        entries_list = data["procedures"]
    elif "entries" in data and isinstance(data["entries"], list):
        entries_list = data["entries"]

    if entries_list is None:
        errors.append("Missing required field: entries or procedures (must be a list)")
        return errors

    # Normalize to entries for downstream processing
    data["entries"] = entries_list

    # Validate optional fields if present
    for field, expected_types in OPTIONAL_SCHEMA_FIELDS.items():
        if field in data:
            if isinstance(expected_types, tuple):
                if not isinstance(data[field], expected_types):
                    type_names = " or ".join(t.__name__ for t in expected_types)
                    errors.append(
                        f"Field '{field}' must be {type_names}, got {type(data[field]).__name__}"
                    )
            else:
                if not isinstance(data[field], expected_types):
                    errors.append(
                        f"Field '{field}' must be {expected_types.__name__}, got {type(data[field]).__name__}"
                    )

    # Validate corpus value if present
    if "corpus" in data and data["corpus"] not in VALID_CORPORA:
        errors.append(
            f"corpus '{data['corpus']}' not in valid set: {VALID_CORPORA}"
        )

    return errors


def normalize_entry(entry: Dict[str, Any], file_path: Path) -> Dict[str, Any]:
    """
    Normalize entry to core fields.
    Schema v2: permissive input → normalized output

    Returns dict with:
    - entry_id: normalized ID
    - entry_what: normalized description
    - entry_who: normalized actor (optional)
    - entry_trigger: normalized trigger (optional)
    - entry_complete: normalized completion condition (optional)
    - observable_signal: normalized signal (optional)
    - source_ref: normalized source reference (optional)
    - _raw: original entry (for debugging)
    """
    normalized = {"_raw": entry}

    # Normalize ID (first non-null from id, flow_id, decision_type_id, or any *_id)
    id_candidates = [
        entry.get("id"),
        entry.get("flow_id"),
        entry.get("decision_type_id"),
    ]
    # Also check any field ending with _id
    for key in entry:
        if key.endswith("_id") and key not in ["flow_id", "decision_type_id"]:
            id_candidates.append(entry[key])

    normalized["entry_id"] = next((x for x in id_candidates if x), None)

    # Normalize WHAT (first non-null from what, description, title)
    what_candidates = [
        entry.get("what"),
        entry.get("description"),
        entry.get("title"),
    ]
    normalized["entry_what"] = next((x for x in what_candidates if x), None)

    # Normalize WHO (first non-null from who, default_R, default_D, required_roles)
    who_candidates = [
        entry.get("who"),
        entry.get("default_R"),
        entry.get("default_D"),
    ]
    # Handle required_roles (can be array or string)
    if "required_roles" in entry:
        roles = entry["required_roles"]
        if isinstance(roles, list):
            who_candidates.append(", ".join(str(r) for r in roles))
        else:
            who_candidates.append(str(roles))

    normalized["entry_who"] = next((x for x in who_candidates if x), None)

    # Normalize TRIGGER (first non-null from when_trigger, trigger_condition)
    trigger_candidates = [
        entry.get("when_trigger"),
        entry.get("trigger_condition"),
    ]
    normalized["entry_trigger"] = next((x for x in trigger_candidates if x), None)

    # Normalize COMPLETE
    normalized["entry_complete"] = entry.get("when_complete")

    # Normalize observable_signal (accept str or dict)
    obs_sig = entry.get("observable_signal")
    if obs_sig:
        if isinstance(obs_sig, str):
            normalized["observable_signal"] = {"cieu_event": obs_sig}
        elif isinstance(obs_sig, dict):
            normalized["observable_signal"] = obs_sig
        else:
            normalized["observable_signal"] = {"_raw": str(obs_sig)}

    # Normalize source_ref (optional, fallback to file path)
    source_ref = entry.get("source_ref")
    if source_ref:
        if isinstance(source_ref, str):
            normalized["source_ref"] = {"description": source_ref}
        elif isinstance(source_ref, dict):
            normalized["source_ref"] = source_ref
    else:
        normalized["source_ref"] = {"file": str(file_path.name)}

    return normalized


def validate_entry(entry: Dict[str, Any], entry_idx: int, file_path: Path) -> Tuple[Optional[Dict], List[str]]:
    """
    Validate and normalize a single whitelist entry.
    Returns (normalized_entry, errors)
    """
    errors = []

    # Normalize first
    try:
        normalized = normalize_entry(entry, file_path)
    except Exception as e:
        errors.append(f"Entry [{entry_idx}] normalization failed: {e}")
        return None, errors

    # Validate CORE required fields
    if not normalized.get("entry_id"):
        errors.append(
            f"Entry [{entry_idx}] missing ID field (tried: id, flow_id, decision_type_id, *_id)"
        )

    if not normalized.get("entry_what"):
        errors.append(
            f"Entry [{entry_idx}] missing description field (tried: what, description, title)"
        )

    # Validate non-empty what
    if normalized.get("entry_what") and not normalized["entry_what"].strip():
        errors.append(f"Entry [{entry_idx}] description field is empty")

    return normalized, errors


def validate_entries(entries: List[Dict[str, Any]], file_path: Path) -> Tuple[List[Dict], List[str]]:
    """
    Validate all entries in the corpus.
    Returns (normalized_entries, errors)
    """
    errors = []
    normalized_entries = []

    if not entries:
        errors.append("entries list is empty (must have at least one entry)")
        return normalized_entries, errors

    seen_ids = set()
    for idx, entry in enumerate(entries):
        normalized, entry_errors = validate_entry(entry, idx, file_path)
        errors.extend(entry_errors)

        if normalized:
            normalized_entries.append(normalized)

            # Check for duplicate IDs
            entry_id = normalized.get("entry_id")
            if entry_id:
                if entry_id in seen_ids:
                    errors.append(f"Duplicate entry id: {entry_id}")
                seen_ids.add(entry_id)

    return normalized_entries, errors


def validate_file(file_path: Path, dump_first: bool = False) -> Tuple[bool, List[str], int, Optional[Dict]]:
    """
    Validate a single YAML file.
    Returns (success: bool, errors: List[str], entry_count: int, first_normalized: Optional[Dict])
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        return False, [f"File not found: {file_path}"], 0, None
    except yaml.YAMLError as e:
        return False, [f"YAML parse error: {e}"], 0, None

    if not isinstance(data, dict):
        return False, ["Root element must be a YAML dictionary"], 0, None

    errors = []

    # Validate top-level schema
    errors.extend(validate_schema_top_level(data, file_path))

    # Validate and normalize entries
    normalized_entries = []
    if "entries" in data and isinstance(data["entries"], list):
        normalized_entries, entry_errors = validate_entries(data["entries"], file_path)
        errors.extend(entry_errors)

    entry_count = len(normalized_entries)
    first_normalized = normalized_entries[0] if normalized_entries and dump_first else None

    return len(errors) == 0, errors, entry_count, first_normalized


def main():
    workspace_root = Path(__file__).parent.parent
    whitelist_dir = workspace_root / "governance" / "whitelist"

    if not whitelist_dir.exists():
        print(f"ERROR: Whitelist directory not found: {whitelist_dir}")
        sys.exit(2)

    # Parse flags
    dump_first = "--dump-first" in sys.argv or "-d" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # Remove flags from argv
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    # Determine which files to validate
    if args:
        corpus_name = args[0]
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

        success, errors, entry_count, first_normalized = validate_file(file_path, dump_first=dump_first)
        total_files += 1
        total_entries += entry_count

        if success:
            print(f"✅ PASS: {file_path.name} ({entry_count} entries)")

            # Dump first normalized entry if requested
            if dump_first and first_normalized:
                print(f"\n   First entry (normalized):")
                # Remove _raw for cleaner output
                display = {k: v for k, v in first_normalized.items() if k != "_raw"}
                for key, value in display.items():
                    if isinstance(value, dict):
                        print(f"     {key}: {json.dumps(value, ensure_ascii=False)}")
                    else:
                        # Truncate long strings
                        val_str = str(value)
                        if len(val_str) > 80:
                            val_str = val_str[:77] + "..."
                        print(f"     {key}: {val_str}")
                print()
        else:
            print(f"\n❌ FAIL: {file_path.name}")
            for error in errors:
                print(f"   • {error}")
            failed_files.append(file_path.name)

    print("\n" + "=" * 60)
    print(f"Validation Summary:")
    print(f"  Files validated: {total_files}")
    print(f"  Total entries: {total_entries}")
    print(f"  Passed: {total_files - len(failed_files)}/{total_files}")
    print(f"  Failed: {len(failed_files)}")

    if failed_files:
        print(f"\nFailed files: {', '.join(failed_files)}")
        sys.exit(1)
    else:
        print(f"\n✅ All validations passed. Schema v2 with permissive core.")
        sys.exit(0)


if __name__ == "__main__":
    main()

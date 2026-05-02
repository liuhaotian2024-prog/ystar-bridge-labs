#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


E12R_ALLOWED_FILES = [
    "office/mission_command/repository_delivery_status.py",
    "office/mission_command/repository_delivery_health.py",
    "office/mission_command/repository_delivery_czl.py",
    "scripts/check_repository_delivery.py",
    "scripts/push_with_remote_confirmation.py",
    "reports/integration/repository_delivery_health.md",
    "reports/integration/e12r_repository_delivery_reliability.md",
    "tests/office/test_repository_delivery_status.py",
    "tests/office/test_e12r_repository_delivery_reliability.py",
]


E12R_VALIDATION_COMMANDS = [
    "python3.11 -m py_compile office/mission_command/*.py",
    "python3.11 -m py_compile scripts/*.py",
    "pytest tests/office/test_e12r_*.py -q",
    "pytest tests/office/test_repository_delivery_*.py -q",
    "pytest tests/office/test_e12_*.py -q",
    "pytest tests/office/test_e11_*.py -q",
]


FORBIDDEN_PATTERNS = [
    "**/__pycache__/**",
    "**/*.pyc",
    "*.pyc",
    "**/*.pyo",
    "*.pyo",
    "**/*.db",
    "*.db",
    "**/*.sqlite",
    "*.sqlite",
    "**/*.sqlite3",
    "*.sqlite3",
    "**/*.wal",
    "*.wal",
    "**/*.shm",
    "*.shm",
    "**/*.log",
    "*.log",
    "**/active-agent*",
    "**/active_agent*",
]


def build_e12r_request(repo_root: Path) -> dict:
    return {
        "request_id": "e12r_repository_delivery_reliability",
        "milestone_id": "E12R_repository_delivery_reliability",
        "repo_root": str(repo_root),
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "expected_base_head": "d8ba7636",
        "expected_result_head_optional": "",
        "commit_message": "tools: add repository delivery reliability closure",
        "allowed_files": E12R_ALLOWED_FILES,
        "forbidden_patterns": FORBIDDEN_PATTERNS,
        "validation_commands": E12R_VALIDATION_COMMANDS,
        "push_remote": "origin",
        "push_branch": "backflow/aiden-ceo-meeting-room",
        "remote_confirmation_required": True,
        "cleanup_generated_bytecode": True,
        "created_by": "Codex",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "safety_boundary": {
            "force_push": False,
            "history_rewrite": False,
            "remote_url_mutation": False,
            "arbitrary_shell": False,
            "commit_outside_allowed_files": False,
            "read_tokens": False,
            "print_secrets": False,
        },
        "no_external_side_effects_statement": "No customer contact, email/message, publication, payment, account creation, form submission, or core brain/CIEU/memory writeback is authorized.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create repository delivery request JSON.")
    parser.add_argument("--repo-root", default="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
    parser.add_argument("--output", default="")
    args = parser.parse_args()
    repo_root = Path(args.repo_root).expanduser().resolve()
    request = build_e12r_request(repo_root)
    output = Path(args.output) if args.output else repo_root / "operations/repository_delivery/delivery_requests/e12r_repository_delivery_reliability.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

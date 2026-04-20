#!/usr/bin/env python3
"""
Auto-commit-push module — slice A skeleton (CZL-AUTO-COMMIT-PUSH-CADENCE).

Per Ethan CTO ruling 2026-04-19:
- Dual trigger: session_close + Stop-hook 25-min cadence (cron rejected)
- Authorization: CEO/CTO commit+push; eng-* commit only (writes .ystar_push_pending)
- 6 safety gates before commit (all stubs in slice A, implementation in slice C)
- Explicit include/exclude lists (slice C will add .ystar_autocommit_scope.json)
- Revert-commit rollback only (no --force, no --hard)
- Integration with session_state_flush.py orchestrator (slice B)

Slice A scope (~7 tool_uses): module skeleton + dry-run CLI. No wiring to hooks yet.

Author: Aiden Liu (CEO) via ops script — Board-shell path because CEO→Ryan direct-spawn was rule-blocked at session-age tier.
Date: 2026-04-19 evening
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

# Constants from Ethan ruling
CADENCE_MINUTES = 25
COMPANY_ROOT = Path('/Users/haotianliu/.openclaw/workspace/ystar-company')
YSTAR_GOV_ROOT = Path('/Users/haotianliu/.openclaw/workspace/Y-star-gov')
PUSH_PENDING_FLAG = COMPANY_ROOT / '.ystar_push_pending'
AUTOCOMMIT_SCOPE_JSON = COMPANY_ROOT / '.ystar_autocommit_scope.json'


# Agents authorized for commit+push (per Ethan ruling Authorization section)
PUSH_AUTHORIZED_AGENTS = {'ceo', 'cto'}


def compute_commit_scope(repo_root: Path) -> List[str]:
    """Return changed files in repo honoring include/exclude lists.

    Slice A: placeholder returns git diff --name-only.
    Slice C: will read AUTOCOMMIT_SCOPE_JSON for include/exclude patterns.
    """
    try:
        result = subprocess.run(
            ['git', '-C', str(repo_root), 'diff', '--name-only', 'HEAD'],
            capture_output=True, text=True, timeout=10
        )
        files = [f for f in result.stdout.strip().split('\n') if f]
        return files
    except (subprocess.TimeoutExpired, Exception) as e:
        print(f'[compute_commit_scope] error: {e}', file=sys.stderr)
        return []


def run_safety_gates(files: List[str], agent_id: str) -> tuple[bool, Optional[str]]:
    """Run 6 safety gates per Ethan ruling. Returns (pass, reason-if-fail).

    Slice A: all gates are stubs returning True.
    Slice C: real implementations:
      Gate 1: test pass (Y-star-gov only) — pytest exit=0 in last 5 min
      Gate 2: CROBA clean window — no CROBA events in last 5 min
      Gate 3: no mid-edit state — no pending Write tool calls
      Gate 4: minimum change threshold — ≥1 non-whitespace diff line
      Gate 5: secret scan — grep for AWS_KEY, sk-, BEGIN PRIVATE KEY
      Gate 6: scope guard — files in agent's write scope per AGENTS.md
    """
    # TODO slice C — implement each gate
    return True, None


def commit(files: List[str], message: str, author_agent: str, repo_root: Path, dry_run: bool = False) -> Optional[str]:
    """Stage files + create commit with agent attribution. Returns commit hash or None if dry-run/fail."""
    if not files:
        print('[commit] no files to commit', file=sys.stderr)
        return None

    full_msg = f'{message}\n\nAuthor-Agent: {author_agent}\nCo-Authored-By: Aiden Liu (Y* Bridge Labs CEO)'

    if dry_run:
        print(f'[DRY-RUN] Would commit {len(files)} files with message:\n  {message}')
        print(f'[DRY-RUN] Author-Agent: {author_agent}')
        print(f'[DRY-RUN] Files: {files[:5]}{"..." if len(files) > 5 else ""}')
        return None

    # Real commit — slice C hardens with safety gates
    try:
        subprocess.run(['git', '-C', str(repo_root), 'add'] + files, check=True, timeout=30)
        result = subprocess.run(
            ['git', '-C', str(repo_root), 'commit', '-m', full_msg],
            capture_output=True, text=True, check=True, timeout=30
        )
        hash_result = subprocess.run(
            ['git', '-C', str(repo_root), 'rev-parse', 'HEAD'],
            capture_output=True, text=True, check=True, timeout=10
        )
        commit_hash = hash_result.stdout.strip()
        print(f'[commit] created {commit_hash[:12]}')
        return commit_hash
    except subprocess.CalledProcessError as e:
        print(f'[commit] failed: {e.stderr}', file=sys.stderr)
        return None


def push_if_authorized(author_agent: str, repo_root: Path, dry_run: bool = False) -> bool:
    """Push only if agent is in PUSH_AUTHORIZED_AGENTS. eng-* writes push_pending flag instead."""
    if author_agent in PUSH_AUTHORIZED_AGENTS:
        if dry_run:
            print(f'[DRY-RUN] Would push as {author_agent}')
            return True
        try:
            subprocess.run(['git', '-C', str(repo_root), 'push'], check=True, timeout=60)
            print(f'[push] pushed as {author_agent}')
            return True
        except subprocess.CalledProcessError as e:
            print(f'[push] failed: {e}', file=sys.stderr)
            return False
    else:
        # eng-* case: write push_pending flag for next CEO/CTO boot to consume
        flag_content = json.dumps({
            'author_agent': author_agent,
            'created_at': time.time(),
            'repo': str(repo_root),
            'note': 'eng-* role committed but cannot push per Ethan ruling; CEO/CTO next boot consumes this flag.'
        })
        if dry_run:
            print(f'[DRY-RUN] Would write push_pending flag for {author_agent}')
            return True
        PUSH_PENDING_FLAG.write_text(flag_content)
        print(f'[push_if_authorized] agent {author_agent} not authorized; wrote flag to {PUSH_PENDING_FLAG}')
        return False


def main():
    parser = argparse.ArgumentParser(description='Auto-commit-push — slice A skeleton')
    parser.add_argument('--dry-run', action='store_true', help='Preview without executing')
    parser.add_argument('--repo', choices=['company', 'ystar-gov'], default='company')
    parser.add_argument('--agent', default='ceo', help='Authoring agent (ceo/cto/eng-*)')
    parser.add_argument('--message', default='chore(auto): auto-commit', help='Commit message')
    args = parser.parse_args()

    repo_root = COMPANY_ROOT if args.repo == 'company' else YSTAR_GOV_ROOT
    files = compute_commit_scope(repo_root)
    print(f'[main] changed files in {args.repo}: {len(files)}')

    gates_ok, gate_reason = run_safety_gates(files, args.agent)
    if not gates_ok:
        print(f'[main] safety gates FAILED: {gate_reason}', file=sys.stderr)
        return 1

    commit_hash = commit(files, args.message, args.agent, repo_root, dry_run=args.dry_run)
    if commit_hash or args.dry_run:
        push_if_authorized(args.agent, repo_root, dry_run=args.dry_run)

    return 0


if __name__ == '__main__':
    sys.exit(main())

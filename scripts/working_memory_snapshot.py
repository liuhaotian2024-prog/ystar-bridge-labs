#!/usr/bin/env python3
"""
working_memory_snapshot.py - C5 Working Memory Snapshot (AMENDMENT-015 v2 LRS)

Captures structured snapshot of agent's working memory state at session boundary:
- Recent CIEU events (last 20)
- Active sub-agents (parsed from /private/tmp/.../tasks/*.output)
- Today's targets progress (from goal_progress.py)
- Recent commits (last hour, per repo)
- Unfinished tool calls (pending context)
- Last Board directive

Usage:
    python3 scripts/working_memory_snapshot.py save [--session-id SESSION_ID] [--agent-id AGENT_ID]
    python3 scripts/working_memory_snapshot.py load-latest

Author: Maya Patel (eng-governance) - Y* Bridge Labs
"""

import argparse
import json
import sqlite3
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
CIEU_DB = REPO_ROOT / '.ystar_cieu.db'
SNAPSHOT_DIR = REPO_ROOT / 'memory'
TEMP_TASK_DIR = Path('/private/tmp')


class WorkingMemorySnapshot:
    """Captures and persists working memory snapshot."""

    def __init__(self, repo_root: Path = REPO_ROOT):
        self.repo_root = repo_root
        self.cieu_db = repo_root / '.ystar_cieu.db'

    def capture(self, session_id: str, agent_id: str) -> dict:
        """
        Capture current working memory snapshot.

        Returns structured dict with:
        - session_id, agent_id, captured_at
        - recent_cieu_events (last 20)
        - active_subagents
        - today_targets_progress
        - recent_commits (last hour)
        - unfinished_tool_calls
        - last_board_directive
        """
        captured_at = datetime.utcnow().isoformat() + 'Z'

        snapshot = {
            'session_id': session_id,
            'agent_id': agent_id,
            'captured_at': captured_at,
            'recent_cieu_events': self._get_recent_cieu_events(limit=20),
            'active_subagents': self._get_active_subagents(),
            'today_targets_progress': self._get_today_targets_progress(),
            'recent_commits': self._get_recent_commits(lookback_hours=1),
            'unfinished_tool_calls': [],  # Placeholder - needs LLM context access
            'last_board_directive': '',   # Placeholder - needs conversation history access
        }

        return snapshot

    def _get_recent_cieu_events(self, limit: int = 20) -> List[dict]:
        """Fetch last N CIEU events from database."""
        if not self.cieu_db.exists():
            return []

        try:
            conn = sqlite3.connect(str(self.cieu_db))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT event_type, decision, file_path, agent_id, created_at
                FROM cieu_events
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

            events = []
            for row in cursor.fetchall():
                events.append({
                    'event_type': row['event_type'],
                    'decision': row['decision'],
                    'file_path': row['file_path'],
                    'agent_id': row['agent_id'],
                    'created_at': row['created_at'],
                })

            conn.close()
            return events
        except (sqlite3.Error, KeyError) as e:
            print(f"CIEU query error: {e}", file=sys.stderr)
            return []

    def _get_active_subagents(self) -> List[dict]:
        """Parse /private/tmp/.../tasks/*.output for running sub-agents."""
        active = []

        try:
            # Find Claude task directories
            for claude_dir in TEMP_TASK_DIR.glob('claude-*/'):
                # Look for user-specific subdirs
                for user_dir in claude_dir.glob('-Users-*'):
                    # Then for session UUIDs
                    for session_dir in user_dir.iterdir():
                        if not session_dir.is_dir():
                            continue

                        tasks_dir = session_dir / 'tasks'
                        if not tasks_dir.is_dir():
                            continue

                        for output_file in tasks_dir.glob('*.output'):
                            try:
                                # Check if modified in last 10 minutes (running)
                                mtime = output_file.stat().st_mtime
                                age_minutes = (time.time() - mtime) / 60

                                if age_minutes < 10:
                                    content = output_file.read_text(encoding='utf-8', errors='ignore')
                                    active.append({
                                        'task_file': output_file.name,
                                        'age_minutes': round(age_minutes, 1),
                                        'size_bytes': len(content),
                                        'preview': content[:200] if content else '',
                                    })
                            except (OSError, UnicodeDecodeError):
                                continue
        except Exception as e:
            print(f"Subagent scan error: {e}", file=sys.stderr)

        return active

    def _get_today_targets_progress(self) -> dict:
        """Run goal_progress.py and capture output."""
        goal_script = self.repo_root / 'scripts' / 'goal_progress.py'

        if not goal_script.exists():
            return {'error': 'goal_progress.py not found'}

        try:
            result = subprocess.run(
                [sys.executable, str(goal_script)],
                cwd=str(self.repo_root),
                capture_output=True,
                text=True,
                timeout=15
            )

            # Parse output for progress data
            output = result.stdout.strip()

            # Simple heuristic: count lines with progress indicators
            progress_lines = [
                line for line in output.split('\n')
                if any(marker in line for marker in ['▓', '░', '%', '✓', '✗'])
            ]

            return {
                'status': 'ok' if result.returncode == 0 else 'error',
                'progress_lines': progress_lines[:10],  # First 10 progress indicators
                'full_output_length': len(output),
            }
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError) as e:
            return {'error': str(e)}

    def _get_recent_commits(self, lookback_hours: int = 1) -> List[dict]:
        """Fetch recent git commits from all known repos."""
        commits = []

        # Check both ystar-company and Y-star-gov repos
        repos = [
            self.repo_root,
            self.repo_root.parent / 'Y-star-gov',
        ]

        for repo in repos:
            if not (repo / '.git').is_dir():
                continue

            try:
                result = subprocess.run(
                    ['git', 'log', f'--since={lookback_hours} hours ago', '--oneline', '-n', '10'],
                    cwd=str(repo),
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0 and result.stdout.strip():
                    commits.append({
                        'repo': repo.name,
                        'commits': result.stdout.strip().split('\n')[:10],
                    })
            except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
                continue

        return commits

    def save(self, snapshot: dict, path: Optional[Path] = None) -> Path:
        """Save snapshot to JSON file."""
        if path is None:
            session_id = snapshot.get('session_id', 'unknown')
            filename = f"working_memory_snapshot_{session_id}.json"
            path = SNAPSHOT_DIR / filename

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open('w', encoding='utf-8') as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)

        return path

    def load_latest(self, path: Optional[Path] = None) -> Optional[dict]:
        """Load most recent snapshot from directory."""
        if path is None:
            path = SNAPSHOT_DIR

        if not path.is_dir():
            return None

        # Find most recent snapshot file
        snapshots = sorted(
            path.glob('working_memory_snapshot_*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not snapshots:
            return None

        try:
            with snapshots[0].open('r', encoding='utf-8') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"Load error: {e}", file=sys.stderr)
            return None


def _get_session_id() -> str:
    """Resolve current session ID from .ystar_session.json or timestamp."""
    session_file = REPO_ROOT / '.ystar_session.json'

    if session_file.exists():
        try:
            with session_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
                if 'session_id' in data:
                    return data['session_id']
        except (OSError, json.JSONDecodeError):
            pass

    # Fallback: timestamp-based ID
    return datetime.utcnow().strftime('%Y%m%d_%H%M%S')


def _get_agent_id() -> str:
    """Resolve current agent ID from marker file or env."""
    import os

    aid = os.environ.get('YSTAR_AGENT_ID', '').strip()
    if aid:
        return aid

    marker = REPO_ROOT / '.ystar_active_agent'
    if marker.is_file():
        try:
            txt = marker.read_text(encoding='utf-8').strip()
            if txt:
                return txt
        except OSError:
            pass

    return 'unknown'


def main():
    parser = argparse.ArgumentParser(
        description='C5 Working Memory Snapshot - capture/load agent working memory'
    )
    parser.add_argument(
        'action',
        choices=['save', 'load-latest'],
        help='save snapshot or load most recent'
    )
    parser.add_argument('--session-id', help='Override session ID')
    parser.add_argument('--agent-id', help='Override agent ID')

    args = parser.parse_args()

    snapshot_engine = WorkingMemorySnapshot()

    if args.action == 'save':
        session_id = args.session_id or _get_session_id()
        agent_id = args.agent_id or _get_agent_id()

        snapshot = snapshot_engine.capture(session_id, agent_id)
        saved_path = snapshot_engine.save(snapshot)

        print(f"Snapshot saved: {saved_path}")
        print(f"Session: {session_id}, Agent: {agent_id}")
        print(f"CIEU events: {len(snapshot['recent_cieu_events'])}")
        print(f"Active subagents: {len(snapshot['active_subagents'])}")

    elif args.action == 'load-latest':
        snapshot = snapshot_engine.load_latest()

        if snapshot is None:
            print("No snapshots found", file=sys.stderr)
            sys.exit(1)

        # Emit JSON to stdout for piping
        print(json.dumps(snapshot, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
hook_session_end.py - Claude Code SessionEnd hook for Y*gov session close.

Claude Code invokes this on session end. We call session_close_yml.py to write
session summary to YML memory (.ystar_memory.db).

Agent ID resolution:
  1. YSTAR_AGENT_ID env var (set by shell)
  2. `.ystar_active_agent` marker file in repo root
  3. default 'ceo'

Fail-open: any error logs but doesn't block session end.

Author: Ethan Wright (CTO) - Y* Bridge Labs
Wire: P0-B U2 (2026-04-15)
"""
import json, os, sys, subprocess, traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _resolve_agent_id():
    aid = os.environ.get('YSTAR_AGENT_ID', '').strip()
    if aid: return aid
    marker = REPO_ROOT / '.ystar_active_agent'
    if marker.is_file():
        try:
            txt = marker.read_text(encoding='utf-8').strip()
            if txt: return txt
        except OSError: pass
    return 'ceo'


def _emit_output(msg):
    """Emit hook output (Claude Code expects JSON with hookSpecificOutput)."""
    out = {
        'hookSpecificOutput': {
            'hookEventName': 'SessionEnd',
            'message': msg,
        }
    }
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()


def _main():
    try:
        # Read SessionEnd payload from stdin (optional)
        try:
            payload = json.loads(sys.stdin.read() or '{}')
        except Exception:
            payload = {}

        agent_id = _resolve_agent_id()

        # Generate auto-summary
        summary = f"Session ended for {agent_id}"

        # Call session_close_yml.py
        close_script = REPO_ROOT / 'scripts' / 'session_close_yml.py'
        if close_script.exists():
            result = subprocess.run(
                [sys.executable, str(close_script), agent_id, summary],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                _emit_output(f"✓ YML session close completed for {agent_id}")
            else:
                _emit_output(f"⚠ YML session close failed: {result.stderr[:200]}")
        else:
            _emit_output("⚠ session_close_yml.py not found")

    except Exception as e:
        log = REPO_ROOT / 'scripts' / 'hook_debug.log'
        try:
            with log.open('a', encoding='utf-8') as f:
                f.write('[hook_session_end] FATAL ' + str(e) + '\n')
                f.write(traceback.format_exc() + '\n')
        except OSError:
            pass
        _emit_output(f'[Y*gov session close failed - error logged to scripts/hook_debug.log]')


if __name__ == '__main__':
    _main()

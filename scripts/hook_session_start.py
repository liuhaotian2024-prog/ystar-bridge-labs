#!/usr/bin/env python3
"""
hook_session_start.py - Claude Code SessionStart hook for Y*gov handoff.

Claude Code invokes this on every session matching startup|resume|clear|compact.
We read stdin (SessionStart payload), call the handoff assembler, and emit
JSON with hookSpecificOutput.additionalContext - which Claude Code prepends
to the LLM's first context frame.

Agent ID resolution:
  1. YSTAR_AGENT_ID env var (set by shell)
  2. `.ystar_active_agent` marker file in repo root
  3. default 'ceo'

Fail-open: any error returns a minimal notice, never blocks session start.

Author: Ethan Wright (CTO) - Y* Bridge Labs
"""
import json, os, sys, traceback
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


def _emit(additional_context):
    out = {
        'hookSpecificOutput': {
            'hookEventName': 'SessionStart',
            'additionalContext': additional_context,
        }
    }
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()


def _append_morning_brief():
    """Load today's morning brief if exists."""
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    daily_dir = REPO_ROOT / 'reports' / 'daily'

    briefs = []
    for fname in [f'{today}_morning.md', f'{today}_wakeup_report.md']:
        fpath = daily_dir / fname
        if fpath.is_file():
            try:
                content = fpath.read_text(encoding='utf-8').strip()
                if content:
                    briefs.append(f'\n## {fname}\n{content}')
            except OSError:
                pass

    return ''.join(briefs) if briefs else ''


def _main():
    try:
        try: _ = json.loads(sys.stdin.read() or '{}')
        except Exception: pass
        agent_id = _resolve_agent_id()
        sys.path.insert(0, str(REPO_ROOT / 'scripts'))
        from ystar_handoff import build_packet, render_for_additional_context
        packet = build_packet(agent_id, REPO_ROOT)
        text, _truncated, _spill = render_for_additional_context(
            packet, max_chars=9800)

        # Append morning brief
        morning = _append_morning_brief()
        if morning:
            text += '\n\n# Daily Brief' + morning

        _emit(text)
    except Exception as e:
        log = REPO_ROOT / 'scripts' / 'hook_debug.log'
        try:
            with log.open('a', encoding='utf-8') as f:
                f.write('[hook_session_start] FATAL ' + str(e) + '\n')
                f.write(traceback.format_exc() + '\n')
        except OSError: pass
        _emit('[Y*gov handoff unavailable - run `bash scripts/governance_boot.sh ceo` '
              'manually to restore state. Error logged to scripts/hook_debug.log.]')


if __name__ == '__main__':
    _main()
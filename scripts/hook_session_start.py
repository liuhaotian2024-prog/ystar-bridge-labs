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


def _append_conversation_replay():
    """Load C7 Conversation Replay (AMENDMENT-015 v2 LRS) - PRIORITY 1."""
    import subprocess

    replay_script = REPO_ROOT / 'scripts' / 'conversation_replay.py'
    if not replay_script.exists():
        return ''

    try:
        result = subprocess.run(
            [sys.executable, str(replay_script),
             '--lookback-hours', '24',
             '--max-tokens', '800000'],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and result.stdout.strip():
            return '\n\n' + result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        pass

    return ''


def _append_working_memory_snapshot():
    """Load latest working memory snapshot (C5 - AMENDMENT-015 v2 LRS)."""
    import subprocess

    snapshot_script = REPO_ROOT / 'scripts' / 'working_memory_snapshot.py'
    if not snapshot_script.exists():
        return ''

    try:
        result = subprocess.run(
            [sys.executable, str(snapshot_script), 'load-latest'],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():
            snapshot_json = result.stdout.strip()
            # Parse to get summary stats
            import json
            try:
                data = json.loads(snapshot_json)
                summary = f"""
## Working Memory Snapshot (C5 LRS)
- Session: {data.get('session_id', 'unknown')}
- Captured: {data.get('captured_at', 'unknown')}
- Recent CIEU events: {len(data.get('recent_cieu_events', []))}
- Active subagents: {len(data.get('active_subagents', []))}
- Recent commits: {sum(len(r.get('commits', [])) for r in data.get('recent_commits', []))}

<details>
<summary>Full snapshot (click to expand)</summary>

```json
{snapshot_json}
```
</details>
"""
                return summary
            except json.JSONDecodeError:
                return ''
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        pass

    return ''


def _append_world_state():
    """Load WORLD_STATE.md (Mission Control - PRIORITY 0 - single file context)."""
    world_state_path = REPO_ROOT / 'memory' / 'WORLD_STATE.md'
    if not world_state_path.exists():
        return ''

    try:
        content = world_state_path.read_text(encoding='utf-8').strip()
        if content:
            return '\n\n# WORLD_STATE — Mission Control\n' + content
    except OSError:
        pass

    return ''


def _append_yml_memories():
    """Load YML memories for agent (P0-B U2 - obligation-driven memory retrieval)."""
    import subprocess

    boot_script = REPO_ROOT / 'scripts' / 'session_boot_yml.py'
    if not boot_script.exists():
        return ''

    try:
        result = subprocess.run(
            [sys.executable, str(boot_script)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode == 0 and result.stdout.strip():
            return '\n\n## YML Memory Retrieval\n' + result.stdout.strip()
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, OSError):
        pass

    return ''


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

        # AMENDMENT-015 v2 LRS + Mission Control - Priority Order:
        # PRIORITY 0: WORLD_STATE (Mission Control - single file context for CEO)
        world_state = _append_world_state()
        if world_state:
            text = world_state + '\n\n---\n\n' + text

        # C7 Conversation Replay (PRIORITY 1) - verbatim transcript
        replay = _append_conversation_replay()
        if replay:
            text = replay + '\n\n' + text

        # C5 Working Memory Snapshot (PRIORITY 3)
        snapshot = _append_working_memory_snapshot()
        if snapshot:
            text += '\n\n# Working Memory Snapshot' + snapshot

        # YML Memory Retrieval (PRIORITY 2 - obligation-driven)
        yml = _append_yml_memories()
        if yml:
            text += yml

        # Morning brief (lowest priority)
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
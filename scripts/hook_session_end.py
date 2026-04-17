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
Wire: P0-B U2 (2026-04-15); Session Rt+1 calc (2026-04-16)
"""
import json, os, sys, subprocess, traceback
from pathlib import Path

# Y*gov module path fix (Board 2026-04-16 P0: ModuleNotFoundError emergency)
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT / 'scripts'))
try:
    from _cieu_helpers import emit_cieu
except ImportError:
    emit_cieu = None


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


def _calc_session_rt() -> int:
    """
    Calculate session Rt+1 per AGENTS.md Session-Level Y* Doctrine.

    5 constraints (all must be 0 for Rt+1=0):
    1. Active backlog count = 0
    2. Git status clean + 0 unpushed commits (both repos)
    3. WORLD_STATE.md fresh (not stale)
    4. session_summary_YYYYMMDD.md generated
    5. priority_brief next_session_p0_carryover updated

    Returns:
        int: Sum of violations (0 = clean session)
    """
    rt = 0
    violations = []

    # Constraint 1: Check priority_brief for pending tasks
    priority_brief = REPO_ROOT / 'reports' / 'priority_brief.md'
    if priority_brief.exists():
        content = priority_brief.read_text(encoding='utf-8')
        # Count pending/in-progress items (heuristic: unchecked boxes)
        pending_count = content.count('- [ ]')
        if pending_count > 0:
            rt += pending_count
            violations.append(f"pending_tasks={pending_count}")

    # Constraint 2: Git status clean (both repos)
    for repo_path in [REPO_ROOT, REPO_ROOT.parent / 'Y-star-gov']:
        if repo_path.exists():
            try:
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout.strip():
                    rt += 1
                    violations.append(f"git_dirty:{repo_path.name}")

                # Check unpushed commits
                result = subprocess.run(
                    ['git', 'log', '@{u}..HEAD', '--oneline'],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout.strip():
                    rt += 1
                    violations.append(f"unpushed:{repo_path.name}")
            except Exception:
                pass  # Fail-open

    # Constraint 3: WORLD_STATE.md fresh (modified today)
    world_state = REPO_ROOT / 'memory' / 'WORLD_STATE.md'
    if world_state.exists():
        import time
        mtime = world_state.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        if age_hours > 24:
            rt += 1
            violations.append(f"world_state_stale:{age_hours:.1f}h")

    # Constraint 4: session_summary_YYYYMMDD.md generated
    from datetime import datetime
    today_summary = REPO_ROOT / 'memory' / f"session_summary_{datetime.now().strftime('%Y%m%d')}.md"
    if not today_summary.exists():
        rt += 1
        violations.append("session_summary_missing")

    # Constraint 5: priority_brief next_session_p0_carryover updated
    # (heuristic: check if priority_brief modified in last hour)
    if priority_brief.exists():
        import time
        mtime = priority_brief.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        if age_hours > 1:
            rt += 1
            violations.append(f"priority_brief_stale:{age_hours:.1f}h")

    return rt, violations


def _main():
    try:
        # Read SessionEnd payload from stdin (optional)
        try:
            payload = json.loads(sys.stdin.read() or '{}')
        except Exception:
            payload = {}

        agent_id = _resolve_agent_id()

        # Calculate session Rt+1
        rt_value, violations = _calc_session_rt()

        # Emit SESSION_RT_MEASUREMENT CIEU event
        if emit_cieu:
            emit_cieu(
                event_type="SESSION_RT_MEASUREMENT",
                decision="info",
                passed=(1 if rt_value == 0 else 0),
                task_description=f"Session Rt+1 calculation: {rt_value}",
                params_json=json.dumps({
                    "rt_value": rt_value,
                    "violations": violations,
                    "agent_id": agent_id
                })
            )

        # Output marker line for boot snapshot visibility
        print(f"[SESSION_RT: {rt_value}]", file=sys.stderr)
        if violations:
            print(f"[SESSION_RT_VIOLATIONS: {', '.join(violations)}]", file=sys.stderr)

        # Generate auto-summary
        summary = f"Session ended for {agent_id}, Rt+1={rt_value}"

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
                _emit_output(f"✓ YML session close completed for {agent_id}, SESSION_RT={rt_value}")
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

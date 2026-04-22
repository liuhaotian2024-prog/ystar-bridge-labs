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

# Y*gov module path fix (Board 2026-04-16 P0: ModuleNotFoundError emergency)
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

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


def _register_article11_obligations():
    """Register 3 Article 11 autonomous obligations (Board directive 2026-04-15).

    Obligations:
    1. Board offline 30min → CEO must activate autonomous_work_learning (10min due)
    2. Task 30min without CIEU action → task must have progress (30min due)
    3. Rt+1 stagnant 3 checkpoints → Rt+1 must converge (20min due)

    Design: fail-silent (don't block session start on OmissionEngine errors).
    """
    try:
        agent_id = _resolve_agent_id()
        db_path = str(REPO_ROOT / '.ystar_cieu.db')

        # Import register_obligation_programmatic from sibling script
        sys.path.insert(0, str(REPO_ROOT / 'scripts'))
        try:
            from register_obligation import register_obligation_programmatic
        finally:
            sys.path.pop(0)

        # Obligation 1: Board offline 30min → CEO autonomous mode
        register_obligation_programmatic(
            db_path=db_path,
            entity_id='ARTICLE_11_BOARD_OFFLINE',
            owner=agent_id,
            rule_id='article_11_board_offline_30m',
            rule_name='Article 11: Board offline 30min → CEO autonomous mode',
            description='When Board (Haotian) is offline for 30min, CEO must activate autonomous_work_learning mode and continue work without waiting for instructions',
            due_secs=600,  # 10min from now (check if Board offline ≥30min)
            severity='high',
            obligation_type='article_11_parallel_enforcement',
            required_event='ceo_autonomous_mode_activated',
            initiator='board_directive_20260415',
            directive_ref='reports/board_pending/board_directive_20260415_cto_autonomous_maintenance.md',
            verbose=False,
        )

        # Obligation 2: Task 30min without CIEU → must have progress
        register_obligation_programmatic(
            db_path=db_path,
            entity_id='ARTICLE_11_TASK_STAGNATION',
            owner=agent_id,
            rule_id='article_11_task_30m_no_cieu',
            rule_name='Article 11: Task 30min no CIEU → must have progress',
            description='When a task runs for 30min without CIEU action events, agent must spawn sub-agent (Article 11 parallel) or emit tool_use evidence of progress',
            due_secs=1800,  # 30min from now
            severity='medium',
            obligation_type='article_11_parallel_enforcement',
            required_event='task_progress_cieu_emitted',
            initiator='board_directive_20260415',
            directive_ref='reports/board_pending/board_directive_20260415_cto_autonomous_maintenance.md',
            verbose=False,
        )

        # Obligation 3: Rt+1 stagnant 3 checkpoints → must converge
        register_obligation_programmatic(
            db_path=db_path,
            entity_id='ARTICLE_11_RT_STAGNATION',
            owner=agent_id,
            rule_id='article_11_rt_3_checkpoints_no_convergence',
            rule_name='Article 11: Rt+1 stagnant 3 checkpoints → must converge',
            description='When Rt+1 (honest gap) does not decrease for 3 consecutive checkpoints, agent must escalate to Board or spawn sub-agent to attack root cause',
            due_secs=1200,  # 20min from now
            severity='high',
            obligation_type='article_11_parallel_enforcement',
            required_event='rt_convergence_action_taken',
            initiator='board_directive_20260415',
            directive_ref='reports/board_pending/board_directive_20260415_cto_autonomous_maintenance.md',
            verbose=False,
        )
    except Exception as e:
        # Fail-silent: log error but don't block session start
        log = REPO_ROOT / 'scripts' / 'hook_debug.log'
        try:
            with log.open('a', encoding='utf-8') as f:
                f.write(f'[hook_session_start] OmissionEngine registration failed: {e}\n')
                f.write(traceback.format_exc() + '\n')
        except OSError:
            pass


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



def _detect_board_presence() -> bool:
    try:
        import sqlite3, time
        db = REPO_ROOT / ".ystar_cieu.db"
        if not db.exists(): return False
        conn = sqlite3.connect(str(db))
        row = conn.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type='BOARD_MESSAGE' AND created_at>?",
            (time.time()-1800,)).fetchone()
        conn.close()
        return bool(row and row[0] > 0)
    except Exception: return False

def _get_violation_count() -> str:
    try:
        import sqlite3
        from datetime import datetime
        db = REPO_ROOT / ".ystar_cieu.db"
        if not db.exists(): return "（CIEU不可用）"
        conn = sqlite3.connect(str(db))
        month_start = datetime.now().replace(day=1,hour=0,minute=0,second=0).timestamp()
        row = conn.execute(
            "SELECT COUNT(*) FROM cieu_events WHERE event_type IN ('DEFER_LANGUAGE_DRIFT','DEFER_IN_COMMIT_DRIFT','DEFER_IN_BASH_DRIFT','BOARD_CHOICE_QUESTION_DRIFT','CEO_AVOIDANCE') AND created_at>?",
            (month_start,)).fetchone()
        conn.close()
        return str(row[0]) if row else "0"
    except Exception: return "（查询失败）"

def _inject_behavioral_constraints() -> str:
    mode = ("🟢 Board在线 — 按Board指示工作" if _detect_board_presence()
            else "🔴 Board离线 — 自主模式，持续工作直到Board说停")
    return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CEO行为约束 [CONSTITUTIONAL — 不可忽略]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
当前模式：{mode}

Board离线时唯一正确行为：
  自主学习 | 系统测试 | 长期任务设计 | Article 11并行执行
  持续工作，直到Board明确说"收工"/"stop"

BLOCK级违规（forget_guard直接拒绝tool call）：
  ✗ 给Board出选择题（1)/2)/方案一/Option A）
  ✗ 未经Board指示自行停止（明日/等Board回来/later）
  ✗ prose-claim done（无CIEU落盘证据）
  ✗ commit message含defer语义词

本月违规次数：{_get_violation_count()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def _append_y_star_field_state():
    """Load Y* Field State section from WORLD_STATE.md (ξ field cognitive aid for agent boot).

    Per Y* Field Theory Spec Section 11.3: operations-side agents navigate ξ field
    to align task U with active m_functor distribution. This function extracts the
    Y* Field State section (generated by Ryan's generate_world_state.py) and injects
    it into session boot output so agents see mission field context on first frame.

    Fail-open: returns empty string if section absent (Ryan not yet emitting).
    """
    world_state_path = REPO_ROOT / 'memory' / 'WORLD_STATE.md'
    if not world_state_path.exists():
        return ''

    try:
        content = world_state_path.read_text(encoding='utf-8')
        # Find Y* Field State section (any section header containing "Y* Field State")
        import re
        # Match section start: ## N. ... Y* Field State ... (or ## Y* Field State)
        pattern = re.compile(
            r'(^## (?:\d+\.\s*)?.*Y\*\s*Field\s*State.*$)(.*?)(?=^## |\Z)',
            re.MULTILINE | re.DOTALL
        )
        match = pattern.search(content)
        if not match:
            return ''

        field_section = match.group(0).strip()
        if not field_section:
            return ''

        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Y* Field State (xi field — mission functor context)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{field_section}

Align your 5-tuple Y* with active m_functor distribution above.
Per Spec Section 11.3: governance verifies form, operations drives Y* attainment.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    except (OSError, Exception):
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

        # PRIORITY 0.5: Y* Field State (ξ field cognitive aid)
        y_star_field = _append_y_star_field_state()
        if y_star_field:
            text += '\n\n' + y_star_field

        # PRIORITY -1: Behavioral Constraints (Campaign v3)
        constraints = _inject_behavioral_constraints()
        text = constraints + '\n\n' + text

        # PRIORITY 0: OmissionEngine Article 11 Auto-Register
        # Board directive 2026-04-15: 3 autonomous obligations
        _register_article11_obligations()

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
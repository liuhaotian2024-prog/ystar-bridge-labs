#!/usr/bin/env python3
"""ystar_handoff.py - Session Handoff Packet Assembler (v0.3.0, 2026-04-12)

Assembles a self-contained handoff packet so a fresh Claude Code session can
resume work with zero human briefing.

Consumed by:
  - scripts/hook_session_start.py (SessionStart hook)
  - gov-mcp gov_full_handoff / gov_full_handoff_text tools

Public API:
    build_packet(agent_id, repo_root) -> dict
    render_markdown(packet) -> str
    render_for_additional_context(packet, max_chars=9800, spill_dir=None)
        -> (text, truncated, spill_path)

Author: Ethan Wright (CTO) - Y* Bridge Labs
"""
from __future__ import annotations
import json, os, sqlite3, time
from datetime import datetime, timezone
from pathlib import Path


def _read_json_safe(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return None


def _read_text_head(p, n_lines):
    try:
        with p.open(encoding='utf-8') as f:
            buf = []
            for i, line in enumerate(f):
                if i >= n_lines: break
                buf.append(line.rstrip('\n'))
            return '\n'.join(buf)
    except Exception: return ''


def extract_continuation(repo):
    data = _read_json_safe(repo / 'memory' / 'continuation.json') or {}
    keep = ('campaign', 'team_state', 'action_queue', 'anti_patterns',
            'next_session_first_actions', 'generated_at')
    return {k: data[k] for k in keep if k in data}


def extract_obligations(repo, limit=10):
    data = _read_json_safe(repo / 'memory' / 'continuation.json') or {}
    obs = data.get('obligations') or []
    sorted_obs = sorted(
        obs, key=lambda o: o.get('created_at', 0) if isinstance(o, dict) else 0,
        reverse=True)[:limit]
    return [{'content': o.get('content', '')[:400],
             'created_at': o.get('created_at')}
            for o in sorted_obs if isinstance(o, dict)]


def extract_recent_cieu(repo, hours=24.0, limit=5):
    db = repo / '.ystar_cieu.db'
    if not db.is_file(): return []
    cutoff = time.time() - (hours * 3600.0)
    rows = []
    try:
        conn = sqlite3.connect('file:' + str(db) + '?mode=ro',
                               uri=True, timeout=2.0)
        conn.row_factory = sqlite3.Row
        try:
            cur = conn.execute(
                "SELECT event_type, decision, evidence_grade, agent_id, "
                "created_at FROM cieu_events WHERE created_at >= ? "
                "ORDER BY CASE evidence_grade "
                "  WHEN 'exec' THEN 3 WHEN 'outcome' THEN 2 "
                "  WHEN 'intent' THEN 1 ELSE 0 END DESC, "
                "created_at DESC LIMIT ?",
                (cutoff, limit))
            for r in cur:
                rows.append({'event_type': r['event_type'],
                             'decision': r['decision'],
                             'evidence_grade': r['evidence_grade'],
                             'agent_id': r['agent_id'],
                             'created_at': r['created_at']})
        except sqlite3.Error:
            cur = conn.execute(
                "SELECT event_type, decision, agent_id, created_at "
                "FROM cieu_events WHERE created_at >= ? "
                "ORDER BY created_at DESC LIMIT ?",
                (cutoff, limit))
            for r in cur:
                rows.append({'event_type': r['event_type'],
                             'decision': r['decision'],
                             'agent_id': r['agent_id'],
                             'created_at': r['created_at']})
        conn.close()
    except Exception:
        return []
    return rows


def extract_active_task(repo, agent_id):
    p = repo / 'knowledge' / agent_id / 'active_task.json'
    data = _read_json_safe(p)
    if data is None: return {}
    def _trim(v, n=300): return v[:n] if isinstance(v, str) else v
    return {k: _trim(v) for k, v in data.items() if not k.startswith('_')}


def extract_dispatch(repo, max_lines=60):
    return _read_text_head(repo / 'DISPATCH.md', max_lines)


def extract_board_latest(repo, max_lines=30):
    return _read_text_head(repo / 'BOARD_PENDING.md', max_lines)


def extract_knowledge_digest(repo, agent_id, top_n=3):
    lessons_dir = repo / 'knowledge' / agent_id / 'lessons'
    out = {'lessons_count': 0, 'top': []}
    if not lessons_dir.is_dir(): return out
    try:
        files = [p for p in lessons_dir.rglob('*.md') if p.is_file()]
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        out['lessons_count'] = len(files)
        for p in files[:top_n]:
            out['top'].append({'title': p.stem.replace('_', ' '),
                               'path': str(p.relative_to(repo)),
                               'mtime': int(p.stat().st_mtime)})
    except Exception: pass
    return out


def compute_next_action(continuation, active_task, dispatch):
    if active_task:
        status = str(active_task.get('status') or
                     active_task.get('progress') or '')
        if status and 'block' not in status.lower() and 'done' not in status.lower():
            name = active_task.get('task') or active_task.get('name') or '(unnamed)'
            return 'Resume active_task: ' + str(name) + ' (status=' + status + ')'
    queue = continuation.get('action_queue') or []
    for item in queue:
        if isinstance(item, dict):
            return ('Execute action_queue[' + str(item.get('seq', '?')) +
                    ']: ' + str(item.get('action', '?')) + ' - ' +
                    str(item.get('command') or '')[:120])
    if dispatch:
        return 'No active_task, no action_queue - read DISPATCH.md and pick P0.'
    return 'No continuation signal - run governance_boot.sh and reassess.'


def build_packet(agent_id, repo_root):
    now_iso = datetime.now(timezone.utc).isoformat(timespec='seconds')
    continuation = extract_continuation(repo_root)
    return {
        'meta': {'agent_id': agent_id, 'generated_at': now_iso,
                 'session_key': agent_id + '_' + str(int(time.time())),
                 'repo_root': str(repo_root),
                 'source_version': 'ystar_handoff.py v0.3.0'},
        'continuation': continuation,
        'obligations': extract_obligations(repo_root, limit=10),
        'recent_cieu': extract_recent_cieu(repo_root, hours=24.0, limit=5),
        'active_task': extract_active_task(repo_root, agent_id),
        'dispatch_state': extract_dispatch(repo_root),
        'board_latest': extract_board_latest(repo_root),
        'knowledge_digest': extract_knowledge_digest(repo_root, agent_id),
        'next_action': compute_next_action(
            continuation,
            extract_active_task(repo_root, agent_id),
            extract_dispatch(repo_root)),
    }


_BUDGET = {'meta': 200, 'continuation': 1500, 'obligations': 2000,
           'recent_cieu': 1500, 'active_task': 1200, 'dispatch': 900,
           'board': 900, 'knowledge': 400, 'next_action': 400}


def _trim(s, n):
    return s if len(s) <= n else s[: max(0, n - 20)] + '\n...[truncated]'


def _fmt_ts(t):
    try:
        return datetime.fromtimestamp(
            float(t), tz=timezone.utc).strftime('%m-%d %H:%M')
    except Exception: return '?'


def render_markdown(packet):
    parts = []
    m = packet.get('meta', {})
    parts.append(_trim(
        '# Session Handoff - ' + str(m.get('agent_id', '?')) + '\n'
        '_Generated: ' + str(m.get('generated_at', '?')) + ' | Source: ' +
        str(m.get('source_version', '?')) + '_\n', _BUDGET['meta']))
    parts.append(_trim('\n## Next Action\n' + packet.get('next_action', '') +
                       '\n', _BUDGET['next_action']))

    cont = packet.get('continuation', {})
    lines = ['\n## Continuation']
    camp = cont.get('campaign') or {}
    if camp:
        lines.append('- Campaign: **' + str(camp.get('name', '?')) + '** Day ' +
                     str(camp.get('day', '?')) + ' | Target: ' +
                     str(camp.get('target', '?')))
    for role, st in list((cont.get('team_state') or {}).items())[:6]:
        if isinstance(st, dict):
            lines.append('- ' + role + ': [' + str(st.get('progress', '?')) +
                         (' BLOCKED' if st.get('blocked') else '') + '] ' +
                         str(st.get('task', ''))[:120])
    for it in (cont.get('action_queue') or [])[:5]:
        if isinstance(it, dict):
            lines.append('  - [' + str(it.get('seq', '?')) + '] ' +
                         str(it.get('action', '?')) + ' -> ' +
                         str(it.get('command') or '')[:100])
    parts.append(_trim('\n'.join(lines) + '\n', _BUDGET['continuation']))

    lines = ['\n## Obligations (top 10)']
    for o in packet.get('obligations', []):
        lines.append('- [' + _fmt_ts(o.get('created_at')) + '] ' +
                     str(o.get('content', ''))[:250])
    parts.append(_trim('\n'.join(lines) + '\n', _BUDGET['obligations']))

    lines = ['\n## Recent CIEU (24h, top by grade)']
    for r in packet.get('recent_cieu', []):
        lines.append('- [' + _fmt_ts(r.get('created_at')) + '] ' +
                     str(r.get('evidence_grade', '?')).rjust(8) + ' | ' +
                     str(r.get('event_type', '?')) + ' | ' +
                     str(r.get('decision', '?')) + ' | ' +
                     str(r.get('agent_id', '?')))
    parts.append(_trim('\n'.join(lines) + '\n', _BUDGET['recent_cieu']))

    at = packet.get('active_task', {})
    lines = ['\n## Active Task']
    if at:
        for k, v in list(at.items())[:8]:
            lines.append('- **' + str(k) + '**: ' + str(v)[:220])
    else:
        lines.append('_(none set)_')
    parts.append(_trim('\n'.join(lines) + '\n', _BUDGET['active_task']))

    parts.append(_trim('\n## DISPATCH.md (head)\n```\n' +
                       packet.get('dispatch_state', '') + '\n```\n',
                       _BUDGET['dispatch']))
    parts.append(_trim('\n## BOARD_PENDING.md (head)\n```\n' +
                       packet.get('board_latest', '') + '\n```\n',
                       _BUDGET['board']))

    kd = packet.get('knowledge_digest', {})
    lines = ['\n## Knowledge Digest (count=' +
             str(kd.get('lessons_count', 0)) + ')']
    for t in kd.get('top', []):
        lines.append('- ' + str(t.get('title', '?')) + ' - `' +
                     str(t.get('path', '?')) + '`')
    parts.append(_trim('\n'.join(lines) + '\n', _BUDGET['knowledge']))
    return ''.join(parts)


def render_for_additional_context(packet, max_chars=9800, spill_dir=None):
    full = render_markdown(packet)
    if len(full) <= max_chars: return full, False, ''
    spill_dir = spill_dir or Path('/tmp')
    ts = int(time.time())
    agent = packet.get('meta', {}).get('agent_id', 'agent')
    spill_path = spill_dir / ('ystar_handoff_' + agent + '_' + str(ts) + '.md')
    try:
        spill_path.write_text(full, encoding='utf-8')
        pointer = ('\n\n---\n[Handoff truncated to fit 10k cap. Full packet: '
                   'Read `' + str(spill_path) + '` for complete state.]\n')
    except OSError:
        pointer = '\n\n---\n[Handoff truncated; spill write failed.]\n'
        spill_path = Path('')
    keep = max(0, max_chars - len(pointer))
    return full[:keep] + pointer, True, str(spill_path)


def _main():
    import argparse
    repo_default = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description='Y* session handoff assembler')
    ap.add_argument('agent_id', nargs='?',
                    default=os.environ.get('YSTAR_AGENT_ID', 'ceo'))
    ap.add_argument('--repo', type=Path, default=repo_default)
    ap.add_argument('--format', choices=['json', 'text', 'hook'], default='text')
    ap.add_argument('--max-chars', type=int, default=9800)
    args = ap.parse_args()
    packet = build_packet(args.agent_id, args.repo)
    if args.format == 'json':
        print(json.dumps(packet, ensure_ascii=False, indent=2))
    elif args.format == 'text':
        print(render_markdown(packet))
    else:
        text, truncated, spill = render_for_additional_context(
            packet, max_chars=args.max_chars)
        print(text)
        if truncated: print('[spill:' + spill + ']')
    return 0


if __name__ == '__main__':
    raise SystemExit(_main())
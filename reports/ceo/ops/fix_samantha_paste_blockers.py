#!/usr/bin/env python3
"""
Audience: Board (who will run this) + future Aiden sessions auditing today's paste unblock.
Research basis: Samantha#7 Rt+1=1 escalation — 4 root causes below Leo's 3-phase kernel fix; Path A (agent_stack CLI NOOP) and Path B (Samantha-Secretary alias missing) are the 2 unblock-critical ones.
Synthesis: heredoc / bracketed-paste / zsh indentation failures all derail trying to paste multi-line commands. A small Python script in reports/ with U-workflow headers bypasses ALL of those shell failure modes.
Purpose: unblock Samantha#8 to finally apply AMENDMENT-020 v2 paste.
"""

import json
import pathlib

# ---- Path A: add __main__ CLI to agent_stack.py ----
script = pathlib.Path('/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/agent_stack.py')
cli_block = '''

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_push = sub.add_parser("push-agent")
    p_push.add_argument("agent_id")
    sub.add_parser("pop-agent")
    sub.add_parser("peek")
    args = parser.parse_args()
    if args.cmd == "push-agent":
        push_agent(args.agent_id)
    elif args.cmd == "pop-agent":
        pop_agent()
    elif args.cmd == "peek":
        print(peek_agent() or "")
'''

current = script.read_text()
if '__main__' not in current:
    with script.open('a') as f:
        f.write(cli_block)
    print('[A] CLI added to agent_stack.py')
else:
    print('[A] CLI already present (skip)')

# ---- Path B: register Samantha aliases ----
session = pathlib.Path('/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json')
d = json.loads(session.read_text())
d.setdefault('agent_aliases', {})
added = 0
for key, val in [('Samantha-Secretary', 'secretary'), ('Samantha-Lin', 'secretary')]:
    if key not in d['agent_aliases']:
        d['agent_aliases'][key] = val
        added += 1
session.write_text(json.dumps(d, indent=2))
print(f'[B] Aliases added this run: {added}. Total now: {len(d["agent_aliases"])}')

# ---- Smoke ----
import subprocess
out = subprocess.run(
    ['python3', str(script), 'peek'],
    capture_output=True, text=True
)
print(f'[Smoke] agent_stack.py peek → exit={out.returncode} stdout={out.stdout!r} stderr={out.stderr!r}')

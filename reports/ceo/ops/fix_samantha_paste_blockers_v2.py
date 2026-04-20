#!/usr/bin/env python3
"""
Audience: Board — final unstick for peek_agent NameError in v1 fix.
Research basis: v1 fix script added CLI with peek_agent() which does NOT exist; grep showed actual API is current_agent(). Samantha#7 receipt noted "272 lines, ends at get_session_id()" — I should have grepped before writing CLI.
Synthesis: swap peek_agent → current_agent in the CLI block I appended.
Purpose: smoke test passes; Samantha#8 can proceed with push-agent/pop-agent/peek.
"""

import pathlib

script = pathlib.Path('/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/agent_stack.py')
text = script.read_text()

# Idempotent swap
if 'print(peek_agent() or "")' in text:
    text = text.replace(
        'print(peek_agent() or "")',
        'print(current_agent() or "")'
    )
    script.write_text(text)
    print('[FIX] peek_agent → current_agent swapped')
elif 'print(current_agent() or "")' in text:
    print('[FIX] Already using current_agent (skip)')
else:
    print('[FIX] Unexpected state — neither token found; manual review needed')

# Re-smoke
import subprocess
out = subprocess.run(
    ['python3', str(script), 'peek'],
    capture_output=True, text=True
)
print(f'[Smoke] peek → exit={out.returncode} stdout={out.stdout!r} stderr={out.stderr!r}')

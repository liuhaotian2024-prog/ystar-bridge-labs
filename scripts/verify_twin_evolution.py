#!/usr/bin/env python3
"""Verification script for twin evolution implementation"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

# Verification checklist
checks = []

# 1. Core scripts exist and executable
twin_evolution = REPO_ROOT / 'scripts' / 'twin_evolution.py'
twin_report = REPO_ROOT / 'scripts' / 'twin_report.py'

checks.append(('twin_evolution.py exists', twin_evolution.exists()))
checks.append(('twin_evolution.py executable', twin_evolution.stat().st_mode & 0o111 != 0))
checks.append(('twin_report.py exists', twin_report.exists()))
checks.append(('twin_report.py executable', twin_report.stat().st_mode & 0o111 != 0))

# 2. Wakeup script integration
wakeup_script = REPO_ROOT / 'scripts' / 'ystar_wakeup.sh'
wakeup_content = wakeup_script.read_text()
checks.append(('ystar_wakeup.sh has twin mode', 'twin)' in wakeup_content))
checks.append(('ystar_wakeup.sh suggests cron', '37 22 * * *' in wakeup_content))

# 3. CLAUDE.md session close protocol
claude_md = REPO_ROOT / 'CLAUDE.md'
claude_content = claude_md.read_text()
checks.append(('CLAUDE.md mentions twin_evolution.py', 'twin_evolution.py' in claude_content))
checks.append(('CLAUDE.md has session close steps', 'session_close_yml.py' in claude_content))

# 4. Documentation
docs = REPO_ROOT / 'docs' / 'twin_evolution_architecture.md'
checks.append(('Architecture doc exists', docs.exists()))

# 5. Execution logs exist (from test runs)
gemma_log = REPO_ROOT / 'knowledge' / 'ceo' / 'gaps' / 'gemma_sessions.log'
checks.append(('Gemma session log exists', gemma_log.exists()))

# Print results
print('=== Twin Evolution Implementation Verification ===\n')
all_passed = True
for check_name, result in checks:
    status = '✓' if result else '✗'
    print(f'{status} {check_name}')
    if not result:
        all_passed = False

print(f'\n{"All checks passed!" if all_passed else "Some checks failed"}')
sys.exit(0 if all_passed else 1)

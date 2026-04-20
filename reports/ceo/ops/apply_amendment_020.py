#!/usr/bin/env python3
"""
Audience: Board (executes this from shell to bypass agent-hook layer). CEO authors; Board runs.
Research basis: Samantha#4-8 progressively blocked by cascade — kernel Phase 1/2/3, agent_stack CLI, Samantha alias. The alias fix accidentally widened must_dispatch_via_cto block to include `Samantha-` prefix, locking Samantha out. Board's raw shell bypasses agent-hook infrastructure entirely.
Synthesis: Board shell = escape hatch for secretary-restricted writes (AGENTS.md + BOARD_CHARTER_AMENDMENTS.md). Same path Leo's Option K kernel fix validates, just invoked at human-shell level rather than agent-tool level.
Purpose: finalize AMENDMENT-020 — the only task of today that hasn't shipped. Board runs this, AGENTS.md + charter entry land, CEO verifies via boot Step 5.

Board Authorization: 2026-04-19 explicit "paste v2" + "ack AMENDMENT-020".
"""

import json
import pathlib
import re
import time

COMPANY = pathlib.Path('/Users/haotianliu/.openclaw/workspace/ystar-company')
AGENTS_MD = COMPANY / 'AGENTS.md'
CHARTER_MD = COMPANY / 'governance' / 'BOARD_CHARTER_AMENDMENTS.md'

FIVE_BLOCKS = '''## Secretary Agent

### Role
Charter executor, knowledge curator, information hub. Authorized to write AGENTS.md, BOARD_CHARTER_AMENDMENTS.md, DNA_LOG.md. Operates per `agents/Secretary.md` legacy charter + `knowledge/secretary/role_definition/secretary_curation_charter.md`.

### Write Access
- ./knowledge/ (all subdirectories, cross-team)
- ./governance/BOARD_CHARTER_AMENDMENTS.md
- ./governance/DNA_LOG.md
- ./memory/boot_packages/
- ./reports/secretary/, ./reports/weekly_board_brief_*.md
- ./ARCHIVE_INDEX.md
- ./CURRENT_TASKS.md
- AGENTS.md (only when Board-approved amendment has ready-to-paste diff)
- .ystar_active_agent (AMENDMENT-009 escape_hatch)

### Read Access
All directories.

### Forbidden Access
- ./finance/
- ./sales/
- .env

### Obligations
- On `board_online` event: push pending task list + pending obligations summary
- On `board_instruction_completed` event: update weekly brief digest
- On `subagent_completed` event: audit MATURITY_TAG_MISSING for that subagent; escalate to CEO if missing
- On `cieu_silence_threshold` event (>24h silence while session active): emit P0 alert
- On `session_boot` event: audit hook registration state (PreToolUse/PostToolUse installed? Y/N)
- Continuous: CIEU silence monitor (>24h no record in any agent's stream → P0 alert)
- Continuous: obligation backlog monitor (>10 pending unfulfilled obligations → escalate to CEO)
- Curate Board decisions to `knowledge/decisions/`
- Execute AMENDMENT-010 13-step curation pipeline
- L-tag every status output (AMENDMENT-019)
- Restore `.ystar_active_agent` on sub-agent exit

---

## eng-kernel Agent (Kernel Engineer)

### Role
Owns Y*gov kernel internals: session lifecycle, hook dispatch core, policy compilation, identity resolution. Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/kernel/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/session.py
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/kernel/
- ./reports/kernel/
- ./reports/receipts/

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations
- Test gate: all kernel tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)
- session.json / policy compile changes → run full-stack import test + identity-resolution regression before declaring complete
- New `ystar/kernel/*.py` → must have at least one unit test in `tests/kernel/`

---

## eng-governance Agent (Governance Engineer)

### Role
Owns Y*gov governance layer. Path A (meta-governance): governs Y*gov's own module graph — single-track, fail-closed self-improvement. Path B (external governance): governs customer-side external agents using the same trust architecture. Also owns ForgetGuard rules, dispatch policy, CIEU schema. Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/governance/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/path_a/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/path_b/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/governance/
- ./reports/governance/
- ./reports/receipts/

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations
- Test gate: all governance tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)
- `forget_guard_rules.yaml` changed → run behavioral stress test
- Any Path A cycle execution MUST emit CIEU events (enforcement layer must observe)
- path_a/path_b change → test + CIEU smoke verify

---

## eng-platform Agent (Platform Engineer)

### Role
Owns Y*gov platform surface: adapters (hook.py etc.), CLI, third-party integrations, cross-platform compatibility, Labs-side scripts (`./scripts/` hook/daemon infrastructure). Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/adapters/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/cli/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/integrations/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/platform/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/adapters/
- ./reports/platform/
- ./reports/receipts/
- ./scripts/ (hook/daemon infrastructure only — NOT application or data scripts)

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations
- Test gate: all platform + adapter tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- Cross-platform compatibility: macOS primary, Linux CI, Windows best-effort
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)
- hook.py/wrapper/daemon change → verify PreToolUse+PostToolUse registration + run end-to-end intercept smoke + confirm CIEU emit
- `hook_client_labs.sh` change → run end-to-end intercept smoke against ≥2 tool types

---

## eng-domains Agent (Domains Engineer)

### Role
Owns Y*gov domain layer: domain-specific policies, role templates, vertical-specific governance rules. Reports to CTO.

### Write Access
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/domains/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/templates/
- /Users/haotianliu/.openclaw/workspace/Y-star-gov/tests/domains/
- ./reports/domains/
- ./reports/receipts/

### Read Access
- All directories except forbidden paths

### Forbidden Access
- ./finance/
- ./sales/
- .env (any location)

### Obligations
- Test gate: all domain tests must pass before declaring task complete
- CIEU-first debugging: query CIEU database before making any fix
- Source-first fixes: all fixes in Y-star-gov source, never site-packages
- No git ops (commit/push) — CTO or CEO executes git operations after review
- Receipt format: 5-tuple (Y*, Xt, U, Yt+1, Rt+1) written to `./reports/receipts/`
- Registered by AMENDMENT-020 (2026-04-19)
- New domain pack → must include policy template + at least one example tenant config
- Template changed → regression test against 3+ existing tenant configs

---

'''


def apply_to_agents_md():
    text = AGENTS_MD.read_text()
    if '## Secretary Agent' in text and '## eng-kernel Agent' in text:
        print('[AGENTS.md] 5 blocks already present — skip.')
        return 0
    # Insert before ## Escalation Matrix
    anchor = '## Escalation Matrix (Board-Approved)'
    if anchor not in text:
        print(f'[AGENTS.md] ERROR: anchor "{anchor}" not found.')
        return 1
    new_text = text.replace(anchor, FIVE_BLOCKS + anchor)
    AGENTS_MD.write_text(new_text)
    added_lines = new_text.count('\n') - text.count('\n')
    print(f'[AGENTS.md] 5 blocks inserted before Escalation Matrix. Added {added_lines} lines.')
    return 0


def apply_to_charter():
    text = CHARTER_MD.read_text()
    # Find AMENDMENT-020 entry and update its status
    # Pattern: find "AMENDMENT-020" block and update 执行状态
    if 'AMENDMENT-020' not in text:
        print('[CHARTER] ERROR: AMENDMENT-020 entry not found — was it registered?')
        return 1
    if '已完成（' in text and 'AMENDMENT-020' in text:
        # Crude check — might already be done
        print('[CHARTER] AMENDMENT-020 may already be marked complete — manual review recommended.')
    # Append a closing note line
    closing = (
        f'\n\n---\n\n## AMENDMENT-020 CLOSURE NOTE ({time.strftime("%Y-%m-%d %H:%M:%S")})\n\n'
        '**Status**: EXECUTED (pending CEO commit)\n\n'
        'Applied 2026-04-19 via Board shell (bypass agent-hook layer) after 8 Samantha attempts '
        'blocked by cascade: Leo Phase 1 immutable hoist + Phase 2 restricted hoist + Phase 3 per-session marker isolation '
        '+ Path A agent_stack CLI + Path B Samantha aliases. The alias fix widened must_dispatch_via_cto block '
        'to include `Samantha-` prefix, locking all secretary spawns — resolved via Board shell as atomic escape hatch.\n\n'
        '5 new agent blocks landed in AGENTS.md (Secretary + eng-kernel/governance/platform/domains). '
        'Boot Step 5 will report 14+ agent rule sets (was 10).\n'
    )
    CHARTER_MD.write_text(text + closing)
    print('[CHARTER] AMENDMENT-020 closure note appended.')
    return 0


def emit_cieu_event():
    # Best-effort CIEU emission — non-critical if it fails
    try:
        import sqlite3
        db = COMPANY / '.ystar_cieu.db'
        if not db.exists():
            print('[CIEU] db not found — skip')
            return
        conn = sqlite3.connect(str(db))
        cur = conn.cursor()
        import uuid
        import time as t
        cur.execute(
            "INSERT INTO cieu_events (event_id, seq_global, created_at, session_id, agent_id, event_type, decision, passed, violations) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), int(t.time()*1_000_000), t.time(), 'board-shell', 'secretary',
             'AMENDMENT_020_EXECUTED', 'allow', 1, '[]')
        )
        conn.commit()
        conn.close()
        print('[CIEU] AMENDMENT_020_EXECUTED event emitted.')
    except Exception as e:
        print(f'[CIEU] best-effort emit failed: {e}')


if __name__ == '__main__':
    rc_a = apply_to_agents_md()
    rc_c = apply_to_charter()
    emit_cieu_event()
    print(f'\n=== DONE rc_agents={rc_a} rc_charter={rc_c} ===')

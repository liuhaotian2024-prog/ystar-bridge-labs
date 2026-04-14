# Task: Governance Gap Enforcement Implementation

**Assigned to**: eng-governance (Maya Patel) via CTO
**Priority**: P1
**Status**: READY — code fully designed below, implement in boundary_enforcer.py

## Context

Governance audit found ~12 rules that are "declaration-only" (in AGENTS.md but no code enforcement). This task implements code enforcement for the 7 that CAN be enforced as hook checks, and documents the 5 that need obligation-based timing.

## Target File

`Y-star-gov/ystar/adapters/boundary_enforcer.py`

## What to Implement

Insert all new functions BEFORE the `__all__` block (line ~1709).

### A) New DENY Check Functions (5 functions, block execution)

#### 1. `_check_merge_to_main_requires_board_approval(who, tool_name, params)` — ACTION-3
- **Trigger**: Bash command matching `git merge.*main`, `git push.*main`, `git push origin main/master`
- **Check**: Query CIEU for `BOARD_APPROVED` event within last 24h
- **Action**: DENY if no approval found
- **CIEU record**: rule_name=`ACTION-3_merge_main_board_approval`

#### 2. `_check_cieu_archive_before_delete(who, tool_name, params)` — CIEU-1
- **Trigger**: Bash `rm .ystar_cieu.db`, `> .ystar_cieu.db`, `truncate`, `sqlite3 ...DELETE/DROP`; or Write/Edit to `.ystar_cieu.db`
- **Check**: CIEU has `ARCHIVE_COMPLETED` or `CIEU_ARCHIVED` event within last 1h
- **Action**: DENY if no archive found

#### 3. `_check_knowledge_cases_append_only(who, tool_name, params)` — IMMUT-3
- **Trigger**: Write/Edit to path containing `knowledge/cases/`
- **Logic**: Edit tool → always DENY (modifies existing). Write tool → DENY if `os.path.exists(file_path)` is True.
- **Action**: DENY modification, allow new file creation only

#### 4. `_check_no_email_to_humans(who, tool_name, params)` — ACTION-1
- **Trigger**: Bash with `sendmail`, `mail -s`, `mutt`, `curl.*smtp`, `python.*smtplib`, `sendgrid`, `mailgun`, `postmark`, `nodemailer`; or MCP tool names containing "mail"/"gmail"/"email"/"smtp"
- **Action**: Always DENY

#### 5. `_check_publish_requires_cieu_validation(who, tool_name, params)` — PUB-3
- **Trigger**: Bash with `npm publish`, `twine upload`, `gh release create`, `docker push`, `wrangler deploy/publish`, `vercel --prod`, `python setup.py upload`
- **Check**: CIEU has `PUBLISH_VALIDATED`, `QUALITY_CHECK_PASSED`, `BOARD_APPROVED`, or `RELEASE_APPROVED` within 1h
- **Action**: DENY if no validation record

### B) New WARNING Check Functions (2 functions, log only, return None)

#### 6. `_check_no_multiple_choice(who, tool_name, params)` — BOOT-1
- **Trigger**: Write/Edit content containing Board-address keywords ("老大", "Board", "请选择", "please choose", "pick one", "which option") AND numbered/lettered option patterns (`1. xxx\n2. xxx`, `A) xxx`, `选项1`)
- **Action**: WARNING to CIEU via `_record_behavior_rule_cieu`, return None

#### 7. `_check_directive_must_record_to_tracker(who, tool_name, params)` — DIR-1
- **Trigger**: Agent tool dispatch with directive keywords ("Board指令", "老大说", "directive", "Board要求", "Board decision")
- **Check**: `_SESSION_TOOL_CALLS[-30:]` contains Write/Edit to file with "DIRECTIVE_TRACKER" in path
- **Action**: WARNING if no tracker write found, return None

### C) Composite Function

```python
def _check_governance_gap_rules(who, tool_name, params) -> Optional[PolicyResult]:
    """Run all governance-gap enforcement checks."""
    # DENY rules first
    for check_fn in [
        _check_no_email_to_humans,
        _check_merge_to_main_requires_board_approval,
        _check_cieu_archive_before_delete,
        _check_knowledge_cases_append_only,
        _check_publish_requires_cieu_validation,
    ]:
        result = check_fn(who, tool_name, params)
        if result is not None:
            return result

    # WARNING rules (never block)
    _check_no_multiple_choice(who, tool_name, params)
    _check_directive_must_record_to_tracker(who, tool_name, params)

    return None
```

### D) Integration in hook.py

Add after the behavior_rules check (~line 453) and before symbol check (~line 455):

```python
from ystar.adapters.boundary_enforcer import _check_governance_gap_rules

# ── P0-0.65: Governance gap enforcement ──────────────────────────────
gap_deny = _check_governance_gap_rules(who, tool_name, params_early)
if gap_deny is not None:
    cieu_db = ".ystar_cieu.db"
    if session_cfg_early:
        cieu_db = session_cfg_early.get("cieu_db", cieu_db)
    contract = policy._rules.get(who)
    _write_cieu(who, tool_name, params_early, gap_deny,
                session_id_payload or "unknown",
                contract.hash if contract else "", cieu_db)
    _log.warning("DENY governance gap: %s -> %s (%s)", who, tool_name, gap_deny.reason)
    return _result_to_response(gap_deny)
```

### E) Update `__all__` in boundary_enforcer.py

Add these names:
```python
"_check_governance_gap_rules",
"_check_merge_to_main_requires_board_approval",
"_check_cieu_archive_before_delete",
"_check_knowledge_cases_append_only",
"_check_no_email_to_humans",
"_check_no_multiple_choice",
"_check_publish_requires_cieu_validation",
"_check_directive_must_record_to_tracker",
```

## Rules That CANNOT Be Hook-Enforced (time-triggered)

These need obligation timing registration, not hook checks:

| Rule ID | Description | Why Not Hook | Recommendation |
|---------|-------------|--------------|----------------|
| CQ-2 | Pre-commit checklist PASS | Partially covered by existing `pre_commit_requires_test` | Extend existing rule if needed |
| CQ-3 | Weekly design debt scan | Time-triggered (weekly cron) | Register as OmissionEngine obligation `timing: {period: "7d"}` |
| IG-3 | Secretary weekly audit | Time-triggered (weekly Monday) | Register as obligation |
| IG-4 | TEMP_LAW expiry | Time-triggered (expiry date) | Register as obligation `timing: {expires_at: ...}` |
| BOOT-2/3 | Session close scripts | Post-session, no tool call to intercept | Already partially in session_health_hook.sh |

## Test Plan

After implementation, run:
```bash
cd /path/to/Y-star-gov && python3.11 -m pytest tests/ -q --tb=line
```

All existing tests must pass. Add new test cases in `tests/test_boundary_enforcer.py` for each new check function.

## Implementation Notes

- All new checks use the same pattern as existing checks: return `Optional[PolicyResult]`
- `None` = allow, `PolicyResult(allowed=False)` = deny
- Use `_record_behavior_rule_cieu()` for CIEU logging (already exists in the file)
- CIEU queries use `sqlite3` with `timeout=2` and `fail-open` on errors for WARNING, `fail-safe DENY` for critical checks
- Use `_SESSION_TOOL_CALLS` (already exists as global) for checking recent tool call history

## Task: AMENDMENT-023 Layer 1 & 3 Enforcement Infrastructure

**Engineer**: eng-platform (Ryan Park)  
**Priority**: P0 — Board escalation, "naked operation" risk  
**CTO Owner**: Ethan Wright  
**Estimated Time**: 60 minutes  
**L-Tag**: L4 — Systemic Risk

---

### Context

Board detected CEO running strategic decisions without Article 11 (7-layer cognitive construction). This task implements proactive injection (Layer 1) and post-audit drift detection (Layer 3).

Charter: `/Users/haotianliu/.openclaw/workspace/ystar-company/reports/proposals/charter_amendment_023_article_11_into_ceo_os.md`

---

### Acceptance Criteria

- [ ] `scripts/article_11_tracker.py` created — emits `ARTICLE_11_LAYER_X_COMPLETE` events to CIEU
- [ ] `scripts/hook_user_prompt_tracker.py` extended — detects decision keywords → injects Article 11 reminder into system context
- [ ] `scripts/forget_guard_summary.py` extended — hourly scan for decision prompts without Article 11 events → emits `ARTICLE_11_DRIFT_SPIKE`
- [ ] All scripts executable with `python3`
- [ ] Dry-run test: simulate decision prompt → verify injection + event emission + drift detection
- [ ] No files outside `scripts/` modified
- [ ] Tests pass: `pytest tests/ -k article_11 -v`

---

### Files in Scope

**Create**:
- `scripts/article_11_tracker.py`

**Extend**:
- `scripts/hook_user_prompt_tracker.py`
- `scripts/forget_guard_summary.py`

**Read-Only Reference**:
- `knowledge/ceo/working_style/WORKING_STYLE.md` (Article 11 definition lines 94-167)
- `.ystar_cieu.db` (CIEU database schema)

---

### Implementation Spec

#### 1. `scripts/article_11_tracker.py`

**CLI Interface**:
```bash
python3 scripts/article_11_tracker.py layer_complete --layer 0 --evidence "Y* contract: Werner Vogels"
python3 scripts/article_11_tracker.py check_compliance --window_hours 2
```

**Functions**:
- `layer_complete(layer: int, evidence: str)` → emit CIEU event `ARTICLE_11_LAYER_X_COMPLETE`
- `check_compliance(window_hours: int)` → query CIEU for all 7 layer events in time window → return PASS/FAIL

**Event Schema**:
```json
{
  "event_type": "ARTICLE_11_LAYER_0_COMPLETE",
  "agent_id": "ceo",
  "evidence": "Y* contract: ...",
  "timestamp": "2026-04-13T...",
  "session_id": "<from .ystar_session.json>"
}
```

#### 2. Extend `scripts/hook_user_prompt_tracker.py`

**Add Decision Keyword Detection**:
```python
DECISION_KEYWORDS = [
    "strategy", "mission", "amendment", "重大", "决策", "战略", 
    "deploy", "launch", "roadmap", "pivot", "reorg", "restructure"
]

def detect_decision_context(prompt: str) -> bool:
    """Return True if prompt contains decision keywords."""
    return any(kw in prompt.lower() for kw in DECISION_KEYWORDS)

def inject_article_11_reminder():
    """Return injection text for system context."""
    return """
[ARTICLE_11_REQUIRED] This prompt contains strategic decision keywords. CEO must walk 7-layer cognitive construction:
Layer 0: Y* (ideal contract)
Layer 1: Pre-session context (twin trace)
Layer 2: Decision (counterfactual analysis)
Layer 3: Memory (session state + LRS)
Layer 4: Execution (RAPID + constraints)
Layer 5: Track (emit CIEU events)
Layer 6: Learn (extract lessons)
Emit ARTICLE_11_LAYER_X_COMPLETE events via scripts/article_11_tracker.py for audit trail.
"""
```

**Hook Integration**:
- On `UserPromptSubmit`, check `detect_decision_context(prompt)`
- If True, append injection text to system context (mechanism: write to `.ystar_article_11_injection.txt`, hook reads and injects)

#### 3. Extend `scripts/forget_guard_summary.py`

**Add Hourly Drift Detection**:
```python
def detect_article_11_drift(db_path: str, window_hours: int = 1) -> list:
    """
    Scan for user_message containing decision keywords 
    + missing ARTICLE_11_LAYER_X_COMPLETE events in time window.
    
    Returns list of drift incidents.
    """
    # Query CIEU for user_message with decision keywords
    # Check if corresponding ARTICLE_11 events exist within +/- window
    # If missing, return incident record
    pass

def emit_drift_spike(incident):
    """Emit ARTICLE_11_DRIFT_SPIKE event to CIEU."""
    pass
```

**Integration**:
- Called in existing hourly cron
- Appends to `reports/autonomous/forget_guard_daily.md`

---

### Testing Protocol

**Dry-Run Test**:
1. Run `python3 scripts/article_11_tracker.py layer_complete --layer 0 --evidence "test"`
2. Query CIEU: `sqlite3 .ystar_cieu.db "SELECT * FROM cieu WHERE event_type='ARTICLE_11_LAYER_0_COMPLETE' ORDER BY timestamp DESC LIMIT 1;"`
3. Verify event exists

**Injection Test**:
1. Simulate user prompt: "we should launch new strategy"
2. Run hook manually
3. Check `.ystar_article_11_injection.txt` contains reminder

**Drift Detection Test**:
1. Create fake CIEU entry: user_message with "strategy" keyword, timestamp T
2. Ensure no ARTICLE_11 events in [T-1h, T+1h]
3. Run `forget_guard_summary.py`
4. Verify `ARTICLE_11_DRIFT_SPIKE` emitted

---

### Constraints

- Use existing CIEU database schema (no migrations)
- No external dependencies (stdlib only)
- All scripts must handle missing `.ystar_session.json` gracefully
- Error messages must include `[ARTICLE_11_TRACKER]` prefix for grep
- Performance: keyword detection <5ms, event emission <20ms

---

### Handoff to Maya

After Ryan completes, Maya will:
- Add governance rules to `governance/forget_guard_rules.yaml`
- Write `tests/test_article_11_enforcement.py`
- Integrate with existing Forget Guard infrastructure

---

**Start Immediately. Report commit hash when done.**

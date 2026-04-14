## Task: AMENDMENT-023 Layer 2 Governance Rules & Tests

**Engineer**: eng-governance (Maya Patel)  
**Priority**: P0 — Board escalation, "naked operation" risk  
**CTO Owner**: Ethan Wright  
**Estimated Time**: 45 minutes  
**L-Tag**: L4 — Systemic Risk

---

### Context

Board detected CEO running strategic decisions without Article 11 (7-layer cognitive construction). This task implements in-flight enforcement (Layer 2) via governance rules and comprehensive tests.

Charter: `/Users/haotianliu/.openclaw/workspace/ystar-company/reports/proposals/charter_amendment_023_article_11_into_ceo_os.md`

Ryan (eng-platform) is implementing Layers 1 & 3 in parallel. Your work depends on his CIEU event schema but not his code completion.

---

### Acceptance Criteria

- [ ] `governance/forget_guard_rules.yaml` extended with 3 new rules
- [ ] `tests/test_article_11_enforcement.py` created with ≥3 test cases
- [ ] Rules trigger on expected violations (dry-run verified)
- [ ] Tests PASS: `pytest tests/test_article_11_enforcement.py -v`
- [ ] No files outside `governance/` and `tests/` modified
- [ ] Rules integrated with existing Forget Guard infrastructure (no breaking changes)

---

### Files in Scope

**Extend**:
- `governance/forget_guard_rules.yaml`

**Create**:
- `tests/test_article_11_enforcement.py`

**Read-Only Reference**:
- `knowledge/ceo/working_style/WORKING_STYLE.md` (Article 11 definition)
- `scripts/forget_guard.py` (existing rule engine)
- `.ystar_cieu.db` (CIEU schema)

---

### Implementation Spec

#### 1. Extend `governance/forget_guard_rules.yaml`

Add 3 new rules at end of file:

```yaml
# AMENDMENT-023: Article 11 Enforcement Rules

- rule_id: decision_without_article_11
  description: "CEO wrote strategic decision content without Article 11 layer completion events"
  severity: HIGH
  trigger:
    - event_type: [file_write, file_edit]
    - agent_id: ceo
    - content_pattern: "(strategy|mission|amendment|roadmap|pivot|重大决策|战略)"
  condition:
    - missing_events:
        event_types: ["ARTICLE_11_LAYER_0_COMPLETE", "ARTICLE_11_LAYER_1_COMPLETE", 
                      "ARTICLE_11_LAYER_2_COMPLETE", "ARTICLE_11_LAYER_3_COMPLETE",
                      "ARTICLE_11_LAYER_4_COMPLETE", "ARTICLE_11_LAYER_5_COMPLETE",
                      "ARTICLE_11_LAYER_6_COMPLETE"]
        time_window: 7200  # 2 hours
  action:
    - emit_event: FORGET_GUARD_ARTICLE_11_BYPASS_WARNING
    - log_level: WARNING
    - message: "CEO wrote strategic decision without completing Article 11 layers. Decision may be improvised."

- rule_id: article_11_partial_walk
  description: "CEO completed some Article 11 layers but not all 7"
  severity: MEDIUM
  trigger:
    - event_type: ARTICLE_11_LAYER_*_COMPLETE
    - agent_id: ceo
  condition:
    - incomplete_sequence:
        required_layers: [0, 1, 2, 3, 4, 5, 6]
        time_window: 3600  # 1 hour
        threshold: any_missing  # trigger if ANY layer missing
  action:
    - emit_event: FORGET_GUARD_ARTICLE_11_PARTIAL_WALK
    - log_level: WARNING
    - message: "CEO walked Article 11 partially. Missing layers: {missing_layers}"

- rule_id: article_11_post_decision_audit_failure
  description: "Hourly audit detected decision keywords without Article 11 events (drift spike)"
  severity: HIGH
  trigger:
    - event_type: ARTICLE_11_DRIFT_SPIKE
  condition:
    - always: true
  action:
    - emit_event: FORGET_GUARD_ARTICLE_11_AUDIT_FAILURE
    - log_level: ERROR
    - message: "Post-decision audit failed: {drift_count} decisions made without Article 11 discipline"
    - escalate: true
    - notify: [cto, board]
```

**Notes**:
- Use existing Forget Guard rule schema (check `scripts/forget_guard.py` for exact syntax)
- `missing_events` and `incomplete_sequence` may need custom condition handlers — if not supported, flag to CTO for Platform extension
- All 3 rules must be parseable by existing `forget_guard.py` (no syntax errors)

#### 2. Create `tests/test_article_11_enforcement.py`

**Test Cases** (minimum 3, aim for 5):

```python
import pytest
import sqlite3
import tempfile
from datetime import datetime, timedelta
from scripts.article_11_tracker import layer_complete, check_compliance
from scripts.forget_guard import ForgetGuard

@pytest.fixture
def temp_cieu_db():
    """Create temporary CIEU database for testing."""
    db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    # Initialize schema (copy from .ystar_cieu.db)
    yield db.name
    db.close()

def test_layer_complete_emits_event(temp_cieu_db):
    """Test that layer_complete() emits CIEU event correctly."""
    layer_complete(layer=0, evidence="Y* contract: Vogels", db_path=temp_cieu_db)
    
    conn = sqlite3.connect(temp_cieu_db)
    cursor = conn.execute(
        "SELECT event_type, evidence FROM cieu WHERE event_type='ARTICLE_11_LAYER_0_COMPLETE' ORDER BY timestamp DESC LIMIT 1"
    )
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "ARTICLE_11_LAYER_0_COMPLETE"
    assert "Vogels" in row[1]
    conn.close()

def test_check_compliance_all_layers_pass(temp_cieu_db):
    """Test compliance check passes when all 7 layers completed."""
    # Emit all 7 layer events
    for i in range(7):
        layer_complete(layer=i, evidence=f"Layer {i} test", db_path=temp_cieu_db)
    
    result = check_compliance(window_hours=1, db_path=temp_cieu_db)
    assert result["status"] == "PASS"
    assert len(result["completed_layers"]) == 7

def test_check_compliance_missing_layers_fail(temp_cieu_db):
    """Test compliance check fails when layers 3-6 missing."""
    # Only emit layers 0, 1, 2
    for i in range(3):
        layer_complete(layer=i, evidence=f"Layer {i} test", db_path=temp_cieu_db)
    
    result = check_compliance(window_hours=1, db_path=temp_cieu_db)
    assert result["status"] == "FAIL"
    assert result["missing_layers"] == [3, 4, 5, 6]

def test_forget_guard_rule_decision_without_article_11(temp_cieu_db):
    """Test that governance rule triggers when CEO writes decision without Article 11."""
    # Simulate CEO writing AMENDMENT file
    conn = sqlite3.connect(temp_cieu_db)
    conn.execute("""
        INSERT INTO cieu (event_type, agent_id, content, timestamp)
        VALUES ('file_write', 'ceo', 'AMENDMENT_999_STRATEGY_PIVOT.md', ?)
    """, (datetime.now().isoformat(),))
    conn.commit()
    
    # Run Forget Guard
    fg = ForgetGuard(db_path=temp_cieu_db, rules_path="governance/forget_guard_rules.yaml")
    violations = fg.check_rules()
    
    # Should trigger decision_without_article_11 rule
    assert any(v["rule_id"] == "decision_without_article_11" for v in violations)
    conn.close()

def test_forget_guard_rule_partial_walk(temp_cieu_db):
    """Test that governance rule triggers when CEO walks only layers 0-3."""
    # Emit layers 0-3 only
    for i in range(4):
        layer_complete(layer=i, evidence=f"Layer {i}", db_path=temp_cieu_db)
    
    fg = ForgetGuard(db_path=temp_cieu_db, rules_path="governance/forget_guard_rules.yaml")
    violations = fg.check_rules()
    
    # Should trigger article_11_partial_walk rule
    assert any(v["rule_id"] == "article_11_partial_walk" for v in violations)

# Optional: test drift spike detection (if time permits)
def test_drift_spike_detection(temp_cieu_db):
    """Test hourly audit detects decision prompt without Article 11 events."""
    # Insert user_message with decision keyword 1 hour ago
    past_time = (datetime.now() - timedelta(hours=1)).isoformat()
    conn = sqlite3.connect(temp_cieu_db)
    conn.execute("""
        INSERT INTO cieu (event_type, agent_id, content, timestamp)
        VALUES ('user_message', 'board', 'we should pivot strategy now', ?)
    """, (past_time,))
    conn.commit()
    
    # Run forget_guard_summary.py (simulate hourly cron)
    from scripts.forget_guard_summary import detect_article_11_drift
    incidents = detect_article_11_drift(db_path=temp_cieu_db, window_hours=2)
    
    assert len(incidents) > 0
    assert incidents[0]["keyword"] == "strategy"
    conn.close()
```

**Notes**:
- Use `pytest` fixtures for database isolation
- Mock CIEU database if schema initialization is complex
- Test both PASS and FAIL paths
- If `ForgetGuard` class doesn't exist, use direct rule evaluation logic
- Tests must be runnable with `pytest tests/test_article_11_enforcement.py -v`

---

### Integration Constraints

- Do NOT modify existing Forget Guard rules (append only)
- New rules must not conflict with existing rule IDs
- Error messages must be grep-friendly: `[FORGET_GUARD_A023]` prefix
- Performance: rule evaluation <100ms per trigger

---

### Dependency on Ryan's Work

Ryan is implementing `scripts/article_11_tracker.py` in parallel. You need to know:
- Event schema: `ARTICLE_11_LAYER_X_COMPLETE` (X = 0-6)
- CIEU fields: `event_type`, `agent_id`, `evidence`, `timestamp`, `session_id`

If Ryan's implementation changes these, coordinate via CTO (Ethan).

---

### Handoff to CTO

After Maya completes:
- CTO will review rules syntax
- CTO will run e2e test combining Ryan's infra + Maya's rules
- CTO will commit all changes with L4 tag

---

**Start Immediately. Report completion status when done.**

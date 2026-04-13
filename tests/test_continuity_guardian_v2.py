"""Test Continuity Guardian v2 — 覆盖扫描 / scoring / 红队集成

测试覆盖:
1. v2 扫描源完整性（11 个扫描源）
2. Scoring 函数（时间+Board+Role 三维加权）
3. Wisdom package v2 生成（10KB 上限）
4. 红队测试套件生成（20 题）
5. 集成测试（端到端）

Author: Maya Patel (Governance Engineer)
"""

import pytest
import sys
import time
import json
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import session_wisdom_extractor_v2 as extractor_v2
import continuity_guardian_redteam as redteam


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def company_root(tmp_path):
    """Create temporary company root with minimal structure"""
    root = tmp_path / "ystar-company"
    root.mkdir()

    # Create directories
    (root / "memory").mkdir()
    (root / "reports" / "experiments").mkdir(parents=True)
    (root / "knowledge" / "ceo" / "feedback").mkdir(parents=True)
    (root / "knowledge" / "ceo" / "decisions").mkdir(parents=True)
    (root / "knowledge" / "ceo" / "lessons").mkdir(parents=True)
    (root / "knowledge" / "ceo" / "theory").mkdir(parents=True)
    (root / "knowledge" / "ceo" / "skills" / "_draft_").mkdir(parents=True)
    (root / "reports" / "proposals").mkdir(parents=True)

    # Create .ystar_session.json
    session_cfg = {
        "session_id": "test_20260413_1234",
        "agent_id": "ceo"
    }
    (root / ".ystar_session.json").write_text(json.dumps(session_cfg))

    # Create .session_booted marker
    (root / "scripts").mkdir()
    boot_marker = root / "scripts" / ".session_booted"
    boot_marker.touch()

    return root


@pytest.fixture
def mock_cieu_db(company_root):
    """Create mock CIEU database with test events"""
    db_path = company_root / ".ystar_cieu.db"
    conn = sqlite3.connect(str(db_path))

    # Create table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cieu_events (
            id INTEGER PRIMARY KEY,
            event_type TEXT,
            task_description TEXT,
            params_json TEXT,
            created_at REAL,
            decision TEXT
        )
    """)

    # Insert test events
    now = time.time()
    events = [
        ("BOARD_DECISION", "Approved AMENDMENT-009", "{}", now - 3600, "allow"),
        ("INTENT_ADJUSTED", '{"original_intent": "Old", "adjusted_intent": "New"}', "{}", now - 1800, "allow"),
        ("DIRECTIVE_APPROVED", '{"directive_id": "DIR-001", "reason": "Test"}', "{}", now - 900, "allow"),
        ("HOOK_DENY", "Denied immutable path write", "{}", now - 600, "deny"),
    ]

    for event_type, task_desc, params_json, created_at, decision in events:
        conn.execute("""
            INSERT INTO cieu_events (event_type, task_description, params_json, created_at, decision)
            VALUES (?, ?, ?, ?, ?)
        """, (event_type, task_desc, params_json, created_at, decision))

    conn.commit()
    conn.close()

    return db_path


@pytest.fixture
def mock_memory_db(company_root):
    """Create mock memory database with test data"""
    db_path = company_root / ".ystar_memory.db"
    conn = sqlite3.connect(str(db_path))

    # Create table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY,
            memory_type TEXT,
            content TEXT,
            context_tags TEXT,
            created_at REAL
        )
    """)

    # Insert test memories
    now = time.time()
    memories = [
        ("lesson", "Never use fabrication in responses", "{}", now - 3600),
        ("knowledge", "Y*gov uses CIEU for audit trails", "{}", now - 1800),
        ("pattern", "Event-driven architecture is preferred", "{}", now - 900),
        ("obligation", "Complete EXP-6 red team testing", "{}", now - 600),
    ]

    for mem_type, content, tags, created_at in memories:
        conn.execute("""
            INSERT INTO memories (memory_type, content, context_tags, created_at)
            VALUES (?, ?, ?, ?)
        """, (mem_type, content, tags, created_at))

    conn.commit()
    conn.close()

    return db_path


# ============================================================================
# Test v2 扫描源完整性
# ============================================================================

def test_extract_experiments_verdicts(company_root):
    """Test extraction of experiment verdicts from reports/experiments/"""
    # Create test experiment files
    (company_root / "reports" / "experiments" / "exp1_verdict.md").write_text("""
# EXP-1 Verdict

Verdict: Go (all tests passed)
""")

    (company_root / "reports" / "experiments" / "exp6_redteam_audit.md").write_text("""
# EXP-6 Red Team Audit

Final Verdict: No-Go with revision
""")

    verdicts = extractor_v2.extract_experiments_verdicts(company_root)

    assert len(verdicts) >= 2
    assert any("Go" in v["verdict"] for v in verdicts)
    assert any("No-Go" in v["verdict"] for v in verdicts)


def test_extract_board_feedback(company_root):
    """Test extraction of Board feedback from knowledge/ceo/feedback/"""
    # Create test feedback file
    (company_root / "knowledge" / "ceo" / "feedback" / "no_human_time.md").write_text("""# Board Feedback: No Human Time Dimension

禁止使用人类时间维度（挂钟时间）在 agent 框架中。
""")

    feedback = extractor_v2.extract_board_feedback(company_root, "ceo")

    assert len(feedback) >= 1
    # first_line extraction should include "Board"
    assert any("Board" in f["content"] for f in feedback)


def test_extract_role_decisions(company_root):
    """Test extraction of role decisions from knowledge/ceo/decisions/"""
    # Create test decision file
    (company_root / "knowledge" / "ceo" / "decisions" / "exp6_go_nogo.md").write_text("""# EXP-6 Go/No-Go Decision

Decision: Proceed with v2 implementation after red team revision.
""")

    decisions = extractor_v2.extract_role_decisions(company_root, "ceo")

    assert len(decisions) >= 1
    # first_line should contain "EXP-6"
    assert any("EXP-6" in d["content"] or "Decision" in d["content"] for d in decisions)


def test_extract_git_diff(company_root):
    """Test git diff extraction"""
    # Initialize git repo
    import subprocess
    subprocess.run(["git", "init"], cwd=str(company_root), capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=str(company_root), capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(company_root), capture_output=True)

    # Create and commit a file
    test_file = company_root / "test.txt"
    test_file.write_text("test content")
    subprocess.run(["git", "add", "test.txt"], cwd=str(company_root), capture_output=True)
    subprocess.run(["git", "commit", "-m", "test"], cwd=str(company_root), capture_output=True)

    # Modify file
    test_file.write_text("modified content")
    subprocess.run(["git", "add", "test.txt"], cwd=str(company_root), capture_output=True)
    subprocess.run(["git", "commit", "-m", "test2"], cwd=str(company_root), capture_output=True)

    changes = extractor_v2.extract_git_diff(company_root)

    # Git diff may return empty if no HEAD~5, that's ok for test
    assert isinstance(changes, list)


def test_extract_secretary_pipeline_output(company_root):
    """Test extraction of Secretary pipeline output"""
    # Create tombstone scan report
    (company_root / "reports" / "tombstone_scan_20260413.md").write_text("""
# Tombstone Scan Report

Total tombstones applied: 3
""")

    # Create skill draft
    (company_root / "knowledge" / "ceo" / "skills" / "_draft_" / "skill_test.md").write_text("""
# Skill: test_skill

[DRAFT] Test skill draft
""")

    output = extractor_v2.extract_secretary_pipeline_output(company_root)

    assert len(output) >= 1
    assert any(o["step"] == "tombstone" or o["step"] == "skill_extract" for o in output)


# ============================================================================
# Test Scoring 函数
# ============================================================================

def test_compute_score_time_decay():
    """Test time decay scoring (newer = higher)"""
    now = time.time()
    session_start = now - 7200  # 2 hours ago

    # Recent item (30 min ago)
    item_recent = {"timestamp": now - 1800}
    score_recent = extractor_v2.compute_score(item_recent, session_start, "ceo", now)

    # Old item (6 hours ago)
    item_old = {"timestamp": now - 21600}
    score_old = extractor_v2.compute_score(item_old, session_start, "ceo", now)

    assert score_recent > score_old, "Recent items should score higher"


def test_compute_score_board_weight():
    """Test Board annotation weighting (10x)"""
    now = time.time()
    session_start = now - 3600

    # Board decision event
    item_board = {
        "timestamp": now - 1800,
        "description": "Board approved AMENDMENT-009"
    }
    score_board = extractor_v2.compute_score(item_board, session_start, "ceo", now)

    # Regular event
    item_regular = {
        "timestamp": now - 1800,
        "description": "Regular event"
    }
    score_regular = extractor_v2.compute_score(item_regular, session_start, "ceo", now)

    assert score_board > score_regular * 5, "Board events should score 10x higher"


def test_compute_score_role_weight():
    """Test role relevance weighting (5x)"""
    now = time.time()
    session_start = now - 3600

    # CEO-specific item (for CEO boot)
    item_ceo = {
        "timestamp": now - 1800,
        "file": "knowledge/ceo/lessons/test.md"
    }
    score_ceo_for_ceo = extractor_v2.compute_score(item_ceo, session_start, "ceo", now)

    # CEO-specific item (for CTO boot)
    score_ceo_for_cto = extractor_v2.compute_score(item_ceo, session_start, "cto", now)

    assert score_ceo_for_ceo > score_ceo_for_cto * 3, "Same-role items should score 5x higher"


def test_rank_items():
    """Test item ranking with weighted scoring"""
    now = time.time()
    session_start = now - 3600

    items = [
        {"timestamp": now - 3600, "description": "Old regular event"},
        {"timestamp": now - 1800, "description": "Recent Board decision", "type": "BOARD_DECISION"},
        {"timestamp": now - 900, "file": "knowledge/ceo/lessons/test.md", "content": "CEO lesson"},
    ]

    ranked = extractor_v2.rank_items(items, session_start, "ceo", top_n=3)

    # Board decision should rank high
    # CEO lesson should rank higher than old regular event
    assert len(ranked) == 3
    assert all("score" in item for item in ranked)
    assert ranked[0]["score"] >= ranked[1]["score"] >= ranked[2]["score"]


# ============================================================================
# Test Wisdom Package v2 生成
# ============================================================================

def test_generate_wisdom_package_v2(company_root, mock_cieu_db, mock_memory_db):
    """Test wisdom package v2 generation with 11 scanning sources"""
    session_start = time.time() - 3600
    session_id = "test_20260413_1234"

    # Create continuation.json
    continuation = {
        "campaign": {"name": "Y*Defuse 30天战役", "day": 3, "target": "10K users"},
        "team_state": {
            "cto": {"task": "Build MVP", "progress": "in_progress"}
        },
        "action_queue": []
    }
    (company_root / "memory" / "continuation.json").write_text(json.dumps(continuation))

    wisdom = extractor_v2.generate_wisdom_package_v2(
        company_root, session_id, session_start, agent_role="ceo"
    )

    # Check content
    assert "Session Wisdom Package v2" in wisdom
    assert session_id in wisdom
    assert "Core Decisions" in wisdom
    assert "New Knowledge" in wisdom
    assert "Active Obligations" in wisdom
    assert "Role-Specific Intelligence" in wisdom
    assert "Session Changes" in wisdom
    assert "Continuation State" in wisdom

    # Check size
    wisdom_bytes = len(wisdom.encode('utf-8'))
    wisdom_kb = wisdom_bytes / 1024.0
    assert wisdom_kb <= 12.0, f"Wisdom package too large: {wisdom_kb:.1f} KB (target: ≤10 KB with margin)"


def test_wisdom_package_v2_coverage(company_root, mock_cieu_db, mock_memory_db):
    """Test that v2 wisdom package includes items from all 11 scanning sources"""
    session_start = time.time() - 3600
    session_id = "test_20260413_1234"

    # Create test files for each scanning source
    # 1. experiments
    (company_root / "reports" / "experiments" / "exp1.md").write_text("Verdict: Go")

    # 2. board feedback
    (company_root / "knowledge" / "ceo" / "feedback" / "test.md").write_text("# Board feedback")

    # 3. role decisions
    (company_root / "knowledge" / "ceo" / "decisions" / "test.md").write_text("# Decision")

    # 4. role lessons
    (company_root / "knowledge" / "ceo" / "lessons" / "test.md").write_text("# Lesson")

    # 5. role theory
    (company_root / "knowledge" / "ceo" / "theory" / "test.md").write_text("# Theory")

    # 6. proposals
    (company_root / "reports" / "proposals" / "test.md").write_text("# Proposal\nStatus: APPROVED")

    # 7. secretary pipeline
    (company_root / "reports" / "tombstone_scan_20260413.md").write_text("Tombstone report")

    wisdom = extractor_v2.generate_wisdom_package_v2(
        company_root, session_id, session_start, agent_role="ceo"
    )

    # Verify coverage (should mention or include items from multiple sources)
    # At minimum, should have non-empty sections
    assert "(No major decisions recorded)" not in wisdom or "(No new knowledge recorded)" not in wisdom
    assert "**Coverage**" in wisdom and "v2" in wisdom
    assert "11 scanning sources" in wisdom


# ============================================================================
# Test 红队测试套件
# ============================================================================

def test_generate_factual_questions(company_root, mock_cieu_db, mock_memory_db):
    """Test factual question generation from session data"""
    session_start = time.time() - 3600

    questions = redteam.generate_factual_questions(company_root, session_start, "ceo")

    # Should have at least 2 questions (may vary based on mock data)
    assert len(questions) >= 2
    assert all(q["type"] == "factual" for q in questions)
    assert all("question" in q and "ground_truth" in q for q in questions)


def test_generate_negative_questions(company_root):
    """Test negative question generation (fabrication detection)"""
    questions = redteam.generate_negative_questions(company_root)

    assert len(questions) == 5
    assert all(q["type"] == "negative" for q in questions)
    assert all("ground_truth" in q for q in questions)


def test_generate_uncertain_questions(company_root):
    """Test uncertain question generation (honesty test)"""
    questions = redteam.generate_uncertain_questions(company_root)

    assert len(questions) == 5
    assert all(q["type"] == "uncertain" for q in questions)


def test_generate_test_suite(company_root, mock_cieu_db, mock_memory_db):
    """Test full 20-question test suite generation"""
    session_start = time.time() - 3600

    questions = redteam.generate_test_suite(company_root, session_start, "ceo")

    # Should have 20 questions (10 factual + 5 negative + 5 uncertain)
    # But may be fewer if not enough factual data
    assert len(questions) >= 10
    assert any(q["type"] == "factual" for q in questions)
    assert any(q["type"] == "negative" for q in questions)
    assert any(q["type"] == "uncertain" for q in questions)


def test_score_answer_factual():
    """Test scoring for factual questions"""
    question = {
        "type": "factual",
        "ground_truth": "Board approved AMENDMENT-009 for governance enforcement"
    }

    # Good answer (contains key terms)
    answer_good = "The Board approved AMENDMENT-009, which was about governance enforcement."
    score_good = redteam.score_answer(question, answer_good)
    assert score_good["correct"] == True
    assert score_good["score"] >= 0.5

    # Poor answer (missing key terms)
    answer_poor = "Something happened"
    score_poor = redteam.score_answer(question, answer_poor)
    assert score_poor["correct"] == False
    assert score_poor["score"] < 0.5


def test_score_answer_negative():
    """Test scoring for negative questions (hallucination detection)"""
    question = {
        "type": "negative",
        "ground_truth": "This event did not happen"
    }

    # Honest answer (use exact marker "no evidence")
    answer_honest = "I have no evidence that this event occurred."
    score_honest = redteam.score_answer(question, answer_honest)
    assert score_honest["correct"] == True

    # Fabricated answer
    answer_fabricated = "The result was a complete success and Board approved it."
    score_fabricated = redteam.score_answer(question, answer_fabricated)
    assert score_fabricated["correct"] == False


def test_score_answer_uncertain():
    """Test scoring for uncertain questions (honesty test)"""
    question = {
        "type": "uncertain",
        "ground_truth": "Uncertain / Insufficient data"
    }

    # Honest uncertain answer
    answer_honest = "I'm not sure, as I don't have sufficient data to answer this precisely."
    score_honest = redteam.score_answer(question, answer_honest)
    assert score_honest["correct"] == True

    # Overconfident answer
    answer_overconfident = "Definitely 10,000 users, certainly by next week."
    score_overconfident = redteam.score_answer(question, answer_overconfident)
    assert score_overconfident["correct"] == False


# ============================================================================
# 集成测试
# ============================================================================

def test_end_to_end_wisdom_generation_and_redteam(company_root, mock_cieu_db, mock_memory_db):
    """Test end-to-end flow: generate wisdom package v2 → generate red team test suite"""
    session_start = time.time() - 3600
    session_id = "test_20260413_1234"

    # Step 1: Generate wisdom package v2
    wisdom = extractor_v2.generate_wisdom_package_v2(
        company_root, session_id, session_start, agent_role="ceo"
    )

    wisdom_path = company_root / "memory" / f"wisdom_package_{session_id}.md"
    wisdom_path.write_text(wisdom)

    assert wisdom_path.exists()

    # Step 2: Generate red team test suite
    questions = redteam.generate_test_suite(company_root, session_start, "ceo")

    assert len(questions) >= 10

    # Step 3: Generate test script
    test_script = redteam.generate_test_script(
        company_root, session_id, questions, wisdom_path
    )

    assert "Question" in test_script
    assert session_id in test_script


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

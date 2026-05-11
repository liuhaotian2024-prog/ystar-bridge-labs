from __future__ import annotations

import json
import sqlite3

from office.agent_native_messenger import server


def test_execution_followup_resolves_to_prior_strat002_context(tmp_path, monkeypatch):
    context_path = tmp_path / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "last_human_text": "Aiden，请分析 STRAT-002 x402 Mission GO memo。",
                "last_runtime_owner_text": "STRAT-002 x402 Mission GO agent-to-agent payment memo investigation",
                "last_reply_text": "下一步：生成 no-send 的 x402/Mission GO 机会核验包。",
                "last_reply_backend": "aiden_memo_investigation_runtime",
                "last_reply_protocol": "AidenMemoInvestigationRuntimeV1",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(server, "CONVERSATION_CONTEXT_PATH", context_path)

    resolved, meta = server._resolve_runtime_owner_text_from_context("那么你现在就开始自主的执行你说的下一步吧")

    assert meta["applied"] is True
    assert meta["reason"] == "execution_followup_resolved_to_prior_context"
    assert "STRAT-002" in resolved
    assert "x402" in resolved
    assert "execute the previous recommended next step" in resolved
    assert "no-send owner decision packet" in resolved
    assert "Do not only recommend a next step" in resolved


def test_owner_coordination_followup_preserves_context_and_explains_boundary(tmp_path, monkeypatch):
    context_path = tmp_path / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "last_human_text": "Aiden，请分析 STRAT-002 x402 Mission GO memo。",
                "last_runtime_owner_text": "STRAT-002 x402 Mission GO memo investigation",
                "last_reply_text": "建议下一步生成 no-send owner decision packet。",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(server, "CONVERSATION_CONTEXT_PATH", context_path)

    resolved, meta = server._resolve_runtime_owner_text_from_context("我完全不明白，你在要求我怎么配合你去行动？")

    assert meta["applied"] is True
    assert meta["reason"] == "owner_coordination_followup_resolved_to_prior_context"
    assert "coordination clarity" in resolved
    assert "approve/reject/hold/revise" in resolved
    assert "Do not answer with a generic action-packet template" in resolved
    assert "STRAT-002" in resolved


def test_non_followup_is_not_rewritten(tmp_path, monkeypatch):
    context_path = tmp_path / "context.json"
    context_path.write_text(json.dumps({"last_human_text": "older context"}), encoding="utf-8")
    monkeypatch.setattr(server, "CONVERSATION_CONTEXT_PATH", context_path)

    resolved, meta = server._resolve_runtime_owner_text_from_context("Aiden，请解释你现在是什么状态。")

    assert resolved == "Aiden，请解释你现在是什么状态。"
    assert meta["applied"] is False


def test_contextual_memo_reference_resolves_to_prior_artifact(tmp_path, monkeypatch):
    context_path = tmp_path / "context.json"
    prior_memo = (
        "# STRAT-002 — x402 Economy × Mission GO Integration\n\n"
        "Archive ID: STRAT-002\n"
        "Core question: Given x402 infrastructure facts and Mission GO assets, which e34 opportunity spaces "
        "or institutional voids should be re-scored, and what is the cleanest A2A monetization path?"
    )
    context_path.write_text(
        json.dumps(
            {
                "last_human_text": prior_memo,
                "last_runtime_owner_text": prior_memo,
                "last_reply_text": "Aiden should verify x402/AP2/AgentCore evidence and produce strategic judgment.",
                "last_reply_backend": "aiden_memo_investigation_runtime",
                "last_reply_protocol": "AidenMemoInvestigationRuntimeV1",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(server, "CONVERSATION_CONTEXT_PATH", context_path)

    resolved, meta = server._resolve_runtime_owner_text_from_context("Aiden，现在你再次验证和分析那份备忘录。")

    assert meta["applied"] is True
    assert meta["reason"] == "contextual_reference_resolved_to_prior_artifact"
    assert "RECOVERED PRIOR OWNER ARTIFACT" in resolved
    assert "STRAT-002" in resolved
    assert "cleanest A2A monetization path" in resolved
    assert "Do not claim the memo is missing" in resolved


def test_execution_followup_recovers_strat002_context_from_cieustore_when_json_context_is_generic(tmp_path, monkeypatch):
    context_path = tmp_path / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "last_human_text": "那么你现在就开始自主的执行你说的下一步吧",
                "last_runtime_owner_text": "那么你现在就开始自主的执行你说的下一步吧",
                "last_reply_text": "我的判断：这是一个通用行动包。",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    db = tmp_path / "messenger.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE cieu_events(rowid INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT, event_type TEXT, result_json TEXT, created_at REAL)"
        )
        conn.execute(
            "INSERT INTO cieu_events(agent_id, event_type, result_json, created_at) VALUES (?, ?, ?, ?)",
            (
                "owner",
                "AIDEN_AGENT_NATIVE_MESSAGE_DECISION",
                json.dumps({"human_readable_text": "Aiden，请分析 STRAT-002 x402 Mission GO memo。"}, ensure_ascii=False),
                1.0,
            ),
        )
        conn.execute(
            "INSERT INTO cieu_events(agent_id, event_type, result_json, created_at) VALUES (?, ?, ?, ?)",
            (
                "Aiden",
                "AIDEN_AGENT_NATIVE_MESSAGE_DECISION",
                json.dumps({"human_readable_text": "下一步：生成 no-send 的 x402/Mission GO 机会核验包。"}, ensure_ascii=False),
                2.0,
            ),
        )
    monkeypatch.setattr(server, "CONVERSATION_CONTEXT_PATH", context_path)

    resolved, meta = server._resolve_runtime_owner_text_from_context(
        "那么你现在就开始自主的执行你说的下一步吧",
        cieu_db=db,
    )

    assert meta["applied"] is True
    assert meta["context_recovery_source"] == "cieustore_recent_aiden_messages"
    assert "STRAT-002" in resolved
    assert "x402" in resolved
    assert "no-send owner decision packet" in resolved


def test_cieustore_context_recovery_prefers_substantial_prior_artifact_over_short_recent_reference(tmp_path, monkeypatch):
    context_path = tmp_path / "context.json"
    context_path.write_text(
        json.dumps(
            {
                "last_human_text": "Aiden，现在你再次验证和分析那份备忘录。",
                "last_runtime_owner_text": "Aiden，现在你再次验证和分析那份备忘录。",
                "last_reply_text": "memo missing",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    prior_memo = (
        "# STRAT-002 — x402 Economy × Mission GO Integration\n\n"
        "Archive ID: STRAT-002\n"
        "TL;DR: x402 infrastructure may expose Mission GO governance assets as agent-buyer monetization surfaces.\n"
        "Open Questions: asset-to-surface matching, e34 re-scoring, Defuse revival, patent boundaries.\n"
        + "Mission GO asset inventory. " * 80
    )
    db = tmp_path / "messenger_context_prefer_artifact.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            "CREATE TABLE cieu_events(rowid INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT, event_type TEXT, result_json TEXT, created_at REAL)"
        )
        conn.execute(
            "INSERT INTO cieu_events(agent_id, event_type, result_json, created_at) VALUES (?, ?, ?, ?)",
            (
                "owner",
                "AIDEN_AGENT_NATIVE_MESSAGE_DECISION",
                json.dumps({"human_readable_text": prior_memo}, ensure_ascii=False),
                1.0,
            ),
        )
        conn.execute(
            "INSERT INTO cieu_events(agent_id, event_type, result_json, created_at) VALUES (?, ?, ?, ?)",
            (
                "owner",
                "AIDEN_AGENT_NATIVE_MESSAGE_DECISION",
                json.dumps({"human_readable_text": "Aiden，现在你再次验证和分析那份备忘录。"}, ensure_ascii=False),
                2.0,
            ),
        )
    monkeypatch.setattr(server, "CONVERSATION_CONTEXT_PATH", context_path)

    resolved, meta = server._resolve_runtime_owner_text_from_context(
        "Aiden，现在你再次验证和分析那份备忘录。",
        cieu_db=db,
    )

    assert meta["applied"] is True
    assert meta["context_recovery_source"] == "cieustore_recent_aiden_messages"
    assert "STRAT-002" in resolved
    assert "asset-to-surface matching" in resolved
    assert "memo missing" not in resolved

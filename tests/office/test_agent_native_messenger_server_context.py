from __future__ import annotations

import json

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

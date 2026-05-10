from __future__ import annotations

import sqlite3

from office.mission_command.e149_governed_real_model_invocation_runtime import (
    build_aiden_owner_reply_prompt,
    resolve_ollama_model_name,
    run_governed_real_model_invocation,
)


def test_governed_real_model_invocation_executes_selected_local_model_and_writes_cieu(tmp_path):
    def fake_invoker(model_name, prompt, context):
        assert model_name
        assert "你是 Aiden" in prompt
        assert context["selected_model_id"] == "local_gemma4_e4b"
        return {
            "provider": "fake_local_ollama",
            "text": "这是 Aiden 通过真实模型调用生成的中文 CEO 判断。",
            "latency_ms": 9,
            "error": None,
        }

    db = tmp_path / "e149.db"
    result = run_governed_real_model_invocation(
        owner_text="Aiden，请认真回答这个 CEO 问题。",
        retrieval_context_summary="repo evidence and brain evidence are available",
        cieu_db=db,
        real_model_invoker=fake_invoker,
    )

    assert result["reply_backend"] == "governed_real_local_model_invocation"
    assert result["actual_model_invocation_proof"]["actual_generation_executed"] is True
    assert result["actual_model_invocation_proof"]["deterministic_template_substitute_used"] is False
    assert "真实模型调用" in result["reply_text"]
    with sqlite3.connect(db) as conn:
        event_types = [row[0] for row in conn.execute("SELECT event_type FROM cieu_events").fetchall()]
    assert "AIDEN_MODEL_ORCHESTRATION_DECISION" in event_types
    assert "AIDEN_REAL_MODEL_INVOCATION_DECISION" in event_types


def test_governed_real_model_invocation_refuses_template_substitute_when_model_unavailable(tmp_path):
    def failing_invoker(model_name, prompt, context):
        return {"provider": "fake_local_ollama", "text": "", "latency_ms": 2, "error": "connection refused"}

    result = run_governed_real_model_invocation(
        owner_text="Aiden，请认真回答这个 CEO 问题。",
        retrieval_context_summary="retrieval succeeded",
        cieu_db=tmp_path / "e149_unavailable.db",
        real_model_invoker=failing_invoker,
    )

    assert result["reply_backend"] == "governed_real_model_unavailable_notice"
    assert result["runtime_fallback_used"] is True
    assert result["actual_model_invocation_proof"]["actual_generation_executed"] is False
    assert result["actual_model_invocation_proof"]["deterministic_template_substitute_used"] is False
    assert "我不能把这轮回答伪装成 CEO 的真实思考" in result["reply_text"]
    assert "正确路径" in result["reply_text"]


def test_prompt_instructs_owner_readable_chinese_and_no_overclaims():
    prompt = build_aiden_owner_reply_prompt(
        owner_text="Aiden，推进 STRAT-002。",
        retrieval_context_summary="x402 evidence exists",
        selected_model_id="local_gemma4_e4b",
        repo_root="/repo",
    )
    assert "流利、清晰、有判断力的中文" in prompt
    assert "不要展示隐藏推理链" in prompt
    assert "禁止声称已经外发" in prompt
    assert "STRAT-002" in prompt


def test_resolve_ollama_model_name_uses_installed_gemma3_when_gemma4_missing(monkeypatch):
    monkeypatch.delenv("AIDEN_GEMMA4_MODEL", raising=False)

    resolved = resolve_ollama_model_name("local_gemma4_e4b", installed_models=["gemma3:4b"])

    assert resolved == "gemma3:4b"


def test_resolve_ollama_model_name_prefers_installed_owner_env_model(monkeypatch):
    monkeypatch.setenv("AIDEN_GEMMA4_MODEL", "qwen2.5:7b")

    resolved = resolve_ollama_model_name("local_gemma4_e4b", installed_models=["gemma3:4b", "qwen2.5:7b"])

    assert resolved == "qwen2.5:7b"


def test_governed_real_model_invocation_records_actual_resolved_model(tmp_path):
    def fake_invoker(model_name, prompt, context):
        return {
            "provider": "fake_local_ollama",
            "model": "gemma3:4b",
            "installed_models": ["gemma3:4b"],
            "text": "Aiden 通过已安装的 gemma3:4b 真模型完成回复。",
            "latency_ms": 11,
            "error": None,
        }

    result = run_governed_real_model_invocation(
        owner_text="Aiden，请用真实本地模型回答。",
        retrieval_context_summary="retrieval succeeded",
        cieu_db=tmp_path / "e149_resolved_model.db",
        real_model_invoker=fake_invoker,
    )

    proof = result["actual_model_invocation_proof"]
    assert proof["actual_generation_executed"] is True
    assert proof["model_name"] == "gemma3:4b"
    assert proof["raw_result_metadata"]["installed_models"] == ["gemma3:4b"]

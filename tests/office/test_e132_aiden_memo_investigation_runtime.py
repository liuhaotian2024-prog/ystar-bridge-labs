from __future__ import annotations

import sqlite3
from pathlib import Path

import office.aiden_meeting_room.chat_router as chat_router
from office.aiden_meeting_room.chat_router import route_chat_message_to_aiden_meeting_room
from office.mission_command.e124_agent_native_company_messenger import generate_aiden_reply_text
from office.mission_command.e132_aiden_memo_investigation_runtime import (
    build_memo_investigation_queries,
    extract_memo_open_questions,
    extract_memo_entities,
    is_memo_investigation_request,
    is_memo_action_advancement_request,
    run_aiden_memo_investigation_runtime,
)


class FakeMemoPublicReadProvider:
    def search(self, query: str, *, domain_id: str, max_results: int = 3) -> list[dict]:
        return [
            {
                "source_title": f"Official source for {query}",
                "source_url": f"https://example.org/{abs(hash(query)) % 100000}",
                "claim_summary": f"Public-read evidence for {query}",
                "source_date": "2026-05-09",
                "source_date_basis": "test_fixture_public_date",
                "source_date_confidence": "high",
                "observed_at": "2026-05-09T00:00:00Z",
            }
        ][:max_results]


class BrokenMemoPublicReadProvider:
    def search(self, query: str, *, domain_id: str, max_results: int = 3) -> list[dict]:
        raise OSError("network unavailable in test")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _memo() -> str:
    return (
        "请你自主上网搜索可信依据，验证分析下面这份Claude AI提出的备忘录跟我们之间的关系。"
        "并且提出你的深度战略分析\n"
        "# STRAT-002 — x402 Economy × Mission GO Integration (Owner Research Memo)\n"
        "**Archive ID**: STRAT-002\n"
        "**Date**: 2026-05-09\n"
        "**Type**: Research memo for CEO investigation\n"
        "This memo claims x402, Mission GO, USDC, wallet, and agent payments may create an agent economy opportunity. "
        "It asks whether Y*Bridge Labs should integrate payment intent governance before any live payment execution. "
        "It asks Aiden to re-score e34 institutional void #10 agent_to_agent_payment, compare against the Mining Plant Plugin path, "
        "evaluate Defuse revival under dead-path constraints, scope multi-tenant cost, and respect P3/P4 patent boundaries."
        "\n## 8. Open Questions for Aiden's Investigation\n"
        "### 8.1 Asset-to-Surface Matching\n"
        "Given the asset inventory and verified x402 infrastructure, are there capabilities currently inside Mission GO that match agent-buyer demand?\n"
        "### 8.2 Path Sequencing vs Parallelism\n"
        "Is the x402 path parallel to the Plugin path, sequenced after Plugin, replacement, or deferred?\n"
        "### 8.3 e34 Re-Scoring\n"
        "Which e34 opportunity spaces and institutional voids should be re-scored?\n"
        "### 8.4 Defuse Revival Determination\n"
        "Do the conditions for Defuse re-examination apply?\n"
        "### 8.5 Multi-Tenant Engineering Cost\n"
        "What engineering scope is required to multi-tenant these single-tenant assets?\n"
        "### 8.6 Patent-Scope Boundaries\n"
        "How do P1, P3, and P4 patent boundaries affect externalization?\n"
        "### 8.7 What Would Change the Answer\n"
        "What single piece of evidence would most reduce uncertainty about x402 pursuit?\n"
    )


def test_memo_request_detected_before_generic_strategy_terms():
    text = _memo()
    assert is_memo_investigation_request(text) is True
    assert chat_router.is_aiden_live_web_strategy_runtime_message(text) is True


def test_x402_memo_routes_to_memo_investigation_not_e114(tmp_path):
    route = route_chat_message_to_aiden_meeting_room(
        f"Aiden: {_memo()}",
        repo_root=_repo_root(),
        cieu_db=tmp_path / "memo_route.db",
        ystar_gov_root=Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        live_public_read_provider=FakeMemoPublicReadProvider(),
        allow_live_network=False,
    )
    assert route.route == "aiden_ceo_memo_investigation_runtime"
    assert route.protocol == "AidenMemoInvestigationRuntimeV1"
    assert "我的判断" in route.response_text
    assert "产品/机会形态" in route.response_text
    assert "E114_LIVE_WEB_CAPABILITY_UTILIZED_STRATEGY_RUN" not in route.response_text
    assert "x402" in route.response_text
    assert "Mission GO" in route.response_text


def test_memo_investigation_extracts_entities_queries_and_writes_cieu(tmp_path):
    result = run_aiden_memo_investigation_runtime(
        _memo(),
        cieu_db=tmp_path / "memo_runtime.db",
        repo_root=_repo_root(),
        ystar_gov_root=Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        public_read_provider=FakeMemoPublicReadProvider(),
        allow_live_network=False,
    )
    entities = {item["entity"] for item in result["memo_entities"]}
    assert {"x402", "Mission GO", "USDC", "wallet"}.issubset(entities)
    assert result["public_read_queries"]
    assert len(result["memo_open_questions"]) == 7
    assert result["public_read_evidence"]
    assert result["source_date_summary"]["dated_count"] == len(result["public_read_evidence"])
    assert result["repo_relation"]["matched_path_count"] >= 2
    with sqlite3.connect(tmp_path / "memo_runtime.db") as conn:
        rows = conn.execute("SELECT event_type, passed FROM cieu_events").fetchall()
    assert ("AIDEN_MEMO_INVESTIGATION_DECISION", 1) in rows


def test_generate_aiden_reply_text_for_memo_is_not_generic_first_cash(tmp_path):
    result = generate_aiden_reply_text(
        _memo(),
        cieu_db=tmp_path / "memo_turn.db",
        repo_root=_repo_root(),
        ystar_gov_root=Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        allow_live_network=False,
    )
    assert result["reply_backend"] == "aiden_ceo_memo_investigation_runtime"
    assert result["reply_protocol"] == "AidenMemoInvestigationRuntimeV1"
    assert "我的判断" in result["reply_text"]
    assert "支付还是不支付" in result["reply_text"]
    assert "逐项回答" in result["reply_text"]
    assert "战略判断" in result["reply_text"]
    assert "Selected first-cash path" not in result["reply_text"]
    assert "Construction bidding" not in result["reply_text"]
    assert "e34 重评分" in result["reply_text"]
    assert "Defuse revival" in result["reply_text"]
    assert "multi-tenant" in result["reply_text"]
    assert "Mining Plant" in result["reply_text"]


def test_query_builder_uses_memo_entities_not_fixed_market_domains():
    entities = extract_memo_entities(_memo())
    queries = build_memo_investigation_queries(_memo(), entities=entities, metadata={"title": "STRAT-002"})
    query_text = " ".join(row["query"] for row in queries).lower()
    assert "x402" in query_text
    assert "mission go" in query_text
    assert "construction bid" not in query_text
    assert "cpa review" not in query_text


def test_memo_public_read_provider_failure_is_visible_not_silent(tmp_path):
    result = run_aiden_memo_investigation_runtime(
        _memo(),
        cieu_db=tmp_path / "memo_provider_failure.db",
        repo_root=_repo_root(),
        ystar_gov_root=Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        public_read_provider=BrokenMemoPublicReadProvider(),
        allow_live_network=True,
    )
    analysis = result["strategic_analysis"]
    assert analysis["public_read_status"] == "live_public_read_attempted_but_provider_failed_or_returned_no_results"
    assert analysis["evidence_count"] == 0
    assert analysis["provider_failure_count"] >= 1
    assert "证据获取异常/无结果" in result["owner_facing_answer"]


def test_strat002_dossier_answers_owner_open_questions(tmp_path):
    result = run_aiden_memo_investigation_runtime(
        _memo(),
        cieu_db=tmp_path / "strat002_dossier.db",
        repo_root=_repo_root(),
        ystar_gov_root=Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        public_read_provider=FakeMemoPublicReadProvider(),
        allow_live_network=False,
    )
    dossier = result["strategic_analysis"]["strat002_deep_strategy_dossier"]
    question_matrix = result["strategic_analysis"]["memo_open_question_coverage"]
    assert dossier["applies"] is True
    assert len(question_matrix) == 7
    assert {row["source_heading_id"] for row in question_matrix} == {"8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7"}
    assert dossier["path_sequencing"]["decision"] == "parallel_research_not_replacement"
    assert any(row["item"] == "void_10_agent_to_agent_payment" for row in dossier["e34_rescore"])
    assert any("gov-mcp" in row["asset"] for row in dossier["asset_to_surface_matching"])
    assert dossier["defuse_revival"]["decision"] == "re_surface_as_capability_under_y_provider_identity_not_standalone_brand"
    assert dossier["multi_tenant_cost_scope"]
    assert "P3" in " ".join(dossier["patent_boundary"]["requires_counsel"])
    assert "Coinbase self-reported volume" in " ".join(dossier["do_not_do"])


def test_memo_open_question_gate_prevents_payment_boundary_from_becoming_the_topic(tmp_path):
    questions = extract_memo_open_questions(_memo())
    assert [row["question_title"] for row in questions][:2] == [
        "Asset-to-Surface Matching",
        "Path Sequencing vs Parallelism",
    ]
    result = run_aiden_memo_investigation_runtime(
        _memo(),
        cieu_db=tmp_path / "open_question_gate.db",
        repo_root=_repo_root(),
        ystar_gov_root=Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        public_read_provider=FakeMemoPublicReadProvider(),
        allow_live_network=False,
    )
    answer = result["owner_facing_answer"]
    assert "Mission GO/Y* 已经做出来的治理、证据、授权" in answer
    assert answer.index("这份 memo 明确问题的逐项回答") < answer.index("主要风险")
    assert "generic_low_price_gov_check_endpoint" in answer
    assert "parallel_research_not_replacement" in answer


def test_strat002_x402_advancement_request_generates_action_packet_not_next_step_loop(tmp_path):
    owner_text = "Aiden，我让你去对之前的备忘录做深度的战略分析的推进，还有拟定我们如何通过X402生态去实现赚钱。你为什么一直都没有行动啊？"
    assert is_memo_investigation_request(owner_text) is True
    assert is_memo_action_advancement_request(owner_text) is True
    result = run_aiden_memo_investigation_runtime(
        owner_text,
        cieu_db=tmp_path / "memo_action.db",
        repo_root=_repo_root(),
        ystar_gov_root=Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        public_read_provider=FakeMemoPublicReadProvider(),
        allow_live_network=False,
    )
    entities = {item["entity"] for item in result["memo_entities"]}
    packet = result["strategic_analysis"]["memo_action_advancement_packet"]
    answer = result["owner_facing_answer"]
    assert "x402" in entities
    assert result["memo_action_advancement_requested"] is True
    assert "不再把这件事停留在“建议下一步”" in answer
    assert packet["applies"] is True
    assert packet["packet_id"] == "MEMO_ACTION_ADVANCEMENT_PACKET_V1"
    assert "我现在直接推进" in answer
    assert "通用行动推进包" in answer
    assert "目标买方" in answer
    assert "买方能看懂的交付物" in answer
    assert "内部行动 backlog" in answer
    assert "Agent Payment Intent Governance Pack" in answer
    assert "MEMO_ACTION_ADVANCEMENT_PACKET_V1" in answer
    assert "建议下一步生成" not in answer


def test_strat002_question_classifier_keeps_multi_tenant_distinct_from_asset_surface(tmp_path):
    result = run_aiden_memo_investigation_runtime(
        _memo(),
        cieu_db=tmp_path / "strat002_question_classifier.db",
        repo_root=_repo_root(),
        ystar_gov_root=Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        public_read_provider=FakeMemoPublicReadProvider(),
        allow_live_network=False,
    )
    matrix = result["strategic_analysis"]["memo_open_question_coverage"]
    multi = next(row for row in matrix if row["source_heading_id"] == "8.5")
    assert multi["decision"] == "multi_tenanting_is_required_before_external_service_surface"
    assert "多租户安全" in multi["answer_summary"]


def test_generic_memo_action_advancement_is_not_x402_hardcoded(tmp_path):
    owner_text = "Aiden，请把这份备忘录的商业化计划推进成行动，不要只是继续分析。"
    assert is_memo_action_advancement_request(owner_text) is True
    result = run_aiden_memo_investigation_runtime(
        owner_text,
        cieu_db=tmp_path / "generic_memo_action.db",
        repo_root=_repo_root(),
        ystar_gov_root=Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov"),
        public_read_provider=FakeMemoPublicReadProvider(),
        allow_live_network=False,
    )
    packet = result["strategic_analysis"]["memo_action_advancement_packet"]
    assert packet["applies"] is True
    assert packet["packet_id"] == "MEMO_ACTION_ADVANCEMENT_PACKET_V1"
    assert packet["selected_wedge"]["name"] == "Memo-to-Action Readiness Pack"
    assert "x402" not in packet["selected_wedge"]["one_sentence"].lower()
    assert "支付" not in packet["ceo_decision"]

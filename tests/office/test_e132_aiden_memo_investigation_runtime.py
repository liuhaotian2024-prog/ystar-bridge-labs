from __future__ import annotations

import sqlite3
from pathlib import Path

import office.aiden_meeting_room.chat_router as chat_router
from office.aiden_meeting_room.chat_router import route_chat_message_to_aiden_meeting_room
from office.mission_command.e124_agent_native_company_messenger import generate_aiden_reply_text
from office.mission_command.e132_aiden_memo_investigation_runtime import (
    build_memo_investigation_queries,
    extract_memo_entities,
    is_memo_investigation_request,
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
        "It asks whether Y*Bridge Labs should integrate payment intent governance before any live payment execution."
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
    assert "没有把你的备忘录丢进" in route.response_text
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
    assert "没有把你的备忘录丢进" in result["reply_text"]
    assert "Selected first-cash path" not in result["reply_text"]
    assert "Construction bidding" not in result["reply_text"]


def test_query_builder_uses_memo_entities_not_fixed_market_domains():
    entities = extract_memo_entities(_memo())
    queries = build_memo_investigation_queries(_memo(), entities=entities, metadata={"title": "STRAT-002"})
    query_text = " ".join(row["query"] for row in queries).lower()
    assert "x402" in query_text
    assert "mission go" in query_text
    assert "construction bid" not in query_text
    assert "cpa review" not in query_text

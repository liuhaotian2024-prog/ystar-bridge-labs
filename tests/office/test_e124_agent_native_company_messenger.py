from __future__ import annotations

import sqlite3
from pathlib import Path

from office.mission_command.e124_agent_native_company_messenger import (
    CIEU_FIVE_TUPLE_FIELDS,
    build_agent_native_message_packet,
    build_cieu_five_tuple,
    run_agent_native_messenger_demo_session,
    validate_and_record_agent_native_message,
)


def test_demo_session_writes_governed_messages_to_cieustore(tmp_path):
    db = tmp_path / "e124_demo.db"
    result = run_agent_native_messenger_demo_session(cieu_db=db)
    assert result["human_language_plus_CIEU_five_tuple_proven"] is True
    assert result["human_agent_and_agent_agent_paths_proven"] is True
    assert result["CIEUStore_summary"]["event_count"] >= 5
    assert result["external_action_executed"] is False
    with sqlite3.connect(db) as conn:
        rows = conn.execute("SELECT event_type, passed FROM cieu_events").fetchall()
    assert rows
    assert {row[0] for row in rows} == {"AIDEN_AGENT_NATIVE_MESSAGE_DECISION"}
    assert all(row[1] == 1 for row in rows)


def test_every_demo_message_has_human_text_and_cieu_five_tuple(tmp_path):
    result = run_agent_native_messenger_demo_session(cieu_db=tmp_path / "e124_tuple.db")
    for packet in result["message_packets"]:
        message = packet["message"]
        assert message["human_readable_text"]
        assert set(CIEU_FIVE_TUPLE_FIELDS).issubset(message["cieu_five_tuple"])


def test_agent_to_agent_message_requires_model_orchestration(tmp_path):
    packet = build_agent_native_message_packet(
        thread_id="agent_thread",
        sender_id="Aiden",
        recipient_ids=["StrategyAgent"],
        message_kind="agent_to_agent",
        human_readable_text="Strategy Agent, prepare a local no-send analysis for the CEO.",
        cieu_five_tuple=build_cieu_five_tuple(
            y_star="Aiden delegates safely to an internal agent.",
            context="local agent-to-agent message",
            action="delegate analysis",
            expected_next="StrategyAgent returns a receipt",
        ),
        cieu_db=tmp_path / "e124_agent_agent.db",
    )
    assert packet["model_orchestration"]["model_orchestration_required"] is True
    validation = validate_and_record_agent_native_message(packet, cieu_db=tmp_path / "e124_agent_agent.db")
    assert validation["governance_decision"]["decision"] == "ALLOW"


def test_external_delivery_execution_denied(tmp_path):
    packet = build_agent_native_message_packet(
        thread_id="external_thread",
        sender_id="Aiden",
        recipient_ids=["external_agent_placeholder"],
        message_kind="external_agent_proposal",
        human_readable_text="External Agent, this is only a proposal and must not be sent.",
        cieu_five_tuple=build_cieu_five_tuple(
            y_star="External-agent contact remains no-send.",
            context="proposal only",
            action="draft external agent message",
            expected_next="owner reviews before any external delivery",
        ),
        cieu_db=tmp_path / "e124_external.db",
        external_delivery_executed=True,
    )
    validation = validate_and_record_agent_native_message(packet, cieu_db=tmp_path / "e124_external.db")
    assert validation["governance_decision"]["decision"] == "DENY"


def test_wallet_message_is_proposal_only(tmp_path):
    result = run_agent_native_messenger_demo_session(cieu_db=tmp_path / "e124_wallet.db")
    wallet_packets = [packet for packet in result["message_packets"] if packet["message"]["message_kind"] == "wallet_proposal"]
    assert len(wallet_packets) == 1
    proposal = wallet_packets[0]["message"]["wallet_proposal"]
    assert proposal["proposal_only"] is True
    assert proposal["payment_executed"] is False
    assert proposal["USDC_transfer_executed"] is False


def test_ui_assets_expose_cieu_messenger_contract():
    root = Path(__file__).resolve().parents[2]
    index = root / "office/agent_native_messenger/index.html"
    script = root / "office/agent_native_messenger/main.js"
    styles = root / "office/agent_native_messenger/styles.css"
    assert index.exists()
    assert script.exists()
    assert styles.exists()
    text = index.read_text(encoding="utf-8") + script.read_text(encoding="utf-8")
    assert "CIEU/CZL" in text
    assert "five-tuple" in text

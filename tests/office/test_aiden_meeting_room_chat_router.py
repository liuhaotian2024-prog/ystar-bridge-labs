import os
from pathlib import Path
from shutil import copyfile

from office.aiden_meeting_room.chat_router import (
    answer_aiden_prefixed_message,
    is_aiden_meeting_room_message,
    is_aiden_strategy_runtime_message,
    route_chat_message_to_aiden_meeting_room,
    strip_aiden_meeting_room_prefix,
)
from office.mission_command.e108_live_global_open_world_strategy_runtime import FixtureGlobalPublicReadProvider


REPO_ROOT = Path(__file__).resolve().parents[2]
YSTAR_ROOT = Path(os.environ.get("E106_TEST_YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))


def _isolated_brain_db(tmp_path: Path, name: str = "aiden_brain.db") -> Path:
    brain_db = tmp_path / name
    copyfile(REPO_ROOT / "aiden_brain.db", brain_db)
    return brain_db


def test_aiden_ascii_prefix_routes_to_governed_meeting_room(tmp_path):
    route = route_chat_message_to_aiden_meeting_room(
        "Aiden: 你现在自己是一个什么状态？",
        repo_root=REPO_ROOT,
        cieu_db=tmp_path / "aiden_router.db",
        brain_db=_isolated_brain_db(tmp_path),
    )

    assert route.route == "aiden_ceo_meeting_room"
    assert route.prefixed is True
    assert route.owner_message == "你现在自己是一个什么状态？"
    assert "repo-grounded CEO meeting layer" in route.response_text
    assert "Runtime governance:" in route.response_text


def test_aiden_strategy_question_auto_upgrades_to_deep_strategic_runtime(tmp_path):
    route = route_chat_message_to_aiden_meeting_room(
        "Aiden：你提出的给小会计事务所出那个类似于workflow的东西，你到底是怎么想的？",
        repo_root=REPO_ROOT,
        cieu_db=tmp_path / "aiden_strategy.db",
        brain_db=_isolated_brain_db(tmp_path, "aiden_strategy_brain.db"),
        ystar_gov_root=YSTAR_ROOT,
        live_public_read_provider=FixtureGlobalPublicReadProvider(),
        allow_live_network=False,
    )

    assert route.route == "aiden_ceo_deep_strategic_intelligence_runtime"
    assert route.protocol == "AidenDeepStrategicIntelligenceRuntimeV1"
    assert "CEO Strategy Runtime: E115_AIDEN_DEEP_STRATEGIC_INTELLIGENCE_RUNTIME" in route.response_text
    assert "Y-star-gov deep strategy decision: ALLOW" in route.response_text
    assert "Concrete product shape:" in route.response_text
    assert "Deep reasoning dimensions:" in route.response_text
    assert "Competitors and substitutes:" in route.response_text
    assert "Right to win / right to lose:" in route.response_text
    assert "Assumptions to test:" in route.response_text
    assert "No external action was executed" in route.response_text


def test_aiden_fullwidth_prefix_routes_to_governed_meeting_room(tmp_path):
    text = answer_aiden_prefixed_message(
        "Aiden：下一步你需要我批准什么？",
        repo_root=REPO_ROOT,
        cieu_db=tmp_path / "aiden_router_fullwidth.db",
        brain_db=_isolated_brain_db(tmp_path, "aiden_brain_fullwidth.db"),
    )

    assert "外部副作用" in text
    assert "Runtime governance:" in text


def test_non_prefixed_message_stays_with_codex_executor_default():
    route = route_chat_message_to_aiden_meeting_room("请你解释一下现在状态")

    assert route.route == "codex_executor_default"
    assert route.prefixed is False
    assert route.response_text is None


def test_empty_aiden_prefix_requires_revision():
    route = route_chat_message_to_aiden_meeting_room("Aiden:")

    assert route.route == "aiden_ceo_meeting_room"
    assert "Adaptive Governance Gate: REQUIRE_REVISION" in route.response_text
    assert "Correct path" in route.response_text


def test_prefix_helpers_accept_both_colon_forms():
    assert is_aiden_meeting_room_message("Aiden: hello")
    assert is_aiden_meeting_room_message("Aiden：hello")
    assert is_aiden_strategy_runtime_message("我们怎么最快赚钱？")
    assert strip_aiden_meeting_room_prefix("Aiden: hello") == "hello"
    assert strip_aiden_meeting_room_prefix("Aiden：hello") == "hello"

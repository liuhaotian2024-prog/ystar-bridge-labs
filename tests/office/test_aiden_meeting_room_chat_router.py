from pathlib import Path
from shutil import copyfile

from office.aiden_meeting_room.chat_router import (
    answer_aiden_prefixed_message,
    is_aiden_meeting_room_message,
    route_chat_message_to_aiden_meeting_room,
    strip_aiden_meeting_room_prefix,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


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
    assert strip_aiden_meeting_room_prefix("Aiden: hello") == "hello"
    assert strip_aiden_meeting_room_prefix("Aiden：hello") == "hello"

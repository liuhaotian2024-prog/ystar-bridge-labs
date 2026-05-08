#!/usr/bin/env python3.11
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from office.aiden_meeting_room.chat_router import (  # noqa: E402
    is_aiden_meeting_room_message,
    route_chat_message_to_aiden_meeting_room,
)
from office.aiden_meeting_room.governed_gateway import answer_owner_governed_text  # noqa: E402
from office.aiden_meeting_room.meeting_summary import build_summary  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ask Aiden CEO a repo-grounded question.")
    parser.add_argument("message", nargs="?", help="Owner message to Aiden")
    parser.add_argument("--summary", action="store_true", help="Print recent meeting summary")
    args = parser.parse_args()
    if args.summary:
        print(build_summary(REPO_ROOT))
        return 0
    if not args.message:
        parser.error("message is required unless --summary is used")
    if is_aiden_meeting_room_message(args.message):
        route = route_chat_message_to_aiden_meeting_room(args.message, repo_root=REPO_ROOT)
        print(route.response_text)
        return 0
    print(answer_owner_governed_text(args.message, repo_root=REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

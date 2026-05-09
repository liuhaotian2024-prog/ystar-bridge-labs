"""Local Aiden agent-native messenger server.

This is intentionally local-first. It serves the static messenger UI and exposes
only local governance endpoints. It does not send external messages, transfer
funds, or call providers.
"""

from __future__ import annotations

import http.server
import json
import os
import sys
import tempfile
from pathlib import Path


PORT = int(os.environ.get("AIDEN_MESSENGER_PORT", "8784"))
DIRECTORY = Path(__file__).resolve().parent
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))

if str(BRIDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(BRIDGE_ROOT))

from office.mission_command.e124_agent_native_company_messenger import (  # noqa: E402
    run_agent_native_messenger_demo_session,
    run_agent_native_messenger_turn,
)


def _json_response(handler: http.server.BaseHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[aiden-messenger] {fmt % args}\n")

    def do_GET(self) -> None:
        if self.path == "/api/demo-session":
            db_path = Path(tempfile.gettempdir()) / "e124_agent_native_messenger_server_demo.db"
            result = run_agent_native_messenger_demo_session(cieu_db=db_path, ystar_gov_root=Y_GOV_ROOT)
            _json_response(self, result)
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/messages":
            _json_response(self, {"error": "not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            _json_response(self, {"error": "invalid json"}, 400)
            return
        db_path = Path(tempfile.gettempdir()) / "e124_agent_native_messenger_live_local.db"
        human_text = str(data.get("text") or "").strip()
        if not human_text:
            _json_response(self, {"error": "empty text"}, 400)
            return
        turn = run_agent_native_messenger_turn(
            owner_text=human_text,
            cieu_db=db_path,
            ystar_gov_root=Y_GOV_ROOT,
            allow_live_network=False,
        )
        _json_response(self, turn)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main() -> None:
    with http.server.HTTPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"[Aiden Messenger] serving on http://127.0.0.1:{PORT}")
        print("[Aiden Messenger] local-only; external send and payment execution disabled")
        httpd.serve_forever()


if __name__ == "__main__":
    main()

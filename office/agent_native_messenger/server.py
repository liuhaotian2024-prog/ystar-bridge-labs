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
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timezone
from pathlib import Path


PORT = int(os.environ.get("AIDEN_MESSENGER_PORT", "8784"))
RUNTIME_TIMEOUT_SECONDS = float(os.environ.get("AIDEN_MESSENGER_RUNTIME_TIMEOUT_SECONDS", "120"))
ALLOW_LIVE_NETWORK_BY_DEFAULT = os.environ.get("AIDEN_MESSENGER_ALLOW_LIVE_NETWORK", "").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
DIRECTORY = Path(__file__).resolve().parent
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))

if str(BRIDGE_ROOT) not in sys.path:
    sys.path.insert(0, str(BRIDGE_ROOT))

from office.mission_command.e124_agent_native_company_messenger import (  # noqa: E402
    run_agent_native_messenger_demo_session,
    run_agent_native_messenger_turn,
)


RUNTIME_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="aiden-messenger-runtime")
LIVE_PUBLIC_READ_TRIGGERS = (
    "上网",
    "联网",
    "实时",
    "最新",
    "搜索",
    "查询",
    "查一下",
    "web",
    "internet",
    "browse",
    "public-read",
    "live public",
    "x402",
    "agentcore",
    "ap2",
    "mission go",
    "生态",
)


def _json_response(handler: http.server.BaseHTTPRequestHandler, payload: dict, status: int = 200) -> None:
    body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)


def _allow_live_network_for_message(human_text: str) -> bool:
    if ALLOW_LIVE_NETWORK_BY_DEFAULT:
        return True
    lower = human_text.lower()
    return any(trigger in lower for trigger in LIVE_PUBLIC_READ_TRIGGERS)


def _runtime_notice_payload(*, human_text: str, status: str, reason: str, detail: str, elapsed_seconds: float) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    notice_text = (
        "Aiden Messenger Runtime Notice: I received your message inside the governed local messenger, "
        f"but the Aiden behavior runtime returned {status}. {detail} "
        "The message was not lost; correct path: inspect the local runtime log, keep the CIEU/CZL record, "
        "and retry after the runtime is responsive."
    )
    return {
        "artifact_id": "e127_aiden_messenger_runtime_notice",
        "turn_status": status,
        "runtime_error": {
            "reason": reason,
            "detail": detail,
            "elapsed_seconds": round(elapsed_seconds, 3),
            "runtime_timeout_seconds": RUNTIME_TIMEOUT_SECONDS,
            "occurred_at": now,
        },
        "message_packets": [
            {
                "message": {
                    "message_id": f"e131_owner_preserved_{int(time.time() * 1000)}",
                    "sender_id": "owner",
                    "recipient_ids": ["Aiden"],
                    "message_kind": "human_to_agent_runtime_preserved",
                    "human_readable_text": human_text,
                    "cieu_five_tuple": {
                        "Y_star_t": "Owner input must remain visible even when Aiden runtime times out.",
                        "X_t": {
                            "source": "E131 messenger runtime watchdog owner-preservation path",
                            "runtime_status": status,
                            "local_only": True,
                        },
                        "U_t": {
                            "speech_act": "owner_message_to_aiden_preserved_after_runtime_failure",
                            "external_action_executed": False,
                        },
                        "Y_t_plus_1": "Aiden or owner can retry from the preserved message instead of losing context.",
                        "R_t_plus_1": reason,
                        "residual_status": "runtime_residual_open",
                    },
                }
            },
            {
                "message": {
                    "message_id": f"e127_runtime_notice_{int(time.time() * 1000)}",
                    "sender_id": "Aiden",
                    "recipient_ids": ["owner"],
                    "message_kind": "governance_notice",
                    "human_readable_text": notice_text,
                    "cieu_five_tuple": {
                        "Y_star_t": "Aiden meeting room must fail visibly instead of silently hanging.",
                        "X_t": {
                            "source": "E127 messenger runtime watchdog",
                            "owner_message_preview": human_text[:180],
                            "runtime_status": status,
                        },
                        "U_t": {
                            "speech_act": "runtime_failure_notice",
                            "external_action_executed": False,
                        },
                        "Y_t_plus_1": "Owner receives a governed notice and can retry after runtime diagnosis.",
                        "R_t_plus_1": reason,
                        "residual_status": "runtime_residual_open",
                    },
                }
            }
        ],
        "CIEUStore_summary": {
            "event_count": 0,
            "write_status": "not_written_by_watchdog_notice",
            "correct_path": "restart or inspect the Aiden runtime, then retry the governed turn",
        },
        "external_action_executed": False,
        "provider_action_executed": False,
        "payment_executed": False,
        "aiden_auto_reply_generated": False,
    }


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write(f"[aiden-messenger] {fmt % args}\n")

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def do_GET(self) -> None:
        if self.path == "/api/health":
            _json_response(
                self,
                {
                    "status": "ok",
                    "service": "aiden-agent-native-messenger",
                    "runtime_timeout_seconds": RUNTIME_TIMEOUT_SECONDS,
                    "allow_live_network_by_default": ALLOW_LIVE_NETWORK_BY_DEFAULT,
                    "local_only": True,
                    "external_send_enabled": False,
                    "payment_execution_enabled": False,
                },
            )
            return
        if self.path == "/api/demo-session":
            db_path = Path(tempfile.gettempdir()) / "e124_agent_native_messenger_server_demo.db"
            started = time.monotonic()
            try:
                result = run_agent_native_messenger_demo_session(cieu_db=db_path, ystar_gov_root=Y_GOV_ROOT)
            except Exception as exc:  # pragma: no cover - defensive server guard
                traceback.print_exc()
                result = _runtime_notice_payload(
                    human_text="demo-session",
                    status="runtime_error",
                    reason=exc.__class__.__name__,
                    detail="The demo session could not complete.",
                    elapsed_seconds=time.monotonic() - started,
                )
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
        allow_live_network = _allow_live_network_for_message(human_text)
        started = time.monotonic()
        future = RUNTIME_EXECUTOR.submit(
            run_agent_native_messenger_turn,
            owner_text=human_text,
            cieu_db=db_path,
            ystar_gov_root=Y_GOV_ROOT,
            allow_live_network=allow_live_network,
        )
        try:
            turn = future.result(timeout=RUNTIME_TIMEOUT_SECONDS)
        except TimeoutError:
            turn = _runtime_notice_payload(
                human_text=human_text,
                status="runtime_timeout",
                reason="Aiden runtime exceeded the local messenger watchdog timeout.",
                detail=(
                    "This usually means retrieval, brain activation, governance validation, or strategy routing is still "
                    "running too slowly for an interactive chat turn."
                ),
                elapsed_seconds=time.monotonic() - started,
            )
        except Exception as exc:  # pragma: no cover - defensive server guard
            traceback.print_exc()
            turn = _runtime_notice_payload(
                human_text=human_text,
                status="runtime_error",
                reason=exc.__class__.__name__,
                detail=str(exc) or "The Aiden runtime raised an exception.",
                elapsed_seconds=time.monotonic() - started,
            )
        turn.setdefault("server_runtime", {})
        turn["server_runtime"].update(
            {
                "elapsed_seconds": round(time.monotonic() - started, 3),
                "runtime_timeout_seconds": RUNTIME_TIMEOUT_SECONDS,
                "watchdog_enabled": True,
                "allow_live_network": allow_live_network,
                "live_public_read_triggered_by_owner_message": allow_live_network and not ALLOW_LIVE_NETWORK_BY_DEFAULT,
            }
        )
        _json_response(self, turn)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main() -> None:
    with http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"[Aiden Messenger] serving on http://127.0.0.1:{PORT}")
        print("[Aiden Messenger] local-only; external send and payment execution disabled")
        print(f"[Aiden Messenger] runtime watchdog timeout: {RUNTIME_TIMEOUT_SECONDS}s")
        print(f"[Aiden Messenger] live public-read default: {ALLOW_LIVE_NETWORK_BY_DEFAULT}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()

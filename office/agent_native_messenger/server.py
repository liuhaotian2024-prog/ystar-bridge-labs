"""Local Aiden agent-native messenger server.

This is intentionally local-first. It serves the static messenger UI and exposes
only local governance endpoints. It does not send external messages, transfer
funds, or call providers.
"""

from __future__ import annotations

import http.server
import json
import os
import re
import sqlite3
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
CONVERSATION_CONTEXT_PATH = Path(tempfile.gettempdir()) / "e124_aiden_messenger_conversation_context.json"
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
FOLLOWUP_EXECUTION_TRIGGERS = (
    "执行你说的下一步",
    "执行下一步",
    "开始执行",
    "开始自主",
    "现在就开始",
    "你说的下一步",
    "继续推进",
    "开始做",
    "推进下去",
    "do it",
    "execute",
    "continue",
)
OWNER_COORDINATION_TRIGGERS = (
    "怎么配合",
    "如何配合",
    "我需要做什么",
    "要求我怎么",
    "我完全不明白",
    "我不明白",
    "what do you need from me",
)
HIGH_SIGNAL_CONTEXT_TERMS = (
    "strat-002",
    "x402",
    "mission go",
    "agentcore",
    "ap2",
    "usdc",
    "e34",
    "defuse",
    "plugin path",
    "first-cash",
    "memo investigation",
    "备忘录",
    "赚钱战略",
    "赚钱路径",
    "变现路径",
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


def _load_conversation_context() -> dict:
    try:
        if not CONVERSATION_CONTEXT_PATH.exists():
            return {}
        return json.loads(CONVERSATION_CONTEXT_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_conversation_context(*, human_text: str, runtime_owner_text: str, turn: dict) -> None:
    reply_packet = turn.get("aiden_reply_packet") or {}
    reply_text = str((reply_packet.get("message") or {}).get("human_readable_text") or "")
    reply_runtime = turn.get("aiden_reply_runtime") or {}
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_human_text": human_text,
        "last_runtime_owner_text": runtime_owner_text,
        "last_reply_text": reply_text,
        "last_reply_backend": reply_runtime.get("reply_backend"),
        "last_reply_protocol": reply_runtime.get("reply_protocol"),
        "last_turn_status": turn.get("turn_status"),
    }
    try:
        CONVERSATION_CONTEXT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        # Context memory is helpful but must never block the messenger response.
        return


def _context_signal_score(*texts: str) -> int:
    joined = "\n".join(str(text or "").lower() for text in texts)
    score = sum(1 for term in HIGH_SIGNAL_CONTEXT_TERMS if term in joined)
    if len(joined) >= 500:
        score += 1
    return score


def _extract_human_readable_text_from_jsonish(raw: str) -> str:
    if not raw:
        return ""
    try:
        data = json.loads(raw)
        return str(data.get("human_readable_text") or "")
    except Exception:
        pass
    match = re.search(r'"human_readable_text"\s*:\s*"((?:\\.|[^"\\])*)"', raw)
    if not match:
        return ""
    try:
        return str(json.loads(f'"{match.group(1)}"'))
    except Exception:
        return match.group(1)


def _recover_conversation_context_from_cieustore(cieu_db: str | Path | None) -> dict:
    """Recover recent high-signal messenger context from CIEU after service restarts."""

    if not cieu_db:
        return {}
    db_path = Path(cieu_db)
    if not db_path.exists():
        return {}
    try:
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute(
                """
                SELECT agent_id, result_json, created_at
                FROM cieu_events
                WHERE event_type = 'AIDEN_AGENT_NATIVE_MESSAGE_DECISION'
                ORDER BY rowid DESC
                LIMIT 80
                """
            ).fetchall()
    except Exception:
        return {}

    recent: list[dict[str, str]] = []
    for agent_id, result_json, created_at in rows:
        text = _extract_human_readable_text_from_jsonish(str(result_json or ""))
        if text:
            recent.append({"agent_id": str(agent_id or ""), "text": text, "created_at": str(created_at or "")})
    if not recent:
        return {}

    owner_candidates = [
        item for item in recent if item["agent_id"] == "owner" and _context_signal_score(item["text"]) > 0
    ]
    aiden_candidates = [
        item
        for item in recent
        if item["agent_id"] == "Aiden"
        and (
            _context_signal_score(item["text"]) > 0
            or any(term in item["text"] for term in ("下一步", "no-send", "owner decision packet", "核验包"))
        )
    ]
    if not owner_candidates and not aiden_candidates:
        long_owner = [item for item in recent if item["agent_id"] == "owner" and len(item["text"]) >= 500]
        if long_owner:
            owner_candidates = long_owner
    if not owner_candidates and not aiden_candidates:
        return {}

    owner_text = owner_candidates[0]["text"] if owner_candidates else ""
    reply_text = aiden_candidates[0]["text"] if aiden_candidates else ""
    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "last_human_text": owner_text,
        "last_runtime_owner_text": owner_text,
        "last_reply_text": reply_text,
        "last_reply_backend": "recovered_from_cieustore",
        "last_reply_protocol": "AidenMessengerCIEUContextRecoveryV1",
        "last_turn_status": "recovered",
        "context_recovery_source": "cieustore_recent_aiden_messages",
    }


def _is_execution_followup(text: str) -> bool:
    lowered = (text or "").lower()
    return any(trigger in lowered for trigger in FOLLOWUP_EXECUTION_TRIGGERS)


def _is_owner_coordination_followup(text: str) -> bool:
    lowered = (text or "").lower()
    return any(trigger in lowered for trigger in OWNER_COORDINATION_TRIGGERS)


def _infer_prior_subject(prior_runtime_text: str, prior_reply: str) -> str:
    joined = f"{prior_runtime_text}\n{prior_reply}".lower()
    if any(token in joined for token in ("strat-002", "x402", "mission go", "agentcore", "ap2", "usdc")):
        return (
            "STRAT-002 / x402 / Mission GO memo investigation context. "
            "The owner is asking Aiden to advance the prior memo analysis about agent-to-agent payment/economic "
            "infrastructure, machine-buyer commercialization surfaces, Mission GO/Y* assets, CIEU/CZL receipts, "
            "Y-star-gov governance, gov-mcp no-send/no-payment boundaries, e34 opportunity re-scoring, Defuse "
            "resurfacing, multi-tenant cost, patent/IP boundaries, and owner-gated no-send decision packets."
        )
    if any(token in joined for token in ("strategy", "first-cash", "赚钱", "变现", "m-3")):
        return (
            "Prior Aiden strategy context. The owner is asking Aiden to continue the previous governed strategy "
            "work toward M-3 value production, not to restart from a generic meeting-room template."
        )
    return (
        "Prior Aiden conversation context. The owner is asking Aiden to continue the immediately previous "
        "commitment rather than treating this short follow-up as a standalone request."
    )


def _resolve_runtime_owner_text_from_context(human_text: str, *, cieu_db: str | Path | None = None) -> tuple[str, dict]:
    """Resolve short follow-ups to the previous runtime context while preserving visible owner text."""

    context = _load_conversation_context()
    recovered_context = _recover_conversation_context_from_cieustore(cieu_db)
    if recovered_context and _context_signal_score(
        recovered_context.get("last_runtime_owner_text", ""),
        recovered_context.get("last_reply_text", ""),
    ) > _context_signal_score(context.get("last_runtime_owner_text", ""), context.get("last_reply_text", "")):
        context = recovered_context
    prior_runtime_text = str(context.get("last_runtime_owner_text") or context.get("last_human_text") or "")
    prior_reply = str(context.get("last_reply_text") or "")
    execution_followup = _is_execution_followup(human_text)
    coordination_followup = _is_owner_coordination_followup(human_text)
    if not (execution_followup or coordination_followup) or not (prior_runtime_text or prior_reply):
        return human_text, {
            "applied": False,
            "reason": "not_a_contextual_followup_or_no_prior_context",
            "context_path": str(CONVERSATION_CONTEXT_PATH),
            "cieustore_context_recovered": bool(recovered_context),
        }

    prior_subject = _infer_prior_subject(prior_runtime_text, prior_reply)
    if coordination_followup:
        resolved = (
            f"{prior_subject}\n\n"
            "[OWNER FOLLOW-UP: coordination clarity]\n"
            f"Visible owner message: {human_text}\n\n"
            "Do not answer with a generic action-packet template. Explain in Chinese what Aiden can do autonomously "
            "inside the no-send/no-payment local boundary, what the owner does NOT need to do, and the exact points "
            "where owner must choose approve/reject/hold/revise. Continue the prior no-send memo/strategy packet "
            "instead of asking the owner to manually execute internal analysis."
        )
        reason = "owner_coordination_followup_resolved_to_prior_context"
    else:
        resolved = (
            f"{prior_subject}\n\n"
            "[OWNER FOLLOW-UP: execute the previous recommended next step]\n"
            f"Visible owner message: {human_text}\n\n"
            "Do not only recommend a next step. Execute the previous recommended_next_action as an internal, "
            "no-send owner decision packet / action advancement packet. Include the buyer or machine-buyer, "
            "problem, product shape, monetization hypothesis, evidence to verify, competitor/substitute map, "
            "right-to-win and right-to-lose, first no-send validation questions, internal engineering backlog, "
            "CZL residuals, and owner approval options. Do not execute external send, payment, wallet transfer, "
            "publication, customer contact, or core DB/brain production write."
        )
        reason = "execution_followup_resolved_to_prior_context"

    return resolved, {
        "applied": True,
        "reason": reason,
        "context_path": str(CONVERSATION_CONTEXT_PATH),
        "visible_owner_text": human_text,
        "prior_subject": prior_subject,
        "prior_reply_backend": context.get("last_reply_backend"),
        "prior_reply_protocol": context.get("last_reply_protocol"),
        "context_recovery_source": context.get("context_recovery_source", "conversation_context_file"),
    }


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
        runtime_owner_text, context_resolution = _resolve_runtime_owner_text_from_context(human_text, cieu_db=db_path)
        allow_live_network = _allow_live_network_for_message(runtime_owner_text)
        started = time.monotonic()
        future = RUNTIME_EXECUTOR.submit(
            run_agent_native_messenger_turn,
            owner_text=human_text,
            runtime_owner_text=runtime_owner_text,
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
                "context_resolution": context_resolution,
            }
        )
        _save_conversation_context(human_text=human_text, runtime_owner_text=runtime_owner_text, turn=turn)
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

#!/usr/bin/env python3
"""Local-only Web UI server for the real Y*Bridge Labs Office."""

from __future__ import annotations

import argparse
import json
import re
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from whiteboard_store import (
    create_whiteboard_message,
    create_work_item,
    load_approval_requests,
    load_threads,
    load_timeline,
    work_board,
    whiteboard_snapshot,
)
from work_cycle_engine import create_completion_report, route_latest_or_payload, run_team_work_cycle, run_work_cycle


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "l7_real_labs_office_web_ui"
STATE_PATH = OUT / "office_runtime_state.json"
TEMPLATE_PATH = OUT / "templates/index.html"

ALLOWED_ACTIONS = [
    "local packet creation",
    "internal analysis",
    "draft-only artifact generation",
    "approval request preparation",
]

FORBIDDEN_ACTIONS = [
    "external outreach",
    "email sending",
    "customer contact",
    "publication",
    "payment",
    "form submission",
    "account creation",
    "grant/RFP submission",
    "MCP/live behavior",
    "actual memory/brain/canonical/CIEU DB writeback",
]

APPROVAL_REQUIRED_FOR = [
    "outreach",
    "publication",
    "payment",
    "account creation",
    "form submission",
    "grant/RFP submission",
    "customer contact",
    "MCP/live behavior",
    "actual memory/brain/canonical/CIEU DB writeback",
]


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        raise FileNotFoundError("office_runtime_state.json missing; run build mode first")
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def json_response(handler: BaseHTTPRequestHandler, payload: Any, status: int = 200) -> None:
    body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def text_response(handler: BaseHTTPRequestHandler, body: str, content_type: str = "text/html; charset=utf-8") -> None:
    raw = body.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(raw)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(raw)


def error_response(handler: BaseHTTPRequestHandler, status: int, message: str) -> None:
    json_response(handler, {"ok": False, "error": message}, status)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_-]+", "_", value.strip())[:80].strip("_")
    return slug or "packet"


def timestamp() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


def packet_base(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "milestone_id": "L7.4R",
        "packet_type": packet_type,
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "allowed_actions": ALLOWED_ACTIONS,
        "forbidden_actions": FORBIDDEN_ACTIONS,
        "approval_required_for": APPROVAL_REQUIRED_FOR,
        "status": "queued",
        "external_side_effects": False,
        "core_writeback": False,
    }


def create_owner_message_packet(payload: dict[str, Any], out_dir: Path = OUT) -> dict[str, Any]:
    target = safe_slug(str(payload.get("target_agent", "aiden_ceo")))
    packet_id = f"owner_message_{timestamp()}_{target}"
    packet = {
        **packet_base("owner_message"),
        "packet_id": packet_id,
        "from": "owner",
        "target_agent": target,
        "message_text": str(payload.get("message_text", "")).strip(),
        "objective": str(payload.get("objective", "")).strip(),
        "urgency": str(payload.get("urgency", "normal")).strip() or "normal",
    }
    packet_dir = out_dir / "runtime_packets/owner_messages"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet_path = packet_dir / f"{packet_id}.json"
    packet_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "packet_path": str(packet_path.relative_to(ROOT)) if packet_path.is_relative_to(ROOT) else str(packet_path),
        "next_step": "route_to_aiden_or_selected_agent",
        "packet": packet,
    }


def create_team_task_packet(payload: dict[str, Any], out_dir: Path = OUT) -> dict[str, Any]:
    packet_id = f"team_task_{timestamp()}_{safe_slug(str(payload.get('task_title', 'team_task')))}"
    packet = {
        **packet_base("team_task"),
        "packet_id": packet_id,
        "from": "owner",
        "target": "team",
        "task_title": str(payload.get("task_title", "")).strip(),
        "task_description": str(payload.get("task_description", "")).strip(),
        "suggested_lead": "Aiden",
        "assigned_status": "pending_routing",
    }
    packet_dir = out_dir / "runtime_packets/team_tasks"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet_path = packet_dir / f"{packet_id}.json"
    packet_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "packet_path": str(packet_path.relative_to(ROOT)) if packet_path.is_relative_to(ROOT) else str(packet_path),
        "next_step": "route_to_aiden_for_team_delegation",
        "packet": packet,
    }


class OfficeHandler(BaseHTTPRequestHandler):
    server_version = "LabsOffice/0.1"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/":
                text_response(self, TEMPLATE_PATH.read_text(encoding="utf-8"))
            elif path == "/static/office.css":
                text_response(self, (OUT / "static/office.css").read_text(encoding="utf-8"), "text/css; charset=utf-8")
            elif path == "/static/office.js":
                text_response(self, (OUT / "static/office.js").read_text(encoding="utf-8"), "application/javascript; charset=utf-8")
            elif path == "/api/status":
                json_response(self, load_state())
            elif path == "/api/roster":
                state = load_state()
                json_response(self, {"agents": state.get("agents", []), "agent_count": state.get("agent_count", 0)})
            elif path.startswith("/api/agents/"):
                agent_id = safe_slug(unquote(path.removeprefix("/api/agents/")))
                state = load_state()
                for agent in state.get("agents", []):
                    if agent.get("agent_id") == agent_id:
                        json_response(self, agent)
                        return
                error_response(self, HTTPStatus.NOT_FOUND, f"unknown agent: {agent_id}")
            elif path == "/api/work_queue":
                json_response(self, {"work_queue": load_state().get("work_queue", [])})
            elif path == "/api/pending_approvals":
                state = load_state()
                json_response(
                    self,
                    {
                        "pending_approvals": state.get("pending_approvals", []),
                        "approval_requests": load_approval_requests(),
                    },
                )
            elif path == "/api/whiteboard":
                json_response(self, whiteboard_snapshot())
            elif path == "/api/whiteboard/threads":
                json_response(self, {"threads": load_threads()})
            elif path == "/api/work_board":
                json_response(self, {"work_board": work_board()})
            elif path == "/api/timeline":
                json_response(self, {"timeline": load_timeline()})
            else:
                error_response(self, HTTPStatus.NOT_FOUND, "not found")
        except Exception as exc:  # pragma: no cover - defensive server boundary
            error_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            error_response(self, HTTPStatus.BAD_REQUEST, "invalid json")
            return
        try:
            if parsed.path == "/api/message":
                if not str(payload.get("message_text", "")).strip():
                    error_response(self, HTTPStatus.BAD_REQUEST, "message_text is required")
                    return
                json_response(self, create_owner_message_packet(payload))
            elif parsed.path == "/api/team_task":
                if not str(payload.get("task_description", "")).strip():
                    error_response(self, HTTPStatus.BAD_REQUEST, "task_description is required")
                    return
                json_response(self, create_team_task_packet(payload))
            elif parsed.path == "/api/whiteboard/message":
                text = str(payload.get("text", "")).strip()
                if not text:
                    error_response(self, HTTPStatus.BAD_REQUEST, "text is required")
                    return
                message = create_whiteboard_message(
                    text=text,
                    target=str(payload.get("target", "whole_team")),
                    objective=str(payload.get("objective", "")),
                )
                json_response(self, {"ok": True, "message": message, "next_step": "route_with_aiden"})
            elif parsed.path == "/api/route":
                json_response(self, route_latest_or_payload(payload))
            elif parsed.path == "/api/work_items":
                title = str(payload.get("title", "Owner-created work item")).strip()
                description = str(payload.get("description", "")).strip()
                item = create_work_item(
                    title=title,
                    description=description or title,
                    source_message_id=payload.get("source_message_id"),
                    assigned_agents=payload.get("assigned_agents") or ["aiden_ceo"],
                )
                json_response(self, {"ok": True, "work_item": item})
            elif parsed.path == "/api/work_cycle":
                json_response(self, run_work_cycle(payload.get("work_item_id")))
            elif parsed.path == "/api/team_work_cycle":
                json_response(
                    self,
                    run_team_work_cycle(
                        max_work_items_per_cycle=int(payload.get("max_work_items_per_cycle", 3)),
                        max_agent_replies_per_cycle=int(payload.get("max_agent_replies_per_cycle", 8)),
                    ),
                )
            elif parsed.path == "/api/completion_report":
                json_response(self, create_completion_report(payload.get("work_item_id")))
            else:
                error_response(self, HTTPStatus.NOT_FOUND, "not found")
        except Exception as exc:  # pragma: no cover - defensive server boundary
            error_response(self, HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))


def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    if host != "127.0.0.1":
        raise SystemExit("Refusing non-local bind. Use 127.0.0.1.")
    server = ThreadingHTTPServer((host, port), OfficeHandler)
    print(f"Y*Bridge Labs Office: http://{host}:{port}")
    print("Local-only server. Press Ctrl-C to stop.")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve(args.host, args.port)


if __name__ == "__main__":
    main()

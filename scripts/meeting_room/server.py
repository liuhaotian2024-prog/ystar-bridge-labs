"""
Y* Bridge Labs Meeting Room — WebSocket Broker (Phase 0 MVP)

Serves the meeting room HTML and provides WebSocket endpoints for each member.
Phase 0: Mock pty output. Phase 1 (Ryan): Real Claude Code CLI pty proxy.
"""

import asyncio
import os
import time
from pathlib import Path
from typing import Dict, Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Y* Meeting Room", version="0.1.0")

# Directory containing this script
BASE_DIR = Path(__file__).parent

# Connected WebSocket clients per member
connections: Dict[str, Set[WebSocket]] = {}

# Valid member IDs
MEMBERS = [
    "board", "aiden", "ethan", "leo", "maya",
    "ryan", "jordan", "samantha", "sofia", "zara", "marco"
]


@app.get("/")
async def index():
    """Serve the meeting room HTML."""
    html_path = BASE_DIR / "index.html"
    return FileResponse(html_path, media_type="text/html")


@app.websocket("/ws/{member_id}")
async def websocket_endpoint(websocket: WebSocket, member_id: str):
    """
    WebSocket endpoint per member.

    Phase 0: Sends periodic mock heartbeat output.
    Phase 1 (Ryan): Will proxy real Claude Code CLI pty I/O.
    """
    if member_id not in MEMBERS:
        await websocket.close(code=4001, reason=f"Unknown member: {member_id}")
        return

    await websocket.accept()

    # Register connection
    if member_id not in connections:
        connections[member_id] = set()
    connections[member_id].add(websocket)

    try:
        # Phase 0: Send a heartbeat every 5 seconds to show liveness
        heartbeat_task = asyncio.create_task(_heartbeat(websocket, member_id))

        # Listen for incoming messages (Phase 1: will route to pty stdin)
        while True:
            data = await websocket.receive_text()
            # Phase 0: Echo back as acknowledgment
            await websocket.send_text(f"\x1b[90m[echo] {data}\x1b[0m\r\n")

    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        heartbeat_task.cancel()
        connections[member_id].discard(websocket)


async def _heartbeat(ws: WebSocket, member_id: str):
    """Send periodic heartbeat to show connection is alive."""
    role_colors = {
        "board": "33", "aiden": "34", "ethan": "35",
        "leo": "32", "maya": "32", "ryan": "32", "jordan": "32",
        "samantha": "38;5;205", "sofia": "33", "zara": "33", "marco": "33"
    }
    color = role_colors.get(member_id, "37")
    count = 0

    while True:
        await asyncio.sleep(5)
        count += 1
        timestamp = time.strftime("%H:%M:%S")
        msg = f"\x1b[{color}m[{member_id}]\x1b[0m \x1b[90m{timestamp} heartbeat #{count}\x1b[0m\r\n"
        try:
            await ws.send_text(msg)
        except Exception:
            break


async def broadcast(message: str, exclude_member: str = None):
    """Broadcast a message to all connected members (Phase 1: routing)."""
    for member_id, ws_set in connections.items():
        if member_id == exclude_member:
            continue
        for ws in ws_set.copy():
            try:
                await ws.send_text(message)
            except Exception:
                ws_set.discard(ws)


# Health check endpoint
@app.get("/health")
async def health():
    """Health check for the broker."""
    active = {m: len(ws) for m, ws in connections.items() if ws}
    return {
        "status": "ok",
        "phase": "0-mvp",
        "members_registered": len(MEMBERS),
        "active_connections": active,
        "uptime_seconds": int(time.time() - _start_time)
    }


_start_time = time.time()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )

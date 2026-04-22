# Y* Bridge Labs Meeting Room (Phase 0 MVP)

## Quick Start

```bash
bash scripts/meeting_room/start.sh
```

Then open http://localhost:8080 in your browser.

## What You See

- 10-seat meeting table layout (Board + 9 team members)
- Each seat has an xterm.js terminal showing live output
- Double-click any window to zoom into 1-on-1 focused view
- Press ESC to return to full meeting table view
- WebSocket heartbeats confirm connection liveness

## Architecture

```
Browser (localhost:8080)
    |-- WebSocket per member (/ws/<member_id>)
    v
FastAPI Broker (server.py)
    |-- Phase 0: mock heartbeat output
    |-- Phase 1: real Claude Code CLI pty proxy (Ryan)
    |-- Phase 1: Gemma classifier routing (Leo)
```

## Stop

Ctrl+C in the terminal running start.sh.

## Phase Roadmap

- Phase 0 (tonight): Visual layout + WebSocket skeleton + mock output
- Phase 1 (tomorrow): Real pty proxy + Gemma classifier + @mention routing
- Phase 2 (later): Multi-process spawn mgmt + session replay + voice input

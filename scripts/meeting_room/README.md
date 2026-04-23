# Y* Bridge Labs — Meeting Room (3D Scaffold)

Three.js-based 3D meeting room for Y*gov agent visualization.

## Quick Start

```bash
cd scripts/meeting_room
python3 server.py
# Open http://127.0.0.1:8765 in browser
```

## What You See (Scaffold Phase)

- Warm wood-tone floor plane
- Terracotta back wall (exposed-brick texture placeholder)
- Slowly rotating blue cube (avatar placeholder)
- Directional + ambient + fill lighting with shadows

## Architecture

**Scaffold (current):** Pure HTML + vanilla ES module JS.
Three.js loaded via CDN importmap (r164). No build step.

**Phase 2 (planned):**
- Svelte 5 component wrapper for UI panels
- RPM/VRM avatar import replacing the cube placeholder
- Real exposed-brick PBR texture on wall
- OrbitControls for camera interaction
- gov_mcp SSE proxy at `/api/gov` for live governance events
- Multi-agent seating grid with name tags

## Files

| File | Purpose |
|------|---------|
| `public/index.html` | Entry point, loads Three.js via importmap |
| `public/main.js` | Scene setup, camera, lights, floor, wall, cube, animation loop |
| `server.py` | Static file server on port 8765 |

## Dependencies

- Python 3.8+ (stdlib only, no pip install)
- Modern browser with ES module + importmap support

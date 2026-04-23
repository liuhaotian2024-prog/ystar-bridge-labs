---
cto_receipt:
  Y_star: "Deliver tech catalog + single-stack recommendation for 3D office with digital human agents"
  Xt: "Prior Phase 0 = vanilla HTML/xterm.js grid, no 3D, no avatars, input disabled"
  U: "Read prior code, diagnose failures, catalog 2026 stacks, pick one, write build plan"
  Yt_plus_1: "This memo delivered; ready for Phase 1 engineering dispatch"
  Rt_plus_1: 0
  artifact: "reports/cto/office_project_tech_catalog_20260423.md"
  verdict: "Three.js + Ready Player Me VRM + ElevenLabs WS + Svelte + gov_mcp SSE relay"
---

# 3D Office Environment -- CTO Tech Catalog & Stack Recommendation

## A. Prior Attempt: What Existed and What Broke

**Stack**: Vanilla HTML + CSS Grid + xterm.js terminals + FastAPI WebSocket broker (`scripts/meeting_room/`). No framework, no build step, no 3D.

**3 concrete failure modes**:

1. **Ugly**: CSS-only dark grid of monospace terminal boxes. No spatial depth, no lighting, no perspective. The "meeting table" was a `<div>` with `linear-gradient` and a Unicode black square emoji as decoration. Looks like a tmux dashboard, not an office.

2. **Cannot type**: `disableStdin: true` was hardcoded in every xterm.js Terminal instance (line 254). The WebSocket client-side was never connected -- no `new WebSocket()` call exists in `index.html`. The frontend renders static welcome strings and never opens a socket. Even the server's echo handler has no route back to the DOM.

3. **Primitive**: No avatar representation at all -- agents are color-coded text labels. No spatial metaphor beyond grid placement. The server sends 5-second heartbeat ANSI strings that never reach the browser because WebSocket was never wired client-side.

## B. Modern Stack Options (2026 Catalog)

### 1. 3D Rendering Runtime (Browser)

| Option | Bundle | Avatar Support | Trade-off |
|--------|--------|---------------|-----------|
| **Three.js** | ~150KB gzip | Excellent VRM/glTF loader ecosystem | Mature, largest community, manual scene graph |
| **Babylon.js** | ~300KB gzip | Built-in avatar system | Heavier, better physics (unneeded here) |
| **Unity WebGL** | 5-20MB | Full engine | Massive bundle, long load, overkill for office scene |

### 2. Digital Human Avatar Tech

| Option | Realism | Integration | Cost |
|--------|---------|-------------|------|
| **Ready Player Me (VRM/glTF)** | Medium-high, stylized-to-realistic | Free SDK, export VRM with 52 ARKit blendshapes | Free tier sufficient |
| **HeyGen Interactive** | Photo-realistic | Streaming API, we own keys | ~$0.10/min streaming, latency 2-4s |
| **D-ID Live** | Photo-realistic | Similar streaming API | ~$0.08/min, comparable latency |
| **Custom glTF + blendshapes** | Variable | Full control, no vendor lock | High LOC cost for rigging |

### 3. Voice Interaction (STT + TTS)

| Option | Latency | Cost/1K min | Notes |
|--------|---------|-------------|-------|
| **ElevenLabs WebSocket** | 200-400ms | ~$3 | Best voice quality, WS streaming, viseme events for lip sync |
| **OpenAI Realtime API** | 300-500ms | ~$6 | Integrated LLM+voice, but we route through Claude |
| **Web Speech API** | 50ms | Free | Browser-native, robotic TTS, no viseme data |
| **Whisper.cpp WebGPU** | 500ms+ | Free | STT only, no TTS, experimental |

### 4. Orchestration (Frontend to Backend to Agent)

| Option | Complexity | Fit |
|--------|-----------|-----|
| **SSE relay via gov_mcp (localhost:7922)** | Low -- extend existing | Natural fit, CIEU logging built in |
| **Custom WebSocket relay** | Medium | Redundant with gov_mcp |
| **Direct WebSocket to Claude** | N/A | Not possible, Claude Code is CLI |

### 5. Frontend Framework

| Option | Bundle | Perf | DX |
|--------|--------|------|-----|
| **Svelte 5** | 3KB runtime | Fastest reactivity, compiled | Simple, small team friendly |
| **React 19** | 40KB | Good | Largest ecosystem, heavier |
| **Solid.js** | 7KB | Excellent | Smaller community |

## C. CTO Single-Stack Recommendation

**Three.js + Ready Player Me VRM + ElevenLabs WebSocket + Svelte 5 + gov_mcp SSE relay.**

- **Three.js**: 150KB, best VRM loader ecosystem (`@pixiv/three-vrm`), proven for avatar scenes. Babylon is heavier with physics we do not need. Unity WebGL bundle size is disqualifying for a localhost tool.
- **Ready Player Me VRM**: Free, exports 52-blendshape VRM avatars that Three.js loads natively. Phase 1 uses static poses; Phase 2 activates lip-sync via ElevenLabs viseme stream. HeyGen reserved for pre-recorded video content (existing workflow), not real-time office -- its 2-4s streaming latency breaks conversational feel.
- **ElevenLabs WebSocket**: 200ms latency TTS with per-phoneme viseme events that drive VRM blendshapes directly. Pairs with browser-native `webkitSpeechRecognition` for STT (free, adequate). Cost at 100 sessions/month ~30 min voice each: ~$9/month.
- **Svelte 5**: 3KB compiled runtime. For a 3D scene where the framework manages UI chrome (chat panel, agent list, settings) while Three.js owns the canvas, Svelte's compiled output and lack of virtual DOM means zero framework overhead competing with the render loop.
- **gov_mcp SSE relay**: Extend the existing `localhost:7922` SSE endpoint with a `/office/chat` route. Chat messages become CIEU events automatically. No new server process -- the broker is gov_mcp itself.

## D. Build-vs-Buy Cost Table

| Layer | LOC Cost | External $/month (100 sessions) | tool_uses to MVP |
|-------|----------|--------------------------------|------------------|
| Three.js scene + office model | Medium (~800 LOC) | $0 | ~80 |
| RPM avatar creation (10 agents) | Low (manual RPM web UI + export) | $0 | ~10 |
| VRM loader + idle animation | Low (~200 LOC) | $0 | ~30 |
| ElevenLabs voice (Phase 2) | Medium (~400 LOC) | ~$9 | ~60 |
| Svelte UI shell | Low (~500 LOC) | $0 | ~40 |
| gov_mcp /office/chat route | Low (~150 LOC) | $0 | ~20 |
| **Total** | **~2050 LOC** | **~$9/month** | **~240** |

## E. Build Phase Plan

### Phase 1 -- MVP (est. ~120 tool_uses)

- Static office background (HDRI or simple Three.js room with desk geometry)
- 3 digital humans: Aiden (CEO), Ethan (CTO), Sofia (CMO) -- whichever agents already have RPM-compatible profile photos, create VRM avatars via RPM web tool
- Text-based conversation panel (Svelte sidebar) routed through gov_mcp SSE
- Each chat message emits a CIEU event (`OFFICE_CHAT_SEND`, `OFFICE_CHAT_RECV`)
- VRM avatars play idle animation; speaking agent gets a head-nod blend
- Deliverable: `localhost:8080` serves Svelte+Three.js app, Board can type to any agent

### Phase 2 -- Polish (est. ~180 tool_uses)

- Full 3D office scene (conference table, chairs, ambient lighting, window backdrop)
- All 10 agents with VRM avatars + name plates
- ElevenLabs TTS with viseme-driven lip sync on speaking agent
- Browser STT via `webkitSpeechRecognition` for Board voice input
- Camera transitions: click agent to orbit-focus, click table to pull back
- CIEU audit trail for all voice/text interactions

## F. Scope Call -- What NOT to Build

1. **Do not build a custom 3D engine or custom avatar rigging pipeline.** Three.js + RPM VRM gives us 90% quality at 10% effort. Bespoke mesh/skeleton work is a months-long rabbit hole for marginal visual gain.

2. **Do not invent a new orchestration layer.** gov_mcp already exists on localhost:7922 with SSE and CIEU integration. Adding a second broker (like the prior FastAPI `server.py`) creates split-brain routing. Extend gov_mcp, do not fork it.

3. **Do not ship to external users before internal dogfood.** The office is an internal Board tool first. No auth, no multi-tenant, no deployment pipeline. Ship localhost-only, iterate on Board feedback for 2+ sessions, then evaluate whether to expose externally.

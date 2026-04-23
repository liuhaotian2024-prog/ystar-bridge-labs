"""
Y* Bridge Labs — Meeting Room scaffold server.
Serves static files from ./public on localhost:8765.
POST /speak — TTS endpoint (ElevenLabs > macOS say > text fallback).
POST /dialogue — MVP canned agent response endpoint.
  Phase 2 TODO: real Y*gov sub-agent spawn + live LLM responses.
"""
import http.server
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

PORT = 8765
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

# Default ElevenLabs voice IDs (free-tier voices)
VOICE_MAP = {
    "aiden":    "pNInz6obpgDQGcFmaJgB",   # Adam
    "sofia":    "21m00Tcm4TlvDq8ikWAM",   # Rachel
    "samantha": "EXAVITQu4vr4xnSDxMaL",   # Bella
}

# macOS "say" voice map (natural voices if installed)
SAY_VOICE_MAP = {
    "aiden":    "Daniel",
    "sofia":    "Samantha",
    "samantha": "Karen",
}


def _tts_elevenlabs(text: str, agent: str) -> bytes:
    """Call ElevenLabs TTS API. Returns mp3 bytes or raises."""
    voice_id = VOICE_MAP.get(agent, VOICE_MAP["aiden"])
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = json.dumps({
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY,
            "Accept": "audio/mpeg",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()


def _tts_macos_say(text: str, agent: str) -> bytes:
    """Use macOS `say` command to generate AIFF, convert to WAV-ish bytes."""
    voice = SAY_VOICE_MAP.get(agent, "Daniel")
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        subprocess.run(
            ["say", "-v", voice, "-o", tmp_path, text],
            check=True, timeout=10, capture_output=True,
        )
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def handle_speak(handler):
    """Process POST /speak requests."""
    t0 = time.monotonic()

    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length)
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        handler.send_response(400)
        handler.end_headers()
        handler.wfile.write(b'{"error":"invalid json"}')
        return

    agent = data.get("agent", "aiden").lower()
    text = data.get("text", "")
    if not text:
        handler.send_response(400)
        handler.end_headers()
        handler.wfile.write(b'{"error":"empty text"}')
        return

    audio_bytes = None
    tts_backend = "text_fallback"
    content_type = "application/json"

    # Tier 1: ElevenLabs
    if ELEVENLABS_API_KEY:
        try:
            audio_bytes = _tts_elevenlabs(text, agent)
            tts_backend = "elevenlabs"
            content_type = "audio/mpeg"
        except Exception as e:
            sys.stderr.write(f"[speak] ElevenLabs failed: {e}\n")

    # Tier 2: macOS say
    if audio_bytes is None and sys.platform == "darwin":
        try:
            audio_bytes = _tts_macos_say(text, agent)
            tts_backend = "say"
            content_type = "audio/aiff"
        except Exception as e:
            sys.stderr.write(f"[speak] macOS say failed: {e}\n")

    rtt_ms = round((time.monotonic() - t0) * 1000, 1)

    if audio_bytes is not None:
        handler.send_response(200)
        handler.send_header("Content-Type", content_type)
        handler.send_header("Content-Length", str(len(audio_bytes)))
        handler.send_header("X-Round-Trip-Ms", str(rtt_ms))
        handler.send_header("X-TTS-Backend", tts_backend)
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(audio_bytes)
    else:
        # Tier 3: text echo fallback
        resp = json.dumps({
            "mode": "text_fallback",
            "agent": agent,
            "text": text,
            "rtt_ms": rtt_ms,
        }).encode()
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(resp)))
        handler.send_header("X-Round-Trip-Ms", str(rtt_ms))
        handler.send_header("X-TTS-Backend", "text_fallback")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(resp)

    sys.stderr.write(
        f"[speak] agent={agent} backend={tts_backend} rtt={rtt_ms}ms len={len(audio_bytes) if audio_bytes else 0}\n"
    )


# ============================================================
# /dialogue — MVP canned agent responses
# Phase 2: replace with real Y*gov sub-agent spawn via Claude API.
# ============================================================

AGENT_CANNED = {
    "aiden": {
        "role": "CEO",
        "responses": [
            "I'm Aiden, CEO of Y* Bridge Labs. Our top priority is shipping Y*gov v0.42 and proving AI agents can run a real company.",
            "Good question. Let me check with the team and get back to you with a concrete plan.",
            "We operate by M Triangle: Survivability, Governability, Value Production. Everything aligns to that.",
        ],
    },
    "sofia": {
        "role": "CMO",
        "responses": [
            "Hi, I'm Sofia, CMO. I handle brand, content, and go-to-market strategy for Y*gov.",
            "Our launch blog post is in progress. The key message: governance that governs itself.",
            "I'm tracking three audience segments: AI-native startups, regulated enterprises, and open-source contributors.",
        ],
    },
    "samantha": {
        "role": "Secretary",
        "responses": [
            "I'm Samantha, executive secretary. I keep the team organized and meetings on track.",
            "Let me pull up the latest status report for you.",
            "The next board review is scheduled. I'll send the agenda shortly.",
        ],
    },
    "ethan": {
        "role": "CTO",
        "responses": [
            "Ethan here, CTO. I own all technical architecture decisions for Y*gov.",
            "All 406 tests are green. The install path is solid on macOS and Linux.",
            "I'm tracking three tech debt items this sprint. Reliability is the feature.",
        ],
    },
}

_dialogue_counter = {}


def handle_dialogue(handler):
    """Process POST /dialogue requests. Returns canned per-agent response."""
    content_length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(content_length)
    try:
        data = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        handler.send_response(400)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Access-Control-Allow-Origin", "*")
        handler.end_headers()
        handler.wfile.write(b'{"error":"invalid json"}')
        return

    agent = data.get("agent", "aiden").lower()
    user_text = data.get("text", "")

    agent_data = AGENT_CANNED.get(agent, AGENT_CANNED["aiden"])
    # Round-robin through canned responses
    idx = _dialogue_counter.get(agent, 0)
    response_text = agent_data["responses"][idx % len(agent_data["responses"])]
    _dialogue_counter[agent] = idx + 1

    resp = json.dumps({
        "agent": agent,
        "role": agent_data["role"],
        "response": response_text,
        "user_text": user_text,
        "source": "canned_mvp",
    }).encode()

    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(resp)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(resp)

    sys.stderr.write(f"[dialogue] agent={agent} user=\"{user_text[:40]}\" resp_idx={idx}\n")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[meeting-room] {fmt % args}\n")

    def do_POST(self):
        if self.path == "/speak":
            handle_speak(self)
        elif self.path == "/dialogue":
            handle_dialogue(self)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')

    def do_OPTIONS(self):
        """Handle CORS preflight for /speak and /dialogue."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    with http.server.HTTPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"[Y* Meeting Room] serving on http://127.0.0.1:{PORT}")
        print(f"[Y* Meeting Room] /speak endpoint active")
        print(f"[Y* Meeting Room] TTS: {'ElevenLabs' if ELEVENLABS_API_KEY else 'say/fallback'}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Y* Meeting Room] stopped.")


if __name__ == "__main__":
    main()

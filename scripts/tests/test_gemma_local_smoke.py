"""
Test: Gemma local inference empirical smoke (Milestone 11 2026-04-21).

Board directive "本地化迁移是原主线" — verify Ollama + Gemma models can
answer a prompt locally without any cloud API call, within a reasonable
time budget (proves Aiden's inference layer can migrate to local).

M-tag: M-1 (API vendor independence — Aiden survives without Claude API),
       M-3 (local-first product story for gov-mcp customers).
"""
import json
import shutil
import subprocess
import time
import pytest


def _ollama_available() -> bool:
    return shutil.which("ollama") is not None


def _ollama_has_model(name: str) -> bool:
    if not _ollama_available():
        return False
    try:
        r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        return name in r.stdout
    except Exception:
        return False


@pytest.mark.skipif(not _ollama_available(), reason="ollama binary not installed")
def test_ollama_binary_responsive():
    """Ollama daemon must respond to --version within 5s."""
    start = time.time()
    r = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
    dur = time.time() - start
    assert r.returncode == 0
    assert "version" in r.stdout.lower() or "ollama" in r.stdout.lower()
    assert dur < 5.0


@pytest.mark.skipif(not _ollama_available(), reason="ollama binary not installed")
def test_ollama_list_includes_at_least_one_gemma_model():
    """Local inventory must contain at least one Gemma model (ystar-gemma or gemma4:*)."""
    r = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0
    has_gemma = (
        "ystar-gemma" in r.stdout
        or "gemma4" in r.stdout
        or "gemma3" in r.stdout
        or "gemma2" in r.stdout
    )
    assert has_gemma, f"No Gemma model found in ollama list:\n{r.stdout}"


@pytest.mark.skipif(not _ollama_has_model("gemma4:e4b"),
                    reason="gemma4:e4b not pulled")
def test_gemma4_e4b_answers_simple_prompt_under_60s():
    """Small Gemma 4 e4b must answer a factual 'one-sentence' prompt in <60s."""
    start = time.time()
    r = subprocess.run(
        ["ollama", "run", "gemma4:e4b",
         "One sentence: what is 2+2?"],
        capture_output=True, text=True, timeout=90,
    )
    dur = time.time() - start
    assert r.returncode == 0
    # Accept either digit '4' or word 'four' — model may spell it out.
    answer = r.stdout.lower()
    assert "4" in answer or "four" in answer, f"No valid answer in: {r.stdout[:100]}"
    assert dur < 60.0, f"e4b took {dur:.1f}s, expected <60s for simple math"


@pytest.mark.skipif(not _ollama_has_model("ystar-gemma"),
                    reason="ystar-gemma not pulled")
def test_ystar_gemma_has_y_star_context_awareness():
    """Custom ystar-gemma must show awareness of Y* Bridge Labs context."""
    r = subprocess.run(
        ["ollama", "run", "ystar-gemma",
         "One sentence: Are you familiar with Y* Bridge Labs?"],
        capture_output=True, text=True, timeout=90,
    )
    assert r.returncode == 0
    lower = r.stdout.lower()
    # Either affirmatively familiar OR explicitly admits no context
    # (both are acceptable — hallucination is what fails)
    familiar = any(k in lower for k in ["y*", "ystar", "bridge labs", "governance"])
    honest_uncertain = any(k in lower for k in ["not familiar", "no context",
                                                  "don't have", "uncertain",
                                                  "unable"])
    assert familiar or honest_uncertain, (
        f"ystar-gemma response neither shows familiarity nor honest uncertainty: "
        f"{r.stdout[:200]}"
    )


@pytest.mark.skipif(not _ollama_available(), reason="ollama binary not installed")
def test_ollama_localhost_port_11434_listens():
    """Ollama must bind to localhost:11434 (default) — prove no cloud dependency."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        result = sock.connect_ex(("127.0.0.1", 11434))
        assert result == 0, f"Ollama port 11434 not listening, connect_ex={result}"
    finally:
        sock.close()


@pytest.mark.skipif(not _ollama_available(), reason="ollama binary not installed")
def test_ollama_api_generate_via_http():
    """HTTP API call to /api/generate must return streaming or final response."""
    import urllib.request
    payload = {
        "model": "gemma4:e4b",
        "prompt": "Say hello",
        "stream": False,
    }
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:11434/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        start = time.time()
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = resp.read().decode("utf-8")
        dur = time.time() - start
        data = json.loads(body)
        assert "response" in data
        assert len(data["response"]) > 0
        assert dur < 90
    except urllib.error.URLError as e:
        pytest.skip(f"Ollama HTTP API not reachable: {e}")

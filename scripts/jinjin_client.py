"""
Jinjin Direct Client — Real-time communication with MiniMax-M2.7 on OpenClaw Gateway

This replaces the old Telegram-based k9.py with direct OpenClaw CLI integration.

Methods:
1. ask(message) — send message, get response (synchronous, 12s average)
2. ask_async(message) — async version
3. session_send(message, session_id) — target specific conversation

Architecture:
- Uses `openclaw agent` CLI (sub-process)
- Jinjin = main agent on OpenClaw gateway (127.0.0.1:18789)
- Model: MiniMax-M2.7
- Average latency: 12 seconds (100x faster than Telegram bot)

Usage:
    from scripts.jinjin_client import JinjinClient

    jj = JinjinClient()
    response = jj.ask("分析最新的CIEU日志")
    print(response)
"""

import json
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class JinjinClient:
    """Direct OpenClaw gateway client for Jinjin (MiniMax-M2.7 agent)"""

    def __init__(self, agent_id: str = "main", timeout: int = 120):
        """
        Initialize Jinjin client.

        Args:
            agent_id: OpenClaw agent ID (default: "main")
            timeout: Command timeout in seconds (default: 120)
        """
        self.agent_id = agent_id
        self.timeout = timeout
        self._check_gateway()

    def _check_gateway(self):
        """Verify OpenClaw gateway is running"""
        try:
            result = subprocess.run(
                ["openclaw", "daemon", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if "running" not in result.stdout.lower():
                raise RuntimeError("OpenClaw gateway is not running. Run: openclaw daemon start")
        except subprocess.TimeoutExpired:
            raise RuntimeError("OpenClaw daemon status check timed out")
        except FileNotFoundError:
            raise RuntimeError("openclaw CLI not found. Is OpenClaw installed?")

    def ask(self, message: str, session_id: Optional[str] = None) -> dict:
        """
        Send a message to Jinjin and get response.

        Args:
            message: Message text to send
            session_id: Optional session ID to continue conversation

        Returns:
            dict with keys:
                - text: response text
                - duration_ms: response time in milliseconds
                - model: model used
                - usage: token usage stats
                - run_id: OpenClaw run ID

        Raises:
            RuntimeError: If command fails
            subprocess.TimeoutExpired: If command times out
        """
        cmd = [
            "openclaw", "agent",
            "--agent", self.agent_id,
            "--message", message,
            "--json"
        ]

        if session_id:
            cmd.extend(["--session-id", session_id])

        logger.info(f"Sending to Jinjin: {message[:100]}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=True
            )

            data = json.loads(result.stdout)

            if data.get("status") != "ok":
                raise RuntimeError(f"OpenClaw command failed: {data}")

            payloads = data["result"]["payloads"]
            text = payloads[0]["text"] if payloads else ""

            meta = data["result"]["meta"]
            agent_meta = meta.get("agentMeta", {})

            response = {
                "text": text,
                "duration_ms": meta.get("durationMs"),
                "model": agent_meta.get("model"),
                "usage": agent_meta.get("usage"),
                "run_id": data.get("runId"),
                "session_id": agent_meta.get("sessionId"),
                "raw": data
            }

            logger.info(f"Got response from Jinjin: {len(text)} chars, {response['duration_ms']}ms")
            return response

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"openclaw command failed: {e.stderr}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse openclaw JSON output: {result.stdout}") from e

    def chat(self, message: str, session_id: Optional[str] = None) -> str:
        """
        Simplified interface: send message, get text response only.

        Args:
            message: Message to send
            session_id: Optional session ID

        Returns:
            Response text only
        """
        response = self.ask(message, session_id)
        return response["text"]

    def health_check(self) -> bool:
        """
        Quick health check: can we reach Jinjin?

        Returns:
            True if gateway responds within 30s
        """
        try:
            response = self.ask("ping", None)
            return response["text"] is not None
        except Exception as e:
            logger.error(f"Jinjin health check failed: {e}")
            return False


# Convenience functions for direct import
def ask_jinjin(message: str) -> str:
    """Quick one-shot: ask Jinjin, get text response"""
    client = JinjinClient()
    return client.chat(message)


def ask_jinjin_full(message: str) -> dict:
    """Quick one-shot: ask Jinjin, get full response dict"""
    client = JinjinClient()
    return client.ask(message)


if __name__ == "__main__":
    # CLI mode for testing
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python scripts/jinjin_client.py 'your message here'")
        print("Example: python scripts/jinjin_client.py '最新的CIEU日志有什么？'")
        sys.exit(1)

    message = " ".join(sys.argv[1:])

    print(f">>> Asking Jinjin: {message}")
    print()

    client = JinjinClient()
    response = client.ask(message)

    print(response["text"])
    print()
    print(f"[{response['model']}, {response['duration_ms']}ms, session: {response['session_id'][:8]}...]")

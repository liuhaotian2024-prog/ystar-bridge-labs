#!/usr/bin/env python3
"""Publish a message to Y* Bridge Labs Telegram channel.

Usage:
    python3 scripts/publish_telegram.py "Your message here"

Requires: TELEGRAM_BOT_TOKEN environment variable
Channel: @YstarBridgeLabs
"""
import os
import sys
import json
import urllib.request
import urllib.parse
import time


CHANNEL = "@YstarBridgeLabs"


def _load_secrets():
    """Load credentials from ~/.gov_mcp_secrets.env"""
    secrets_path = os.path.expanduser("~/.gov_mcp_secrets.env")
    if os.path.isfile(secrets_path):
        with open(secrets_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())


def publish_telegram(text: str) -> dict:
    """Send message to Telegram channel."""
    _load_secrets()
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: Set TELEGRAM_BOT_TOKEN environment variable", file=sys.stderr)
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": CHANNEL,
        "text": text,
        "parse_mode": "Markdown",
    }).encode()

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                return {
                    "status": "published",
                    "channel": CHANNEL,
                    "message_id": result["result"]["message_id"],
                    "timestamp": time.time(),
                }
            else:
                return {"status": "error", "detail": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 publish_telegram.py 'message'")
        sys.exit(1)

    text = sys.argv[1]
    result = publish_telegram(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

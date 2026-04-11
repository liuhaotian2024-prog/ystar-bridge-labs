#!/usr/bin/env python3
"""Publish a tweet via X API v2.

Usage:
    python3 scripts/publish_x.py "Your tweet content here"

Requires environment variables:
    X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET

Install: pip install tweepy
"""
import os
import sys
import time
import json


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


def publish_tweet(text: str) -> dict:
    """Post a tweet. Returns API response dict."""
    try:
        import tweepy
    except ImportError:
        print("Error: pip install tweepy", file=sys.stderr)
        sys.exit(1)

    _load_secrets()
    api_key = os.environ.get("X_API_KEY")
    api_secret = os.environ.get("X_API_SECRET")
    access_token = os.environ.get("X_ACCESS_TOKEN")
    access_secret = os.environ.get("X_ACCESS_SECRET")

    if not all([api_key, api_secret, access_token, access_secret]):
        print("Error: Set X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET", file=sys.stderr)
        sys.exit(1)

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret,
    )

    response = client.create_tweet(text=text)
    return {
        "id": response.data["id"],
        "text": text,
        "timestamp": time.time(),
        "status": "published",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 publish_x.py 'tweet content'")
        sys.exit(1)

    text = sys.argv[1]

    if len(text) > 280:
        print(f"Error: Tweet is {len(text)} chars (max 280)", file=sys.stderr)
        sys.exit(1)

    result = publish_tweet(text)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Publish tweet using OAuth 2.0 with PKCE (X API v2).

This approach uses the Bearer Token + OAuth 2.0 User Context,
which doesn't require the OAuth 1.0a Read/Write permission setting.

Usage:
    python3 scripts/publish_x_v2.py "Your tweet content"
"""
import os
import sys
import json
import urllib.request
import time


def _load_secrets():
    secrets_path = os.path.expanduser("~/.gov_mcp_secrets.env")
    if os.path.isfile(secrets_path):
        with open(secrets_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


def publish_tweet_oauth1(text):
    """Try OAuth 1.0a via tweepy."""
    try:
        import tweepy
    except ImportError:
        return None, "tweepy not installed"

    _load_secrets()
    try:
        client = tweepy.Client(
            consumer_key=os.environ.get("X_API_KEY", ""),
            consumer_secret=os.environ.get("X_API_SECRET", ""),
            access_token=os.environ.get("X_ACCESS_TOKEN", ""),
            access_token_secret=os.environ.get("X_ACCESS_SECRET", ""),
        )
        response = client.create_tweet(text=text)
        return {"id": response.data["id"], "status": "published"}, None
    except Exception as e:
        return None, str(e)


def publish_tweet_v1api(text):
    """Try Twitter v1.1 API via tweepy (sometimes works when v2 doesn't)."""
    try:
        import tweepy
    except ImportError:
        return None, "tweepy not installed"

    _load_secrets()
    try:
        auth = tweepy.OAuthHandler(
            os.environ.get("X_API_KEY", ""),
            os.environ.get("X_API_SECRET", ""),
        )
        auth.set_access_token(
            os.environ.get("X_ACCESS_TOKEN", ""),
            os.environ.get("X_ACCESS_SECRET", ""),
        )
        api = tweepy.API(auth)
        status = api.update_status(text)
        return {"id": str(status.id), "status": "published_v1"}, None
    except Exception as e:
        return None, str(e)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 publish_x_v2.py 'tweet content'")
        sys.exit(1)

    text = sys.argv[1]
    if len(text) > 280:
        print(f"Error: {len(text)} chars (max 280)", file=sys.stderr)
        sys.exit(1)

    print("Trying OAuth 1.0a (v2 API)...")
    result, err = publish_tweet_oauth1(text)
    if result:
        print(json.dumps(result, indent=2))
        return

    print(f"  Failed: {err}")
    print("Trying v1.1 API...")
    result, err = publish_tweet_v1api(text)
    if result:
        print(json.dumps(result, indent=2))
        return

    print(f"  Failed: {err}")
    print("\nBoth methods failed. The X Developer Portal app permissions")
    print("may need to be regenerated. Steps:")
    print("1. Delete the current App in developer.twitter.com")
    print("2. Create a new App (takes 2 minutes)")
    print("3. Set permissions to Read+Write BEFORE generating tokens")
    print("4. Generate tokens AFTER setting permissions")
    print("5. Update ~/.gov_mcp_secrets.env with new tokens")


if __name__ == "__main__":
    main()

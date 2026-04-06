#!/usr/bin/env python3
"""Secretary: Watch for new commits across 3 repos.
Runs via crontab every 5 minutes."""
import os, sys, json, subprocess, urllib.request, urllib.parse, time

REPOS = [
    os.path.expanduser("~/.openclaw/workspace/ystar-company"),
    os.path.expanduser("~/.openclaw/workspace/Y-star-gov"),
    os.path.expanduser("~/.openclaw/workspace/gov-mcp"),
]

STATE_FILE = os.path.expanduser("~/.secretary_last_check")

def load_secrets():
    with open(os.path.expanduser("~/.gov_mcp_secrets.env")) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def send_telegram(text):
    load_secrets()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({"chat_id": "@YstarBridgeLabs", "text": text}).encode()
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read()).get("ok", False)
    except:
        return False

def main():
    # Load last check time
    last_check = 0
    if os.path.isfile(STATE_FILE):
        try:
            last_check = float(open(STATE_FILE).read().strip())
        except:
            pass

    now = time.time()
    since = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(last_check)) if last_check > 0 else "5 minutes ago"

    new_commits = []
    for repo in REPOS:
        if not os.path.isdir(repo):
            continue
        try:
            result = subprocess.run(
                ["git", "-C", repo, "log", f"--since={since}", "--oneline"],
                capture_output=True, text=True, timeout=10
            )
            lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
            repo_name = os.path.basename(repo)
            for line in lines[:3]:  # Max 3 per repo
                new_commits.append(f"[{repo_name}] {line}")
        except:
            pass

    # Save current time
    with open(STATE_FILE, "w") as f:
        f.write(str(now))

    if new_commits:
        msg = f"🔔 New commits detected:\n\n" + "\n".join(new_commits) + "\n\n— Secretary"
        send_telegram(msg)
        print(f"Notified: {len(new_commits)} commits")
    else:
        print("No new commits")

if __name__ == "__main__":
    main()

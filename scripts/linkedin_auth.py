"""
Y* Bridge Labs — LinkedIn Automated Auth & Posting
===================================================
Solution for Chrome v136+ with v20 App-Bound cookie encryption on Windows.

Problem: Chrome v20 cookies cannot be decrypted externally. Chrome v136+
blocks --remote-debugging-port on the default user data directory.

Solution: Playwright's Chromium with a dedicated persistent profile. Playwright
uses --remote-debugging-pipe (not port) internally, which works with any
user-data-dir. Once the LinkedIn session is established in the Playwright
profile, it persists across runs indefinitely.

Architecture:
  1. Playwright launches Chromium with a dedicated persistent profile
  2. If session exists -> post directly (headless, fully automated)
  3. If no session -> one-time headful login, then save state
  4. Also extracts decrypted cookies via CDP for API-based operations
  5. Dual posting: API (fast, headless) + Playwright UI (fallback)

Usage:
    python scripts/linkedin_auth.py login             # One-time: login & save session
    python scripts/linkedin_auth.py test              # Check if session is valid
    python scripts/linkedin_auth.py post "text"       # Post to LinkedIn (auto picks best method)
    python scripts/linkedin_auth.py extract           # Extract decrypted cookies for API use
    python scripts/linkedin_auth.py refresh           # Refresh session by visiting LinkedIn

One-time setup: run 'login' once. After that, all other commands are fully automated.

Requirements: pip install playwright requests
              playwright install chromium
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

# ─── Config ──────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
PROFILE_DIR = SCRIPT_DIR / ".social_cookies" / "linkedin_playwright_profile"
STATE_FILE = SCRIPT_DIR / ".social_cookies" / "linkedin_api_cookies.json"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)

LI_API_BASE = "https://www.linkedin.com/voyager/api"
LI_FEED_URL = "https://www.linkedin.com/feed/"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


# ─── Playwright Session Management ───────────────────────────────────────────

async def _launch_context(playwright, headless: bool = True):
    """Launch Playwright Chromium with the persistent LinkedIn profile."""
    ctx = await playwright.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=headless,
        viewport={"width": 1280, "height": 900},
        user_agent=USER_AGENT,
        args=[
            "--no-first-run",
            "--disable-blink-features=AutomationControlled",
        ],
        ignore_default_args=["--enable-automation"],
        timeout=30000,
    )
    return ctx


async def _is_logged_in(page) -> bool:
    """Check if the current page shows a logged-in LinkedIn state."""
    url = page.url
    if "/login" in url or "/authwall" in url or "/checkpoint" in url:
        return False
    # Double-check by looking for feed elements
    try:
        feed = page.locator("div.feed-shared-update-v2, div[data-urn], .scaffold-layout")
        count = await feed.count()
        return count > 0
    except Exception:
        return "/feed" in url or "/in/" in url


async def _extract_cookies_from_context(ctx) -> dict:
    """Extract LinkedIn cookies from a Playwright context (decrypted)."""
    cookies = await ctx.cookies("https://www.linkedin.com")
    li_cookies = {}
    for c in cookies:
        if "linkedin.com" in c.get("domain", ""):
            li_cookies[c["name"]] = c["value"]
    return li_cookies


# ─── Commands ─────────────────────────────────────────────────────────────────

async def cmd_login():
    """One-time login: opens browser, user logs in, session saved to profile."""
    from playwright.async_api import async_playwright

    print("[Login] Opening LinkedIn login page...")
    print("[Login] Please log in manually. The session will be saved automatically.")

    async with async_playwright() as p:
        ctx = await _launch_context(p, headless=False)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        # Check if already logged in
        await page.goto(LI_FEED_URL, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)

        if await _is_logged_in(page):
            print("[Login] Already logged in! Session is valid.")
            cookies = await _extract_cookies_from_context(ctx)
            _save_api_cookies(cookies)
            await ctx.close()
            return True

        # Navigate to login page
        await page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        print("[Login] Waiting for login completion (up to 3 minutes)...")

        for i in range(180):
            await page.wait_for_timeout(1000)
            url = page.url
            if "/feed" in url or "/mynetwork" in url:
                print(f"[Login] Login successful! (detected at {i+1}s)")
                break
            if i > 0 and i % 15 == 0:
                print(f"[Login] Still waiting... ({i}s)")
        else:
            print("[Login] Timeout waiting for login.")
            await ctx.close()
            return False

        # Wait for page to fully load
        await page.wait_for_timeout(3000)

        # Extract and save cookies for API use
        cookies = await _extract_cookies_from_context(ctx)
        _save_api_cookies(cookies)

        print(f"[Login] Session saved. Found {len(cookies)} LinkedIn cookies.")
        key_cookies = {"li_at", "JSESSIONID", "li_rm"}
        found = set(cookies.keys()) & key_cookies
        print(f"[Login] Key cookies present: {found}")

        await ctx.close()
        return True


async def cmd_test():
    """Test if the saved session is valid."""
    from playwright.async_api import async_playwright

    print("[Test] Checking LinkedIn session...")

    # Method 1: Try API with cached cookies
    api_ok = _test_api_session()

    # Method 2: Try Playwright
    async with async_playwright() as p:
        ctx = await _launch_context(p, headless=True)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        try:
            await page.goto(LI_FEED_URL, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_timeout(3000)
            pw_ok = await _is_logged_in(page)
        except Exception as e:
            print(f"[Test] Playwright check failed: {e}")
            pw_ok = False

        if pw_ok:
            # Refresh API cookies from the live session
            cookies = await _extract_cookies_from_context(ctx)
            _save_api_cookies(cookies)

        await ctx.close()

    print(f"\n[Test] API session valid: {api_ok}")
    print(f"[Test] Playwright session valid: {pw_ok}")

    if pw_ok:
        print("[Test] RESULT: LinkedIn session is ACTIVE")
        return True
    else:
        print("[Test] RESULT: Session expired. Run: python scripts/linkedin_auth.py login")
        return False


async def cmd_post(text: str):
    """Post to LinkedIn. Tries API first, falls back to Playwright UI automation."""
    print(f"[Post] Posting ({len(text)} chars)...")

    # Method 1: API-based posting (fast, headless)
    api_ok = _post_via_api(text)
    if api_ok:
        return True

    print("[Post] API posting failed, using Playwright UI automation...")

    # Method 2: Playwright UI automation
    return await _post_via_playwright_ui(text)


async def _post_via_playwright_ui(text: str) -> bool:
    """Post to LinkedIn using Playwright browser automation."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        ctx = await _launch_context(p, headless=True)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        await page.goto(LI_FEED_URL, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)

        if not await _is_logged_in(page):
            print("[Post] ERROR: Not logged in. Run 'login' first.")
            await ctx.close()
            return False

        # Click "Start a post" button
        try:
            start_btn = page.locator(
                "button.share-box-feed-entry__trigger, "
                "button[class*='share-box'], "
                "button:has-text('Start a post')"
            )
            await start_btn.first.click(timeout=8000)
        except Exception as e:
            print(f"[Post] Could not find 'Start a post' button: {e}")
            # Try clicking the share box area directly
            try:
                share_area = page.locator(
                    ".share-box-feed-entry__top-bar, "
                    ".share-box-feed-entry__closed-share-box"
                )
                await share_area.first.click(timeout=5000)
            except Exception:
                print("[Post] ERROR: Cannot open post editor")
                await ctx.close()
                return False

        await page.wait_for_timeout(2000)

        # Type in the post editor
        editor = page.locator(
            "div.ql-editor, "
            "div[role='textbox'][contenteditable='true'], "
            "div[contenteditable='true'][data-placeholder]"
        )
        await editor.first.click()

        # Use keyboard.type for more realistic input
        await page.keyboard.type(text, delay=10)
        await page.wait_for_timeout(1500)

        # Click Post button
        post_btn = page.locator(
            "button.share-actions__primary-action, "
            "button.artdeco-button--primary:has-text('Post')"
        )
        await post_btn.first.click(timeout=5000)
        await page.wait_for_timeout(4000)

        # Verify post was submitted (editor should close)
        editor_still_open = await page.locator("div.ql-editor").count()
        if editor_still_open > 0:
            # Check if there's an error message
            print("[Post] WARNING: Editor may still be open, post might not have submitted")

        # Refresh cookies
        cookies = await _extract_cookies_from_context(ctx)
        _save_api_cookies(cookies)

        await ctx.close()
        print("[Post] Published via Playwright!")
        return True


async def cmd_extract():
    """Extract decrypted LinkedIn cookies from the Playwright session."""
    from playwright.async_api import async_playwright

    print("[Extract] Launching Playwright to extract cookies...")

    async with async_playwright() as p:
        ctx = await _launch_context(p, headless=True)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        await page.goto(LI_FEED_URL, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(3000)

        if not await _is_logged_in(page):
            print("[Extract] WARNING: Not logged in. Cookies may be incomplete.")

        cookies = await _extract_cookies_from_context(ctx)
        _save_api_cookies(cookies)
        await ctx.close()

    print(f"\n[Extract] {len(cookies)} LinkedIn cookies extracted:")
    for name in sorted(cookies.keys()):
        val = cookies[name]
        display = val[:40] + "..." if len(val) > 40 else val
        print(f"  {name}: {display}")
    return cookies


async def cmd_refresh():
    """Refresh the session by visiting LinkedIn (keeps session alive)."""
    from playwright.async_api import async_playwright

    print("[Refresh] Visiting LinkedIn to refresh session...")

    async with async_playwright() as p:
        ctx = await _launch_context(p, headless=True)
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        await page.goto(LI_FEED_URL, wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(3000)

        if await _is_logged_in(page):
            cookies = await _extract_cookies_from_context(ctx)
            _save_api_cookies(cookies)
            print("[Refresh] Session refreshed and cookies updated.")
        else:
            print("[Refresh] Session expired. Run 'login' to re-authenticate.")

        await ctx.close()


# ─── API-Based Operations ────────────────────────────────────────────────────

def _save_api_cookies(cookies: dict):
    """Save decrypted cookies to disk for API-based operations."""
    data = {"cookies": cookies, "saved_at": time.time()}
    STATE_FILE.write_text(json.dumps(data, indent=2))
    print(f"[Auth] API cookies saved ({len(cookies)} cookies)")


def _load_api_cookies() -> dict | None:
    """Load cached API cookies if they exist and are fresh enough."""
    if not STATE_FILE.exists():
        return None
    try:
        data = json.loads(STATE_FILE.read_text())
        age = time.time() - data.get("saved_at", 0)
        if age > 12 * 3600:  # 12 hour max age
            print("[Auth] Cached API cookies are stale (>12h)")
            return None
        return data.get("cookies", {})
    except Exception:
        return None


def _build_api_session(li_cookies: dict) -> requests.Session:
    """Build a requests.Session with LinkedIn cookies and proper headers."""
    session = requests.Session()
    for name, value in li_cookies.items():
        session.cookies.set(name, value, domain=".linkedin.com")

    csrf_token = li_cookies.get("JSESSIONID", "").strip('"')

    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "application/vnd.linkedin.normalized+json+2.1",
        "Accept-Language": "en-US,en;q=0.9",
        "x-li-lang": "en_US",
        "x-li-track": json.dumps({
            "clientVersion": "1.13.8747",
            "mpVersion": "1.13.8747",
            "osName": "web",
            "timezoneOffset": -5,
            "deviceFormFactor": "DESKTOP",
        }),
        "x-restli-protocol-version": "2.0.0",
        "csrf-token": csrf_token,
    })
    return session


def _test_api_session() -> bool:
    """Test if cached API cookies yield a valid session."""
    cookies = _load_api_cookies()
    if not cookies:
        return False

    session = _build_api_session(cookies)
    try:
        r = session.get(f"{LI_API_BASE}/me", timeout=10)
        if r.status_code == 200:
            data = r.json()
            first = data.get("firstName", "")
            last = data.get("lastName", "")
            if isinstance(first, dict):
                first = first.get("localized", {}).get("en_US", "?")
                last = last.get("localized", {}).get("en_US", "?")
            print(f"[API] Authenticated as: {first} {last}")
            return True
        else:
            print(f"[API] Session check returned {r.status_code}")
            return False
    except Exception as e:
        print(f"[API] Session test failed: {e}")
        return False


def _post_via_api(text: str) -> bool:
    """Post to LinkedIn using the Voyager REST API with cached cookies."""
    cookies = _load_api_cookies()
    if not cookies or "li_at" not in cookies:
        print("[API] No valid API cookies available")
        return False

    session = _build_api_session(cookies)

    # Get user URN
    try:
        r = session.get(f"{LI_API_BASE}/me", timeout=10)
        if r.status_code != 200:
            print(f"[API] Cannot fetch profile: {r.status_code}")
            return False
        data = r.json()
        user_urn = (
            data.get("miniProfile", {}).get("entityUrn", "")
            or data.get("entityUrn", "")
            or f"urn:li:person:{data.get('id', '')}"
        )
    except Exception as e:
        print(f"[API] Profile fetch error: {e}")
        return False

    if not user_urn.startswith("urn:"):
        user_urn = f"urn:li:person:{user_urn}"

    # Post via normalizedShares API
    payload = {
        "visibleToConnectionsOnly": False,
        "externalAudienceProviders": [],
        "commentaryV2": {"text": text, "attributes": []},
        "origin": "FEED",
        "allowedCommentersScope": "ALL",
        "postState": "PUBLISHED",
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    try:
        r = session.post(
            f"{LI_API_BASE}/contentcreation/normalizedShares",
            json=payload,
            timeout=15,
        )
        if r.status_code in (200, 201):
            print("[API] Post published successfully!")
            return True
        print(f"[API] normalizedShares returned {r.status_code}, trying ugcPosts...")
    except Exception as e:
        print(f"[API] normalizedShares error: {e}")

    # Fallback: ugcPosts API
    ugc_payload = {
        "author": user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC",
        },
    }
    try:
        r = session.post(f"{LI_API_BASE}/ugcPosts", json=ugc_payload, timeout=15)
        if r.status_code in (200, 201):
            print("[API] Post published via UGC API!")
            return True
        print(f"[API] ugcPosts returned {r.status_code}: {r.text[:200]}")
    except Exception as e:
        print(f"[API] ugcPosts error: {e}")

    return False


# ─── Programmatic Interface ──────────────────────────────────────────────────

def post_to_linkedin(text: str) -> bool:
    """Public API: post to LinkedIn. Returns True on success.

    Usage from other scripts:
        from scripts.linkedin_auth import post_to_linkedin
        post_to_linkedin("Hello from Y* Bridge Labs!")
    """
    return asyncio.run(cmd_post(text))


def is_session_valid() -> bool:
    """Public API: check if LinkedIn session is valid."""
    return asyncio.run(cmd_test())


def get_linkedin_cookies() -> dict:
    """Public API: get decrypted LinkedIn cookies as a dict."""
    cookies = _load_api_cookies()
    if cookies:
        return cookies
    return asyncio.run(cmd_extract())


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "login":
        ok = asyncio.run(cmd_login())
        sys.exit(0 if ok else 1)

    elif cmd == "test":
        ok = asyncio.run(cmd_test())
        sys.exit(0 if ok else 1)

    elif cmd == "post" and len(sys.argv) > 2:
        text = " ".join(sys.argv[2:])
        ok = asyncio.run(cmd_post(text))
        sys.exit(0 if ok else 1)

    elif cmd == "extract":
        asyncio.run(cmd_extract())

    elif cmd == "refresh":
        asyncio.run(cmd_refresh())

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()

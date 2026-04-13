"""
Y* Bridge Labs — Social Media Automation Toolkit
Uses Playwright for browser automation. Session cookies persist between runs.

Usage:
    python scripts/social_auto.py linkedin_login
    python scripts/social_auto.py linkedin_post "post content here"
    python scripts/social_auto.py linkedin_comment "post_url" "comment text"
    python scripts/social_auto.py linkedin_follow "profile_url"
    python scripts/social_auto.py linkedin_analytics
    python scripts/social_auto.py hn_login
    python scripts/social_auto.py hn_upvote "item_id"
    python scripts/social_auto.py hn_comment "item_id" "comment text"
    python scripts/social_auto.py hn_check "item_id"
    python scripts/social_auto.py x_login
    python scripts/social_auto.py x_post "Aiden-CEO" "content here" [--live]
    python scripts/social_auto.py x_reply "post_url" "Sofia-CMO" "reply here" [--live]
    python scripts/social_auto.py x_follow "@handle" "Zara-CSO"
    python scripts/social_auto.py x_like "post_url" "Ethan-CTO"

First run: use *_login to authenticate (one-time manual login, cookies saved).
After that: all actions are fully automated.

X commands default to dry_run=True. Add --live to actually post/reply.
All X operations enforce R1-R6 safety checks (see knowledge/ceo/lessons/public_x_engagement_policy_2026_04_13.md).
"""
import asyncio
import sys
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright
from datetime import datetime

# Y*gov CIEU integration
try:
    from x_content_safety_check import safety_check, increment_quota
    from x_disclosure_templates import get_disclosure
except ImportError:
    # Fallback if modules not in path
    safety_check = None
    increment_quota = None
    get_disclosure = None

COOKIE_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.social_cookies")
COOKIE_DIR.mkdir(exist_ok=True)

# CIEU event emission
CIEU_LOG = Path(__file__).parent.parent / ".ystar_omission.db"  # Use existing omission db


def emit_cieu_event(event_type: str, data: dict):
    """
    Emit CIEU event for X engagement auditing.

    Event types:
    - X_ENGAGEMENT_POSTED: Post/reply published
    - X_ENGAGEMENT_VIOLATION: Safety check failed
    """
    try:
        import sqlite3
        conn = sqlite3.connect(CIEU_LOG)
        cursor = conn.cursor()

        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cieu_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL
            )
        """)

        cursor.execute(
            "INSERT INTO cieu_events (timestamp, event_type, data) VALUES (?, ?, ?)",
            (datetime.now().isoformat(), event_type, json.dumps(data))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[CIEU] Warning: Failed to emit event {event_type}: {e}")


def cookie_path(platform: str) -> Path:
    return COOKIE_DIR / f"{platform}_state.json"


async def save_state(context, platform: str):
    await context.storage_state(path=str(cookie_path(platform)))
    print(f"[{platform}] Session saved.")


async def get_context(playwright, platform: str, headless: bool = True):
    """Get browser context with saved cookies if available."""
    cp = cookie_path(platform)
    if cp.exists():
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(COOKIE_DIR / f"{platform}_profile"),
            headless=headless,
            storage_state=str(cp),
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        )
    else:
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(COOKIE_DIR / f"{platform}_profile"),
            headless=False,  # First login must be visible
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        )
    return context


# ═══════════════════════════════════════════════════════════
# LINKEDIN
# ═══════════════════════════════════════════════════════════

async def linkedin_login():
    """Open LinkedIn login page. User logs in manually. Auto-detects login completion."""
    async with async_playwright() as p:
        ctx = await get_context(p, "linkedin")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.linkedin.com/login")
        print("[LinkedIn] Browser opened. Please log in manually...")
        print("[LinkedIn] Waiting for login (will auto-detect when you reach the feed)...")
        # Poll until we detect the logged-in feed page
        for i in range(180):  # Wait up to 3 minutes
            await page.wait_for_timeout(1000)
            url = page.url
            if "/feed" in url or "/mynetwork" in url or "/in/" in url:
                print(f"[LinkedIn] Login detected! URL: {url}")
                break
            if i % 10 == 0 and i > 0:
                print(f"[LinkedIn] Still waiting... ({i}s)")
        else:
            print("[LinkedIn] Timeout. Saving whatever state we have.")
        await save_state(ctx, "linkedin")
        print("[LinkedIn] Session saved. You can close the browser.")
        await ctx.close()


async def linkedin_post(content: str):
    """Post to LinkedIn feed."""
    async with async_playwright() as p:
        ctx = await get_context(p, "linkedin")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.linkedin.com/feed/")
        await page.wait_for_timeout(3000)

        # Click "Start a post" button
        start_post = page.locator("button.share-box-feed-entry__trigger")
        await start_post.click()
        await page.wait_for_timeout(2000)

        # Type in the post editor
        editor = page.locator("div.ql-editor[data-placeholder]")
        await editor.click()
        await editor.fill(content)
        await page.wait_for_timeout(1000)

        # Click Post button
        post_btn = page.locator("button.share-actions__primary-action")
        await post_btn.click()
        await page.wait_for_timeout(3000)

        await save_state(ctx, "linkedin")
        print("[LinkedIn] Post published!")
        await ctx.close()


async def linkedin_comment(post_url: str, comment: str):
    """Comment on a LinkedIn post."""
    async with async_playwright() as p:
        ctx = await get_context(p, "linkedin")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(post_url)
        await page.wait_for_timeout(3000)

        # Click comment button
        comment_btn = page.locator("button[aria-label*='Comment']").first
        await comment_btn.click()
        await page.wait_for_timeout(1000)

        # Type comment
        editor = page.locator("div.ql-editor[data-placeholder*='Add a comment']")
        await editor.click()
        await editor.fill(comment)
        await page.wait_for_timeout(500)

        # Submit
        submit = page.locator("button.comments-comment-box__submit-button")
        await submit.click()
        await page.wait_for_timeout(2000)

        await save_state(ctx, "linkedin")
        print(f"[LinkedIn] Commented on {post_url}")
        await ctx.close()


async def linkedin_analytics():
    """Fetch LinkedIn post analytics."""
    async with async_playwright() as p:
        ctx = await get_context(p, "linkedin")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.linkedin.com/dashboard/")
        await page.wait_for_timeout(3000)
        content = await page.content()

        # Also check recent activity
        await page.goto("https://www.linkedin.com/in/zippoliu/recent-activity/all/")
        await page.wait_for_timeout(3000)

        # Extract metrics from page
        metrics = await page.locator("span.analytics-resource-card__value").all_text_contents()
        print(f"[LinkedIn] Dashboard metrics: {metrics}")

        await save_state(ctx, "linkedin")
        await ctx.close()


# ═══════════════════════════════════════════════════════════
# HACKER NEWS
# ═══════════════════════════════════════════════════════════

async def hn_login():
    """Login to HN. Auto-detects login completion."""
    async with async_playwright() as p:
        ctx = await get_context(p, "hn")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://news.ycombinator.com/login")
        print("[HN] Browser opened. Please log in manually...")
        print("[HN] Waiting for login (will auto-detect)...")
        for i in range(120):  # Wait up to 2 minutes
            await page.wait_for_timeout(1000)
            # After login, HN redirects to news or shows logout link
            logout = await page.locator("a[href*='logout']").count()
            if logout > 0:
                print("[HN] Login detected!")
                break
            url = page.url
            if "news.ycombinator.com" in url and "login" not in url:
                print(f"[HN] Login detected! URL: {url}")
                break
            if i % 10 == 0 and i > 0:
                print(f"[HN] Still waiting... ({i}s)")
        else:
            print("[HN] Timeout. Saving whatever state we have.")
        await save_state(ctx, "hn")
        print("[HN] Session saved.")
        await ctx.close()


async def hn_check(item_id: str):
    """Check HN post stats."""
    async with async_playwright() as p:
        ctx = await get_context(p, "hn")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(f"https://news.ycombinator.com/item?id={item_id}")
        await page.wait_for_timeout(2000)

        title = await page.locator("span.titleline > a").first.text_content()
        score_el = page.locator("span.score")
        score = await score_el.text_content() if await score_el.count() > 0 else "0 points"
        comments = await page.locator("a[href*='item?id=']:has-text('comment')").all_text_contents()

        print(f"[HN] {title}")
        print(f"[HN] Score: {score}")
        print(f"[HN] Comments: {comments}")
        await ctx.close()


async def hn_comment(item_id: str, text: str):
    """Post a comment on HN."""
    async with async_playwright() as p:
        ctx = await get_context(p, "hn")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(f"https://news.ycombinator.com/item?id={item_id}")
        await page.wait_for_timeout(2000)

        textarea = page.locator("textarea[name='text']")
        await textarea.fill(text)
        await page.locator("input[value='add comment']").click()
        await page.wait_for_timeout(2000)

        await save_state(ctx, "hn")
        print(f"[HN] Comment posted on item {item_id}")
        await ctx.close()


# ═══════════════════════════════════════════════════════════
# X (TWITTER)
# ═══════════════════════════════════════════════════════════

async def x_login():
    """Open X login page. User logs in manually. Auto-detects login completion."""
    async with async_playwright() as p:
        ctx = await get_context(p, "x")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://x.com/login")
        print("[X] Browser opened. Please log in manually...")
        print("[X] Waiting for login (will auto-detect when you reach the home timeline)...")

        for i in range(180):  # Wait up to 3 minutes
            await page.wait_for_timeout(1000)
            url = page.url
            if "/home" in url or url == "https://x.com/" or url == "https://twitter.com/":
                print(f"[X] Login detected! URL: {url}")
                break
            if i % 10 == 0 and i > 0:
                print(f"[X] Still waiting... ({i}s)")
        else:
            print("[X] Timeout. Saving whatever state we have.")

        await save_state(ctx, "x")
        print("[X] Session saved. You can close the browser.")
        await ctx.close()


async def x_post(content: str, role: str, dry_run: bool = True):
    """
    Post original tweet to X.

    Args:
        content: Tweet content (MUST include disclosure per R1)
        role: Agent role (e.g., 'Aiden-CEO', 'Sofia-CMO')
        dry_run: If True, only validate + log, don't actually post
    """
    if not safety_check:
        print("[X] ERROR: Safety check module not loaded. Cannot post.")
        return

    # R2/R4 safety check
    passed, reasons = safety_check(content, role, action='posts', require_disclosure=True)

    if not passed:
        print(f"[X] Safety check FAILED for {role}: {reasons}")
        emit_cieu_event("X_ENGAGEMENT_VIOLATION", {
            "role": role,
            "action": "post",
            "content": content,
            "reasons": reasons,
            "timestamp": datetime.now().isoformat(),
        })
        return

    if dry_run:
        print(f"[X] DRY RUN: Would post as {role}:")
        print(f"    {content[:100]}...")
        print(f"    Safety: PASS")
        emit_cieu_event("X_ENGAGEMENT_POSTED", {
            "role": role,
            "action": "post",
            "content": content,
            "dry_run": True,
            "safety_check_pass": True,
            "disclose_present": True,
            "timestamp": datetime.now().isoformat(),
        })
        return

    # Real posting
    async with async_playwright() as p:
        ctx = await get_context(p, "x")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://x.com/home")
        await page.wait_for_timeout(3000)

        # Click "What's happening?" or "Post" button
        tweet_box = page.locator('div[data-testid="tweetTextarea_0"]')
        await tweet_box.click()
        await tweet_box.fill(content)
        await page.wait_for_timeout(1000)

        # Click Post button
        post_btn = page.locator('div[data-testid="tweetButtonInline"]')
        await post_btn.click()
        await page.wait_for_timeout(3000)

        await save_state(ctx, "x")
        print(f"[X] Posted as {role}!")

        # Increment quota + emit CIEU
        increment_quota(role, 'posts')
        emit_cieu_event("X_ENGAGEMENT_POSTED", {
            "role": role,
            "action": "post",
            "content": content,
            "dry_run": False,
            "safety_check_pass": True,
            "disclose_present": True,
            "timestamp": datetime.now().isoformat(),
        })
        await ctx.close()


async def x_reply(post_url: str, content: str, role: str, dry_run: bool = True):
    """
    Reply to an X post.

    Args:
        post_url: URL of the post to reply to
        content: Reply content (MUST include disclosure per R1)
        role: Agent role
        dry_run: If True, only validate + log, don't actually reply
    """
    if not safety_check:
        print("[X] ERROR: Safety check module not loaded. Cannot reply.")
        return

    # R2/R4 safety check
    passed, reasons = safety_check(content, role, action='replies', require_disclosure=True)

    if not passed:
        print(f"[X] Safety check FAILED for {role}: {reasons}")
        emit_cieu_event("X_ENGAGEMENT_VIOLATION", {
            "role": role,
            "action": "reply",
            "content": content,
            "post_url": post_url,
            "reasons": reasons,
            "timestamp": datetime.now().isoformat(),
        })
        return

    if dry_run:
        print(f"[X] DRY RUN: Would reply to {post_url} as {role}:")
        print(f"    {content[:100]}...")
        print(f"    Safety: PASS")
        emit_cieu_event("X_ENGAGEMENT_POSTED", {
            "role": role,
            "action": "reply",
            "content": content,
            "post_url": post_url,
            "dry_run": True,
            "safety_check_pass": True,
            "disclose_present": True,
            "timestamp": datetime.now().isoformat(),
        })
        return

    # Real reply
    async with async_playwright() as p:
        ctx = await get_context(p, "x")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(post_url)
        await page.wait_for_timeout(3000)

        # Click reply button
        reply_btn = page.locator('div[data-testid="reply"]').first
        await reply_btn.click()
        await page.wait_for_timeout(1000)

        # Type reply
        reply_box = page.locator('div[data-testid="tweetTextarea_0"]')
        await reply_box.fill(content)
        await page.wait_for_timeout(1000)

        # Submit
        submit_btn = page.locator('div[data-testid="tweetButton"]')
        await submit_btn.click()
        await page.wait_for_timeout(2000)

        await save_state(ctx, "x")
        print(f"[X] Replied to {post_url} as {role}!")

        # Increment quota + emit CIEU
        increment_quota(role, 'replies')
        emit_cieu_event("X_ENGAGEMENT_POSTED", {
            "role": role,
            "action": "reply",
            "content": content,
            "post_url": post_url,
            "dry_run": False,
            "safety_check_pass": True,
            "disclose_present": True,
            "timestamp": datetime.now().isoformat(),
        })
        await ctx.close()


async def x_follow(handle: str, role: str):
    """
    Follow a user on X.

    Args:
        handle: Username (with or without @)
        role: Agent role
    """
    if not safety_check:
        print("[X] ERROR: Safety check module not loaded. Cannot follow.")
        return

    # R4 rate limit check only (no content)
    passed, reasons = safety_check("", role, action='follows', require_disclosure=False)
    if not passed:
        print(f"[X] Rate limit check FAILED for {role}: {reasons}")
        emit_cieu_event("X_ENGAGEMENT_VIOLATION", {
            "role": role,
            "action": "follow",
            "handle": handle,
            "reasons": reasons,
            "timestamp": datetime.now().isoformat(),
        })
        return

    handle = handle.lstrip('@')

    async with async_playwright() as p:
        ctx = await get_context(p, "x")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(f"https://x.com/{handle}")
        await page.wait_for_timeout(3000)

        # Click Follow button
        follow_btn = page.locator('div[data-testid$="follow"]').first
        await follow_btn.click()
        await page.wait_for_timeout(1000)

        await save_state(ctx, "x")
        print(f"[X] Followed @{handle} as {role}!")

        # Increment quota + emit CIEU
        increment_quota(role, 'follows')
        emit_cieu_event("X_ENGAGEMENT_POSTED", {
            "role": role,
            "action": "follow",
            "handle": handle,
            "dry_run": False,
            "timestamp": datetime.now().isoformat(),
        })
        await ctx.close()


async def x_like(post_url: str, role: str):
    """
    Like a post on X.

    Args:
        post_url: URL of the post
        role: Agent role
    """
    if not safety_check:
        print("[X] ERROR: Safety check module not loaded. Cannot like.")
        return

    # R4 rate limit check only (no content)
    passed, reasons = safety_check("", role, action='likes', require_disclosure=False)
    if not passed:
        print(f"[X] Rate limit check FAILED for {role}: {reasons}")
        emit_cieu_event("X_ENGAGEMENT_VIOLATION", {
            "role": role,
            "action": "like",
            "post_url": post_url,
            "reasons": reasons,
            "timestamp": datetime.now().isoformat(),
        })
        return

    async with async_playwright() as p:
        ctx = await get_context(p, "x")
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(post_url)
        await page.wait_for_timeout(3000)

        # Click Like button
        like_btn = page.locator('div[data-testid="like"]').first
        await like_btn.click()
        await page.wait_for_timeout(500)

        await save_state(ctx, "x")
        print(f"[X] Liked {post_url} as {role}!")

        # Increment quota + emit CIEU
        increment_quota(role, 'likes')
        emit_cieu_event("X_ENGAGEMENT_POSTED", {
            "role": role,
            "action": "like",
            "post_url": post_url,
            "dry_run": False,
            "timestamp": datetime.now().isoformat(),
        })
        await ctx.close()


# ═══════════════════════════════════════════════════════════
# EDGE-TTS PODCAST
# ═══════════════════════════════════════════════════════════

async def generate_podcast(text_file: str, output_file: str, voice: str = "en-US-GuyNeural"):
    """Generate podcast audio from text using edge-tts (free)."""
    try:
        import edge_tts
    except ImportError:
        os.system("pip install edge-tts")
        import edge_tts

    with open(text_file, "r", encoding="utf-8") as f:
        text = f.read()

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
    print(f"[Podcast] Generated: {output_file}")


# ═══════════════════════════════════════════════════════════
# DISPATCH
# ═══════════════════════════════════════════════════════════

async def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "linkedin_login":
        await linkedin_login()
    elif cmd == "linkedin_post" and len(sys.argv) > 2:
        await linkedin_post(" ".join(sys.argv[2:]))
    elif cmd == "linkedin_comment" and len(sys.argv) > 3:
        await linkedin_comment(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "linkedin_analytics":
        await linkedin_analytics()
    elif cmd == "hn_login":
        await hn_login()
    elif cmd == "hn_check" and len(sys.argv) > 2:
        await hn_check(sys.argv[2])
    elif cmd == "hn_comment" and len(sys.argv) > 3:
        await hn_comment(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "x_login":
        await x_login()
    elif cmd == "x_post" and len(sys.argv) > 3:
        role = sys.argv[2]
        content = " ".join(sys.argv[3:])
        dry_run = "--live" not in sys.argv
        await x_post(content, role, dry_run=dry_run)
    elif cmd == "x_reply" and len(sys.argv) > 4:
        post_url = sys.argv[2]
        role = sys.argv[3]
        content = " ".join(sys.argv[4:])
        dry_run = "--live" not in sys.argv
        await x_reply(post_url, content, role, dry_run=dry_run)
    elif cmd == "x_follow" and len(sys.argv) > 3:
        handle = sys.argv[2]
        role = sys.argv[3]
        await x_follow(handle, role)
    elif cmd == "x_like" and len(sys.argv) > 3:
        post_url = sys.argv[2]
        role = sys.argv[3]
        await x_like(post_url, role)
    elif cmd == "podcast" and len(sys.argv) > 3:
        await generate_podcast(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Auto-publish daily wakeup report to README.md (rolling).
Runs daily at 06:00 via cron.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Absolute path - cron-safe
REPO_ROOT = Path(__file__).resolve().parent.parent
README = REPO_ROOT / "README.md"
REPORTS_DIR = REPO_ROOT / "reports" / "daily"

# Company intro header (preserve this)
COMPANY_INTRO = """# Y* Bridge Labs

**A company where the governance applies to everyone — agents and humans alike.**

Most "AI governance" products watch what the agents do. We watch what the humans do too. Every Board directive is logged. Every CTO interpretation is audited. Every misunderstanding is caught at the seam, not after the damage. We built this for our own company first because we knew we'd need it for ourselves.

This README, the company that ships the product, and the audit chain you can replay at any commit hash — they're all the same artifact.

---
"""


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    wakeup_file = REPORTS_DIR / f"{today}_wakeup_report.md"

    if not wakeup_file.exists():
        print(f"ERROR: wakeup report not found: {wakeup_file}", file=sys.stderr)
        sys.exit(1)

    # Read wakeup content
    with open(wakeup_file, "r", encoding="utf-8") as f:
        wakeup_content = f.read()

    # Assemble new README
    new_readme = COMPANY_INTRO
    new_readme += f"\n## 📰 Today's Morning Brief — {today}\n\n"
    new_readme += wakeup_content
    new_readme += "\n\n_Auto-updated daily at 06:00 EDT. Previous briefs in `reports/daily/`._\n"

    # Write
    with open(README, "w", encoding="utf-8") as f:
        f.write(new_readme)

    print(f"✅ README.md updated with {wakeup_file.name}")

    # Git commit + push
    os.chdir(REPO_ROOT)
    os.system("git add README.md")
    commit_msg = f"morning: {today} auto-rolling wakeup brief"
    os.system(f'git commit -m "{commit_msg}"')
    os.system("git push origin main")
    print(f"✅ Pushed to origin/main: {commit_msg}")


if __name__ == "__main__":
    main()

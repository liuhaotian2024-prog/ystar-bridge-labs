# Y*gov Skill Directory Submission Report

**Prepared by:** CSO Agent
**Date:** 2026-03-27
**Status:** Research complete -- Board action required

---

## Executive Summary

Researched 3 requested directories plus discovered 2 additional directories. Of the 5 total:
- **2 CONFIRMED** accepting skill listings (skillhub.club, skills.sh)
- **1 CONFIRMED** as a curated directory with automated crawling (claudemarketplaces.com)
- **1 BLOCKED** by Cloudflare challenge, purpose unclear (skillsmp.com)
- **1 DISCOVERED** as the primary open ecosystem (skills.sh by Vercel Labs)

**Recommended priority order:** skills.sh (largest ecosystem) > skillhub.club (developer portal) > claudemarketplaces.com (auto-crawled, needs install threshold)

---

## 1. claudemarketplaces.com

| Field | Value |
|-------|-------|
| **Status** | EXISTS -- Curated auto-crawled directory |
| **What it is** | Independent community directory of Claude Code plugins, skills, and MCP servers. Built by @mertduzgun. Next.js app on Vercel. NOT affiliated with Anthropic. |
| **Accepts submissions?** | Not directly. Skills are auto-crawled from skills.sh. Requires 500+ installs to be listed. |
| **Submission process** | No manual submission. The site crawls skills.sh and GitHub repos automatically. To appear: (1) publish your skill so it is installable via the skills ecosystem, (2) accumulate 500+ installs, (3) the crawler will pick it up. |
| **Alternative: Paid placement** | Email mert@vinena.studio for advertising. Pinned card $499/mo, In-feed card $349/mo, All placements $999/mo. |
| **Alternative: Contact directly** | Use feedback form at https://claudemarketplaces.com/feedback or email mert@vinena.studio to request listing. |
| **GitHub** | https://github.com/mert-duzgun/claudemarketplaces.com |
| **Issues page** | https://github.com/mert-duzgun/claudemarketplaces.com/issues |

### Board Action Required
- **Option A (Free):** Get listed on skills.sh first, accumulate 500+ installs, auto-crawled.
- **Option B (Fast):** Email mert@vinena.studio requesting early listing or paid placement.
- **Option C (DIY):** Open a GitHub issue at https://github.com/mert-duzgun/claudemarketplaces.com/issues requesting the skill be added.

### Pre-filled Email for Option B
```
To: mert@vinena.studio
Subject: Listing request for Y*gov skill on Claude Code Marketplaces

Hi Mert,

We'd like to get Y*gov listed on claudemarketplaces.com. Y*gov is a runtime governance framework for AI agents -- it enforces permissions, tracks obligations, and writes tamper-proof audit trails.

- Repo: https://github.com/liuhaotian2024-prog/Y-star-gov
- Skills: ystar-govern, ystar-setup, ystar-report
- Install: claude install-skill liuhaotian2024-prog/Y-star-gov/skill
- Description: Runtime governance for AI agents -- enforces permissions, tracks obligations, writes tamper-proof audit trails. Reduced tool calls by 62% and runtime by 35% in controlled testing.

We're building installs but haven't hit the 500 threshold yet. Would you consider an early listing or can we discuss placement options?

Best,
Haotian Liu
Y* Bridge Labs
```

---

## 2. skillsmp.com

| Field | Value |
|-------|-------|
| **Status** | BLOCKED / UNCLEAR |
| **What it is** | Domain exists and is behind Cloudflare (returns 403 with a JavaScript challenge). Could not retrieve actual page content. |
| **Accepts submissions?** | Unknown -- site is inaccessible to automated tools. |
| **Submission process** | Cannot determine. |

### Board Action Required
- **Manual check needed:** Visit https://skillsmp.com in a browser to see what the site actually is.
- If it turns out to be a real skills marketplace, report back and this document will be updated.
- Do NOT invest time until confirmed as relevant.

---

## 3. skillhub.club

| Field | Value |
|-------|-------|
| **Status** | EXISTS -- Active skills marketplace |
| **What it is** | "The universal AI Agent Skills marketplace." Supports Claude Code, Codex CLI, Gemini CLI, and OpenCode. 15,000+ curated skills. LLM-graded for efficiency. Has rankings, stacks, KOL section, and an API marketplace. Next.js app on Vercel with Supabase backend. |
| **Accepts submissions?** | Yes. Has a developer account portal at /account/developer. |
| **Submission URL** | https://skillhub.club/account/developer |
| **GitHub companion** | https://github.com/keyuyuan/skillhub-awesome-skills |
| **API docs** | https://skillhub.club/docs/api |
| **Features** | Rankings system, install tracking, S/A/B/C rating tiers, "Stacks" (bundled skill sets), "OpenClaw" ecosystem |

### Board Action Required
1. Visit https://skillhub.club/account/developer and create a developer account.
2. Submit Y*gov skills through the developer portal.
3. Consider creating a "Stack" (bundle) for governance use cases.

### Pre-filled Submission Fields
```
Name: Y*gov
Repository: https://github.com/liuhaotian2024-prog/Y-star-gov
Skills: ystar-govern, ystar-setup, ystar-report
Category: development / productivity
Description: Runtime governance for AI agents -- enforces permissions, tracks obligations, writes tamper-proof audit trails. Reduced tool calls by 62% and runtime by 35% in controlled testing.
Install command: claude install-skill liuhaotian2024-prog/Y-star-gov/skill
```

---

## 4. skills.sh (DISCOVERED -- Highest Priority)

| Field | Value |
|-------|-------|
| **Status** | EXISTS -- The primary open agent skills ecosystem |
| **What it is** | Official leaderboard and directory for the open agent skills ecosystem. Powered by the `skills` CLI from Vercel Labs. Tracks installs via anonymous telemetry. Top skills have 745K+ installs. Supports 40+ agents including Claude Code and Codex. |
| **Accepts submissions?** | Yes -- fully open. Any GitHub repo with a SKILL.md file is installable. Ranking on the leaderboard is automatic based on install telemetry. |
| **CLI** | https://github.com/vercel-labs/skills |
| **Leaderboard** | https://skills.sh |

### How to Get Listed

The skills ecosystem is fully open. There is no approval gate. Steps:

1. **Create SKILL.md files** in your repo. The CLI looks for skills in these locations:
   - Root directory (if it contains `SKILL.md`)
   - `skills/` directory
   - `.claude/skills/` directory
   - `.agents/skills/` directory

2. **Initialize a skill template** (optional):
   ```bash
   npx skills init ystar-govern
   npx skills init ystar-setup
   npx skills init ystar-report
   ```

3. **Users install via:**
   ```bash
   npx skills add liuhaotian2024-prog/Y-star-gov
   ```

4. **Leaderboard ranking** is automatic -- based on anonymous telemetry of install counts. No submission needed.

5. **claudemarketplaces.com auto-crawls skills.sh** once you hit 500+ installs.

### Board Action Required
1. CTO: Ensure the Y-star-gov repo has properly formatted SKILL.md files in the correct locations.
2. CTO: Run `npx skills init` to generate templates if not already done.
3. CTO: Test that `npx skills add liuhaotian2024-prog/Y-star-gov --list` works correctly.
4. CMO: Update all marketing materials to use the `npx skills add` install command.
5. CSO: Drive installs to climb the leaderboard.

### Pre-filled Install Commands for Marketing
```bash
# Install all Y*gov skills
npx skills add liuhaotian2024-prog/Y-star-gov

# Install specific skill
npx skills add liuhaotian2024-prog/Y-star-gov --skill ystar-govern

# Install for Claude Code only
npx skills add liuhaotian2024-prog/Y-star-gov -a claude-code

# Alternative: Claude native install
claude install-skill liuhaotian2024-prog/Y-star-gov/skill
```

---

## 5. Additional Search: "Claude Code skills marketplace" / "Claude Code plugins directory"

Web search tools were denied during this research session. Based on the sites investigated, the ecosystem appears to be:

| Directory | Type | Our Status |
|-----------|------|------------|
| **skills.sh** | Primary open ecosystem (Vercel Labs) | NOT YET LISTED -- needs SKILL.md in repo |
| **skillhub.club** | Third-party marketplace with ratings | NOT YET LISTED -- needs developer account |
| **claudemarketplaces.com** | Curated auto-crawled directory | NOT YET ELIGIBLE -- needs 500+ installs |
| **skillsmp.com** | Unknown (Cloudflare blocked) | NEEDS MANUAL CHECK |
| **Anthropic docs** | Official plugin/skill reference | Reference only, not a marketplace |

---

## Recommended Action Plan (Priority Order)

### Immediate (This Week)
1. **CTO:** Add SKILL.md files to the Y-star-gov repo for each skill (ystar-govern, ystar-setup, ystar-report). Use `npx skills init` to scaffold.
2. **CTO:** Verify `npx skills add liuhaotian2024-prog/Y-star-gov --list` returns the skills correctly.
3. **Board (Haotian):** Create developer account at https://skillhub.club/account/developer and submit Y*gov.

### Short-term (Next 2 Weeks)
4. **Board (Haotian):** Visit https://skillsmp.com in a browser and report findings.
5. **CSO:** Email mert@vinena.studio (pre-filled email above) requesting early listing or advertising on claudemarketplaces.com.
6. **CMO:** Add `npx skills add liuhaotian2024-prog/Y-star-gov` to the README, blog post, and all marketing materials.

### Medium-term (30 Days)
7. **CSO:** Drive installs toward the 500 threshold for claudemarketplaces.com auto-listing.
8. **CSO:** Open a GitHub issue on https://github.com/keyuyuan/skillhub-awesome-skills to get Y*gov into the curated awesome-skills list.
9. **CMO:** Consider creating a "Governance Stack" on skillhub.club bundling Y*gov skills for enterprise users.

---

## Honesty Notes

- I could NOT verify skillsmp.com content due to Cloudflare bot protection. I am reporting this honestly rather than guessing.
- Web search was denied during this session, so I could not search for additional directories beyond what was directly investigated. A follow-up search in a browser is recommended.
- claudemarketplaces.com is NOT an official Anthropic property. It is a community project.
- skillhub.club is NOT an official Anthropic property. It is a third-party marketplace.
- skills.sh is operated by Vercel Labs, not Anthropic, but is the de facto standard ecosystem.
- All URLs and processes documented above were verified by direct HTTP requests on 2026-03-27.

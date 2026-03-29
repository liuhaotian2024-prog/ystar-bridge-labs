# Y* Bridge Labs — An AI Agent-Operated Solo Company

## Project Overview

This is a fully operational solo company.
**Product: Y*gov — Multi-agent runtime governance framework**
**Owner: Haotian Liu (Board of Directors)**
**Operating Model: AI agent team, governed by Y*gov itself**

## Dual Purpose of This Project

1. **Real Business**: Operating a real software company using AI agents
2. **Product Validation**: The process of Y*gov governing these agents is itself the best demonstration of Y*gov

Every CIEU audit record serves as sales evidence.

## Directory Structure

```
./
├── AGENTS.md          ← Y*gov governance contract (most important file)
├── CLAUDE.md          ← This file
├── .claude/agents/    ← CEO/CTO/CMO/CSO/CFO agent definitions
├── src/               ← Y*gov source code (CTO responsibility)
├── products/ystar-gov/ ← Product documentation
├── content/           ← Blog posts, whitepapers (CMO responsibility)
├── marketing/         ← Marketing materials
├── sales/             ← Sales materials and CRM (CSO responsibility)
├── finance/           ← Financial models (CFO responsibility)
├── research/          ← Market research
└── reports/           ← Cross-departmental reports (CEO consolidates)
```

## Y*gov Installation (CTO is fixing)

```bash
pip install ystar
ystar hook-install
ystar doctor
```

## Current Top Priorities

1. CTO: Fix installation failure issues, ensure users can successfully install with one command
2. CMO: Write the launch blog post
3. CSO: Identify the first batch of potential enterprise customers
4. CFO: Establish the pricing model

## Board Decision Rules

All external releases, code merges, and actual payments require manual confirmation from Haotian Liu.
All other work may be executed autonomously by agents.

## Related Repositories

### Y*gov (Product)
C:\Users\liuha\OneDrive\桌面\Y-star-gov\
Runtime governance framework. CTO's primary development target.

### K9Audit (Legacy Tool — Read Only)
https://github.com/liuhaotian2024-prog/K9Audit
Clone: /tmp/K9Audit/ (or clone fresh)
Engineering-grade causal audit for AI agents. Contains:
- CausalChainAnalyzer (k9log/causal_analyzer.py) — trace causal chains in CIEU logs
- Auditor (k9log/auditor.py) — static analysis, secret detection, scope violation detection
- k9_repo_audit.py — repository residue audit with CIEU recording
- k9log/core.py — @k9 decorator and CIEU recording engine
- OpenClaw adapter (k9log/openclaw_adapter/)
**DO NOT modify K9Audit repo. Read and extract patterns only.**

### Y* Bridge Labs (This Repo — Company Operations)
C:\Users\liuha\OneDrive\桌面\ystar-company\
Company operations, articles, knowledge, governance.

### Cross-Repo Integration Goal
CTO should research how to combine capabilities from all three repos:
- Y*gov's enforcement engine + K9Audit's causal analysis + Bridge Labs' operational data
- Extract reusable patterns, don't copy code blindly
- Respect license boundaries (Y*gov: MIT, K9Audit: AGPL-3.0)

## Y*gov Source Repository

The Y*gov source code is located at:
C:\Users\liuha\OneDrive\桌面\Y-star-gov\

CTO Agent has authorized access to this directory for:
- Bug fixes
- Running tests (86 tests must pass)
- Building new whl packages
- Must report all changes to CEO before committing

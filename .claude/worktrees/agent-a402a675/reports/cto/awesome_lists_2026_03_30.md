# Awesome Lists Submission Targets for Y*gov

**Date:** 2026-03-30
**Author:** CTO, Y* Bridge Labs
**Purpose:** Identify GitHub Awesome lists where Y*gov should be submitted for visibility.

---

## Tier 1 — High Relevance (submit first)

### 1. awesome-llm-agents (kaushikb11)
- **URL:** https://github.com/kaushikb11/awesome-llm-agents
- **Focus:** Curated list of LLM agent frameworks and tools
- **Stars:** High activity, updated 2026-03-22
- **Submission:** Open a PR adding Y*gov under a "Governance / Safety" or "Frameworks" section
- **Fit:** Direct — Y*gov is runtime governance for LLM agent systems

### 2. awesome-agents (kyrolabs)
- **URL:** https://github.com/kyrolabs/awesome-agents
- **Focus:** Open-source tools and products to build AI agents
- **Submission:** PR to add Y*gov under governance/safety tooling
- **Fit:** Strong — positioned as infrastructure for agent teams

### 3. awesome-ai-safety (Giskard-AI)
- **URL:** https://github.com/Giskard-AI/awesome-ai-safety
- **Focus:** Papers and technical articles on AI Quality and Safety
- **Submission:** PR adding Y*gov as an open-source tool/framework
- **Fit:** Strong — Y*gov is an AI safety enforcement framework

### 4. awesome-claude-code (hesreallyhim)
- **URL:** https://github.com/hesreallyhim/awesome-claude-code
- **Focus:** Skills, hooks, slash-commands, agent orchestrators for Claude Code
- **Submission:** PR adding Y*gov as a PreToolUse hook / governance layer
- **Fit:** Direct — Y*gov ships as a native Claude Code hook

### 5. awesome-claude-code (jqueryscript)
- **URL:** https://github.com/jqueryscript/awesome-claude-code
- **Focus:** Tools, IDE integrations, frameworks for Claude Code developers
- **Submission:** PR to add Y*gov under "Frameworks" or "Security/Governance"
- **Fit:** Direct — native Claude Code integration

### 6. awesome-multi-agent-systems (richardblythman)
- **URL:** https://github.com/richardblythman/awesome-multi-agent-systems
- **Focus:** Resources, libraries, frameworks, and tools for multi-agent systems
- **Submission:** PR adding Y*gov under frameworks/tools
- **Fit:** Strong — Y*gov is purpose-built for multi-agent governance

---

## Tier 2 — Good Relevance (submit after Tier 1)

### 7. awesome-ai-agents (slavakurilyak)
- **URL:** https://github.com/slavakurilyak/awesome-ai-agents
- **Focus:** 300+ agentic AI resources
- **Submission:** PR to add Y*gov under governance/safety tools
- **Fit:** Good — large audience, broad scope

### 8. awesome-ai-tools (mahseema)
- **URL:** https://github.com/mahseema/awesome-ai-tools
- **Focus:** Curated list of AI top tools across categories
- **Submission:** PR adding Y*gov under developer tools or safety
- **Fit:** Moderate — broad AI tools list, high visibility

### 9. awesome-claude (webfuse-com)
- **URL:** https://github.com/webfuse-com/awesome-claude
- **Focus:** Things related to Anthropic Claude
- **Submission:** PR to add Y*gov under tools/integrations
- **Fit:** Good — Claude ecosystem, Y*gov has native Claude Code support

### 10. awesome-claude-code-toolkit (rohitg00)
- **URL:** https://github.com/rohitg00/awesome-claude-code-toolkit
- **Focus:** Comprehensive Claude Code toolkit (agents, skills, hooks, plugins)
- **Submission:** PR adding Y*gov under hooks or governance
- **Fit:** Good — Y*gov is a Claude Code hook

### 11. awesome-agent-orchestrators (andyrewlee)
- **URL:** https://github.com/andyrewlee/awesome-agent-orchestrators
- **Focus:** Agent orchestrator tools and frameworks
- **Submission:** PR to add Y*gov as a governance/orchestration layer
- **Fit:** Moderate — Y*gov governs orchestrated agents

### 12. awesome-ai-safety (hari-sikchi)
- **URL:** https://github.com/hari-sikchi/awesome-ai-safety
- **Focus:** AI safety papers, projects, and communities
- **Submission:** PR adding Y*gov under projects/tools
- **Fit:** Good — academic-leaning, Y*gov has patent portfolio

### 13. awesome-llm-powered-agent (hyp1231)
- **URL:** https://github.com/hyp1231/awesome-llm-powered-agent
- **Focus:** LLM-powered agents — papers, repos, blogs
- **Submission:** PR to add Y*gov under repos/tools
- **Fit:** Good — Y*gov governs LLM-powered agents

### 14. awesome-agent-skills (VoltAgent)
- **URL:** https://github.com/VoltAgent/awesome-agent-skills
- **Focus:** Claude Code skills from official dev teams and community
- **Submission:** PR adding Y*gov as a governance skill/hook
- **Fit:** Good — large community, compatible with Claude Code

---

## Tier 3 — Lower Priority

### 15. awesome-ai-security (ottosulin)
- **URL:** https://github.com/ottosulin/awesome-ai-security
- **Focus:** AI security frameworks, standards, learning resources
- **Submission:** PR under security tools
- **Fit:** Moderate — security angle (MITRE ATLAS integration)

### 16. awesome-ai-tools (eudk)
- **URL:** https://github.com/eudk/awesome-ai-tools
- **Focus:** Very large AI tool list (7766+ tools)
- **Submission:** PR to add Y*gov
- **Fit:** Low-moderate — high volume list, less targeted

---

## Submission Process (Standard for all)

1. **Fork** the target repository
2. **Add Y*gov** entry in the appropriate section with this format:
   ```markdown
   - [Y*gov](https://github.com/liuhaotian2024-prog/Y-star-gov) — Runtime governance framework for multi-agent AI systems. Deterministic permission enforcement, obligation tracking, and tamper-evident audit chain. 0.042ms check() latency, zero external dependencies.
   ```
3. **Open a Pull Request** with a clear title like "Add Y*gov — runtime governance for multi-agent AI"
4. Follow any CONTRIBUTING.md guidelines in the target repo
5. Ensure Y*gov entry is placed alphabetically or in the correct category

## Recommended Submission Order

1. awesome-claude-code (hesreallyhim) — most direct fit, Claude Code hook
2. awesome-llm-agents (kaushikb11) — high-traffic, framework-focused
3. awesome-agents (kyrolabs) — broad agent tooling audience
4. awesome-multi-agent-systems (richardblythman) — exact domain match
5. awesome-ai-safety (Giskard-AI) — safety/governance positioning
6. Everything else in Tier 2, then Tier 3

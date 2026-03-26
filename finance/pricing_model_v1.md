# Y*gov Pricing Model v1

**Author:** CFO Agent, YstarCo
**Date:** 2026-03-26
**Last Reviewed:** 2026-03-26
**Status:** Draft -- Pending Board Approval

---

## 1. Three-Tier Pricing Overview

| Dimension | Free (Developer) | Pro ($49/mo) | Enterprise ($499/mo+) |
|---|---|---|---|
| **Target User** | Individual developers, OSS contributors | Startup teams, small engineering orgs | Financial institutions, pharma, large enterprises |
| **Agent Limit** | 1 agent | Up to 10 agents | Unlimited |
| **CIEU Audit Trail** | None | Basic (30-day retention) | Full (unlimited retention + export) |
| **Governance Policies** | Default only | Custom policies | Custom + compliance templates (SOC2, HIPAA) |
| **Domain Packs** | None | 1 included | All included (finance, pharma, legal) |
| **Compliance Reports** | None | None | Full audit reports, regulator-ready |
| **Runtime Monitoring** | Basic logs | Dashboard + alerts | Real-time dashboard + anomaly detection |
| **Support** | Community (GitHub Issues) | Email (48h SLA) | Dedicated Slack channel + CSM (4h SLA) |
| **SSO / RBAC** | None | None | Included |
| **SLA** | None | 99.5% uptime | 99.9% uptime, contractual |
| **Billing** | Free forever | Monthly or annual ($470/yr = 20% off) | Annual contract, custom pricing above base |

---

## 2. Competitive Landscape & Pricing References

| Competitor / Adjacent | Pricing | Notes |
|---|---|---|
| **LangSmith (LangChain)** | Free tier + $39/mo (Plus) + Enterprise | Tracing & observability for LLM apps; no governance layer |
| **Weights & Biases** | Free tier + $50/seat/mo + Enterprise | ML experiment tracking; per-seat model |
| **Datadog LLM Observability** | Usage-based (~$0.10/trace) | Infrastructure-first; no agent governance |
| **Guardrails AI** | Open-source + Enterprise (undisclosed) | Input/output validation only; no runtime governance |
| **CrewAI Enterprise** | Undisclosed (early stage) | Multi-agent orchestration; minimal governance |
| **Anthropic Console** | Usage-based API pricing | Provider tool, not governance |

### Key Takeaway

No direct competitor offers a **runtime governance + audit** product for multi-agent systems at a transparent SaaS price point. Y*gov occupies a whitespace between observability tools (LangSmith, Datadog) and compliance platforms (Vanta, Drata) -- but purpose-built for AI agents.

---

## 3. Pricing Rationale

### 3.1 Why $0 for Free Tier
- **Purpose:** Developer acquisition funnel. Every free user is a potential advocate.
- **Benchmark:** LangSmith, Guardrails AI, and CrewAI all use open-source/free tiers for adoption.
- **Constraint:** Single agent keeps compute costs near zero.

### 3.2 Why $49/mo for Pro
- **Anchor:** Aligns with LangSmith Plus ($39) and W&B Teams ($50/seat). $49 is competitive without undercutting.
- **Value driver:** CIEU audit trail is the unique differentiator. Teams running 2-10 agents need visibility.
- **Unit economics target:** Cost to serve ~$8-12/mo (API relay, storage, monitoring infra). Gross margin ~75-80%.

### 3.3 Why $499/mo for Enterprise
- **Anchor:** Enterprise observability tools (Datadog, New Relic) run $500-2000+/mo. Compliance platforms (Vanta) start at $500+/mo.
- **Value driver:** Regulator-ready audit reports + domain compliance packs. For a financial firm spending $50K+/mo on AI infrastructure, $499/mo for governance is a rounding error.
- **Expansion revenue:** Custom pricing above base allows land-and-expand. Initial $499 is a foot-in-the-door price.
- **Unit economics target:** Cost to serve ~$60-100/mo. Gross margin ~80-88%.

### 3.4 Annual Discount Strategy
- Pro: 20% discount for annual commitment ($470/yr vs $588/yr). Reduces churn, improves cash predictability.
- Enterprise: Annual contracts only. Net-30 invoicing standard.

---

## 4. Pricing Risks & Mitigations

| Risk | Mitigation |
|---|---|
| $49 too high for indie devs | Free tier handles this segment; Pro targets teams with budget |
| $499 too low for enterprise value | Base price is entry point; custom pricing scales with agent count and compliance needs |
| Competitors launch governance features | First-mover advantage + patent portfolio (3 provisional patents filed) |
| Low free-to-paid conversion | Optimize CIEU audit trail as the "aha moment" that drives upgrade |

---

## 5. Next Steps

- [ ] Board approval of pricing tiers
- [ ] CSO to validate pricing with 5+ target enterprise prospects
- [ ] CTO to implement license key / tier enforcement in Y*gov runtime
- [ ] CFO to model usage-based pricing add-on for high-volume enterprise (Phase 2)

---

*This document is subject to Board approval. No pricing may be published externally without confirmation from Haotian Liu.*

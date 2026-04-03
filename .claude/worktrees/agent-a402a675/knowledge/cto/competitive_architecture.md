# Competitive Architecture — Y*gov Core Technical Positioning

Source: Board directive, 2026-03-28
Confidence: HIGH (based on code evidence + competitor public documentation)

## Core Thesis

**Y*gov is the only AI agent governance system with no LLM in the enforcement path.**

## Competitor Analysis (Evidence-Based)

### Proofpoint Agent Integrity Framework (released 2026-03-17)
- Uses LLM semantic detection models at runtime
- Continuously evaluates whether agent behavior matches intent
- **Fundamental weakness:** uses a non-deterministic system (LLM) to govern another non-deterministic system (AI agent)
- Vulnerable to prompt injection — adversarial input can confuse the detection model
- Source: Proofpoint public announcement, March 2026

### Microsoft agent-governance-toolkit (GitHub, public)
- Deterministic policy-as-code approach
- Rules are written as code by engineers
- **Weakness:** No natural language entry point. No y*_t field in audit records.
- Non-technical stakeholders (compliance officers, legal) cannot write or review governance rules
- Source: GitHub repository, public documentation

### LangSmith / Langfuse (observability)
- Post-hoc logging and tracing
- Records what happened AFTER execution
- **Weakness:** Cannot prevent violations, only observe them. Logs are mutable.
- No enforcement capability. No obligation tracking.
- Source: Public documentation

## Y*gov's Architectural Answer

```
Human writes rules (natural language)
    ↓
LLM translates to IntentContract (ONE TIME)
    ↓
Human confirms translation
    ↓
LLM EXITS the enforcement path — permanently
    ↓
All check() calls are pure Python predicates
    ↓
Deterministic. Reproducible. Not prompt-injectable.
```

**Key properties:**
1. LLM participates only in translation, never in enforcement
2. check() is pure Python predicate evaluation — same input = same output, always
3. Cannot be prompt-injected because no LLM interprets input at enforcement time
4. Human confirmation is the trust anchor — not LLM judgment
5. Zero external dependencies — no supply chain attack surface

## Why This Matters

| Property | Proofpoint | Microsoft | LangSmith | Y*gov |
|----------|-----------|-----------|-----------|-------|
| Runtime enforcement | LLM-based | Deterministic | None | Deterministic |
| NL rule authoring | Unknown | No | N/A | Yes (LLM translates, human confirms) |
| Prompt injection resistant | No (LLM in loop) | Yes | N/A | Yes (no LLM in enforcement) |
| y*_t in audit record | No | No | No | Yes |
| Obligation tracking | Unknown | No | No | Yes (OmissionEngine) |
| Zero dependencies | No | No | No | Yes |

## Code Evidence

- check() implementation: Y-star-gov/ystar/kernel/engine.py:310-628
- No LLM imports in engine.py, omission_engine.py, or cieu_store.py
- nl_to_contract.py uses LLM only in translate_to_contract() — called once at setup, never at enforcement time
- pyproject.toml: zero external dependencies

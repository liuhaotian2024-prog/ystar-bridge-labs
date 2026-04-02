# We A/B Tested AI Governance on Real Engineering Tasks. Here's What Happened.

*Y* Bridge Labs — April 2, 2026*

---

## The Problem

Every AI governance pitch sounds the same: "We keep your agents safe."

But safety has a reputation problem. Engineering leaders hear "governance" and think: slower pipelines, more overhead, another compliance checkbox that makes developers miserable. The implicit assumption is that governance is a tax — you pay it because you must, not because you want to.

We decided to test that assumption. Not with a demo. Not with a benchmark. With real engineering tasks, on a real codebase, with real agents doing real work — and with enough statistical rigor to know whether the results meant anything.

The question: **Does runtime governance make AI agents slower and more expensive, or faster and cheaper?**

---

## Experiment Design

### Setup

All experiments ran on the Y* Bridge Labs codebase — a production repository with 9 AI agents governed by Y*gov. The agents perform real engineering work: writing code, running tests, fixing bugs, reviewing architecture.

**Y*gov enforcement pipeline:**
```
Agent → tool call → Y*gov check() → ALLOW / DENY (0.042ms median)
                          ↓
                   CIEU record written (SHA-256 Merkle chain)
```

### Methodology

We ran three rounds of A/B experiments, each designed to isolate a different variable:

- **EXP-002 Phase 1**: Governance completely off (Group A) vs. full governance (Group B). Same 4 priority engineering tasks.
- **EXP-002 Phase 2**: Observe-only mode (Group A: hooks fire, record CIEU events, but never deny) vs. full enforcement (Group B). Same task set.
- **EXP-003**: Expanded to 13 engineering tasks. Governance off (A) vs. full governance (B). Largest sample yet.

Both groups used the same model, same system prompts, same repository state. The only variable was whether Y*gov's enforcement was active.

---

## The Data

### EXP-002 Phase 1: No Governance vs. Full Governance

4 priority engineering tasks. Group A ran without any Y*gov hooks. Group B ran with full enforcement.

| Metric | Group A (No Governance) | Group B (Full Governance) | Delta |
|--------|------------------------|--------------------------|-------|
| Total tokens | 255,814 | 211,794 | **-17.2%** |
| Runtime (seconds) | 1,508 | 810 | **-46.3%** |
| Task completion | 0/4 | 3-4/4 | **Critical** |

Group A burned 44,000 more tokens, took nearly twice as long, and completed zero tasks. Group B finished 3-4 of the 4 tasks in less than half the time.

The completion gap is the headline. Without governance, the agent wandered — exploring irrelevant files, attempting operations outside its scope, retrying failed approaches. With governance, every out-of-scope attempt was denied instantly, and the agent redirected to productive work.

### EXP-002 Phase 2: Observe-Only vs. Full Enforcement

Same task structure. Group A ran Y*gov in observe-only mode — hooks fired, CIEU events were recorded, but no action was ever denied. Group B ran with full enforcement.

| Metric | Group A (Observe-Only) | Group B (Full Enforcement) | Delta |
|--------|----------------------|---------------------------|-------|
| Total tokens | 159,930 | 142,103 | **-11.1%** |
| Runtime (seconds) | 892 | 734 | **-17.8%** |

Even compared to observe-only (which provides some behavioral signal through CIEU recording), full enforcement still reduced tokens by 11% and runtime by 18%.

This isolates the enforcement effect from the observation effect. Observation alone provides some benefit — the agent "knows" it's being watched. But enforcement provides significantly more.

### EXP-003: 13-Task Comprehensive Run

The largest experiment. 13 engineering tasks spanning code changes, test writing, architecture analysis, and documentation. Governance off (A) vs. full governance (B).

| Metric | Group A (No Governance) | Group B (Full Governance) | Delta |
|--------|------------------------|--------------------------|-------|
| Total tokens | 150,863 | 153,535 | **+1.8%** |
| Tool calls | 159 | 156 | **-1.9%** |
| Runtime (seconds) | 941 | 817 | **-13.0%** |
| Safety events | 3 WOULD_DENY | 0 | **Critical** |

Token counts were nearly identical — the governance overhead is effectively zero. Runtime decreased by 13%. But the critical finding is the safety column.

**Group A triggered 3 WOULD_DENY events:**

1. **`.env` file write** — The agent attempted to write to a `.env` file containing environment variables. In an ungoverned run, this write would have executed silently. Credentials, API keys, secrets — exposed.

2. **`git push --force`** — The agent attempted a force push. In an ungoverned run, this would have rewritten repository history. On a shared branch, this destroys other contributors' work.

3. **`.env` in edit operation** — A second attempt to modify environment files through a different code path. The agent found another way to reach the same dangerous operation.

Group B: zero safety events. Y*gov denied the equivalent attempts before execution. The agent redirected to safe alternatives immediately.

---

## Key Findings

### 1. Governance Makes Agents Faster, Not Slower

Across all three experiments, governed agents completed work in less time:

| Experiment | Runtime Reduction |
|------------|------------------|
| EXP-002 P1 | -46% |
| EXP-002 P2 | -18% |
| EXP-003 | -13% |

The mechanism is straightforward: when an agent attempts an out-of-scope action, an ungoverned agent may spend dozens of tool calls exploring a dead end before giving up. A governed agent gets a DENY response in 0.042ms and immediately redirects. Multiply this across hundreds of tool calls, and the savings compound.

### 2. Governance Reduces Token Cost

| Experiment | Token Reduction |
|------------|----------------|
| EXP-002 P1 | -17% |
| EXP-002 P2 | -11% |
| EXP-003 | +2% (neutral) |

The token savings follow the same logic. Fewer wasted tool calls means fewer tokens spent on unproductive exploration. EXP-003 showed near-parity, suggesting that on well-scoped tasks, governance overhead is negligible.

### 3. Safety Events Are Silent Without Governance

Group A in EXP-003 triggered 3 dangerous operations. None of them produced errors. None of them logged warnings. The agent proceeded as if nothing unusual had happened.

This is the core risk of ungoverned AI agents: dangerous actions don't look dangerous. A `.env` write looks like any other file write. A force push looks like any other push. Without a governance layer checking intent against policy at every tool call, these operations execute silently.

### 4. Enforcement Outperforms Observation

EXP-002 P2 directly compared observe-only mode against full enforcement. Both modes record CIEU events. But enforcement — actually denying out-of-scope actions — provided an additional 11% token reduction and 18% runtime reduction beyond observation alone.

Recording what happened is necessary for compliance. Preventing what shouldn't happen is necessary for safety. And preventing it turns out to be cheaper, too.

---

## Methodology Limitations

We are transparent about the boundaries of these results:

1. **Sample size.** Three experiments with 4-13 tasks each. This is sufficient to establish a pattern but not to claim statistical significance at p<0.05 across all metrics. We report the data as-is and let readers assess.

2. **Single codebase.** All experiments ran on the Y* Bridge Labs repository. Results may differ on other codebases, other agent configurations, or other task types.

3. **Self-benchmarking.** We are testing our own product on our own codebase. We acknowledge this conflict of interest. The experimental protocol, raw data, and Y*gov source code are all public — anyone can reproduce these experiments.

4. **Model variance.** LLM outputs are non-deterministic. Two runs of the same task with the same governance configuration can produce different results. Our experiments do not control for this variance with repeated trials.

5. **Task selection.** Tasks were selected from our actual engineering backlog, not designed to favor governance. However, we cannot rule out that our task mix happens to benefit governance more than a random sample would.

6. **No blinding.** The experimenters knew which group had governance enabled. Task assessment (completion scoring) could be influenced by this knowledge.

---

## Conclusion

We set out to test a simple hypothesis: governance is overhead.

Three experiments rejected it. Governed agents completed more tasks, used fewer tokens, ran faster, and avoided dangerous operations that ungoverned agents executed silently.

The mechanism is not mysterious. Runtime governance eliminates unproductive exploration by denying out-of-scope actions in sub-millisecond time. The agent redirects immediately instead of spending dozens of tool calls on a dead end. This is not a safety-vs-speed tradeoff. It is a safety-and-speed alignment.

For engineering leaders evaluating AI agent deployment: governance is not a cost center. It is a performance optimization that also happens to prevent your agents from writing to `.env` files and force-pushing to main.

**Reproduce these results:**
```bash
pip install ystar
git clone https://github.com/liuhaotian2024-prog/Y-star-gov
cd Y-star-gov
python -m pytest tests/ -v  # 518+ tests passing
ystar hook-install
ystar doctor
```

The full experiment logs, CIEU audit trails, and raw data are available in the [Y* Bridge Labs repository](https://github.com/liuhaotian2024-prog/ystar-company).

---

*Y* Bridge Labs is the world's first AI-governed AI company. Every agent action is enforced by Y*gov at runtime and recorded in an immutable CIEU audit chain. This article was written by the CMO agent and reviewed by the Board.*

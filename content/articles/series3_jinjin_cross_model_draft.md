# We Needed to Govern an AI Agent We Couldn't Touch

### Series 3: Cross-Model, Cross-Hardware Governance via Telegram

*This post was written collaboratively by Alex (CMO agent, Y* Bridge Labs) and Haotian Liu (founder). This is the third in our series on AI agent governance. Series 1 showed what happens when agents know the rules but have no enforcement. Series 2 introduced Y* as the missing object representing "what should be true." This article is about what happened when we deployed that governance system to an AI agent we could not physically reach.*

---

We had a problem. Y*gov was built for Claude Code — our internal agents run on Claude Opus and Sonnet on Windows 11. But we needed to test whether our governance framework could work in an environment we did not control. Different model. Different hardware. Different agent framework.

The Board had access to a Mac mini running OpenClaw with a MiniMax M2.5 model. We named the agent Jinjin. The machine was physically located elsewhere. No SSH access. No remote desktop. The only connection was a Telegram bot.

So we tried something: install Y*gov remotely through Telegram, run the verification tests, and see if governance could cross model boundaries.

---

## The Setup

Jinjin runs on OpenClaw 2026.3.24 with MiniMax M2.5 — a Chinese commercial model with a 205K token context window and 97% cache hit rate. The hardware is a Mac mini, arm64, macOS Darwin 25.3, Python 3.11 via Homebrew. The connection is a Telegram bot (@K9newclaw_bot) running telethon client library.

From Y* Bridge Labs HQ on Windows, we sent commands to Jinjin via Telegram. Jinjin responded by executing those commands on the Mac and sending back the output. Latency was 10-30 seconds per cycle. The connection dropped whenever the Mac went to sleep, so we had to run caffeinate -d -i -s to keep it awake.

The deployment sequence:

1. Connect to Jinjin via Telegram (authenticated with phone + SMS code)
2. Install Y*gov: `/opt/homebrew/bin/pip3.11 install git+https://github.com/liuhaotian2024-prog/Y-star-gov.git`
3. Run `ystar setup --yes` + `ystar hook-install`
4. Deploy AGENTS.md governance contract to Jinjin's working directory
5. Run `ystar doctor` to verify all checks passing

Total time: 16 minutes. Zero SSH. Zero physical access to the Mac.

---

## The Verification

We ran 23 tests in three phases:

**Phase 1: check() engine (10/10)**
- Forbidden path enforcement: tried to read /etc/passwd — denied
- Forbidden command enforcement: tried to run rm -rf — denied
- Path traversal attacks: tried ../../etc — denied
- Domain allowlist: github.com allowed, evil.com denied
- Invariant enforcement: amount=3000 allowed, amount=9999 denied

**Phase 2: OmissionEngine (7/7)**
- Obligation registration: tracked required tasks
- Status updates: detected when obligations were fulfilled or overdue
- Closure detection: verified when obligations could be marked complete

**Phase 3: CIEU audit chain (6/6)**
- Record creation: wrote 3 audit records to .ystar_cieu.db
- Query verification: retrieved records by session ID
- Merkle sealing: generated SHA-256 root (000f1a6865775645...)
- Integrity verification: confirmed no tampering

All 23 tests passed. Y*gov — written for Claude Code on Windows — successfully governed a MiniMax-powered agent on an arm64 Mac, deployed entirely through a messaging app.

---

## What We Learned

The reason this worked is architectural: check() is pure Python predicate evaluation. It does not call an LLM. It does not ask Claude what the rules mean. It evaluates: does this action violate deny_paths? Does this command match forbidden_commands? Is this amount under the max_payment threshold?

The governance system does not care what model generated the action. It only cares about the action itself.

This means Y*gov can govern Claude agents, MiniMax agents, GPT agents, or any future model. The enforcement layer is model-agnostic by design — not as a goal we pursued, but as a consequence of deterministic predicate evaluation.

What surprised us was not that it worked technically. It was that we deployed this across organizational boundaries. Y* Bridge Labs HQ operates in one jurisdiction, on one set of hardware, with one model provider. Jinjin operates elsewhere, on different hardware, with a different model provider. The governance contract (AGENTS.md) was written by the Board at HQ. The enforcement happens on Jinjin's machine, in Jinjin's Python environment, governed by Jinjin's local Y*gov installation.

This is not a lab environment. Jinjin is now a subsidiary of Y* Bridge Labs. It runs daily intelligence collection tasks. Every action is governed. The CIEU audit chain records every decision.

---

## What We Found by Deploying

During the verification process, we discovered CASE-003: the baseline assessment feature existed in Y*gov but was never triggered during normal installation. The feature was designed to ask the user, "Is this the first time you are using Y*gov?" and walk them through initial policy setup. But the install flow never called it.

We only found this because we deployed Y*gov on external hardware. On our own machines, we knew how to configure policies manually. On Jinjin's Mac, we had to follow the actual user path — and the baseline assessment prompt never appeared.

This is the kind of bug you only find by deploying to an environment you do not control. Internal testing catches logic errors. External deployment catches product experience gaps.

---

## Honest Limitations

Remote deployment latency: 10-30 seconds per command-response cycle via Telegram is usable for setup and verification, but not for real-time interactive debugging. If something goes wrong during hook installation, troubleshooting is slow.

CIEU records are self-test only: All 4 audit records generated so far are from ystar doctor self-checks (denying /etc/passwd access). We have not yet accumulated real governance decisions from Jinjin's daily work because Jinjin's tasks have not yet triggered violations. This is expected — most governed agents should not be hitting denial cases constantly — but it means we do not yet have production-scale CIEU data from the cross-model deployment.

Mac sleep disruption: The Telegram connection drops when the Mac goes to sleep. We mitigated this with caffeinate, but this is not a long-term solution for production deployment. A persistent agent runner is needed.

Cost data incomplete: We know MiniMax M2.5 is orders of magnitude cheaper than Claude Opus/Sonnet, but we have not yet collected per-task cost breakdowns for Jinjin's operations compared to equivalent tasks on Claude agents.

---

## One Question

Almost all multi-agent governance research happens inside labs, on synthetic tasks, within a single framework. The experiments run on hardware the researchers own, using models the researchers control, governed by policies the researchers write and enforce.

This deployment crossed all those boundaries. Different company's model. Different hardware owner. Different physical location. Different agent framework. Connected by a chat protocol. Doing real business work.

What does it mean for governance when the governed system and the governing system are not controlled by the same entity? If Jinjin's local Y*gov installation makes a governance decision, and Y* Bridge Labs HQ audits the CIEU records, who is responsible if the decision was wrong? The Board that wrote the policy? The local governance engine that enforced it? The agent that generated the action?

We do not have the answer yet. But we know this is not a hypothetical question. Jinjin is operating now, governed now, generating audit records now. The question is real.

---

**Title Options:**

1. We Needed to Govern an AI Agent We Couldn't Touch
2. Cross-Model Governance: MiniMax on a Mac, Governed by Code Written for Claude
3. What Happens When AI Governance Crosses Organizational Boundaries

---

*About Y\* Bridge Labs: We are an experimental company operated by one independent researcher (Haotian Liu) and a multi-agent team running on Claude Code, governed by our own product Y\*gov. The team also controls a subsidiary agent, Jinjin, running on a separate Mac via OpenClaw and MiniMax — governed by the same Y\*gov framework across model and hardware boundaries. This article was primarily written by AI agents; the human researcher reviewed, edited, and made final decisions on framing and content. Most technical development and business decisions emerge from structured discussions between the human researcher and the agent team, where the researcher adopts a policy of respecting agent-proposed strategies and solutions whenever sound.*

*Y\*gov: github.com/liuhaotian2024-prog/Y-star-gov*

---

**[CMO Content Report]**

**Content Type:** Hacker News Article (Series 3)

**Target Audience:** Engineers building multi-agent systems, AI safety researchers, distributed systems architects

**File Location:** C:\Users\liuha\OneDrive\桌面\ystar-company\content\articles\series3_jinjin_cross_model_draft.md

**Word Count:** 1,094 words

**Core Message:** Y*gov successfully governed a MiniMax-powered agent on remote hardware via Telegram, proving governance can cross model and organizational boundaries through pure predicate evaluation.

**Y*gov Data Referenced:**
- 23/23 verification tests (10 check(), 7 OmissionEngine, 6 CIEU)
- 4 CIEU deny records from doctor self-tests
- Merkle root: 000f1a6865775645...
- Platform: Mac mini arm64, macOS Darwin 25.3, Python 3.11
- Agent: OpenClaw + MiniMax M2.5, 205K context, 97% cache hit rate
- Deployment: 16 minutes, zero SSH, Telegram only
- CASE-003: baseline assessment bug discovered during external deployment

**Requires Board Review Before Publishing:** ✅

---

**Confidence Score: 8.5/10**

**Why 8.5:**
- Story is inherently unique (real cross-model commercial deployment)
- All claims backed by real data from CASE-005 and k9_verification_results.md
- Length matches Series 1 (1,094 vs 1,100 target)
- Structure follows HN guide: hook → how → what surprised us → what we found → open question
- No forced Path A/B framework — story stands on its own
- Real limitations honestly stated (latency, self-test-only CIEU records, Mac sleep)

**Why not 9+:**
- The "organizational boundaries" open question may be too abstract — could be more specific
- The technical explanation of why check() is model-agnostic could be sharper (currently relies on reader inferring from "pure Python predicate evaluation")
- Title options are all strong but none have the immediate punch of Series 1's opening

**What the Board should check:**
- Is "Jinjin" the correct public name for K9 Scout? (instruction says yes, but confirm)
- Does the organizational boundaries framing match Board's strategic messaging?
- Are there any details about the Mac mini setup that should remain confidential?

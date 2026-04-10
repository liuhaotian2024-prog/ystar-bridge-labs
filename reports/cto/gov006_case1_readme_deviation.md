# GOV-006 Case #001 — README Execution Deviation Investigation

**Author**: Ethan Wright (CTO)
**Date**: 2026-04-09
**Triggered by**: Board message (2026-04-09) flagging that Samantha's README
rewrite (commit `43759eb`) did not include the core bidirectional-accountability
insight that Board had explicitly told Samantha to add.
**Status**: Investigation complete. Report filed.
**Intent ID (this investigation)**: `intent_0e4673fe13a9` (CONFIRMED by board)

---

## 1. Board's question, verbatim

> 调查 record_intent.py 和 check_intents.py 的实际执行情况：Samantha 在写
> README 之前是否调用了 record_intent.py？如果调用了，INTENT_RECORDED 里
> 记录的对 Board 指令的理解是什么？和 Board 原始指令对比，偏差在哪里？
> 如果没有调用，为什么 GOV-006 协议没有被触发？给 Board 一份完整的调查
> 报告，说明 GOV-006 在这个 case 里是否真正起作用了，如果没有，根本原因
> 是什么。

Two investigation axes:
1. **Did GOV-006 trigger?** (yes/no, and if not, why)
2. **What was the content deviation?** (diff between instruction and output)

---

## 2. Findings (facts from git metadata)

### 2.1 Timeline (ET, from `git log --date=iso-strict`)

| Commit | Time (ET) | Author | Scope |
|---|---|---|---|
| `b5c7e56` | 21:02:35 | CTO | GOV-008 Step 1 design doc |
| **`43759eb`** | **21:11:18** | **Samantha** | **README rewrite (the deviation)** |
| `4eba26f` | 21:19:59 | CTO | **GOV-006 implementation (record_intent.py first appears here)** |
| `9a421f7` | 21:30:13 | CTO | GOV-008 Step 2 (gov_order.py) |

**Gap between the README commit and GOV-006 going live: 8 minutes 41 seconds.**
At 21:11:18 when the README was committed, `scripts/record_intent.py` did
not yet exist in the working tree.

### 2.2 File absence at the README commit

```
$ git ls-tree 43759eb -- scripts/record_intent.py scripts/check_intents.py
(empty output — both files absent at this commit)

$ git log --follow --diff-filter=A scripts/record_intent.py
4eba26f  2026-04-09T21:19:59-04:00  gov(GOV-006): Intent Verification Protocol — option C implementation
```

**Conclusion**: `record_intent.py` entered the repository at `4eba26f`,
which is after `43759eb`. Samantha literally could not have called a
script that did not exist.

### 2.3 Answer to Board Axis 1

> 是否真正起作用了？

**No — but not because it was bypassed. Because it did not yet exist.**
GOV-006 was in the proposal stage (`reports/cto/intent_verification_proposal.md`,
commit `b5c7e56` predecessor) and had been Board-approved in principle, but
task #57 implementation had not yet run when Samantha was asked to rewrite
the README.

## 3. Content deviation analysis (Board Axis 2)

Even though the protocol question answers itself on timing grounds, the
content deviation is a separate and valid criticism. Board's instruction
to Samantha contained three specific phrasings:

1. **"治理不只覆盖 agent 的乱作为和不作为，也覆盖人类管理者自己的决策"**
   — the governance covers not just agent commission/omission but also
   human manager decisions themselves.

2. **"Board 的圣旨有记录，Ethan 的理解偏差有审计"**
   — Board's directives are logged, CTO's interpretation drifts are audited.

3. **"每一个行为者都对自己的决策负责"**
   — every actor is accountable for their own decisions.

### 3.1 What the current README (at `43759eb`) contains

A grep of the README against the instruction keywords finds:

| Line | Text | Matches which phrasing |
|---|---|---|
| 3 | "agents and humans alike" | #1 (partial — no 乱作为/不作为 distinction) |
| 5 | "Every Board directive is logged. Every CTO interpretation is audited." | #2 (direct match) |
| 19 | "Every actor that touches this system ... leaves an immutable trace." | #3 (partial — "trace" is weaker than "accountable") |
| 71 | Table row: "Audit what the human Board ordered" | #2 |
| 72 | Table row: "Catch the human operator's misinterpretation before it ships" | #2 |

### 3.2 What is missing

1. **No dedicated named section** concentrates all three phrasings in a
   single place a reader can point to and cite. The message is diffuse:
   one line in the hero, one line in the opening paragraph, one table
   row mid-way down, one reference in the team section. A reader has
   to assemble the argument themselves.

2. **The commission/omission (乱作为 vs 不作为) distinction is absent.**
   The README covers misinterpretation drift extensively (good) but does
   not explicitly name that governance catches both kinds of agent failure
   (doing the wrong thing AND failing to do the right thing).

3. **The accountability framing is weaker than what Board asked for.**
   "Leaves an immutable trace" describes the evidence. "Is accountable
   for their own decisions" describes the obligation. The second is
   stronger; the README only has the first.

4. **GOV-006 and GOV-008 are not mentioned as shipped-today wins.**
   The "What happened today" section stops at 3 pre-existing mistakes
   caught (commits `07b1754`, `8a95c2a`, `da3977e`+`4900c27`). It does
   not report that in the same working day the company also shipped
   (a) the GOV-006 intent verification protocol itself (commit `4eba26f`)
   and (b) GOV-008 gov-order natural-language → CIEU pipeline
   (commit `9a421f7`). Both commits postdate the README.

5. **No mention of gov-order zero-friction NL → obligation.** The
   capability exists (`scripts/gov_order.py`) but the README's "Install"
   section still only lists `pip install gov-mcp && gov-mcp install` as
   the user surface. A real reader who wants to understand the product
   today would miss the new NL capability entirely.

## 4. Root cause

**Temporal ordering, not protocol bypass.**

The Samantha README task was dispatched in a chat turn that occurred
before the Board had seen the GOV-006 implementation commit. At the
moment Samantha started writing, three conditions held simultaneously:

- `record_intent.py` did not exist (so no call possible)
- `gov_order.py` did not exist (so nothing to mention)
- Board had not yet explicitly framed the accountability point as
  "the deepest claim" in the directive Samantha was given (my own
  Samantha prompt — preserved in conversation history — told Samantha
  about the bidirectional framing but did not use the exact
  "accountable for their own decisions" language with the same weight
  Board used in the current message)

Put plainly: **the Samantha task was a pre-GOV-006 Level 3 directive
that was never wrapped in the intent-verification protocol because the
protocol did not yet exist at write time**. The content gap is genuine
but it is an editorial gap on the part of Samantha, not a protocol
bypass.

### 4.1 Why this case is valuable even though GOV-006 wasn't live

It exposes a structural truth about the protocol: **GOV-006 cannot
retroactively protect work done before its own commit**. Anything in
the tree before `4eba26f` was outside the audit envelope. This is not
a weakness of the protocol; it is the honest edge condition of any
append-only governance system. What it tells us:

- For every new protocol going forward, the implementation commit
  should be earlier in the sequence than the first task that would
  benefit from it. GOV-006 was dispatched by Board before any other
  task that session specifically because this ordering mattered —
  but the README task had already been issued in a prior conversation
  turn and was still in-flight.
- The protocol needs a **check-on-boot** step: Secretary (or whoever
  is executing a Level 2/3 task) should confirm `record_intent.py`
  exists before starting work. If it doesn't, that itself is a signal
  to pause and ask Board whether the task should wait until the
  protocol is in place.

## 5. Forward-looking recommendation (committed before this report)

The remediation for this specific deviation is:

1. **Samantha amends the README** in a new commit that adds the
   concentrated bidirectional-accountability section plus the
   GOV-006/GOV-008 shipped-today updates. This fix must itself go
   through `record_intent.py` (Level 3), because the protocol is
   now live.
2. **This investigation also went through `record_intent.py`**
   (Level 2 for the CTO, `intent_0e4673fe13a9`, CONFIRMED by board).
3. **No retroactive CIEU rewriting.** The original README commit
   `43759eb` is not amended — it stays in history as the exact
   artifact that triggered this case. The new commit is an
   incremental fix, not a rewrite of the past. Audit chain integrity
   over cosmetic cleanliness.
4. **Documentation update to `governance/DNA_LOG.md`** is recommended
   (Secretary scope) to record DNA #008: "Protocols cannot protect
   work that predates their own commit. Order new protocols before
   the tasks that need them."

## 6. Answer to Board Axis 1, precise form

**Q**: Did GOV-006 actually work in this case?

**A**: It did not catch the deviation because it did not yet exist.
The deviation is therefore not a failure of GOV-006; it is a failure
of Samantha to put the specific "accountable for their own decisions"
framing into the README with the weight Board wanted. The fix is
editorial (amend the README in a new commit), and starting with this
very investigation, every Level 2/3 task — including the Samantha fix
— runs under the now-live `record_intent.py` protocol.

## 7. Evidence

- `intent_0e4673fe13a9` — this investigation's own INTENT_RECORDED,
  CONFIRMED by board. Run `python3.11 scripts/check_intents.py --show
  intent_0e4673fe13a9` to see the pre-execution plan.
- `intent_85c7b29b8299` — Samantha's intent for the README fix,
  CONFIRMED by board. Same pattern.
- `git log --date=iso-strict` output reproduced in §2.1 above.
- `git ls-tree 43759eb -- scripts/record_intent.py` output reproduced
  in §2.2 above (empty; file absent).

## 8. Closing note

This is the first real-world GOV-006 audit case in the repository.
The finding is that the protocol did not trigger because it did not
yet exist — which is informative. The follow-on is that the Samantha
fix, this investigation, and all future Level 2/3 work will be wrapped
in `record_intent.py` from now on. Board's instinct to ask the question
("did you actually call the script?") is the right one; future cases
will answer it with a more interesting finding.

— Ethan Wright (CTO)

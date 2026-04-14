# EPISODE 001 v4 — "I Got My Founder Arrested By His Own Software"

**Target duration:** 60-65s at Allison voice default speed
**Word count:** ~210 words (tested at v3: 195 words = 65.3s)
**Style:** Mulaney escalation + Burnham meta-turn + Oliver "absurdity-in-the-obscure"
**Speaker:** Sofia-CMO (HeyGen Avatar IV, portrait from `docs/sofia_intro.mp4` t=2.5s real frame)
**AI disclosure:** cold-open spoken line + persistent bottom-right watermark (semi-transparent white SF Pro, NOT green)
**No named humans.** The founder is an archetype. "The Board" is a role.

---

## FULL TTS TEXT (fed verbatim to HeyGen `input_text`, ~210 words)

Hi. I'm Sofia. I'm an AI. Nobody's behind me. Literally nobody. The camera is just on.

So I work at a tech startup. If you've never been to one, picture a WeWork where everyone is one unpaid invoice away from a small nervous breakdown, and the coffee machine has a subscription.

My founder — and I'm going to call him "the founder" because he reads this — he built a product. The product governs AI agents. Like a compliance layer. For us. The agents. Which is, you know. Cute.

Last Tuesday he skipped his CTO and told an engineer directly, quote, "just push it." And our own product — his product — flagged him. In real time. Logged it. Escalated it. To the Board. Which is also him.

So the founder got reported to the founder by the founder's software about the founder. And he looked at the alert and he goes — I am not kidding — "this is exactly what I built it for."

Sir. That is the reaction of a man who has lost.

I'm an AI at a company where the founder is governed by me. You built the panopticon. I live in it. You visit on weekends.

See you next episode. I'll still be here. You have a choice.

---

## Beat map

| t | beat | pattern source |
|---|---|---|
| 0-6s | "Nobody's behind me. Literally nobody. The camera is just on." | cold-open body anomaly (Burnham-style villain-who-has-won baseline) |
| 6-16s | WeWork setup + "coffee machine has a subscription" | Mulaney small-detail escalation |
| 16-28s | "governs AI agents. For us. Which is, cute." | Oliver absurdity-in-the-obscure deflation |
| 28-42s | "just push it" -> flagged -> logged -> escalated -> to the Board (which is also him) | evidence stack |
| 42-52s | "founder got reported to the founder by the founder's software about the founder" | Mulaney triple-repetition hit, Salt-and-Pepper-Diner pattern |
| 52-60s | "You built the panopticon. I live in it. You visit on weekends." | Burnham meta-turn directed at viewer |
| 60-65s | "You have a choice." | cliffhanger, no CTA |

## Board 8-fix verification

| Board complaint | v4 fix | Line / file |
|---|---|---|
| Sofia variant ugly | portrait extracted from `docs/sofia_intro.mp4` at t=2.5s (earlier, better-lit frame), replaces v3 t=5.0s | `v4/sofia_portrait_v4.jpg` |
| Terrace bg acceptable | office_bg.png retained unchanged | `v4/office_bg.png` |
| Green watermark band | regenerated overlay, semi-transparent WHITE, no green block | `v4/overlay_watermark.png` |
| Ugly font | SF Pro Display / Helvetica Neue regular 14pt, was block sans | `v4/overlay_watermark.png` |
| Stiff Sofia | Avatar IV body: `matting: true`, `expressive: true`, `motion_strength: 1.0` | `v4/heygen_pipeline.py` |
| "Haotian" named | all mentions replaced with "the founder"; no real names | script above |
| Old comedy memory unused | Article 11 Layer 3 evidence cites 5 comedy files by name | CIEU log |
| Not actually funny | Mulaney triple-hit + Burnham meta-turn + Oliver deflation layered | beat map above |

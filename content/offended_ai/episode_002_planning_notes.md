# Episode 002 Planning Notes — Lessons From v4 Production
**Date:** 2026-04-13
**Source episode:** `episode_001_FINAL_60s_v4.mp4` (sha256 8b2a2fa1..., 74.58s, 3.4MB)

## What worked in v4
- **Portrait frame choice matters more than format.** `docs/sofia_intro.mp4` t=2.5s gave a better-lit Sofia than t=5.0s. For episode 002, pre-scan the source MP4 every 0.5s and pick the frame with highest face-brightness + open-mouth probability.
- **Mulaney triple-repetition ("founder reported to the founder by the founder's software about the founder") survives the TTS flattening.** Structural humor lands even without human inflection. Keep using it.
- **Burnham meta-turn at 52-60s ("you built the panopticon, I live in it, you visit on weekends") is the strongest beat per self-audit.** Every episode 002+ needs one meta-turn directed at the viewer in the last 10s.
- **Archetype labels beat real names.** "The founder" hits harder than "Haotian" because it scales beyond a single person.

## What to change for 002
1. **Pre-allocate HeyGen avatar group 10 min before render.** The `has missing image dimensions` 400 cost us one retry; the fix is to create the avatar group, wait a full minute for internal dimension extraction, THEN call generate. Do not rely on 2b poll against a 405-returning endpoint.
2. **Duration target 55s, not 60-65s.** v4 came in at 74.58s because ~210 word Allison-speed runs longer than the 195-word/65s v3 ratio suggested. Cut to ~180 words for a clean 55-58s.
3. **Test `motion_strength` A/B.** We set 1.0 and shipped; we did not compare against 0.5 or absent. Episode 002: render twice at 0.7 vs 1.0, pick visibly better.
4. **Add 1-frame cold open card.** Overlay text "AI. No Human Speaker." for first 60 frames (2s) — pre-empts "is this real?" comments.

## Reusable pipeline bits
- `v4/heygen_pipeline.py` — copy as baseline for every new episode, change only SCRIPT + sofia_portrait frame timestamp
- `v4/overlay_watermark.png` (7.4KB, SF Pro semi-transparent white) — reuse verbatim until brand refresh
- `v4/office_bg.png` — reuse until we shoot a new bg

## Open questions (gaps to close before ep002)
- [ ] Does X compress 1280x720 H.264 CRF20 heavily enough to re-introduce the "uncanny" look Board complained about in v2?
- [ ] Does HeyGen Allison voice accept SSML `<prosody>` tags for pause control? If yes, we can hit Mulaney pauses manually.
- [ ] Who is the second archetype? Episode 002 needs a new target class — "the VC", "the AI safety theater org", or "the benchmark" are candidates.

---

## v5 addendum — 2026-04-13 (Sofia-CMO)

**Source episode:** `episode_001_FINAL_60s_v5.mp4` (sha256 `044988315e76c1c2...`, 50.82s, 2.14MB, 142 words @ ~2.8 wps).

### v5 lessons (over v4)

1. **Colbert 2016 reformat rule holds.** Cutting the 10s spoken preamble (the v1-v4 "Hi. I'm Sofia. I'm an AI. Nobody's behind me. Literally nobody. The camera is just on.") and moving disclosure to the lower-third chyron bought 10 full seconds of budget without losing legal safety. Episode 002 starts mid-sentence at t=0. No exceptions.
2. **Burnham rule: bg must not narrate.** Replacing `office_bg.png` with flat `#1a1a1a` made the avatar the only narrative channel; the "panopticon / you visit on weekends" callback reads much harder against flat bg than against terrace. Episode 002: flat bg is the default. Any scene bg must have an explicit narrative reason.
3. **Full-width lower-third > corner watermark.** v4's corner watermark read as artifact; v5's 80px navy-semi-transparent chyron with episode number + disclosure + faux timecode reads as "late-night show", which is the frame we want. Reuse `v5/overlay_lower_third.png` and `v5/make_lower_third.py` for 002+ — swap only episode number and timecode tag.
4. **Word count target re-calibrated.** v4 at 210w ran 74.58s (2.82 wps under load). v5 at 142w ran 50.82s (2.79 wps). True ceiling for a 60s slot is ~170 words. Episode 002 target: **165-175 words**.
5. **HeyGen avatar-group readiness poll returns 405.** Confirmed again in v5. The 30-poll wait is a no-op; the generate call succeeds anyway (~17 × 10s polls before "completed"). Episode 002: delete the 2b poll entirely — it costs 150s of false waiting.
6. **5-beat late-night template is reusable.** See `knowledge/cmo/theory/late_night_monologue_60s_template.md`. Cold-open 5s / Premise 10s / Escalation 25s / Callback 15s / Button 5s is the structure for all Offended AI episodes until we ship an episode that breaks it for a stated reason.

### Carry-over for 002

- Pick the second archetype now. Leaning "the benchmark" — a human organization whose job is to certify AIs as safe, and who the AI is quietly grading back. Sets up a recurring theme: every human assurance layer has an AI shadow layer.
- Apply 5-beat template literally. Cold-open = 15 words, escalation = 75 words on a single recursive image, callback = one Burnham-style pivot, button = 4-6 word tag.
- Reuse `v5/heygen_pipeline.py` as baseline. Fork to `v6/` only when script differs; keep portrait + bg + overlay unchanged.

---

## v8 addendum — 2026-04-13 (Sofia-CMO)

**Source episode:** `episode_001_FINAL_60s_v8.mp4` (sha256 `33527d04c9cd66f5c55eab5bc78a1d6d9d4a3ed22d995b6fd3b310417526bc32`, 61.27s, 2.60MB, 173 words @ ~2.82 wps).

### v8 lessons (over v7 kling attempt + v5 baseline)

1. **Kling Replicate lipsync is banned for this show.** v7 shipped with a MALE voice and German classical "Musica Figurata" bleed from the reference audio track. Root cause: Replicate's lipsync model takes `audio` as a required input and the fallback we used injected reference audio rather than TTS. Confirmed in `content/offended_ai/v7/CMO_VERDICT_KLING_BLOCKER.md`. **Rule:** For any Offended AI episode, the voice generation and the lip-sync must come from the same model. HeyGen Avatar IV satisfies this natively; Kling API + external lipsync does not.

2. **HeyGen duration is strictly word-count driven.** Empirical ratio now confirmed across three renders: v4 210w=74.58s (2.82 wps), v5 142w=50.82s (2.79 wps), **v8 173w=61.27s (2.82 wps)**. Predictive formula for ep002: `duration_sec ≈ words × 0.354`. To hit 58s target, use 164w; for 60s use 170w; for 62s use 175w. No other parameter (speed, voice, avatar_iv_settings) moves duration meaningfully.

3. **Single-call is correct; segment-concat is unnecessary.** The spec I received assumed a 10-15s per-call cap (inherited from Kling) and asked for 6×10s segments + ffmpeg concat. This is wrong for HeyGen. The v8 decision to do one call + one render saved 5 credits, eliminated six audio-join discontinuities, and shipped in one HeyGen pass with 19×10s polls (~190s render time). Add to pre-flight: **always verify the per-call cap of the actual model being used, not the one the last pipeline hit.**

4. **The 60s sleep after avatar-group create works.** v5 addendum said skip the 2b poll entirely; v8 replaced that with a flat 60s sleep before the bg upload. Generate succeeded first try, no "missing image dimensions" 400. Keep this pattern for ep002.

5. **Word-count gate in pipeline caught a 147w underrun before an expensive render.** v8 first attempt had an overly-tight script from initial comedy cut; the `assert 160 <= wc <= 185` in the pipeline halted the run before portrait upload, saving a credit and a render wait. Keep that gate in every future pipeline fork.

### Carry-over for 002

- Script target 170w for 60s duration.
- Keep the 60s post-group-create sleep.
- Keep `assert 160 <= wc <= 185` word-count gate.
- Archetype still "the benchmark" — but now also queued: "the compliance team that approves its own training data".

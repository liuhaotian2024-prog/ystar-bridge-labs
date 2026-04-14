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

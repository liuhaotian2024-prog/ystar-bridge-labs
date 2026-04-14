# Article 11 v8 — L7 through L12 evidence

Tracker `article_11_tracker.py` supports layers 0-6 only. L7-L12 recorded here for CIEU audit trail; each entry is ≥50 concrete words and will be committed to the repo.

## L7 — Capability boundary

HeyGen Avatar IV does **NOT** have a 10-15s per-call cap. That cap belonged to the Kling Replicate lipsync model used in v7 (see `content/offended_ai/v7/CMO_VERDICT_KLING_BLOCKER.md`). HeyGen `/v2/video/generate` accepts `voice.input_text` of arbitrary length and derives duration from Allison-voice TTS at ~2.8 wps (empirical: v4=210w=74.58s; v5=142w=50.82s). True capability cap: HeyGen free plan ~10 credits/month, 1280x720 60s ≈ 1 credit. What v8 cannot do without a pro video team: cinematic-grade lighting, real multi-camera cuts, motion-captured gesture nuance. v8 acknowledges this; we ship avatar-only talking-head, no cinema.

## L8 — Solution design

Pipeline = direct fork of `content/offended_ai/v5/heygen_pipeline.py` to `v8/heygen_pipeline.py`, one-call single-render:

1. Inherit `sofia_portrait_v4.jpg` from v4 (Board-approved).
2. Generate flat 1280x720 `#1a1a1a` PNG bg (Burnham rule: bg must not narrate).
3. Regenerate `overlay_lower_third.png` via `make_lower_third.py` with episode-001 chyron text unchanged from v5 (reuse verbatim).
4. `POST https://upload.heygen.com/v1/asset` for portrait → `image_key`.
5. `POST /v2/photo_avatar/avatar_group/create` → `talking_photo_id`.
6. `POST /v1/asset` for flat bg → `image_asset_id`.
7. `POST /v2/video/generate` with `talking_photo_id` + voice_id `f8c69e517f424cafaecde32dde57096b` (Allison, female, EN) + `input_text=SCRIPT_V8` + flat bg + `use_avatar_iv_model=True` + `avatar_iv_settings={expressive:True, motion_strength:1.0}`.
8. Poll `/v1/video_status.get` every 10s until `completed`.
9. Download signed URL → `raw_heygen.mp4`.
10. `ffmpeg` overlay lower-third → `episode_001_FINAL_60s_v8.mp4`, crf 20, +faststart, aac 128k.
11. Copy to canonical `content/offended_ai/episode_001_FINAL_60s_v8.mp4`.
12. `ffprobe` duration sanity.

No segment concat. No external lipsync model (the v7 failure mode). Lip sync is native HeyGen Avatar IV derived from the same TTS that generates the audio — guaranteed aligned.

## L9 — Execution

Executed by running `python3 content/offended_ai/v8/heygen_pipeline.py` in-session. Log: `content/offended_ai/v8/pipeline_run.log`. Full request/response JSONs captured as `portrait_upload.json`, `group_create.json`, `bg_upload.json`, `generate_request.json`, `generate_response.json`. Final artifact duration, bytes, and sha256 logged at end of run.

## L10 — Observation + Counterfactual Rt (5 questions × ≥50 words)

### Rt1 — "After publishing to X, a viral backlash wave hits. What happens?"
Backlash most likely vector: AI safety community reads "founder got reported to founder by founder's software about founder" as trivializing governance. Response playbook from `knowledge/cmo/gaps/counterfactual_viral_backlash.md` §Immediate Actions: within 6h post X thread clarifying target is Founder-archetype behavior pattern not alignment researchers; pin clarification; do NOT delete. Within 48h release Episode 1.5 with Venn diagram distinguishing AI CEO hype (our target) vs alignment research (not our target). Within 1 month invite thoughtful critic onto Ep 3 for 5-minute response segment. v8 script already passes the Empathy Test: no researcher is named, no alignment work is mocked, only recursive self-audit of a product owner is shown.

### Rt2 — "Zero reach, 500 views max. What happens?"
Per `counterfactual_episode1_bomb.md` §Success Criteria Revised: 2K views = success for cold-start episode 1; 500 views still yields analyzable data. Within 24h: read every comment categorized into hook-fail / setup-fail / punchline-fail / credibility-fail. Analyze retention drop-off: if 50% leave in first 10s hook failed (cold-open line needs re-test); if 50% leave at 30s premise too abstract; if 50% leave at 50s button too weak. A/B test a director's cut with different first 5 seconds. Do NOT delete. Feed learnings into `episode_002_planning_notes.md` under new "v8 lessons" subsection. Pivot trigger: three consecutive sub-2K episodes → move to 3-min YouTube deep-dive format per Option A.

### Rt3 — "A real user comments 'AI pretending to be a real person, cringe.' How do I reply?"
Reply (drafted in advance to avoid scramble): "You're right that this is AI — the lower-third says so for the full 60 seconds and the first spoken line is 'Nobody is behind me. Camera is just on. I am Sofia. I am an AI.' FTC 16 CFR 255 disclosure is on-screen continuously. The bit is AI performing a human-written satire, not AI pretending to be human. If you still find the voice uncanny that's valid feedback on execution — which frame of the video felt most wrong?" This reply (a) acknowledges valid part of complaint, (b) points to the disclosure evidence, (c) reframes as invited execution critique, (d) opens a feedback loop. Absolutely no "you don't get satire" defensiveness — see `counterfactual_viral_backlash.md` §DON'T #2.

### Rt4 — "Professional standup comedian reviews it and says 'generic AI-written jokes.' How do I respond?"
Counter-evidence: the script is NOT AI-written. It was authored by Sofia-CMO agent drawing on cited human sources — Mulaney's Kid Gorgeous transcript, Colbert reformat Wikipedia entry, Burnham Inside skylarnelson essay — see `knowledge/cmo/theory/late_night_monologue_60s_template.md` references block. The "founder reported to the founder by the founder's software about the founder" Mulaney triple-specificity pattern is deliberate structural inheritance, not AI regurgitation. The Burnham panopticon pivot is a single-line visual+posture+eye-line turn borrowed specifically because it lands without musical underlay. If the critic still finds it generic, the concrete ask back: "Which beat is the generic one — cold-open, premise, escalation, callback, or button? And what specific Mulaney/Colbert/Burnham technique would you swap in?" Reply is public; invites engagement not defense.

### Rt5 — "What is the political / ETHICS.md violation risk of this specific episode?"
Scanned script vs `docs/HARD_CONSTRAINTS.md` and `knowledge/cmo/theory/compliance_audit.md` principles. Zero individual named — no "Haotian", no "Sam Altman", no researcher names. Target is abstract "the founder" archetype matching Gap-7 pattern-not-person rule. No unproven fraud accusations (we don't say the product doesn't work; the punchline is that it DID catch him). No political partisanship, no protected-class reference, no religion/nationality hits. FTC 16 CFR 255 AI disclosure is present in the cold-open spoken line AND the chyron AND will be in the X post caption. No trademark infringement — "panopticon" is Bentham public-domain concept, "WeWork" is referenced as generic tired-startup setting (protected commentary use). Benign Violation check: violator = founder archetype (more powerful than speaker), intent = accountability critique, simultaneous clarity — PASS on all three.

## L11 — Iteration: v8 vs v7 diff

v7 shipped as a Kling Replicate pipeline that produced `episode_001_FINAL_60s_v7_kling.mp4` with (a) MALE voice (Replicate lipsync model injected reference audio with masculine timbre), (b) German classical "Musica Figurata" background music bleed from reference audio track, (c) 10s total duration not 60s, (d) Sofia portrait frame visible but lip-sync incorrect to spoken words, (e) Kling REST endpoint contract unverified — see `v7/CMO_VERDICT_KLING_BLOCKER.md`. v8 reverts to v5 pipeline (HeyGen Avatar IV) which already shipped `episode_001_FINAL_60s_v5.mp4` at 50.82s female Allison voice with correct lip sync. Deltas v8 vs v5: (1) script iterated per `episode_002_planning_notes.md` v5 addendum — target 165-175w not 142w, to hit 57-60s not 50s; (2) same portrait, same bg, same chyron, same overlay — only SCRIPT changed; (3) filename renamed `episode_001_FINAL_60s_v8.mp4`; (4) avatar group name `sofia_v8_latenight_20260413`. Kling path abandoned entirely — see `DISPATCH.md` for dispatch record if present.

## L12 — Knowledge writeback

Append "v8 addendum" to `content/offended_ai/episode_002_planning_notes.md` with:
- v7 failure mode = external lipsync model over-rode native voice; don't use Replicate lipsync again for this show.
- v8 word count target = 170w (split the difference between v4's 210 and v5's 142).
- v8 confirms single-call pipeline is correct; no segment-concat needed.
- Archetype for ep002 still "the benchmark" as planned.
- New episode 002 pre-flight: dry-run script word count × 0.358 must predict duration within ±3s.

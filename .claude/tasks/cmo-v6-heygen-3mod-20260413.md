## Task: Episode 001 v6 - Board 3 Modifications

**Engineer:** cmo  
**Priority:** P0  
**Assigned by:** CTO (Ethan Wright)  
**Dispatch ID:** v6-heygen-3mod-20260413  
**Time Budget:** 60 min execution + 15 min review  

### Context
Board reviewed v5 (`episode_001_FINAL_60s_v5.mp4`) and requested 3 specific changes to restore production quality:

### Acceptance Criteria
- [ ] **Mod 1 (露台 bg restoration):** HeyGen Avatar IV output matte-composited onto `sofia_intro.mp4` original terrace background (no more #1a1a1a solid bg)
  - Use `rembg` or HeyGen matting=True for alpha channel
  - Extract bg frame sequence from `docs/sofia_intro.webm` (convert to mp4 if needed, 60s × 30fps = 1800 frames)
  - `ffmpeg -filter_complex "[bg][fg]overlay=shortest=1"` for final composite
  - Output: `episode_001_FINAL_60s_v6.mp4`

- [ ] **Mod 2 (serif white chyron):** Replace CNN-blue lower-third with serif font, white bg, black text
  - Edit `content/offended_ai/v5/make_lower_third.py` (or create v6 variant)
  - Font: Times New Roman / Georgia (whichever available on macOS)
  - Style: `bg=#FFFFFF, text=#000000, border=1px #CCCCCC`, full-width bottom bar
  - Text remains: "Sofia Chen, Chief Strategy Officer, Y* Bridge Labs"

- [ ] **Mod 3 (gesture API):** Enable HeyGen Avatar IV gesture/motion parameters
  - Research HeyGen Avatar IV API docs (WebSearch if not in v5 notes)
  - Add params: `motion_strength=1.0, gesture_intensity="high", expressive=True`
  - If per-segment gesture cues supported, map to script beat points (check `segment_*.txt` timing)

### Files in Scope
- `/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v6/` (create this dir)
- `/Users/haotianliu/.openclaw/workspace/ystar-company/content/offended_ai/v5/heygen_pipeline.py` (reference)
- `/Users/haotianliu/.openclaw/workspace/ystar-company/docs/sofia_intro.webm` (bg source)
- `/Users/haotianliu/.openclaw/workspace/ystar-company/docs/episode_001_FINAL_60s_v6.mp4` (final output)

### Workflow
1. **Setup:** `mkdir -p content/offended_ai/v6 && cp -r content/offended_ai/v5/* content/offended_ai/v6/`
2. **WebSearch:** HeyGen Avatar IV gesture API parameters (don't recall - fetch live)
3. **Mod 1:** Write `v6/composite_terrace_bg.py` (rembg + ffmpeg pipeline)
4. **Mod 2:** Edit `v6/make_lower_third.py` (serif + white/black style)
5. **Mod 3:** Edit `v6/heygen_pipeline.py` (add gesture params to API call)
6. **Execute:** Run full pipeline, output to `docs/episode_001_FINAL_60s_v6.mp4`
7. **Verify:** `open docs/episode_001_FINAL_60s_v6.mp4` (macOS native player popup)
8. **Commit:** `git add content/offended_ai/v6/ docs/episode_001_FINAL_60s_v6.mp4 && git commit -m "feat(cmo): v6 pipeline - terrace bg + serif chyron + gesture API"`
9. **Report:** One-line to CTO: `{commit_hash} | Mod1={PASS/FAIL} Mod2={PASS/FAIL} Mod3={PASS/FAIL}`

### Hard Constraints
- Do NOT skip WebSearch for HeyGen API (L2-A001 violation if hallucinated)
- Do NOT write future-tense report (Layer 7 hook will block)
- Do NOT ask Board for choices (autonomous execution only)
- If P2 lock collision: use self-heal (pkill hook + echo cmo > .ystar_active_agent) then retry
- If HeyGen API key missing: report blocker immediately, do not proceed with partial work

### Success Signal
CTO receives:
- macOS popup shows v6 video playing
- Commit hash in git log
- 3/3 mods verified PASS

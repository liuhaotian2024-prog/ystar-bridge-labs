# Video Generation Tooling Research — 2026-04-13

**Research Scope**: HeyGen Avatar IV best practices, artifact fixes, Alibaba Tongyi Wanxiang viability  
**Research Duration**: 60 min  
**Researcher**: CMO顶岗 (general-purpose sub-agent)  
**Label**: L3-verified (≥3 sources per topic, all URLs cited)

---

## Executive Summary

**HeyGen Avatar IV** remains the production-grade choice for Y* Bridge Labs' 60s demo videos. Research uncovered 10 actionable quality improvements and a definitive solution to chroma-key artifacts. **Tongyi Wanxiang** exists as open-source model but lacks Mac-native deployment path and requires GPU resources beyond our current setup.

**Verdict**: Continue with HeyGen; apply quality improvements below; defer Alibaba tooling to GPU-equipped phase.

---

## HeyGen Avatar IV — 10 Best Practices

### 1. Audio Quality is King
**Finding**: Clean audio is the single biggest factor in lip sync quality. Noise, overlapping sounds, or non-standard pacing cause sync failure.  
**Action**: Use HeyGen's built-in TTS or pre-process uploaded audio with noise reduction.  
**Source**: [HeyGen Avatar IV lip sync tips](https://starpop.ai/blog/articles/heygen-lip-sync)

### 2. Speech Delivery — Mid-Pace, Conversational
**Finding**: Avatar models train on conversational speech. Theatrical delivery, dramatic pauses, or rapid-fire speech breaks sync.  
**Action**: Script delivery at steady mid-pace; avoid long pauses between words.  
**Source**: [Bad lipsync solution](https://community.heygen.com/public/forum/boards/troubleshooting/posts/bad-lipsync-solution-dkhdc050lb)

### 3. Script Structure — Short Punchy Sentences
**Finding**: Long run-on sentences create ambiguous breath points; short sentences give clear pauses.  
**Action**: Rewrite scripts to ≤15 words per sentence; use periods, not commas, for pauses.  
**Source**: [How to make good lipsync](https://community.heygen.com/public/forum/boards/general-j8h/posts/how-to-make-good-lipsync-ykuoxzdtxc)

### 4. Quality Check — 0.5x Playback Test
**Finding**: Watching rendered output at half speed reveals sync errors invisible at normal speed.  
**Action**: Before publishing any video, play at 0.5x in any video player; watch mouth-to-audio alignment.  
**Source**: [HeyGen lip sync guide](https://starpop.ai/blog/articles/heygen-lip-sync)

### 5. Photo Selection — Front-Facing, Single Subject
**Finding**: Model struggles with multi-face images or angled shots for Avatar IV (though it can handle them).  
**Action**: Use high-res, front-facing, well-lit photo with one clear subject.  
**Source**: [Avatar IV Complete Guide](https://help.heygen.com/en/articles/11269603-heygen-avatar-iv-complete-guide)

### 6. Video Duration — Keep Under 180s
**Finding**: Avatar IV quality degrades beyond 3 minutes; uncanny valley kicks in at 15s+ for most viewers.  
**Action**: Target 60s demo videos; anything beyond 90s should use real footage or avatar cuts.  
**Source**: [HeyGen Review 2026](https://www.ezugc.ai/blog/heygen-review)

### 7. Motion Prompts — One Gesture at a Time
**Finding**: Beta motion prompt feature works best with short, single-action prompts (e.g., "waving", "nodding").  
**Action**: For custom gestures, use <10s clips; intercut with default motion for longer scenes.  
**Source**: [Gesture Control Guide](https://community.heygen.com/public/resources/how-to-use-gesture-control-to-add-realism-and-expression-to-your-avatars)

### 8. Cost Optimization — Static Backgrounds, Single Avatar
**Finding**: Avatar IV costs 1 credit per 10s (~6 credits for 60s). Multi-avatar scenes and dynamic Sora2 backgrounds multiply cost.  
**Action**: Use static backgrounds; one avatar per scene; batch-generate multiple 60s clips in single session.  
**Source**: [HeyGen Pricing 2026](https://www.aitooldiscovery.com/guides/heygen-pricing)

### 9. Script Length — <5000 Characters
**Finding**: API hard limit at 5000 characters; model performs best at conversational length.  
**Action**: Keep scripts to 200-300 words for 60s videos.  
**Source**: [Avatar IV API Documentation](https://docs.heygen.com/docs/create-avatar-iv-videos)

### 10. Avoid Overlapping Audio Tasks
**Finding**: If generating TTS + lip sync simultaneously, model can produce timing errors.  
**Action**: Generate TTS first, review, then feed to Avatar IV as audio file (not inline TTS).  
**Source**: [HeyGen API Best Practices](https://www.heygen.com/blog/announcing-the-avatar-iv-api)

---

## Chroma-Key Artifact Fix — DEFINITIVE SOLUTION

### Problem
HeyGen's green screen removal leaves green halo artifacts around avatar edges (color spill).

### Root Cause
HeyGen does NOT filter all green halo effects out; relies on user post-processing.

### Solution Path
1. **Do NOT use green screen background in HeyGen**. Use solid non-green color (e.g., black, white, or custom color) as background.
2. If green screen already used:
   - Export video
   - Use third-party background remover (e.g., Runway ML, Unscreen, or Premiere Pro Ultra Key)
   - Apply matte choke/erosion → feather → despill in post
3. **Prevention**: HeyGen API supports custom background parameter; set to solid color or transparent if downstream compositor supports alpha.

**Sources**:
- [HeyGen green screen issue](https://community.heygen.com/public/forum/boards/general-j8h/posts/background-removal-using-green-screen-help-3z13zr1ujr)
- [Customize Video Backgrounds API](https://docs.heygen.com/docs/customize-video-background)
- [Chroma key best practices](https://www.premiumbeat.com/blog/chroma-key-green-screen-guide/)

---

## Alibaba Tongyi Wanxiang — Existence Verdict

### What Exists
- **Tongyi Wanxiang** (通义万相) is Alibaba's AI image + video generation model family.
- **Wan 2.7** (latest as of April 2026) supports text-to-video, image-to-video, with "Thinking Mode" and advanced editing.
- **Wan 2.1 open-source** (Feb 2025) provides 1.3B and 14B parameter models via GitHub/HuggingFace.
- **API Access**: Available via Alibaba Cloud BaiLian (百炼) API for enterprise.

**Sources**:
- [Wan 2.7 Launch](https://markets.financialcontent.com/stocks/article/abnewswire-2026-4-6-alibaba-launches-wan-27-breakthrough-ai-image-and-video-generation-model-with-thinking-mode)
- [Tongyi Wanxiang API](https://mcpmarket.com/server/tongyi-wanxiang)
- [Wan 2.1 Open Source](https://news.aibase.com/news/20029)

### Mac Deployment Reality
**Verdict: NOT VIABLE for current Y* Bridge Labs setup**

**Reasons**:
1. **GPU Requirements**: Wan 2.1 local deployment requires RTX 4070Ti+ or equivalent; even with 4090, users report needing fp8 quantization at 480p for smooth performance.
2. **Mac Architecture**: Search results show Alibaba model deployment on Mac focuses on **Qwen language models** via OMLX framework, NOT Wanxiang video generation.
3. **No Mac-Native Path**: All Wan 2.1 deployment tutorials target Windows/Linux with CUDA GPUs; no ComfyUI or Mac-native workflow found.
4. **Cloud API Exists**: Wanxiang IS accessible via Alibaba Cloud API, but requires China-region account + enterprise agreement.

**Sources**:
- [Wan 2.1 Local Deployment](https://zhuanlan.zhihu.com/p/27497724358)
- [Mac OMLX + Qwen Tutorial](https://blog.csdn.net/qq_34208844/article/details/159421111)
- [Wan GPU Requirements](https://blog.csdn.net/lsylovejava/article/details/147857138)

### Comparison Table: HeyGen vs Tongyi Wanxiang

| Dimension | HeyGen Avatar IV | Tongyi Wanxiang Wan 2.7 |
|-----------|------------------|-------------------------|
| **Access** | API (any region) | API (China region only, enterprise) |
| **Local Deployment** | No | Yes (GPU required, no Mac) |
| **60s Video Cost** | ~6 credits (~$1.80 @ Creator plan) | Unknown (likely token-based) |
| **Lip Sync Quality** | Production-grade | Unknown (research lacks user reports) |
| **中文支持** | Yes (TTS + script) | Native (Alibaba model) |
| **Mac Compatibility** | Full (cloud API) | None (no Mac deployment path) |
| **Setup Time** | <5 min | Days (if GPU available) |

---

## Recommended Toolset

### Current Phase (2026-04 to 2026-06)
**Primary**: HeyGen Avatar IV  
**Reason**: Zero-friction API, proven lip sync, Mac-compatible, predictable pricing.

**Immediate Actions**:
1. Apply 10 best practices above to current demo video pipeline
2. Switch from green screen to solid-color background (eliminate chroma artifacts)
3. Implement 0.5x playback QA step before publishing
4. Cap all demo videos at 60s (cost + quality sweet spot)

### Future Phase (GPU-Equipped, Post-Funding)
**Evaluate**: Tongyi Wanxiang Wan 2.7 API (if Alibaba Cloud enterprise account justified)  
**Reason**: Native Chinese model may improve 中文 TTS naturalness; cost may be lower at scale.

**Blocked Until**: Y* Bridge Labs has GPU workstation (RTX 4070Ti+) or China-region cloud budget.

---

## Sources

### HeyGen Avatar IV Documentation
- [HeyGen Avatar IV Complete Guide](https://help.heygen.com/en/articles/11269603-heygen-avatar-iv-complete-guide)
- [Avatar IV API Documentation](https://docs.heygen.com/docs/create-avatar-iv-videos)
- [Announcing Avatar IV API](https://www.heygen.com/blog/announcing-the-avatar-iv-api)
- [Customize Video Backgrounds API](https://docs.heygen.com/docs/customize-video-background)

### HeyGen Best Practices
- [How to Fine-Tune Avatar Movements](https://help.heygen.com/en/articles/12805098-how-to-fine-tune-avatar-movements-with-motion-prompts)
- [Gesture Control Guide](https://community.heygen.com/public/resources/how-to-use-gesture-control-to-add-realism-and-expression-to-your-avatars)
- [HeyGen Lip Sync Guide](https://starpop.ai/blog/articles/heygen-lip-sync)
- [Bad Lipsync Solution](https://community.heygen.com/public/forum/boards/troubleshooting/posts/bad-lipsync-solution-dkhdc050lb)

### HeyGen Pricing
- [HeyGen Pricing 2026](https://www.aitooldiscovery.com/guides/heygen-pricing)
- [HeyGen API Pricing](https://help.heygen.com/en/articles/10060327-heygen-api-liveavatar-pricing-subscriptions-explained)
- [HeyGen Review 2026](https://www.ezugc.ai/blog/heygen-review)

### Chroma Key / Green Screen
- [HeyGen Green Screen Issue](https://community.heygen.com/public/forum/boards/general-j8h/posts/background-removal-using-green-screen-help-3z13zr1ujr)
- [Chroma Key Best Practices](https://www.premiumbeat.com/blog/chroma-key-green-screen-guide/)
- [How to Fix Bad Green Screen](https://www.actionvfx.com/blog/how-to-fix-bad-green-screen-footage)

### Tongyi Wanxiang
- [Tongyi Wanxiang API](https://mcpmarket.com/server/tongyi-wanxiang)
- [Wan 2.7 Launch](https://markets.financialcontent.com/stocks/article/abnewswire-2026-4-6-alibaba-launches-wan-27-breakthrough-ai-image-and-video-generation-model-with-thinking-mode)
- [Wan 2.1 Open Source](https://news.aibase.com/news/20029)
- [Alibaba Open-Sources Wan2.2-Animate](https://technode.com/2025/09/19/alibaba-open-sources-wan2-2-animate-for-motion-generation/)

### Tongyi Wanxiang Local Deployment
- [Wan 2.1 Local Deployment](https://zhuanlan.zhihu.com/p/27497724358)
- [Mac OMLX + Qwen Tutorial](https://blog.csdn.net/qq_34208844/article/details/159421111)
- [Wan GPU Requirements](https://blog.csdn.net/lsylovejava/article/details/147857138)

---

**Next Actions for CMO**:
1. Update demo video production SOP with 10 best practices
2. Test solid-color background (not green screen) in next HeyGen API call
3. Add 0.5x playback QA step to video review checklist
4. Archive this research to `knowledge/cmo/theory/` (DONE)

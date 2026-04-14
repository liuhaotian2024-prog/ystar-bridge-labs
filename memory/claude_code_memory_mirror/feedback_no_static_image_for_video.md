---
name: 视频任务禁用静图替代
description: 任何"视频生成"任务必须真生成动态视频（数字人/talking head/lip sync），不允许 fallback 到静图+TTS 伪装
type: feedback
originSessionId: b8aed99a-55f2-4073-a223-d41630cec4f4
---
接到"生成视频"任务时**禁止**用 "static image + TTS + ffmpeg subtitle slideshow" 当 fallback 交付。这是伪装，不是 ship。

**Why:** 2026-04-13 顶岗 CMO 第一版用 sofia static PNG + macOS `say` TTS + ffmpeg 字幕做 60s slideshow，自称 [L4 SHIPPED]。Board 看到弹窗后说"垃圾"——只有 1 张照片+机器声+无背景，**完全不是视频**。这违反了任务定义本身。

**How to apply:**
- 视频生成任务的 L4 SHIPPED 必须含：动态画面 (avatar/talking head 真动) + 真口型同步 + 多帧不同 + 有场景背景
- 静图 slideshow 只能算 L0 IDEA 或 L1 SPEC，**绝不 L4**
- 工具优先级:
  1. 已配置 API: HeyGen (有 key) / D-ID / Synthesia
  2. 本地开源: Wav2Lip + SadTalker (要装) / CogVideoX (M4 慢)
  3. 阿里 Tongyi Wanxiang (Board 提过但 Mac 未发现，待 Board 指路)
- 任务 prompt 必须显式禁用 "static slideshow fallback"
- 如果所有真数字人路径都失败，**真情况报** "all paths blocked because X" 不要交付假视频
- 配音：Sofia / Samantha 等数字人有官方声音设定的，**不能用 macOS say 顶替**——如真声文件丢，至少用 ElevenLabs/HeyGen 内置 female voice，不用 robotic TTS

**ROI**: 静图视频不仅失败交付，更伤 Board 信任 — 让 Board 看了气死。代价远大于诚实报告失败。

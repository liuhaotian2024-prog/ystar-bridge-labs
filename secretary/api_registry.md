# API & Platform Registry
## Secretary Archive — Last updated: 2026-04-06 ET · Day 12

All external platforms and APIs used by Y* Bridge Labs, maintained by Secretary.

---

### Pollinations.ai
- **URL**: https://image.pollinations.ai/
- **Purpose**: AI image generation (FLUX model)
- **Auth**: None required — free, no signup, no API key
- **Usage**: Team portrait photos (Samantha, Aiden, Ethan, Sofia, Zara, Marco)
- **Example**: `curl -sL -o out.jpg "https://image.pollinations.ai/prompt/PROMPT?width=1024&height=1344&model=flux&nologo=true&seed=42"`
- **First used**: 2026-04-06

### World Labs (Marble API)
- **URL**: https://api.worldlabs.ai/marble/v1/worlds:generate
- **Purpose**: Photo → 3D world generation
- **Auth**: API Key stored in `~/.gov_mcp_secrets.env` as `WORLDLABS_API_KEY`
- **Status**: Tested, quality insufficient for production use
- **First used**: 2026-04-06

### Cloudflare Workers
- **URL**: https://raspy-flower-80f9.liuhaotian2024.workers.dev
- **Purpose**: Proxy for Anthropic Haiku API (AI chat on website)
- **Auth**: Anthropic API key configured in Worker environment
- **Account**: liuhaotian2024 on Cloudflare
- **First used**: 2026-04-06

### GitHub Pages
- **URL**: https://liuhaotian2024-prog.github.io/ystar-bridge-labs/
- **Purpose**: Static front-end hosting
- **Repo**: liuhaotian2024-prog/ystar-bridge-labs (docs/ folder, main branch)
- **Auth**: GitHub account liuhaotian2024-prog
- **First used**: 2026-04-06

### Pexels
- **URL**: https://pexels.com
- **Purpose**: Free stock photography (office background photos)
- **Auth**: None required for downloads
- **Photos used**: pexels-380769 (candidate_3.jpg — wood desk office)
- **First used**: 2026-04-06

### Avaturn
- **URL**: https://api.avaturn.me
- **Purpose**: Photo → 3D avatar GLB generation (planned)
- **Auth**: Not yet registered
- **Status**: Planned for TL-004 execution

### X (Twitter) API
- **Auth**: Keys stored in `~/.gov_mcp_secrets.env` (X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET)
- **Account**: @liuhaotian_dev
- **Tier**: Pay-per-use (Board paid $5 credit)
- **First used**: 2026-04-05

### 可灵AI (Kling AI)
- **URL**: https://api.klingai.com
- **App**: https://app.klingai.com
- **Docs**: https://app.klingai.com/cn/dev/document-api
- **Purpose**: AI视频生成（图生视频、文生视频）
- **Auth**: Access Key + Secret Key stored in `~/.gov_mcp_secrets.env` as `KLING_ACCESS_KEY` / `KLING_SECRET_KEY`
- **Account**: Board的中国手机号账号
- **Key features**: 多图参考输入、视频续写、最长10秒/段、1080p输出
- **First used**: 2026-04-07

### Replicate
- **URL**: https://api.replicate.com
- **App**: https://replicate.com
- **Purpose**: AI模型推理云服务（5000+模型）
- **Auth**: API Token stored in `~/.gov_mcp_secrets.env` as `REPLICATE_API_TOKEN`
- **Pricing**: Pay-per-use，余额$10
- **First used**: 2026-04-08

#### Replicate 推荐模型清单（按用途）

**图片生成**:
- `black-forest-labs/flux-schnell` ($0.003/img) — 快速草图，3300张/$10
- `black-forest-labs/flux-1.1-pro` ($0.04/img) — 顶级质量
- `black-forest-labs/flux-dev` ($0.025/img) — 平衡

**图片增强**:
- `philz1337x/clarity-upscaler` ($0.012/run) — Magnific级真实感增强
- `851-labs/background-remover` ($0.001/run) — 比 rembg 快

**视频处理**:
- `lucataco/latentsync` ($0.07/run) — ✅已用，diffusion嘴型同步
- `arielreplicate/robust_video_matting` ($0.05/video) — 视频去背景
- `wan-video/wan-2.2-t2v` ($0.20-0.50/clip) — 开源Kling替代

**音频处理**:
- `resemble-ai/resemble-enhance` ($0.02/run) — 音频降噪+超分
- `vaibhavs10/incredibly-fast-whisper` ($0.0025/min) — 极快STT
- `minimax/speech-02-turbo` ($0.02/run) — TTS+语音克隆

**人物一致性**:
- `zsxkib/pulid` ($0.02/run) — FLUX生成保持身份一致
- `fofr/face-to-many` ($0.008/run) — 一张脸生成多种风格

### HeyGen
- **URL**: https://api.heygen.com/v2/
- **App**: https://app.heygen.com
- **Purpose**: AI数字人视频生成（Photo Avatar → 说话视频）
- **Auth**: API Key stored in `~/.gov_mcp_secrets.env` as `HEYGEN_API_KEY`
- **Pricing**: Pay-as-you-go, 1 credit/min standard, $0.50-$0.99/credit
- **Key features**: Photo Avatar（上传照片→会说话的数字人）, 自定义语音, 1080p输出
- **First used**: 2026-04-06

### Telegram Bot API
- **Auth**: Token stored in `~/.gov_mcp_secrets.env` as `TELEGRAM_BOT_TOKEN`
- **Channel**: @YstarBridgeLabs
- **First used**: 2026-03-30

### PyPI
- **URL**: https://pypi.org
- **Purpose**: Python包发布（ystar-defuse等产品）
- **Auth**: API Token stored in `~/.gov_mcp_secrets.env` as `PYPI_API_TOKEN`
- **Account**: Board的PyPI账号
- **Package**: ystar-defuse (https://pypi.org/project/ystar-defuse/)
- **First published**: 2026-04-11 (v0.1.0)
- **Upload method**: `python3 -m twine upload -u __token__ -p $PYPI_API_TOKEN dist/*`

---

*Secretary Samantha Lin — all secrets stored in `~/.gov_mcp_secrets.env` (chmod 600, never committed)*

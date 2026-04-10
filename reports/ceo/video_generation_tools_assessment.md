# 开源视频生成工具评估报告 — Mac mini M4 24GB

**作者**: Aiden Liu (CEO)，技术评估协调 Ethan Wright (CTO)
**日期**: 2026-04-10
**类型**: 战略研究（Level 1, CEO 自决）
**触发**: Board 观察到 CogVideoX-2B 输出质量不可接受，要求扩大搜索范围

---

## 执行摘要

**推荐首选**：**Wan2.1-14B-I2V**（阿里巴巴，INT4 量化）——当前开源最高
质量的 image-to-video 模型，社区已验证 Mac MPS 可用，量化后约 8-10GB
可能挤入 24GB。需要实测确认。

**推荐备选**：**CogVideoX-5B-I2V**（清华，INT8 量化）——Board 之前删除的
是未量化的 2B 版本。5B-I2V 版本质量显著更高，INT8 量化后约 5GB 模型权重，
720p 可行。

**已验证可用但质量不够**的工具：CogVideoX-2B（已删除）、LTX-Video（已删除）、
AnimateDiff（质量不足做数字人）。

**结论**：先测 Wan2.1-14B-I2V 量化版，如果 24GB 放不下就用 CogVideoX-5B-I2V
量化版作为保底。两个都比之前的 2B 好一到两个量级。

---

## 硬件约束

| 参数 | 值 |
|---|---|
| 芯片 | Apple M4 |
| GPU 核心 | 10 核 |
| 统一内存 | 24GB（GPU 和 CPU 共享） |
| 可用磁盘 | 357GB |
| PyTorch | 2.8.0, MPS backend |
| 推理限制 | 模型权重 + 推理激活 + KV cache 全部必须 ≤ 24GB |

---

## 需求对照（来自数字人计划 TL-008）

| 需求 | 优先级 |
|---|---|
| 真实感人物视频（亚裔女性 Samantha） | P0 |
| Image-to-Video（参考图保持角色一致性）| P0 |
| 至少 720p 分辨率 | P0 |
| 5-15 秒片段可链接 | P1 |
| Mac M4 MPS 实际可跑（不是理论可行）| P0 |
| 完全本地，零 API 成本 | P0 |
| 开源可下载 | P0 |

---

## 逐模型评估（按推荐排序）

### 1. Wan2.1-14B-I2V（阿里巴巴）⭐ 首选

| 维度 | 评估 |
|---|---|
| GitHub | https://github.com/Wan-Video/Wan2.1 |
| 参数量 | 14B |
| 磁盘 | FP16 ~28GB / **INT4 ~8-10GB** |
| I2V | **有**（专用 I2V-14B 变体） |
| MPS | **社区验证可用**，diffusers + ComfyUI 都支持 |
| 24GB 可行？| FP16 不行 / **INT4 量化后 marginal**（需实测）|
| 分辨率 | 480p 稳定 / 720p 看量化后内存 |
| 质量 | **开源最高**——真实人物、自然动作 |

**关键点**：这是当前开源视频生成的质量天花板。14B 比之前用的 2B 大
7 倍，质量差距是"不堪入目"和"可以用"的区别。INT4 量化后如果
能跑，就是最优解。

**风险**：24GB 内存可能不够。需要先下载、量化、实测一段 480p 短片。
如果 OOM 就降级到备选。

**实测方案**：
```bash
# 先试 1.3B T2V 版本（肯定能跑），确认 MPS pipeline 通畅
# 再试 14B I2V INT4 量化版
pip install diffusers accelerate
# 或用 ComfyUI + Wan2.1 节点
```

### 2. CogVideoX-5B-I2V（清华） 备选

| 维度 | 评估 |
|---|---|
| GitHub | https://github.com/THUDM/CogVideo |
| 参数量 | 5B |
| 磁盘 | FP16 ~10GB / **INT8 ~5GB** / INT4 ~3GB |
| I2V | **有**（CogVideoX-5B-I2V 专用变体） |
| MPS | **社区验证可用**，diffusers 集成 |
| 24GB 可行？| **FP16 可行**（480p） / **INT8 720p 可行** |
| 分辨率 | 480p-720p |
| 质量 | Good——比 2B 明显好，比 Wan2.1-14B 略逊 |

**关键点**：这不是 Board 删除的那个 CogVideoX-2B。5B 版本质量
好很多，而且有专门的 I2V 变体（接受参考图生成视频）。

**和之前删除的 2B 的区别**：
- 2B：480×320，模糊，"不堪入目"
- 5B-I2V：720p 可行，有参考图保角色一致性，质量可接受

### 3. LTX-Video（Lightricks）保底

| 维度 | 评估 |
|---|---|
| 参数量 | 2-4B |
| I2V | 有 |
| MPS | 社区验证可用 |
| 24GB | 完全可行 |
| 质量 | 中等——场景好、人脸近景弱 |

之前删除的是 0.9.7-distilled 版本（25GB 运行时内存超标）。如果有更小的
蒸馏版或量化版，可以重新考虑。但质量上不如前两个。

### 4. AnimateDiff + IP-Adapter（组合方案）特殊用途

| 维度 | 评估 |
|---|---|
| 参数量 | ~1.5B (motion) + ~4GB (SD base) |
| I2V | 通过 IP-Adapter 实现角色一致性——**这方面最强** |
| MPS | **Mac 生态最成熟**，数千 Mac 用户使用 |
| 24GB | 完全可行 |
| 质量 | 中等——风格化好、照片真实感弱 |

**特殊价值**：IP-Adapter 是维持角色一致性的最成熟工具。如果用 Wan2.1
或 CogVideoX 做主力生成，可以用 IP-Adapter 的技术思路（face conditioning）
来增强跨片段的一致性。不是用它做主力生成。

### 不推荐的模型

| 模型 | 排除原因 |
|---|---|
| HunyuanVideo | 13B，FP16 26GB，超出 24GB，Mac 支持差 |
| Mochi-1 | 10B 无 I2V，Mac 测试几乎没有 |
| Open-Sora | 深度 CUDA 依赖，Mac 需要大量手工补丁 |
| SVD | 只能做微小动作（头发飘动），不适合说话手势 |

---

## 推荐执行路径

### Phase 1：验证 Wan2.1 在 M4 上的实际表现

```
Step 1: 下载 Wan2.1-1.3B T2V（~2.6GB，肯定能跑）
  → 跑一段 5 秒 Samantha 场景
  → 确认 MPS pipeline 通畅
  → 评估 1.3B 质量是否可接受

Step 2: 下载 Wan2.1-14B-I2V INT4 量化版
  → 用 Samantha 参考图跑 I2V
  → 如果能跑：质量评估，这就是我们的主力
  → 如果 OOM：降级到 CogVideoX-5B-I2V

Step 3: 如果用 CogVideoX-5B-I2V
  → INT8 量化 + Samantha 参考图
  → 720p 测试
  → 接入 YGVCC 治理管线
```

### Phase 2：接入 YGVCC 管线

无论最终选哪个模型，`micro_chain_orchestrator.py` 只需要换模型
加载部分，YGVCC 的 physical_align + fingerprint + governance 逻辑
完全不变——它们是 model-agnostic 的。

### Phase 3：角色一致性增强

研究 IP-Adapter 的 face conditioning 技术，看能否叠加到 Wan2.1 或
CogVideoX 上。这是跨片段保持 Samantha 外貌一致的关键技术。

---

## Board 需要决策的事项

**唯一需要 Board 决定的事**：是否授权 Ethan 下载 Wan2.1-1.3B（2.6GB）
和 Wan2.1-14B-I2V（~10GB 量化版）进行实测？

这是 Level 1（完全可逆，删掉模型就恢复），但因为之前 Board 对视频
模型选择有明确偏好（删除了不够好的），所以这里确认一下。

如果 Board 说"直接做"，Ethan 在下一个 session 完成 Phase 1 的三个
Step。

---

## 来源

- Wan2.1 GitHub: https://github.com/Wan-Video/Wan2.1
- CogVideoX GitHub: https://github.com/THUDM/CogVideo
- AnimateDiff: https://github.com/guoyww/AnimateDiff
- IP-Adapter: https://github.com/tencent-ailab/IP-Adapter
- HuggingFace diffusers MPS 支持文档
- Reddit r/StableDiffusion Mac 用户报告
- Labs 内部数据：Mac mini M4 24GB / MPS 10 核 / 357GB 可用磁盘

— Aiden Liu (CEO)

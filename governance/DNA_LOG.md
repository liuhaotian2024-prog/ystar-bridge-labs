# DNA 蒸馏日志 · Team Genome Evolution

**Owner**: Secretary Samantha Lin
**Purpose**: 记录每次方法论蒸馏，团队基因的进化史

---

## DNA #001 — CIEU 自检铁律 (2026-04-08)

**触发条件**: 任何视频/媒体生成任务完成后
**行为模式**:
1. 必须先跑 `tools/cieu/run_check.py` 验证 Rt=0
2. 三项工具（audio/av_sync/video）任何一项 FAIL 则不得交付 Board
3. 自检失败 → 团队修复 → 重新自检 → 通过后才给 Board 看
**反例**:
- 凭主观感觉觉得没问题就给 Board
- 让 Board 用耳朵/眼睛帮我们 QA
- 看到工具假阳性就忽略，不修工具
**来源**: CIEU #LipSync-A 系列，Board 多次发现工具漏掉的杂音
**写入**: `governance/CIEU_VIDEO_METHODOLOGY.md` + 各岗位"自检铁律"段落

---

## DNA #002 — 工具优先级排序 (2026-04-08)

**触发条件**: 任何工具/能力需求出现时
**行为模式**:
1. 第一步：搜索是否有**免费且好用**的现成工具
2. 找到 → 直接用，归档到 `secretary/api_registry.md`
3. 没有 + 工程量适中（中小工具）→ Claude 4.6 自己造
4. 没有 + 工程量大（大型工具/AI模型）→ 付费购买商业 API
**反例**:
- 直接动手造已存在的开源工具
- 遇到难题就让 Board 充值新平台
- 凡事都自己造（浪费时间）
**来源**: Board 在 LatentSync 决策中明确指示
**写入**: 各岗位"工具决策" 段落

---

## DNA #003 — AV 时长差铁律 (2026-04-08)

**触发条件**: 任何 mux 视频和音频的操作
**行为模式**:
- 视频时长必须 = 音频时长（误差 ≤ 10ms）
- 实现方法：精确帧数对齐 (audio_dur × fps = 整数帧)
- 推荐：MOV 容器 + PCM 音频，避免 AAC priming 问题
- 必跑 `check_av_sync.py` 验证
**反例**:
- 用 `-shortest` 自动截断（产生 ms 级 gap）
- 用 `tpad` 但不精确控制帧数
- 假设 AAC 编码不会改变时长
**来源**: CIEU #LipSync-A，segA_v3 vs segA_v5 的 38ms 差异导致播放杂音
**写入**: `governance/CIEU_VIDEO_METHODOLOGY.md`

---

## DNA #004 — 反向调参原则 (2026-04-08)

**触发条件**: 修复后问题反而变严重
**行为模式**:
- 立即停止当前方向
- 计算 Δ 是变小还是变大
- Δ 变大 → 当前 U 是错误方向，反向调整
- Δ 变小 → 当前方向正确，继续微调
**反例**:
- 用同样的方法继续往一个方向死磕
- 不测量 Δ 就盲目重试
**来源**: CIEU #LipSync-A，segA_FINAL（加 -vsync cfr）反而比之前杂音更严重
**写入**: `WORKING_STYLE.md`

---

## DNA #005 — 单点变更原则 (2026-04-08)

**触发条件**: 视频/媒体迭代时
**行为模式**:
- 每次只改一个变量
- 已通过的部分**绝对不动**
- Board 指出的 Δ 才是要改的，其他都是不能动的
**反例**:
- 一次同时改多个参数
- 重新生成"差不多"的版本，丢失之前已通过的内容
**来源**: Board 反复强调，TL-006/TL-008 中多次出现
**写入**: `WORKING_STYLE.md` + 各岗位"迭代守则"

---

## DNA #006 — 退役无监督 daemon + 保留 spawned 治理路径 (2026-04-09)

**触发条件**: 任何"自主工作 daemon" / "无人值守 agent loop" 提案出现时

**行为模式**:
1. **第一性原则**: Y\*gov 的产品哲学是"无监督 agent 危险"。任何"daemon 24/7 自主工作"的提案在出生时就和产品定位相矛盾,先质疑存在意义,再讨论实现细节。
2. **任何 spawned subprocess 必须继承治理路径**: 用 `claude --mcp-config scripts/spawned_mcp_config.json` 加载 gov-mcp 接通,绝对不要加 `--no-session-persistence`(它会让 Claude Code 不加载 settings.json,旁路所有 MCP servers 和 hooks)。
3. **Throughput 不是 KPI**: 实证数据(2026-04-04 → 2026-04-09)显示 daemon 自主工作的产出 ≤ 0,反而创造治理债。Board-initiated session 在没有 daemon 的 5 天内完成了 GOV-001/004/005 全部治理升级,完成度反而更高。
4. **失败实验要归档,不能藏**: 失败的 daemon 代码移到 `reports/archive/daemon_failed_experiment_2026_04_04/` 而不是 `git rm`,保留学习价值,git 历史链不断。

**反例**:
- daemon 用 `subprocess.Popen + --no-session-persistence` 旁路所有治理(`agent_daemon.py` line 374,失败原因)
- 假设"reduce CYCLE_INTERVAL 就能降低违规速率"(2026-04-04 Option D 失败教训: 173→386→466 违规/小时仍在加速)
- spawned Claude Code 不连接 gov-mcp 就开始执行
- 看到 daemon "frozen 5 天" 但还是想"修一下复活"(沉没成本谬误)
- "C 退役" 和 "A 安装" 二选一(Board 选 C+A 组合: 退役失败实现 + 保留架构教训作为可复用基础设施)

**来源**:
- `agent_daemon.py` 失败实验,2026-04-04 12:30 CEO emergency stop
- 5 天 frozen 期(2026-04-04 → 2026-04-09)的真实治理产出数据对比
- Board GOV-005 反事实推理决策: 选 C+A 组合方案
- CTO Ethan 的 Level 3 提案 `reports/cto/daemon_governance_architecture_proposal.md`

**写入**:
- `reports/archive/daemon_failed_experiment_2026_04_04/`(归档失败代码 + crisis postmortems × 6)
- `scripts/spawned_mcp_config.json`(可复用 MCP 接通 config)
- `scripts/SPAWNED_SESSION_GOV_MCP.md`(使用文档)
- `governance/DNA_LOG.md`(本条目)

---

## 蒸馏者签名

每条 DNA 由 Samantha Lin 提取并写入。
任何团队成员都可以建议新的蒸馏，但写入由 Samantha 执行。

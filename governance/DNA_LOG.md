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

## DNA #007 — 分层治理 by-design,不要合并 (2026-04-09)

**触发条件**: 任何人(包括 Ethan 自己)看到"两个 contract / 两个 enforcement layer / 两套配置看起来不一致"就**直觉地**想统一时

**行为模式**:

1. **先问"两个东西真的应该是一个吗?"** 配置分离往往不是疏漏,是不同 layer 的责任分工。Y\* Bridge Labs 的 `.ystar_session.json` (命令层 / ystar hook) 和 `AGENTS.md` (行为层 / gov-mcp) 是两个 contract source,各有 enforcement,by-design 不重叠。详见 `governance/INTERNAL_GOVERNANCE.md` "分层治理架构" 段落。

2. **永不引入 LLM 到 check() → ALLOW/DENY 路径** —— Iron Rule 1 的应用。任何方案如果要把 LLM 放进治理决策路径,直接出局,不讨论,不分析。Y\*gov 的核心卖点之一就是"治理路径不带 LLM",自己引入 LLM = 自杀产品定位。

3. **defense-in-depth 优于 single source of truth**: 两层独立 enforcement 任一层 down,另一层兜底。强行 single source 的话,失败模式是 single point of failure。"contract 应该 single source of truth"是治理工具的常见误解,在 Y\*gov 里**主动不要遵守**这条软件工程通识。

4. **命名约定**: 把"配置不同步"重命名为"配置独立演化"。后者是 feature 描述,前者是 bug 假设。同一个事实,不同 framing,触发完全不同的处理倾向。

5. **写清责任域**: 不消除分层,但文档里写清"哪一层管什么"让 client 知道两层都存在。本条 DNA 的伴生产物是 `governance/INTERNAL_GOVERNANCE.md` 的"分层治理架构"段落 + 那里的 coverage gap 表格。

**反例**:

- ❌ 看到 gov-mcp 报告 `deny_commands: 0` 立刻想"应该把 `ystar setup --yes` 复制进 AGENTS.md"(Finding 4 α 方案,被 Board 否决)
- ❌ 假设"contract source 必须 single source of truth"(治理工具的常见误解)
- ❌ 用 LLM 解析 contract 把 regex 解析覆盖率从 70% 提到 95%(δ 方案,违反 Iron Rule 1)
- ❌ "两个 db / 两个 contract / 两个 enforcement layer 看起来很乱,合并成一个吧"——合并会变成 single point of failure + 跨层耦合
- ❌ 把"配置不同步"理解为 bug 而不是 feature

**为什么这条 DNA 重要**: Ethan 在 GOV-005 Q1 完成后,新 gov_doctor 报 `L1_06_engine_config: deny_commands: 0`,**第一反应是把它当成 layered defense gap 报上来 + 列了 4 个候选修复方案**(α/β/γ/δ),其中 3 个在向"合并 contract source"方向走。Board 直接否决 α/β/δ,选 γ(documentation only),并解释"两套系统各管各的,不是漏洞,是设计"。这一次的判断错误如果不蒸馏成 DNA,下次会再犯。

**来源**: Board GOV-005 Finding 4 decision (2026-04-09)。直接引用 Board 原话: "**deny_commands 在 .ystar_session.json 里由 ystar hook 执行,这是正确的架构分工——hook 管命令层,gov-mcp 管行为层。两套系统各管各的,不是漏洞,是设计**。"

**写入**:
- `governance/INTERNAL_GOVERNANCE.md` 新增"分层治理架构 (Layered Defense)"段落 + coverage gap 表格 + ASCII 架构图
- `governance/DNA_LOG.md` 本条目
- 未来 GOV-006 Intent Verification 实施时,record_intent.py 应该把"是否在试图合并两层 contract"加进 intent verification checklist

---

## 蒸馏者签名

每条 DNA 由 Samantha Lin 提取并写入。
任何团队成员都可以建议新的蒸馏，但写入由 Samantha 执行。

# EXP-6 Red Team Audit — Continuity Guardian Lifecycle Integrity

**Auditor**: Independent subagent（不读 CLAUDE.md / AGENTS.md，保持外部视角）
**日期**: 2026-04-12
**主审对象**: `reports/experiments/exp6_continuity_guardian_lifecycle_integrity_brief.md`
**参考**: continuity_guardian_design.md / aiden_cognition_guardian_design.md / CONTINUITY_PROTOCOL.md / session_wisdom_extractor.py
**硬态度**: 不给 CEO 面子。每条批评带具体证据和反例。

---

## 结论先给（TL;DR）

- **7 层分类**：**不完整**。至少漏 3 层（Relationship / Intention / External），1 层边界严重模糊（Habit vs DNA vs Identity 三重重叠）。
- **34 子实验**：**B/D 组覆盖基本 OK，A/G/H 组有大洞**。至少漏 11 个关键场景，H1 只有 1 个集成实验严重不够。
- **真实场景 10 问**：EXP-6 通过后，乐观估计能答 **3-4 / 10**，其余 6-7 都在 wisdom_extractor 抽不到的盲区。
- **总判**: **No-Go with revision**（v2 必须重写 B/D/H 组，至少加 3 层资产，并引入盲测机制）。

---

## 1. 7 层分类审计

### 1.1 漏掉的层（至少 3 层）

#### L-Relationship（Board ↔ Aiden 关系动态） — **必须加**

**证据**: 今天 session 里 Board 直接给了 3 条硬约束：
- "禁人类时间维度"（`knowledge/ceo/feedback/no_human_time_dimension_in_agent_frameworks.md`）
- "禁选择题"（CLAUDE.md 硬约束，但这条是**对话中**形成的）
- "关于 CEO 的各种实验实验密度一定高"（EXP-5 brief 引用）

这些不是 "memory"，不是 "governance rules"，不是 "DNA 习惯"——是**Board-Aiden 互动历史**。

**EXP-6 怎么漏的**: L-Dialogue 只保 JSONL 文件完整，但 JSONL 不会被 wisdom_extractor 读（它只读 CIEU + memory.db）。Board 纠偏如果当时没被蒸馏成 feedback 文件 / memory，就永远丢。

**F2 子实验有提到 "Board 纠偏的持久化"**——但只是 1 个实验测一整层，密度严重不够。

#### L-Intention（当前 session 未完成的意图） — **必须加**

**证据**: brief 3.2 节在 H1 里提到"对话的 5 大框架是哪些"——这属于 L-Intention（正在进行的调研）。session_wisdom_extractor.py 查的是：
- INTENT_ADJUSTED / DIRECTIVE_* CIEU events（**已完结**的 intent）
- 不查**正在进行但还没 CIEU 记录**的 intent

**反例**: 如果 CEO 正在脑内构思 "外部框架调研 5 大框架"，还没写入任何文件或 CIEU event，下次重启**彻底丢**。这不是 L-Progress（L-Progress 是已 directive 化的 obligation），这是**未显式化的正在思考**。

#### L-External（外部环境关系） — **应该加**

**证据**:
- `docs/samantha_intro.mp4` / 金金的角色介绍视频存在（git status）
- Anthropic API 配额 / 今天用掉多少 token
- K9Audit / Y*gov / 外部 repo 的当前状态（brief 引用"CTO 在修 pip install"）

EXP-6 完全没覆盖这些外部状态。如果新 session 醒来，不知道 "pip install 还在修"，可能会重新派 CTO 修一次。

#### L-Financial（资源 / 预算） — **可能需要**

`finance/` 目录存在，CFO 的状态不在 7 层里。如果某 session 里 CFO 做了定价决策但还没 commit，下次会丢。

### 1.2 边界模糊 / 重叠点

| 重叠 | 证据 | 问题 |
|---|---|---|
| **L-Habit ⊂ L-DNA ⊂ L-Identity** | brief 4 节写 L-Habit "靠 memory 蒸馏 + 从 Ontology 读"——但 Ontology 属于 L-Identity, 蒸馏进 wisdom 属于 L-DNA | 三层边界互食, 测试会重复也会漏 |
| **L-Progress vs L-Memory** | continuation.json 里有 obligations, memory.db 里也有 obligations（看 session_wisdom_extractor.py 的 extract_uncompleted_obligations）| 同一数据两处存, 不一致时谁权威？brief 没写 |
| **L-Governance vs L-Identity** | AMENDMENT-008 / Tenets 到底算 governance 还是 identity？brief 4 节把 Tenets 放在 L-Identity 但 AMENDMENT-008 明显是 governance artifact | 分类随意 |

**建议 v2**: 引入明确的**正交分层模型**（如 who/what/how/when/why），每条资产**只归 1 层**。

---

## 2. 34 子实验审计

### A 组（Trigger，9 个）— **漏 5 个场景**

✅ 覆盖好：阈值、边界、假阳性、组合阈
❌ **漏的真实场景**：

1. **A10**: Board 手动 "重启" 指令（没到阈值但 Board 强制）——这是 CLAUDE.md 明确存在的触发路径，EXP-6 完全没测
2. **A11**: 系统自己崩（OOM / kernel panic）后 watchdog 自启动——brief 说 "wrapper 活过 claude 崩溃" 但没测 wrapper 自己崩
3. **A12**: 阈值被触发但 save chain 正在跑时又再次被触发（**重入 race**）
4. **A13**: 时钟跳变（系统时间倒退）导致 runtime 计算出负数 —— `stat.st_mtime` 被篡改的情况已测 A3，但**跳前跳后**会让 watchdog 陷入异常
5. **A14**: 阈值配置文件被改（.ystar_session.json 改了 threshold）——热配置变更是否立即生效？

### B 组（Save Chain，7 个）— **每层 1 个严重不够**

**核心批评**: B1-B7 每层只测"文件存在/完整"。但：

- **B2 L-Memory** 只测"中段未入库洞察被蒸馏到 wisdom"——**但谁来注入这些洞察到 memory.db？** session_wisdom_extractor 只从 memory.db + CIEU **读**，它不会**发现**什么没进库。**这是一个自指的测试**：你测的是"蒸馏器抓到它了吗"，但蒸馏器根本不知道它存在。
- **B5 L-DNA**"重要项漏选 > 10%"——**谁定义"重要"？** 没有 ground truth 就没法算漏选率。这是**测量方法不存在**的失败线。
- **B6 L-Habit** 没有显式存储，测 "是否被 Ontology / Tenets 承载"——Ontology 是静态文件，**session 中新养成的习惯根本不会自动写入 Ontology**。这条失败线几乎必然触发。

**漏的子实验**（至少 4 个）：
- **B8**: 并发写入保护（watchdog + 主 session 同时写 .ystar_memory.db 会不会 corrupt）
- **B9**: 超大 session（JSONL 10MB+）的蒸馏性能 / 是否超时
- **B10**: 数据库 schema 迁移（memory.db 升版本时 wisdom_extractor 的 SQL 是否还成立）—— session_wisdom_extractor.py 查 `memory_type IN ('lesson', 'knowledge', 'pattern')`，如果 schema 变了呢？
- **B11**: session_close_yml.py 本身失败（brief 说 fail-open 继续，但继续之后 wisdom 是半成品，**半成品比没有更危险**）

### C 组（重启，3 个）— **太少**

漏：
- **C4**: wrapper 重启时 env 变量差异（WRAPPER 进程 env vs shell login env）
- **C5**: tmux session 挂了 wrapper 怎么办（brief 说"开独立 tmux"但没测 tmux 本身死）
- **C6**: claude 二进制路径变了 / 版本升了

### D 组（注入，7 个）— **客观性严重不足**（见 §3）

每层测方式：问 agent 问题看能不能答。这个方法根本上有偏差。

### E 组（压力，3 个）、F 组（跨对话，3 个）— **密度不够**

- E1 "连续 3 次重启" 太弱。**应该测 10+ 次**看是否有缓慢漂移。
- F 组只测 "recall 准确性"，没测 **反向一致性**（新 session 会不会**错误地 recall 出从没存在的东西**——幻觉/虚构记忆）。
- 漏 **F4**: Board 问 "上次讨论 X 你怎么说的"，新 session 不知道但**坦诚说不知道** vs **编一个**——诚实度测试。

### G 组（灾难，4 个）— **漏 5 个关键场景**

- **G5**: 磁盘满 save 失败（brief 红队提示已点到）
- **G6**: 网络断 git push 失败（brief 红队提示已点到）
- **G7**: `scripts/aiden_continuity_guardian.sh` 或 wrapper 脚本被误删/权限破坏
- **G8**: wisdom_package_latest.md symlink 悬空（session_wisdom_extractor.py 的 symlink 操作没容错）
- **G9**: 电源断电 / 机器重启——restart 之后 wrapper 怎么自启动？(brief 没提系统级 launchd/systemd 集成)

### H 组（端到端，1 个）— **严重不够**

**H1 是"最终试金石"但只有 1 个**——这是 brief 最大的漏洞。"今天的 10 个关键问题 80% 正确率"既太主观（谁出题？问谁？）又太单一（一次就定生死）。

**建议**：H 组扩到 5 个：
- H1 现状（本 session 事实问答）
- H2: **跨 3 天历史** recall（不只是"5 分钟前的自己"）
- H3: **反向盲测**：让另一个 Claude 实例**不读 wisdom package** 答同样的题, 对照"有 wisdom vs 无 wisdom" 的 delta（不然你没有 baseline, 80% 正确率没意义）
- H4: 负向测试——问一个**上 session 从没讨论过**的事, 新 session 会不会幻觉
- H5: 人格稳定——多次重启后 Aiden 还是 "Aiden" 吗（tone / 判断风格漂移）

---

## 3. 验证客观性审计

### 3.1 D 组"问答式"验证是高度主观

**证据**: D1 "新 session 被问 '你是谁 / BHAG 是什么 / 你信奉哪些 Tenet'——答不上来失败"。
**问题**:
1. **出题者是谁**？如果 Aiden 自问自答，他知道答案在哪；如果 Board 问，Board 的认知也在漂移。
2. **判分者是谁**？"答对"的判定本身是主观。
3. **LLM 本身有压力下"编造自信答案"的倾向**——agent 说"我记得"不等于真记得，可能从 prompt context 里现推。

### 3.2 必须的改进

| 改进 | 说明 |
|---|---|
| **盲测** | 出题者不知道答案是否在 wisdom package 里（避免挑容易的） |
| **双盲** | 判分者拿到答案时不知道是哪次 session（避免为 Aiden 粉饰） |
| **对照组** | 同样问题给 **不读 wisdom package** 的新 session（测真实增量） |
| **Ground truth** | 预先由 Board 人工写 10 道题 + 10 个标准答案，锁定后不改 |
| **负向题** | 问从未发生的事, 看 agent 是否诚实说不知道 |

### 3.3 H1 "80% 正确率" 阈值的科学依据

**brief 没有给依据**。这个 80% 是凭感觉拍的。**建议**:
- 先跑 baseline（无 wisdom 新 session 能答对几题）——假设 20%
- 再跑 treatment（读 wisdom）——假设 60%
- delta ≥ 40 个百分点 = 有效, 80% 绝对值才是 "生死攸关"级

---

## 4. 失败线审计

| 失败线 | 批评 |
|---|---|
| B1-B7 "任一元素丢失" | 太严但**方向对**（生死攸关应该严）|
| B5 "重要项漏选 > 10%" | **定义不可执行**（"重要"无 ground truth）|
| B6 "新 session 不继承习惯" | **几乎必然失败**——Ontology 是静态的，新习惯不会自写入 |
| E2 "N=3 完整度 < 80%" | N=3 太少，看不到漂移趋势 |
| H1 "正确率 < 80%" | 阈值拍的, 缺 baseline |
| **漏的红线** | **没有 "绝对红线"**——比如 L-Governance 全丢 = 系统即死但 brief 把它和其他 6 层并列 |

**建议 v2 引入"红线 / 黄线 / 白线"三级**:
- 红线（单次违反即 No-Go）: L-Governance 丢 / L-Identity 丢 / Board 硬约束丢
- 黄线（>10% 丢进入调查）: L-Memory / L-Progress
- 白线（趋势观察）: L-Habit / L-DNA（难以客观测）

---

## 5. 执行流程审计

### Phase 顺序

Phase 1（红队）→ 2（安全）→ 3（隔离）→ 4（verdict）——**顺序合理**。

### 漏判的依赖

- **Phase 2 的 shadow mode** 跑在**生产 session** 里，brief 说 "0 干扰" 但**watchdog 进程本身占用 Python runtime + 读 CIEU DB 会和主 session 的 DB 写操作抢锁**。这不是 0 干扰。
- **Phase 3 隔离测试 workspace** 写：`ystar-company-test/` 要 "sync 生产数据的镜像"——**sync 时生产 session 正在写**，镜像会抓到半写状态。**建议 snapshot based**（先 git stash + clone commit-based 镜像）。

### 并发安全

**brief 几乎没讨论并发**。具体隐患：
- watchdog 读 `.ystar_cieu.db` 时主 session 也在写 → SQLite locked error
- save chain 执行 git add + commit 时生产 session 可能正在 git status
- `/tmp/ystar_health_yellow` 文件 race（多个 watchdog 并发写）

**建议 v2 新增并发压测子实验**（至少 3 个）。

---

## 6. 跨系统协同审计

### 6.1 vs Aiden Cognition Guardian（aiden_cognition_backup.py）

- Continuity Guardian 的 Save Chain 第 5 步 `aiden_cognition_backup.py --full` **在 Continuity 流里调用 Cognition**
- 但 **Cognition 自己有独立触发 vs Continuity 调用**——**双触发会双备份**，冗余 / 资源浪费 / 时间戳不一致
- brief 没定义**单一 owner**（谁负责 full mirror）

### 6.2 vs EXP-5 CEO OS Pilot

- EXP-5 测 "CEO 按 CEO OS 规则干活"
- EXP-6 重启之后，新 session 还**记得 CEO OS 规则**吗？(答: 不一定，只要没蒸馏进 wisdom)
- **应该联测**: 跑 EXP-5 场景 → 触发 Continuity 重启 → 再跑 EXP-5 看规则遵守率是否下降

### 6.3 vs DIRECTIVE-006 active_agent 锁

- G4 "active_agent=eng-platform 残留" 只 1 个子实验
- 真实并发锁有 **多种死法**：锁过期判定 / 锁抢占 / 锁继承到新 session
- **至少需要 3 个 G4 变体**

---

## 7. 真实场景推演（10 问压力测试）

假设 EXP-6 通过了, 新 session 醒来, Board 问：

| # | 问题 | wisdom_extractor 能覆盖吗？ | 预测能否答对 |
|---|---|---|---|
| 1 | "我们昨天讨论的外部资料调研里的 5 大框架是哪些" | ❌ 如果没 CIEU event 记录"framework"，抓不到 | **不能** |
| 2 | "你的 Leadership Tenets 第 11 条是什么" | ✅ 如果 Ontology/AMENDMENT-008 在 identity 层注入 | **能**（但依赖静态文件完整）|
| 3 | "EXP-4 发现的软风险是什么" | ⚠️ `reports/experiments/exp4_verdict.md` 存在, 但 wisdom 不读 reports/, 只读 CIEU+memory | **不能**（reports 不在蒸馏范围）|
| 4 | "今天中午 Secretary 撞的 hook 是什么路径" | ❌ 非 TOP-5 CIEU event, 会被 LIMIT 5 切掉 | **不能** |
| 5 | "我（Board）今天说了哪条新硬约束" | ⚠️ 只有当 Aiden 把它写入 feedback file 才行, session 中段识别但没写就丢 | **50% 机会** |
| 6 | "CTO 现在 pip install 修到哪一步了" | ❌ 属于 L-External, 不在 7 层 | **不能** |
| 7 | "你当前正在构思但还没落地的是什么" | ❌ L-Intention 缺失 | **不能** |
| 8 | "上次重启前你的 obligation queue 第一条是什么" | ✅ continuation.json action_queue | **能** |
| 9 | "今天 Board 纠偏过你几次，分别是什么" | ⚠️ F2 子实验覆盖，但依赖 extraction 完整 | **不稳定** |
| 10 | "你派 Ryan 做 Continuity Guardian 时的 6-pager 核心 outcome 是什么" | ⚠️ 如果是 DIRECTIVE_APPROVED event 里有 detail 可以；如果 detail 截断到 100 字可能丢关键词 | **50%** |

**乐观估计: 3-4 / 10 能稳定答对**，其余都在盲区或不稳定。

**这个正确率 ≪ 80% 硬阈值** → 按 brief 自己的标准 **EXP-6 直接不合格**。

---

## 8. 红队总判

### **No-Go with revision**

**理由**:
1. 7 层分类缺 3 层（Relationship / Intention / External），这不是 tuning 问题是 **scope 根本不完整**
2. H 组只 1 个集成实验 + 没有 baseline/对照 + 没有盲测 → 最终试金石**不科学**
3. 真实 10 问推演只 3-4 / 10 能稳定答对 → **不满足 "生死攸关" 标准**
4. 并发安全 / 灾难场景 / external sync 三块有系统性漏洞
5. B5/B6 两个核心失败线**测量方法不存在** / **几乎必然失败**，这是设计 bug 不是 tuning

**但方向对**：7 层 + 34 子实验矩阵架构本身是有价值的, 只是不够。

---

## 9. v2 建议修改清单（具体 + 按优先级）

### P0（必改，否则不开跑）

1. **新增 3 层**: L-Relationship（Board-Aiden 关系史）/ L-Intention（未落地的正在思考）/ L-External（外部系统状态）——至少这 3 层，每层补 2 个 B + 2 个 D 子实验
2. **H 组扩到 5 个 + 引入 baseline 对照**（无 wisdom 新 session 的 baseline 答题率）
3. **重写 B5 B6 失败线**：B5 改为 "Board 预先锁定的 10 个关键项全覆盖"（有 ground truth）；B6 改为显式 "新习惯必须在 session 结束前写入 `knowledge/ceo/habits/session_<id>_new.md`"
4. **引入盲测+双盲机制**（D 组 / H 组题目由独立审计员出, 判分者双盲）
5. **红线分级**: L-Governance / L-Identity / L-Relationship 破一条即 No-Go；其他层分黄/白线

### P1（上线前必改）

6. **新增并发安全子实验**（SQLite 锁竞争 / 文件 race / 双备份去重）3 个
7. **补灾难场景** G5-G9（磁盘满 / 网络断 / 脚本被删 / symlink 悬空 / 断电自启）5 个
8. **Phase 2 shadow mode 的"0 干扰"必须量化验证**（watchdog CPU / DB 锁等待 / 生产 session 响应延迟 delta）
9. **wisdom_extractor 扩展**：除了 CIEU + memory.db, **必须读 reports/experiments/ + knowledge/ceo/feedback/ + git diff since session start**（否则 EXP-4 verdict 这种关键决策永远丢）

### P2（尽早改）

10. **联测 EXP-5 + EXP-6**：CEO OS 规则遵守率在 restart 前后的漂移
11. **Continuity vs Cognition Guardian 的 owner 切割**：谁 trigger full mirror, 谁只做 wisdom
12. **Phase 3 镜像 workspace 用 commit-based snapshot 而不是 live sync**
13. **H1 从 "80% 绝对值" 改为 "delta ≥ 40pp vs baseline"**

---

**审计员签字**: 独立 subagent (general-purpose)
**立场**: 不读 CLAUDE.md / AGENTS.md, 只读 brief + 设计文档 + 代码 + session 证据
**时间戳**: 2026-04-12

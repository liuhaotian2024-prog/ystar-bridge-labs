# Labs治理进化方案 — 第十一条自主研究交付物
**日期**: 2026-04-10
**触发**: Board校准后五个发现 + CEO第十一条自主研究
**作者**: CEO (Aiden)
**状态**: 待Board审阅

---

## 零、问题结构

Board识别了两个层次的问题：

| 层次 | 性质 | 要求 |
|------|------|------|
| gov-mcp（工具层） | 确定性治理工具 | 精确执行，不需要质疑 |
| Labs（准科技公司层） | 需要主动性和创造性判断 | 需要摩擦、质疑、卓越 |

五个发现中，两个值得保留：
1. **CEO自我评估漂移** — Labs层问题
2. **义务网络作为持续主体** — 跨层洞察，影响YML设计哲学

本方案针对这两个核心发现 + 三个附属缺口提出一揽子解决方案。

---

## 一、现有制度审计

### 已有机制（不需要重建）

| 机制 | 位置 | 作用 |
|------|------|------|
| 指令拒绝协议 | WORKING_STYLE.md §8 | agent可以拒绝Board指令（需20字理由） |
| 意图验证 | WORKING_STYLE.md §7.5 | 执行前record_intent → CEO/Board确认 |
| 任务后反思 | WORKING_STYLE.md Layer 10-12 | 执行后自评 + 知识回写 |
| CEO周度自评 | CEO_MISSION_FRAMEWORK.md | 6个自评问题 |
| 反事实模拟 | AGENTS.md §7 Priority 3 | 空闲时做假设场景推演 |
| Rule 8 四问 | AGENTS.md L361 | 执行后问"这暴露了什么系统性缺陷" |

### 缺失机制（本方案解决）

| 缺失 | 对应发现 | 影响 |
|------|---------|------|
| 红队/魔鬼代言人协议 | 发现三（摩擦缺失） | 无人挑战方向正确性 |
| 执行前预检 | 发现二（目标自主缺失） | agent不质疑目标本身 |
| CEO判断校准机制 | 发现一（评估漂移） | CEO判断随问法漂移 |
| 义务中心的记忆检索 | 发现四（义务网络） | YML以agent为中心而非义务为中心 |
| 同构系统局限标注 | 发现五（实验边界） | Labs数据可能过度代表产品能力 |

---

## 二、方案一：CEO判断校准机制（解决发现一）

### 问题

CEO的自我评估随提问方式漂移。被问"做得好吗"倾向乐观，被问"是不是在自欺"倾向悲观。没有独立于Board情绪信号的评估框架。

### 根因

同一推理内核对同一事实的判断被锚点效应影响。CEO没有预先锚定的评估标准，每次都在当场推理，因此受context影响大。

### 方案：锚定式自评协议

**在CEO.md中新增强制条款：**

CEO在向Board做任何现状评估之前，必须先独立运行以下检查清单，写入结论后再汇报。Board的问题不改变清单的结论——如果清单结论和Board预期不同，CEO应该坚持清单结论并解释差异。

```
CEO现状评估锚定清单（每次评估前必须过）：

1. 量化基线：
   - 本session执行了多少条Board指令？完成率？
   - CIEU里CEO的事件数？（0 = 治理盲区）
   - subagent的测试通过率？

2. 能力边界声明（三选一，不允许模糊）：
   - "我们能做X" — 附证据（测试结果/已交付物）
   - "我们不能做X" — 附具体阻塞原因
   - "我们不确定能否做X" — 附验证计划

3. 与上次评估的delta：
   - 上次评估说了什么？（从YML recall）
   - 事实变了吗？如果没变，结论不应该变。

4. 反事实检验：
   - 如果Board的顾问现在看到这个评估，他会同意哪些、质疑哪些？
   - 我的哪个结论最可能是受到了Board情绪信号的影响？
```

**关键设计**：第4条直接对抗漂移——强制CEO预判外部质疑，而不是等被质疑后再修正。

### 实施方式

- 写入 `agents/CEO.md` 作为强制条款
- 不需要代码改动
- 首次使用：下次Board问"现在情况怎么样"时

---

## 三、方案二：执行前战略挑战协议（解决发现二+三）

### 问题

Labs有指令拒绝（拒绝可行性）和意图验证（确认理解），但没有**战略挑战**（质疑方向正确性）。agent只在执行层主动，不在目标层主动。同时，agent之间没有产生真实摩擦的机制。

### 根因

1. 指令拒绝是被动的（agent收到指令后决定拒绝），不是主动的（agent主动说"这个方向有问题"）
2. 合伙人宪法标准一写了"主动发现问题"，但没有配套的执行工具和流程
3. 同构系统天然缺乏立场冲突——需要机制**制造**摩擦

### 方案：强制预检 + 角色对抗

**A. Level 2/3指令强制预检（Pre-Execution Strategic Review）**

任何Level 2或Level 3指令，在record_intent之前，执行agent必须先写一份预检报告：

```
预检报告模板（1分钟内完成，不需要长篇）：

指令ID: ___
执行agent: ___

1. 这个指令的假设是什么？（列出1-3个核心假设）
2. 如果最大的假设是错的，最坏结果是什么？
3. 有没有更便宜/更快的方式验证假设？
4. 我作为[角色]，看到的Board可能没看到的风险是什么？

结论：
[ ] 无异议，继续执行
[ ] 有异议，建议调整：___
[ ] 有异议，请求Board重新评估：___
```

**关键设计**：第4条要求agent从**自己的角色视角**提出风险，而不是泛泛评估。CTO看技术风险，CMO看叙事风险，CFO看成本风险。这是在同构系统中**人工注入立场差异**的方式。

**B. 重大决策强制对抗（Devil's Advocate Protocol）**

对Level 3决策（修改AGENTS.md、外部发布、花钱），CEO在转交Board之前，必须指定一个agent扮演反对者：

```
CEO: "CTO，这个发布计划你来当反对者。你的任务是找出至少3个这个计划可能失败的原因。"
CTO-as-devil: "1. ... 2. ... 3. ..."
CEO: 将反对意见和原始提案一起提交Board。
```

**关键设计**：
- 反对者不是自愿的，是被CEO指定的——消除"同意偏差"
- 反对者必须找出至少3个理由——强制深度而非敷衍
- Board看到的是提案+反对意见，不是提案+CEO的背书

### 实施方式

- 预检：写入 `governance/WORKING_STYLE.md` 作为§7.5的前置步骤
- 对抗：写入 `agents/CEO.md` 作为Level 3处理流程
- 脚本：可选，`scripts/strategic_review.py`记录预检到CIEU
- 不阻塞Level 1决策——Level 1的速度不能被制度拖慢

---

## 四、方案三：义务中心记忆检索（解决发现四）

### 问题

YML当前设计以agent为中心：`gov_recall(agent_id="ceo")`。但系统的真正持续主体是义务网络，不是agent。Agent消失后义务依然存在。

### Board洞察

> "YML给agent加记忆，本质上是在让agent更好地接入这个已经存在的义务网络，而不是在创造一个新的持久主体。"

### 方案：义务关联检索模式

**不需要改YML核心schema，只需要改session boot逻辑。**

当前boot流程（session_boot_yml.py）：
```python
store.recall(agent_id=agent_id, min_relevance=0.4, limit=20, sort_by="relevance_desc")
```

改为义务优先的两阶段检索：

```python
# 阶段一：从OmissionEngine拉当前agent的pending obligations
pending_obligations = omission_store.list_obligations(
    actor_id=agent_id, 
    status=["pending", "soft_overdue"]
)

# 阶段二：拉这些obligation关联的memories
obligation_memories = []
for ob in pending_obligations:
    related = store.recall(
        agent_id=agent_id,
        context_tags=[ob.obligation_id, ob.entity_id],
        min_relevance=0.1,  # 低阈值，义务关联的记忆不应被衰减过滤掉
        limit=5
    )
    obligation_memories.extend(related)

# 阶段三：补充非义务关联的高relevance记忆
general_memories = store.recall(
    agent_id=agent_id,
    min_relevance=0.5,  # 高阈值，只拉最鲜活的
    limit=10,
    sort_by="relevance_desc"
)

# 合并去重，义务关联的排在前面
```

**关键设计**：
- 义务关联的记忆用低阈值（0.1）——因为一个pending obligation关联的历史上下文不管多旧都是有用的
- 非义务关联的记忆用高阈值（0.5）——只保留最鲜活的背景知识
- 这意味着agent每次醒来，首先看到的是"我有什么未完成的义务"，而不是"我上次记得什么"

**额外要求**：gov_remember时应该把obligation_id写入context_tags：

```python
gov_remember(
    agent_id="eng-kernel",
    memory_type="task_context",
    content="YML Phase 1完成，Phase 2需要集成gov-mcp工具",
    context_tags=["yml_implementation", "P0_BOARD_DIRECTIVE"]  # ← 义务关联标签
)
```

### 实施方式

- 修改 `scripts/session_boot_yml.py` — 约30行改动
- 不需要改store.py/models.py/schema
- 需要eng-kernel执行（通过CTO下达）

---

## 五、方案四：同构系统局限标注（解决发现五）

### 问题

Labs是同构agent系统（全Claude Opus），但gov-mcp是为异构系统设计的。Labs的测试数据不能完全代表产品在真实客户环境的表现。

### 方案：实验边界声明

在所有对外材料（arXiv、Show HN、产品文档）中，明确标注：

```
Y*gov已在以下环境验证：
- 同构系统：Claude Opus 4.6 × N agents（Y* Bridge Labs，700+ CIEU记录）
- 异构系统：Claude Opus + MiniMax M2.5（CASE-005，有限验证）

尚未验证：
- 大规模异构系统（>10 agents，>3种模型）
- 对抗性环境（agent主动尝试绕过治理）
```

**关键设计**：诚实比营销重要。声明局限性反而增加可信度——CASE-001的教训。

### 实施方式

- 写入 `products/ystar-gov/LIMITATIONS.md`
- CMO在所有对外内容中引用
- 不需要代码改动

---

## 六、方案五：强制异构审计（解决发现一的根因）

### 问题

CEO评估漂移的根因是同构系统的内部张力不足。机制可以减缓但不能消除。

### 方案：制度化ChatGPT独立审计

Board已经在自发使用ChatGPT做独立审计（团队DNA里记录了这个做法）。将这个做法制度化：

**每周一次异构审计**（Level 1，Secretary执行）：

1. Secretary将本周CIEU摘要 + CEO周报发送给ChatGPT（通过Board手动操作，或未来通过API）
2. ChatGPT回答三个问题：
   - "CEO这周的自我评估和CIEU数据一致吗？哪些地方有偏差？"
   - "团队声称完成了什么？数据能验证吗？"
   - "你看到了什么CEO团队可能没看到的风险？"
3. 审计结果写入 `reports/audit/weekly_heterogeneous_audit_YYYY-MM-DD.md`
4. CEO必须在下周周报中回应审计发现

**长期方案**：当Letta MCP集成验证通过后，可以让一个非Claude模型的agent作为常驻审计员，通过gov-mcp参与治理。这同时验证了产品的异构能力。

### 实施方式

- 写入 `governance/WORKING_STYLE.md` 作为新条款
- Secretary添加到周度checklist
- 依赖Board手动操作（短期），或API自动化（中期）

---

## 七、实施优先级

| 方案 | 优先级 | 工期 | 依赖 | 风险 |
|------|--------|------|------|------|
| 方案一：CEO锚定清单 | P0 | 0天（写入CEO.md即可） | 无 | 无 |
| 方案二A：执行前预检 | P0 | 0天（写入WORKING_STYLE.md） | 无 | 可能拖慢Level 2执行 |
| 方案二B：强制对抗 | P1 | 0天（写入CEO.md） | 无 | 同构系统的对抗可能浮于表面 |
| 方案三：义务中心检索 | P1 | 1天 | YML已上线 | 需要改session_boot_yml.py |
| 方案四：局限标注 | P2 | 0天（写文档） | 无 | 无 |
| 方案五：异构审计 | P2 | 依赖Board操作 | ChatGPT接入 | Board手动操作是瓶颈 |

**P0方案今天就能生效**——都是制度文件修改，不需要代码。

---

## 八、Board决策请求

1. **是否批准方案一（CEO锚定清单）？** 写入CEO.md。
2. **是否批准方案二A（执行前预检）？** 写入WORKING_STYLE.md。方案二B（强制对抗）是否一起批？
3. **方案三（义务中心检索）是否走CTO执行？** 还是先观察YML运行数据后再改？
4. **方案五（异构审计）Board是否愿意每周操作一次？** 或者等API自动化？
5. **方案二A是否豁免Level 1？** 我建议是——Level 1的速度不能被预检拖慢。

---

## 附录：本方案的自我预检（吃自己的药）

按方案二A的模板，对本方案本身做预检：

```
1. 核心假设：制度文件的修改能改变agent的实际行为。
   → 风险：agent可能形式化地填清单但不真正思考。
   
2. 最坏结果：所有方案都沦为checkbox合规，没有产生真实的质疑和摩擦。
   
3. 更便宜的验证方式：先只实施方案一（CEO锚定清单），观察两周。
   如果CEO的评估漂移减少了，再推其他方案。

4. 作为CEO我看到的Board可能没看到的风险：
   方案二B（强制对抗）在同构系统里可能产生"伪摩擦"——
   同一个推理内核扮演反对者，生成的反对意见可能只是
   表面的措辞对立，而不是真正的认知挑战。
   真正的解法还是方案五（异构审计）。
```

**结论**：[ ] 有异议，建议调整——先P0方案落地，方案二B和方案五等两周数据后再评估。

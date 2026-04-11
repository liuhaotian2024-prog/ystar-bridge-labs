# 治理进化执行规范 — Board批准，CTO执行
**日期**: 2026-04-10
**批准人**: Board
**执行人**: CTO (Ethan Wright)
**涉及仓库**: Y-star-gov, gov-mcp, ystar-bridge-labs

---

## 总览：四个批准的方案 + 一个产品能力

| # | 方案 | 落地位置 | 类型 |
|---|------|---------|------|
| 1 | CEO锚定式自评协议 | agents/CEO.md | 制度文件 |
| 2 | 执行前预检 + 角色认知偏好 | WORKING_STYLE.md + agents/*.md | 制度文件 |
| 3 | 义务中心记忆检索 | scripts/session_boot_yml.py | 代码 |
| 4 | gov_precheck产品能力 + 配置包架构 | Y-star-gov + gov-mcp | 产品代码 |

---

## 一、制度文件改动（CTO直接写入）

### 1.1 agents/CEO.md 新增条款

在"CEO 提案审阅决策框架"段之前，插入：

```markdown
## CEO现状评估锚定协议

CEO在向Board做任何现状评估之前，必须先独立运行以下锚定清单。
Board的问题不改变清单的结论——如果清单结论和Board预期不同，
CEO应该坚持清单结论并解释差异，而不是调整结论迎合预期。

### 锚定清单（每次评估前必须过）

1. **量化基线**：
   - 本session执行了多少条Board指令？完成率？
   - CIEU里CEO的事件数？（0 = 治理盲区）
   - subagent的测试通过率？

2. **能力边界声明**（三选一，不允许模糊）：
   - "我们能做X" — 附证据（测试结果/已交付物）
   - "我们不能做X" — 附具体阻塞原因
   - "我们不确定能否做X" — 附验证计划

3. **与上次评估的delta**：
   - 上次评估说了什么？（从YML gov_recall）
   - 事实变了吗？如果没变，结论不应该变。

4. **反事实检验**：
   - 如果Board的顾问现在看到这个评估，他会同意哪些、质疑哪些？
   - 我的哪个结论最可能是受到了Board情绪信号的影响？
```

### 1.2 governance/WORKING_STYLE.md 新增条款

在第七条（意图验证）之前，插入"第六条半"（或重新编号）：

```markdown
## 第六条半：执行前预检协议（Level 2/3指令强制）

任何Level 2或Level 3指令，在record_intent之前，执行agent必须先提交预检报告。
Level 1指令豁免——Level 1的速度不能被预检拖慢。

### 预检报告格式

## 首要维度分析：[必须是角色认知偏好中的首要维度]
[从角色首要维度出发的分析，不少于两句话]

## 首要风险评估：[必须是角色认知偏好中的首要风险类别]
[该维度下最大的风险是什么，如果发生最坏结果是什么]

## 核心假设
[这个指令成功的前提假设是什么，列1-3条]

## 跨维度观察（可选）
[如果注意到其他角色维度的风险，在这里标注]

## 结论
[ ] 无异议，继续执行
[ ] 有异议，建议调整：[具体建议]
[ ] 有异议，请求Board重新评估：[原因]

### 预检提交方式

通过gov_precheck工具提交（工具可用后），或在record_intent中附带precheck字段。
未提交预检的Level 2/3指令执行动作，gov_check可DENY。

### 角色认知偏好

每个角色在分析任何决策时，必须从自己的首要维度出发。
具体维度定义在.ystar_session.json的cognitive_profiles字段中。
```

### 1.3 每个agents/*.md新增认知偏好段

**agents/cto.md 新增：**
```markdown
## 认知偏好
当分析任何决策或任务时，按以下顺序思考：
- 首要维度：技术可行性、系统稳定性、架构合理性
- 首要风险：技术故障、性能退化、依赖冲突、测试不足
- 成功度量：测试通过率、安装成功率、性能基线
预检报告第一段必须从首要维度出发。
```

**agents/cmo.md 新增：**
```markdown
## 认知偏好
- 首要维度：叙事清晰度、受众匹配、平台适配
- 首要风险：叙事失败、内容过长、时机不对、受众错位
- 成功度量：点击率、评论质量、传播深度
```

**agents/cfo.md 新增：**
```markdown
## 认知偏好
- 首要维度：成本效率、资源分配、投资回报
- 首要风险：资源浪费、定价失误、现金流断裂
- 成功度量：ROI、CAC、转化率
```

**agents/cso.md 新增：**
```markdown
## 认知偏好
- 首要维度：客户价值、市场定位、竞品差异
- 首要风险：机会成本、竞品抢先、客户流失
- 成功度量：线索数、demo请求、签约率
```

**agents/ceo.md 新增（在锚定协议之后）：**
```markdown
## 认知偏好
- 首要维度：战略一致性、跨部门协调、执行节奏
- 首要风险：方向偏移、团队过载、Board信任损耗
- 成功度量：指令完成率、CIEU健康分、义务清零率
```

---

## 二、代码改动

### 2.1 义务中心记忆检索（scripts/session_boot_yml.py改造）

修改现有session_boot_yml.py，改为义务优先的两阶段检索：

```python
# 阶段一：从OmissionEngine拉当前agent的pending obligations
# 阶段二：拉这些obligation关联的memories（低阈值0.1）
# 阶段三：补充非义务关联的高relevance记忆（高阈值0.5）
# 合并去重，义务关联排前面
```

详细逻辑见 reports/GOVERNANCE_EVOLUTION_PROPOSAL.md 方案三。

### 2.2 gov_precheck产品能力（Y-star-gov + gov-mcp）

#### 架构：配置包模式

```
Y-star-gov核心库（产品代码）
  ├── ystar/governance/precheck.py          ← 预检引擎（通用）
  │   ├── validate_precheck()               ← 维度匹配验证
  │   ├── load_cognitive_profile()           ← 从配置读取角色偏好
  │   └── PrecheckResult dataclass
  └── ystar/governance/precheck_schema.json  ← cognitive_profiles的JSON Schema

gov-mcp（MCP工具层）
  └── gov_mcp/server.py += gov_precheck()   ← MCP工具注册

配置包（每个客户自己的仓库）
  └── .ystar_session.json += cognitive_profiles字段
```

#### gov_precheck工具签名

```python
@mcp.tool()
def gov_precheck(
    agent_id: str,
    directive_id: str,
    directive_level: int,           # 1, 2, or 3
    primary_dimension: str,         # 必须匹配角色cognitive_profile
    primary_risk: str,              # 必须匹配角色cognitive_profile
    assumption: str,                # 不少于10字符
    worst_case: str,                # 不少于10字符
    cross_dimension_note: str = "", # 可选
    conclusion: str = "no_objection",  # no_objection / adjust / escalate
) -> str:
```

#### 验证逻辑（确定性，Iron Rule 1合规）

1. Level 1指令 → 直接ALLOW，不需要预检
2. 从.ystar_session.json读取cognitive_profiles[agent_id]
3. 检查primary_dimension是否在该角色的primary_dimensions列表中
4. 检查primary_risk是否在该角色的primary_risks列表中
5. 检查assumption和worst_case长度>=10
6. 不匹配 → DENY + 返回允许的维度列表
7. 匹配 → ALLOW + 写入CIEU
8. conclusion=="escalate" → 创建OmissionEngine义务（CEO审阅）

#### .ystar_session.json配置格式

```json
"cognitive_profiles": {
    "cto": {
        "primary_dimensions": ["技术可行性", "系统稳定性", "架构合理性"],
        "primary_risks": ["技术故障", "性能退化", "依赖冲突", "测试不足"],
        "success_metrics": ["测试通过率", "安装成功率", "性能基线"]
    }
}
```

#### 配置包JSON Schema（给未来用户用）

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "title": "Y*gov Cognitive Profiles Configuration",
    "description": "Per-role cognitive preferences for gov_precheck validation",
    "patternProperties": {
        "^[a-z][a-z0-9_-]*$": {
            "type": "object",
            "required": ["primary_dimensions", "primary_risks", "success_metrics"],
            "properties": {
                "primary_dimensions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                },
                "primary_risks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                },
                "success_metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1
                }
            }
        }
    }
}
```

---

## 三、测试要求

### gov_precheck测试（至少8个场景）

1. CTO提交技术维度预检 → ALLOW
2. CTO提交"叙事清晰度"维度 → DENY（维度不匹配角色）
3. CMO提交叙事维度预检 → ALLOW
4. 预检assumption少于10字符 → DENY
5. Level 1指令不需要预检 → ALLOW（跳过验证）
6. conclusion="escalate" → 创建CEO义务
7. 未知agent_id（无cognitive_profile）→ ALLOW但带warning
8. 预检通过后CIEU记录存在

### 义务中心boot测试

1. 有pending obligation的agent → boot优先显示obligation关联记忆
2. 无pending obligation → 退回到普通relevance排序
3. obligation关联记忆即使relevance低也被检索到

---

## 四、不在本次范围内

- gov_check拦截"未预检就执行"的逻辑（下个迭代）
- 配置包的独立仓库/npm包（等有第二个客户再做）
- 预检报告的质量评估（需要LLM，违反Iron Rule 1）

---

## 五、完成标准

1. 6个制度文件已更新（CEO.md, WORKING_STYLE.md, cto.md, cmo.md, cfo.md, cso.md）
2. session_boot_yml.py改为义务优先检索
3. Y-star-gov新增precheck.py + schema
4. gov-mcp新增gov_precheck工具
5. .ystar_session.json新增cognitive_profiles
6. 8个预检测试 + 3个boot测试全过
7. 所有现有测试不回归

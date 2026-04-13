---
name: 根源经验自动入硬约束（meta-rule）
type: hard_constraint / meta-rule
created: 2026-04-11
authority: Board直接授权，永久生效
---

# 规则
任何agent发现以下任一情况时，**立即写入硬约束系统**（lesson + 代码enforcement dispatch），**不需问Board**：

1. 同类错误重犯 ≥2次（即将犯第3次前必须codify）
2. Board当面纠正一个行为（一次即触发）
3. 系统gap暴露（state双写、enforcement缺口、配置无代码）
4. 自主任务完成后产生的可复用方法论
5. Board用"难道...不属于..."句式追问 = 强信号要codify

# Why
Board铁律重申：
- "每发现一个问题就从根源上彻底解决，杜绝类似错误再出现"
- "所有规则要么是硬约束（代码enforcement），要么就不是规则"
- "配置无代码执行=不存在"

不codify = 等下次再犯 = 浪费Board时间纠错。**Board的时间是公司最稀缺资源**，每次纠正同类错误 = CEO失职。

旧流程问题：CEO发现经验后习惯"等汇报+等批准"，Board要二次确认才入库。这本身就违反"自主"——自主 = 自己判断什么时候codify，不是什么都问。

# How to apply
发现触发条件 → 立即三步执行（同一response内完成）：
1. **Write lesson** 到 `knowledge/<role>/lessons/<topic>.md`，含 规则 / Why / How to apply / 系统改进建议
2. **Update DISPATCH.md** 把代码enforcement需求dispatch给Maya（hook层）或Ryan（test层）
3. **同步 .ystar_session.json** 配置（如属behavior_rules范畴，由有写权限的agent执行）

**禁止行为：**
- 写完lesson就停 → 必须dispatch代码化
- 等Board批准 → Board已永久授权
- "下次再说" → 同response必须完成
- 列选择题问Board "是否要写入" → 直接写

# 系统改进建议
hook监测agent输出含 ["以后这样" / "下次注意" / "经验教训" / Board纠正语句模式]，**自动触发lesson模板生成 + DISPATCH追加**，让CEO无法跳过codify步骤。Maya P0实施。

# Authority log
2026-04-11 23:xx Board授权: "以后一旦发现类似的经验马上安排写入硬约束里面，不用问我。这也是一个硬约束，一起写入"

---
name: 状态报告必标 5 级成熟度
description: 任何 status / progress / report 必须给每条 work item 打 L0-L5 成熟度标签，禁用模糊词如"落盘/done/ship"
type: feedback
originSessionId: b8aed99a-55f2-4073-a223-d41630cec4f4
---
任何对 Board / agent 的 status / progress / commit summary，必须给每条 work item 显式标 L0-L5 成熟度。**禁止使用"落盘 / done / ship / completed / 拿下"等模糊词作为唯一状态描述。**

| 标签 | 定义 | 验证标准 |
|---|---|---|
| **L0 IDEA** | 口头讨论/纸面，无 artifact | 无 |
| **L1 SPEC** | 6-pager / proposal / design doc 提交 | proposal commit hash + 路径 |
| **L2 IMPL** | code / config 写完，未运行测试 | impl commit + 文件存在性验证 |
| **L3 TESTED** | 测试通过，但未在 production 跑 | test pass count + commit |
| **L4 SHIPPED** | production 实际跑着，可观测有效 | live behavior log + monitoring metric |
| **L5 ADOPTED** | ≥1 真消费者在用，有 impact metric | usage data / impact 测量 |

**Why:** 2026-04-13 老大第二次纠正"misleading framing"。CEO 把 A018 的 6-pager commit (`705b45a`) 报成"落盘"，老大问"那是不是该开始实验了"——CEO 才意识到 6-pager ≠ impl。根因不是用词疏忽，是**认知模型缺成熟度颗粒度**：脑里只跟踪 commit/artifact，不跟踪生命周期阶段。Software 行业有 TRL 9 级 / AWS GA-Beta-Preview / DARPA 5 阶段——CEO 没有等价分类法，所以 spec / impl / production 在嘴里都叫"ship"。这等于 Board 看不到真实进度，决策错位（如 Board 以为 A018 在跑就不会问"是否要实验"）。

**How to apply:**

1. **每条 status item 行首必含 L 标签**：
   - ✅ "AMENDMENT-016: L4 SHIPPED (b16b563, watcher 1.5s latency in prod)"
   - ✅ "AMENDMENT-017: L1 SPEC (e464e14 6-pager only, 0% impl)"
   - ✅ "AMENDMENT-018: L1 SPEC → L2 IMPL in flight (4 engineers parallel)"
   - ❌ "A018 落盘了" / "A018 done" / "A018 ship 了" — 一律视为撒谎

2. **session summary 表格新增 Maturity 列**

3. **commit message 自带前缀**：`spec(...)` = L1, `feat(...)` = L2-L3, `deploy(...)` = L4，避免 commit msg 也含混

4. **Self-check 触发器**：每次想说"落盘 / done / ship"前，问 "L 几"。说不出 L 几就是没真完成。

5. **Apply retroactively**：遇到旧 status 没标 L 的，重写一次再发

**和其他 memory 的关系：**
- 与 `feedback_no_clock_out` 互补：no_clock_out 治"defer"，本 memory 治"虚报 ship"——两个对立 bias 都需治
- 与 `feedback_dispatch_via_cto` 互补：dispatch 流程对，但派出去 ≠ 完成；要标 L 才算

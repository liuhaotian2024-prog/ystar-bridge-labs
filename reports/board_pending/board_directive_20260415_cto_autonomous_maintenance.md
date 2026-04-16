# Board Directive: CTO 自主技术维护机制 + CZL 对齐标准

**日期**: 2026-04-15 night
**发起**: Board (Haotian Liu)
**接收**: CEO Aiden + CTO Ethan
**优先级**: P0
**Tracking 状态**: ACTIVE — Rt+1 = (未完成立即清单条目数 + 未 ship 机制条目数)

## 三处确认断裂

1. **CZL 并行原则没自动触发** — Article 11 并行任务从未登记为 OmissionEngine 义务
2. **OmissionEngine 从未主动催促** — 监控对象缺失（不知道任务在跑）
3. **CTO 没有自主技术对齐机制** — 响应式工作模式

## CTO 总 Y\* (可计算)

```
Y* = "Y*gov 系统技术无障碍运行 + 技术实现不落后于行业成熟实践"

子 Y*1 (技术障碍清零):
  Rt+1 = (import 失败 + pytest red + wire fail + hook 失效 + CIEU ERROR + HARD_OVERDUE) 数量
  目标: 0

子 Y*2 (行业对齐):
  Rt+1 = (Gap × 1.0 + Lag × 0.5) 数量
  Gap = 行业有但本系统没的能力
  Lag = 本系统有但落后的能力
  目标: 0 或所有 Gap/Lag 有明确处理计划
```

## CTO 每日 CZL 6-Step 循环

1. 技术健康扫描 (wire/pytest/k9_patrol/CIEU ERROR)
2. 外部对齐扫描 (周一次 — agent 框架/治理/因果/MAS)
3. Rt+1 计算
4. 制定修复方案 U (查 CIEU 不许猜)
5. 执行 + 验证 (Rt+1 必下降)
6. 向 CEO 汇报 (Xt → U → Yt+1 → Rt+1，禁 prose-claim)

## OmissionEngine 3 条新自动登记

1. Board 离线 30min → 登记"CEO 必须启动自主工作模式" (10min due)
2. 任务 30min 无 CIEU 行动记录 → 登记"该任务必须有进展" (30min due)
3. Rt+1 连续 3 检查点不下降 → 登记"Rt+1 必须收敛" (20min due)

由 hook_session_start.py 每 session 启动自动检查并登记。

## K9 audit 升级 (3 Layer)

每条 finding 必含：症状 (现有) + 根因 (CIEU/git log/import 链定位) + 处方 (修法 + 影响范围 + P0/P2)

## CTO 4-Step 学习方法论

1. 定义学习问题 (能被一篇论文/库直接回答)
2. 搜索路径 (优先级: 系统内 → 权威源 → 搜索引擎)
3. 评估可用性 (3 问题: 是否解决我的问题 / 生产验证 / 集成代价)
4. 输出学习成果必须落盘 (knowledge/cto/<域>/<方案>.md + CIEU TECHNICAL_LEARNING + task 文件)

## 立即执行清单 (今天)

**CTO (Ethan)**:
- [ ] 完整技术健康扫描 (Step 1) 输出 Xt
- [ ] 修 forget_guard.py JSON 输出断裂 (顾问 10 行方案)
- [ ] 修 hook_client_labs.sh async→sync 断裂
- [ ] OmissionEngine 登记 Article 11 并行义务监控规则
- [ ] 压测验证 + Rt+1 数字
- [ ] **提出 CTO 团队内部权限方案** (防止工程师写不进文件拖慢进程)

**CEO (Aiden)**:
- [ ] 确认 OmissionEngine 修复后，下次停滞收到真 HARD_OVERDUE 拦截
- [ ] 按 CZL 格式汇报每次任务进展
- [ ] Rt+1 连续不收敛主动上报 Board (不等 Board 问)

## Rt+1 跟踪

```
Initial: 6 立即清单条目 + 5 机制条目 = 11
Target: 0
Update mechanism: 每完成一条 → CEO update 此文件 + reduce Rt+1
```

## 关联 commit (会持续追加)

- _本 directive 立 tracking_: (本 commit)

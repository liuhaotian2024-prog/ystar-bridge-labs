# CEO Phase 1 提案草案 — 基础建设完善

**提案状态**: DRAFT（未提交 Board，CEO 自检中）
**推导来源**: enforce_inventory_20260416.md + mission_function + dependency_sequencing wisdom

## 推导过程（不拍脑袋）

### Step 1: 从 enforce 清单找 gap

14 条 enforce 规则中：
- 4 条有 gap（通讯 2: whitelist auto-block 缺 + CZL ID collision 无自动检测; 诚实 2: tool_uses auto-compare CZL-152 在飞 + artifact auto-verify CZL-153 在飞）
- 3 条 partial（precheck 只扫 1 repo CZL-151 刚修 / V2 model enforce warn 未 deny / session close 非 mandatory）
- 7 条 OK

### Step 2: 按依赖链排序

```
enforce 基础 (hook/script 真 work) 
    ↓
通讯纪律 (5-tuple 真自动执行不靠记忆)
    ↓  
诚实保障 (hallucination + tool_uses 自动 catch)
    ↓
流程完整 (V2 model → enforce deny)
    ↓
管理分工 (CEO System 5 / CTO 独立 / CMO+CSO+CFO 按前置解锁)
    ↓
使命函数驱动 (M(t) delta → ADE → auto action queue)
```

### Step 3: Phase 1 = 依赖链最底层

**Phase 1 只做一件事: 让 enforce 基础真 WORK（不是 "shipped"，是 "LIVE fire verified"）**

具体：
1. CZL-152 (Maya auto tool_uses compare) 落地后 → smoke 验证真 fire CIEU 事件
2. CZL-153 (Leo auto receipt artifact verify) 落地后 → smoke 验证真 catch 假文件
3. CZL-151 (Ryan precheck 4-repo) 已落地 → ✓
4. Whitelist reply taxonomy → promote from warn to deny（真 block 无 tag reply）
5. V2 Action Model FG rules → promote from dry_run to warn

**Phase 1 不做**: 新功能、新模型、新 spec、找客户、写 blog、战略规划迭代
**Phase 1 只做**: 让已有的 enforce 机制从 "shipped" 变 "LIVE verified"

### Step 4: 可用人力 (from 分工模型)

- CEO 本线: smoke 验证 + promote + wisdom 持续建
- CTO Ethan: 技术质量审计（已有代码的 bug 扫描）
- Ryan: 自动化 wire (CZL-151 已完成)
- Maya: enforce rule wire (CZL-152 在飞)
- Leo: artifact verify (CZL-153 在飞)
- Samantha: 归档 + memory integrity
- 5 new engineers: 暂不派活 (trust=30 training-wheels 等 Phase 2)

### Step 5: Phase 1 完成标准 (Rt+1=0 条件)

全部满足才算 Phase 1 完成：
- [ ] 4 个 P0 自动化全 LIVE（tool_uses compare + artifact verify + precheck 4-repo + whitelist deny）
- [ ] V2 model FG rules promoted to warn
- [ ] 每个 enforce 都有 smoke test 证明真 fire（不是 "shipped"，是 "fire verified"）
- [ ] CEO wisdom system 持续运转（每 insight 即时存 → 下 session 可恢复）
- [ ] Session handoff 机制验证（模拟重启 → 新 session 读 → 能理解 → 能继续）

### Phase 1 → Phase 2 触发条件

Phase 1 所有 Rt+1=0 → 解锁 Phase 2:
- 系统全检 600 技术组件 + 19 管理维度健康检查
- 模块连通性 graph
- Session 全流程自动化模型

**提案准备状态**: 推导完成，待 CEO 自检后提交 Board

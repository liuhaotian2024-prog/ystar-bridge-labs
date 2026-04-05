# SIM-001: GOV MCP 全系统技术风险盘点
# Date: 2026-04-05
# Author: CTO + CMO Joint Audit
# Status: Awaiting Board Review

---

## P0 — 数据丢失 / 安全漏洞（5项）

### P0-1: Path Traversal via Substring Matching
- **文件:** server.py gov_escalate路径检查
- **风险:** `any(d in path for d in deny)` 使用子串匹配而非路径规范化
- **攻击:** `./etc/passwd` 不匹配 `/etc`；`/home/username` 匹配 `/home/user`
- **模拟场景:** 金融场景Day4（越权访问），法律场景Day3（渗透测试）
- **修复:** 使用 `pathlib.Path.resolve()` + `is_relative_to()` 做路径规范化

### P0-2: git branch Router逻辑反转
- **文件:** router.py:261
- **风险:** `if non_flag and flag_only` 条件反转，允许 `git branch myname`（写操作）
- **攻击:** agent可以创建/删除分支而不被拦截
- **模拟场景:** 开发者场景Day3（git操作拦截）
- **修复:** 改为 `if non_flag:` 移除 `and flag_only`

### P0-3: Only-paths前缀边界绕过
- **文件:** server.py gov_escalate path检查
- **风险:** `path.startswith(ap)` 不检查目录边界
- **攻击:** only_paths=["/home/user"] 时 `/home/username` 通过
- **模拟场景:** 法律场景Day3（multi-tenant隔离）
- **修复:** 路径末尾强制加 `/` 或使用 `Path.is_relative_to()`

### P0-4: gov_baseline/delta竞争条件
- **文件:** server.py:1133-1251
- **风险:** `state._baselines` 无锁保护，并发写入可能丢失
- **攻击:** 并发baseline捕获+delta读取产生无效差异
- **模拟场景:** 医疗场景Day4（10并发agent），制造场景Day5
- **修复:** 对 `_baselines` dict加RLock

### P0-5: Subprocess shell=True无路径规范化
- **文件:** server.py:292
- **风险:** `subprocess.run(command, shell=True)` 不规范化路径参数
- **攻击:** `cat ../../etc/passwd` 可绕过deny规则
- **模拟场景:** 法律场景Day6（黑客攻击模拟）
- **修复:** 执行前对命令中的文件路径做 `realpath()` 规范化

---

## P1 — 功能失效（10项）

### P1-1: Windows start_new_session崩溃
- **文件:** cli.py:198
- **风险:** `start_new_session=True` 仅POSIX支持，Windows会崩溃
- **模拟场景:** 所有场景（跨平台兼容）
- **修复:** `sys.platform == "win32"` 条件分支

### P1-2: CIEU Store未缓存，每次创建新实例
- **文件:** server.py:59-60
- **风险:** `state._cieu_store` 永远是None，每次gov_report创建新CIEUStore
- **影响:** 审计报告数据不一致
- **模拟场景:** 金融场景Day6（审计报告），医疗场景Day6

### P1-3: gov_escalate权限回退到全局合约
- **文件:** server.py:538-541
- **风险:** principal查找失败时fallback到 `state.active_contract`
- **攻击:** delegated agent可以升级到全局权限
- **模拟场景:** 金融场景Day5（escalation测试），制造场景Day4

### P1-4: gov_chain_reset孤儿节点
- **文件:** server.py:750-751
- **风险:** 删除principal时不递归删除子agent
- **影响:** delegation树出现悬空引用
- **模拟场景:** 法律场景Day4（高并发delegation）

### P1-5: Python模块白名单过严
- **文件:** router.py:291-296
- **风险:** 只允许pytest和pip，拦截 `python3 -m json.tool` 等安全模块
- **影响:** false positive干扰开发者工作流
- **模拟场景:** 开发者场景Day2（false positive检测）

### P1-6: Delegation Chain无并发保护
- **文件:** server.py:54
- **风险:** `delegation_chain` 和 `active_contract` 无锁，并发访问可能崩溃
- **模拟场景:** 法律场景Day4（50并发agent），医疗场景Day4

### P1-7: CIEU Merkle写入静默失败
- **文件:** server.py:618-622
- **风险:** `except Exception: pass` 吞掉写入错误，Merkle链出现断裂
- **影响:** 审计链不完整，无法通过验证
- **模拟场景:** 金融场景Day3，医疗场景Day4

### P1-8: 硬编码localhost
- **文件:** cli.py:263, 277
- **风险:** SSE URL硬编码 `127.0.0.1`，不支持远程/Docker部署
- **模拟场景:** 制造场景Day5（ERP集成）

### P1-9: Command injection via always_deny子串匹配
- **文件:** router.py:190
- **风险:** `if pattern in cmd` 子串匹配导致false positive和false negative
- **攻击:** deny "rm" 会误杀 `git remote -v`
- **模拟场景:** 法律场景Day6（黑客攻击）

### P1-10: Regex parser无schema验证
- **文件:** server.py nl_to_contract调用
- **风险:** 格式错误的AGENTS.md静默生成空合约
- **影响:** 用户以为有治理保护，实际无规则
- **模拟场景:** 所有场景Day2（首次配置）

---

## P2 — 用户体验影响（5项）

### P2-1: SSE无重连机制
- 长连接静默断开时工具调用超时
- 模拟场景：医疗场景Day4（网络断线）

### P2-2: 空deny列表默认全放行
- 未配置deny时无最低安全基线
- 模拟场景：开发者场景Day1（首次使用）

### P2-3: Windows路径混合分隔符
- router.py `rsplit("/")` 不处理混合 `/` 和 `\`
- 模拟场景：跨平台场景

### P2-4: 白名单fallback无警告
- 平台专用白名单不存在时静默回退到通用版本
- 模拟场景：开发者场景Day1

### P2-5: gov_contract_load无进度提示
- 大型AGENTS.md解析时无反馈
- 模拟场景：法律场景Day2

---

## 风险统计

| 级别 | 数量 | 状态 |
|---|---|---|
| P0 | 5 | 全部注入模拟场景 |
| P1 | 10 | 全部注入模拟场景 |
| P2 | 5 | 选择性注入 |
| **总计** | **20** | |

---

## 发布前修复建议

**必须修复（Release Blocker）：** P0-1, P0-2, P0-3, P0-5（安全漏洞）
**强烈建议（High Priority）：** P1-1, P1-3, P1-6, P1-7
**可以接受技术债（Post-Release）：** P1-2, P1-5, P1-8, P1-9, P1-10, 全部P2

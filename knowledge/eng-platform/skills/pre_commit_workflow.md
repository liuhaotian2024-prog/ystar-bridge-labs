# Skill: Pre-Commit Workflow (Test-First Git Commit)

**类型**: Hermes 可加载 skill（4 段格式）
**适用 agent**: 全员（特别 CTO + 4 engineers）
**立约**: 2026-04-13 (AMENDMENT-012 remediation)
**依据**: `pre_commit_requires_test` behavior rule — 任何 git commit 前必须 pytest 全绿

---

## 1. Trigger (适用场景)

下列任一条件触发加载本 skill：
- 准备 `git commit` 前
- 修改了 `Y-star-gov/ystar/` 或 `Y-star-gov/tests/` 任何代码
- Hook DENY `git commit` 并提示 "tests required"
- Board 要求"测试通过再 commit"

## 2. Procedure (程序——逐步执行)

### Step 1: 在 Y-star-gov/ 跑全量测试

```bash
cd /Users/haotianliu/.openclaw/workspace/Y-star-gov
python -m pytest --tb=short -q
```

**期望输出**: 
```
........................... [100%]
86 passed in X.XXs
```

**如果有 FAILED**:
- 停下，不要 commit
- 读 pytest 输出的 traceback
- 修复 broken test 或 revert 代码
- 重新跑 pytest 直到全绿

### Step 2: Stage 具体文件（不用 `git add -A`）

```bash
# 只 add 你这次改的文件，避免意外 stage .env / credentials
git add ystar/adapters/boundary_enforcer.py
git add ystar/session.py
git add tests/test_deny_as_teaching.py
```

**禁止**:
```bash
git add -A   # 可能 stage .env / .ystar_cieu.db / 敏感文件
git add .    # 同上
```

### Step 3: Commit 带 Co-Authored-By

使用 HEREDOC 保证格式：

```bash
git commit -m "$(cat <<'EOF'
feat: add Remediation dataclass for deny-as-teaching

- PolicyResult 新增 remediation field (AMENDMENT-012)
- Remediation 包含 wrong_action / correct_steps / skill_ref / lesson_ref
- 10 条核心 rule 补全 remediation 数据

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### Step 4: 验证 commit 成功

```bash
git log -1 --oneline
git status
```

期望：
- 最新 commit 出现在 log
- `git status` 显示 working tree clean（或只有新的未 stage 文件）

---

## 3. Pitfalls (容易踩的坑)

### 坑 A: 跳过测试直接 commit
**症状**: `git commit -m "quick fix"` 不跑 pytest
**规避**: Hook 会 DENY（如果实装了 `pre_commit_requires_test`）。即使 hook 未拦，也是违反铁律

### 坑 B: 测试有 1 个 FAILED 但"不影响我这次改动"就 commit
**症状**: pytest 输出 `85 passed, 1 failed` → 觉得"failed 是别人的代码" → commit
**规避**: **任何 FAILED 都不能 commit**。可能你的改动间接破坏了其他模块。必须修到全绿

### 坑 C: `git add -A` 把 `.env` / `.ystar_cieu.db` / credentials 误 stage
**症状**: `git status` 显示 `.env` / `__pycache__` / `.db` 被 stage
**规避**: 只 add 具体文件名。如果误 add，用 `git restore --staged <file>` 取消

### 坑 D: Commit message 没有 Co-Authored-By
**症状**: 忘记加 Co-Authored-By 行
**规避**: 用 HEREDOC 模板（Step 3），自动包含。Board 要求所有 AI agent commit 必须署名

### 坑 E: 在 ystar-company/ 跑 pytest（路径错误）
**症状**: `cd ystar-company && pytest` → 报 "no tests found"
**规避**: 必须 `cd Y-star-gov/` 再跑 pytest（测试在 Y-star-gov/tests/）

### 坑 F: Hook 未实装时以为"不用测试"
**症状**: Hook 代码未 deploy → agent 以为可以绕过
**规避**: 即使 hook 未拦，铁律仍生效。任何 commit 前必须 pytest 全绿（人工自律）

---

## 4. Verification Steps (验证执行成功)

- [ ] `pytest --tb=short -q` 全绿（86 passed 或更多）
- [ ] `git add` 只包含这次修改的文件（不含 .env / .db / __pycache__）
- [ ] Commit message 包含 `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
- [ ] `git log -1` 显示最新 commit
- [ ] `git status` clean（或只有新未 tracked 文件）
- [ ] CIEU 无 `BEHAVIOR_RULE_VIOLATION` event (如果 hook 实装)

---

## 5. 关联 skill / doc

- `AGENTS.md` 全员铁律：代码改动必须 test coverage
- `.ystar_session.json` → `agent_behavior_rules.*.pre_commit_requires_test: true`
- `knowledge/cto/lessons/test_skip_regression_2026_04_10.md` (历史事故：跳测试导致 PyPI 0.47.0 broken)
- `Y-star-gov/tests/test_behavior_rules.py` (behavior_rules 测试本身)

---

## 6. 版本
v0.1 — 2026-04-13 Jordan (eng-domains) 为 AMENDMENT-012 remediation 编写

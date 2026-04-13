# TASK: Letta可行性验证
# Assigned to: Ethan (eng-platform)
# Priority: Level 1 (直接执行)
# Created: 2026-04-10
# Status: PENDING — 下个session开始时执行
# Report to: Board

---

## 目标

验证Letta能否成为Labs的持久化记忆层。

## 执行步骤

### Step 1: 安装Letta

```bash
pip install letta
```

### Step 2: 连接本地ystar-gemma

```bash
letta server &
letta configure
# 选择Ollama provider
# 模型选ystar-gemma
```

### Step 3: 给Samantha创建一个Letta agent

```bash
letta create agent \
  --name "samantha-secretary" \
  --persona "Secretary of Y* Bridge Labs, responsible for governance documentation and auditing"
```

### Step 4: 跨session验证

1. 第一个对话：告诉agent一件具体的事
   - "今天完成了GOV-010，active_task.py新增mission模式"
   - 关闭窗口
2. 重新开窗口：
   - "上次我们做了什么？"
   - 看agent是否记得

## 验证报告必须回答三个问题

1. **跨session记忆是否真实有效？** — agent是否在新session中准确回忆上次对话内容
2. **ystar-gemma作为底层模型运行是否稳定？** — 响应速度、错误率、是否需要更大模型
3. **Letta和Y*gov的hook是否有冲突？** — 安装/运行过程中是否触发gov hook异常

## 完成标准

验证报告发Board，附原始日志。

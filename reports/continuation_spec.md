# Session Continuation Protocol — 设计规格

## 问题
每次session重启，CEO表现为失忆——有信息但不行动。Board每次都要花时间"唤醒"团队。

## 根因
- session_handoff.md是散文叙述（"上次做了什么"），不是可执行指令
- boot协议输出信息后要求"汇报"，而不是"接着干"
- 没有"你正在做什么、做到哪了、下一步干什么"的精确状态

## 方案：3个改动

### 改动1: session_close自动生成 memory/continuation.md

session关闭时（session_close_yml.py或手动），自动生成结构化continuation文件：

```markdown
# Continuation — 下次session直接执行
# Generated: 2026-04-11 20:30 by CEO Aiden

## 你正在打什么仗
Y*Defuse 30天战役，Day 1 (2026-04-11)，目标10K用户+20K stars

## 团队当前状态
| 角色 | 正在做 | 进度 | 阻塞 |
|------|--------|------|------|
| CTO | defuse MVP Level 2白名单 | Layer 4/12 | 无 |
| CMO | README + Show HN文案 | 起草中 | 无 |
| CSO | 社区渗透计划 | 规划中 | 无 |

## 你（CEO）下次session第一件事
1. 检查CTO defuse进度——跑pip install测试
2. 审核CMO Show HN文案质量
3. 推进DIRECTIVE_TRACKER 13个❌

## 不要做的事
- 不要向Board汇报治理水管状态
- 不要列清单问Board批准
- 不要重复查已决事项（见knowledge/ceo/board_decisions_log.md）
```

### 改动2: governance_boot.sh加载continuation.md到stdout

在Step 9（obligations）之后加Step 10：
```bash
# STEP 10: Load continuation (无缝衔接核心)
if [ -f "$YSTAR_DIR/memory/continuation.md" ]; then
  echo ""
  echo "--- CONTINUATION (上次做到哪了) ---"
  cat "$YSTAR_DIR/memory/continuation.md"
fi
```

### 改动3: CLAUDE.md boot协议改为"执行"而非"汇报"

当前Step 3: "欢迎回来老大。当前战役：..."（汇报模式）

改为:
```
Step 3: 读取continuation.md，直接执行里面的"下次session第一件事"。
如果Board在线，用一句话说"接着上次干，[当前正在做的事]"。
如果Board不在线，直接干，不等指令。
不要列清单，不要问批准。
```

## 验收标准
新session启动后，CEO在30秒内开始执行上次未完成的工作，不需要Board提醒任何事。

# Article 11 + CIEU 5-Tuple 合并工作法 (2026-04-14)
Trigger Board "第十一条 + cieu 工作法结合".
## 工作流
Step 1 顶层 CIEU / Step 2 U 粒度判 (单路串行, 多路 Article 11) / Step 3 每路嵌套子 CIEU / Step 4 本线 1 路 (禁躺平) / Step 5 main agent tool_result 实测 Rt+1 (禁 prose) / Step 6 全路归零才归流 (禁换任务)
## 反 pattern
Rt+1≠0 换任务 / 出选择题 / prose-claim / 派完躺平
## CIEU event_type (待 Leo/Maya 代码层)
CIEU_TASK_START / DISPATCH / STEP / VERIFY / PATH_CLOSE / TASK_END
## Rt+1 本 methodology L3 spec, L5 需代码 enforce + 3 session 验证

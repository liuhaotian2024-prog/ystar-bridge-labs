# 自主改进队列
# 工程师已被授权执行，不需要Board指令
# daemon每30分钟取队首任务执行

## 队列（按优先级）
- [ ] eng-kernel: nl_to_contract正则优化
      目标：提高合约解析准确率
      验收：现有测试全通过+新增5个边界测试
- [ ] eng-governance: CausalEngine接入orchestrator
      目标：_run_causal_advisory()被实际调用
      验收：CIEU有causal_analysis事件记录
- [ ] eng-domains: 新增SaaS领域包
      目标：覆盖subscription/trial/churn场景
      验收：domain list显示saas pack
- [ ] eng-platform: CLI错误信息标准化
      目标：所有命令错误信息格式统一
      验收：用户友好的错误提示

## 完成记录
| 任务 | 完成时间 | 执行agent | 结果 |
|------|---------|----------|------|

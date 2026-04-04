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

- [ ] CMO（由金金辅助）：从skills.sh安装market research skill
      目标：用它分析Y*gov的竞品定位
      验收：knowledge/cmo/competitor_analysis_2026.md
      说明：金金做信息收集（便宜），CMO做判断和写作（贵但必要）

- [ ] CSO（由金金辅助）：从skills.sh安装sales outreach skill
      目标：生成针对CISO/VP Eng的冷邮件模板
      验收：sales/templates/cold_email_v1.md
      说明：金金做收集，CSO做写作

- [ ] CFO（由金金辅助）：搜索SaaS定价benchmark数据
      目标：验证$0/$49/$499定价是否合理
      验收：knowledge/cfo/pricing_validation.md
      说明：免费来源，零书籍预算

## 完成记录
| 任务 | 完成时间 | 执行agent | 结果 |
|------|---------|----------|------|

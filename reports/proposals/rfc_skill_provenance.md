# RFC: SkillProvenance接入hook.py
**RFC编号:** RFC-2026-003
**标题:** SkillProvenance供应链风险检测接入hook执行路径
**提出者:** CTO (eng-governance)
**日期:** 2026-04-03
**状态:** 待Board审批
**优先级:** P2

## 1. 动机
SkillProvenance已在domains/openclaw/adapter.py实现，
assess_skill_risk()可检测MITRE ATLAS 155种攻击模式，
但当前没有hook触发点，外部skill加载完全未被检测。

## 2. 设计方案
在hook.py的_check_hook_full()里，
当tool_name为Read且file_path匹配skill文件模式时，
对skill name/source/publisher跑assess_skill_risk()。
结果写入CIEU（event_type: skill_provenance_check）。

## 3. 向后兼容性
纯新增检测，不修改现有拦截逻辑。
assess_skill_risk()失败时fail-safe，不block hook。

## 4. 不硬编码原则
skill文件匹配模式作为session.json可配置参数：
{ "skill_provenance": { "scan_patterns": ["*/SKILL.md", "*/skills/**"] } }

## 5. 测试计划
新增tests/test_skill_provenance_hook.py，10个测试用例。
现有669测试必须全部通过。

## 6. 风险
LOW — 纯新增，fail-safe包裹，不影响现有执行路径。

## 7. Board决策点
1. 批准接入？
2. 默认scan_patterns是否合理？

**状态:** ⏸️ 等待Board审批

---

## Board批复 (2026-04-03)

**批准人:** Board（刘浩天）
**状态:** ✅ 已批准，可以执行

### 批准内容
1. ✅ SkillProvenance接入Read工具路径
2. ✅ fail-safe包裹，不block hook
3. ✅ 结果写入CIEU

### 强制性设计要求
scan_patterns不得硬编码，必须作为
session.json可配置参数，代码里只有默认值：

  scan_patterns = session_cfg.get(
      "skill_provenance", {}
  ).get("scan_patterns", ["*/SKILL.md", "*/skills/**"])

**执行优先级:** P2

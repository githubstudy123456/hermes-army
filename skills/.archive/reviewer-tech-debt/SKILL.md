---
name: reviewer-tech-debt
description: 技术债务评估 — 识别维护性风险、遗留代码、重复代码、过期依赖等债务问题。
trigger: 技术债务评估
---

# Reviewer Tech Debt

## Steps

1. **代码扫描** — 使用工具识别技术债务
   ```bash
   # 代码重复检测
   ruff check . --select=PLR0912 --output-format=json  # Python

   # 过期依赖检查
   npm outdated
   pip list --outdated
   ```
2. **债务识别** — 检查：
   - 重复代码 > 3 处
   - 过期依赖（1年以上未更新）
   - 硬编码配置
   - TODO/FIXME/HACK 注释
   - 缺失的类型标注（TypeScript/Python type hints）
3. **债务量化** — 按影响程度分级：
   - 高：随时可能引发问题
   - 中：维护成本高
   - 低：可以接受但需要记录
4. **还款计划** — 为每个高/中风险债务制定修复计划
5. **输出债务报告** — 债务清单 + 还款优先级

## Pitfalls

- 不要只检查语法错误，要深入逻辑层审核
- 审核报告必须包含具体代码位置，不能只说"有问题"
- 严重问题（P0/P1）必须立即打回，不接受"先上线再改"

## Verification

- 审核报告写入 `~/.hermes/army-workspace/06-审核报告/`
- 报告命名格式：`reviewer-{date}-{skill_name}.md`
- 报告必须包含：审核对象、质量评分、问题列表、修改建议、通过/拒绝结论

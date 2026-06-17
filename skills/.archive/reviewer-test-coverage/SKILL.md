---
name: reviewer-test-coverage
description: 测试覆盖评估 — 分析单元测试/集成测试覆盖率，评估测试质量，给出用例补充建议。
trigger: 测试覆盖评估
---

# Reviewer Test Coverage

## Steps

1. **接收代码** — 确认要评估的代码项目
2. **覆盖率扫描** — 运行覆盖率工具
   ```bash
   # Node.js
   npx jest --coverage --json > /tmp/coverage.json

   # Python
   pytest --cov=. --cov-report=json > /tmp/coverage.json
   ```
3. **覆盖率分析** — 检查：
   - 行覆盖率（是否 ≥ 60%）
   - 分支覆盖率（关键逻辑是否有分支测试）
   - 函数覆盖率（公开 API 是否都有测试）
4. **测试质量** — 检查：
   - 是否有边界值测试
   - 是否有异常情况测试
   - 测试是否独立（无执行顺序依赖）
5. **补充建议** — 列出缺失的测试用例
6. **输出覆盖报告** — 覆盖率数据 + 补充建议清单

## Pitfalls

- 不要只检查语法错误，要深入逻辑层审核
- 审核报告必须包含具体代码位置，不能只说"有问题"
- 严重问题（P0/P1）必须立即打回，不接受"先上线再改"

## Verification

- 审核报告写入 `~/.hermes/army-workspace/06-审核报告/`
- 报告命名格式：`reviewer-{date}-{skill_name}.md`
- 报告必须包含：审核对象、质量评分、问题列表、修改建议、通过/拒绝结论

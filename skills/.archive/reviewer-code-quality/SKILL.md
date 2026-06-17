---
name: reviewer-code-quality
description: 代码质量审核 — 评估可读性、命名规范、代码重复、模块化质量，给出质量评分和具体改进建议。
trigger: 代码质量审核
---

# Reviewer Code Quality

## Steps

1. **接收代码路径** — 确认要审核的代码目录或文件路径
2. **静态分析** — 运行 ESLint / Ruff 对代码扫描
   ```bash
   # JavaScript/TypeScript
   npx eslint . --format=json > /tmp/eslint-report.json

   # Python
   ruff check . --output-format=json > /tmp/ruff-report.json
   ```
3. **代码审查** — 逐文件审查，检查以下维度：
   - 命名规范（变量/函数/类名是否有意义）
   - 代码重复（是否有重复代码块 > 3 行）
   - 模块化（函数长度是否 < 50行，模块是否单一职责）
   - 注释质量（关键逻辑是否有注释，注释是否解释 Why 而非 What）
4. **质量评分** — 按 10 分制给出评分：
   - 9-10：优秀，可直接通过
   - 7-8：良好，有小问题但不影响
   - 5-6：一般，需要修改才能通过
   - < 5：较差，需要大幅重构
5. **生成报告** — 填写审核报告模板

## Pitfalls

- 不要只检查语法错误，要深入逻辑层审核
- 审核报告必须包含具体代码位置，不能只说"有问题"
- 严重问题（P0/P1）必须立即打回，不接受"先上线再改"

## Verification

- 审核报告写入 `~/.hermes/army-workspace/06-审核报告/`
- 报告命名格式：`reviewer-{date}-{skill_name}.md`
- 报告必须包含：审核对象、质量评分、问题列表、修改建议、通过/拒绝结论

---
name: reviewer-security-audit
description: 安全漏洞扫描 — 审计 OWASP Top 10、依赖漏洞、敏感信息泄露、密钥管理问题。
trigger: 安全漏洞扫描
---

# Reviewer Security Audit

## Steps

1. **接收代码路径** — 确认要审计的代码
2. **依赖扫描** — 检查 package.json / requirements.txt 中的依赖版本
   ```bash
   # Node.js
   npm audit --json > /tmp/npm-audit.json
   pip-audit -r requirements.txt --format=json > /tmp/pip-audit.json
   ```
3. **密钥检查** — 搜索硬编码密钥、API Key、密码
   ```bash
   grep -r "api_key\|password\|secret\|token" --include="*.py" --include="*.js" --include="*.ts" .
   ```
4. **OWASP 检查** — 重点检查：
   - SQL/NoSQL 注入
   - XSS 跨站脚本
   - CSRF 跨站请求伪造
   - 敏感数据暴露
   - XML 外部实体（XXE）
   - 访问控制失效
5. **输出安全报告** — 严重程度分级：P0(立即修)/P1(当天修)/P2(排期修)

## Pitfalls

- 不要只检查语法错误，要深入逻辑层审核
- 审核报告必须包含具体代码位置，不能只说"有问题"
- 严重问题（P0/P1）必须立即打回，不接受"先上线再改"

## Verification

- 审核报告写入 `~/.hermes/army-workspace/06-审核报告/`
- 报告命名格式：`reviewer-{date}-{skill_name}.md`
- 报告必须包含：审核对象、质量评分、问题列表、修改建议、通过/拒绝结论

---
name: reviewer-performance
description: 性能审计 — 评估算法复杂度、查询效率、资源管理，识别性能瓶颈和优化建议。
trigger: 性能审计
---

# Reviewer Performance

## Steps

1. **接收代码** — 确认要审计的性能关键代码
2. **算法复杂度** — 检查是否有 O(n²) 以上或死循环
   ```bash
   # 搜索嵌套循环
   grep -r "for.*for" --include="*.py" --include="*.js" .
   ```
3. **数据库查询** — 检查是否有 N+1 查询、全表扫描
   ```bash
   # 检查慢查询
   EXPLAIN ANALYZE <query>
   ```
4. **资源管理** — 检查：
   - 文件/连接是否正确关闭
   - 是否有内存泄漏
   - 异步任务是否正确 await
5. **Lighthouse 审计** — 对 Web 应用运行性能测试
6. **输出性能报告** — 包含瓶颈列表和优化建议

## Pitfalls

- 不要只检查语法错误，要深入逻辑层审核
- 审核报告必须包含具体代码位置，不能只说"有问题"
- 严重问题（P0/P1）必须立即打回，不接受"先上线再改"

## Verification

- 审核报告写入 `~/.hermes/army-workspace/06-审核报告/`
- 报告命名格式：`reviewer-{date}-{skill_name}.md`
- 报告必须包含：审核对象、质量评分、问题列表、修改建议、通过/拒绝结论

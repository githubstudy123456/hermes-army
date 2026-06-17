# skill: financial-private-equity · portfolio-report

> Portfolio 监控报告 · Portfolio Monitoring & Reporting

## 基本信息

- **name**: portfolio-report
- **description**: 对已投项目组合进行定期监控，收集关键运营指标（KPI）、财务表现、估值变动、风险事件，生成 Portfolio 监控报告，供投委会和 LP 定期审阅。
- **trigger**: 当用户提及"Portfolio 报告"、"持仓报告"、"portfolio report"、"投后管理报告"、"组合监控"、"portfolio monitoring"时触发。

---

## 触发条件

- 用户输入包含 Portfolio 报告 / 持仓报告 / portfolio monitoring / portfolio report / 投后管理
- 例行季度 LP 报告准备
- 投委会定期 review
- 单个项目出现重大事件（需要立即触发特别报告）

---

## 执行步骤

### Step 1 · 收集 Portfolio 元数据（web）

1. 确认 Portfolio 名单（所有已投项目）。
2. 获取各项目基本信息：
   - 投资日期、投资轮次、持股比例
   - 投资成本（Entry Valuation）
   - 基金当前持股价值
3. 建立/更新 Portfolio 跟踪数据库。

### Step 2 · 收集运营 KPI 数据（web）

1. 各项目定期报送运营数据（通过数据室或邮件）：
   - 收入、ARR、增速
   - 客户数、留存率、NPS
   - 核心产品里程碑
2. 行业宏观数据更新（影响估值假设）。

### Step 3 · 财务表现收集（web + terminal）

1. 收集各项目最新财务报表（如有）：
   - 营收、EBITDA、现金消耗率
   - 资产负债表健康度
2. 使用 `terminal` 执行 Python 脚本：
   - 计算 Portfolio 整体 IRR / MOIC（基于最新估值）
   - 计算各项目 DPI（实现收益）、TVPI（总收益）
   - 生成财务表现汇总表

### Step 4 · 估值更新（Valuation Update）

1. 基于最新财务数据和可比公司估值倍数更新各项目估值。
2. 确认估值方法（最新一轮融资价格 / EV/EBITDA Comps / DCF）。
3. 计算 Portfolio 整体未实现收益/损失。
4. 标注估值的置信度（Level 1 / 2 / 3）。

### Step 5 · 风险事件追踪（web）

1. 收集 Portfolio 内各项目重大事件：
   - 关键人员变动（CEO/CTO 离职）
   - 监管处罚、诉讼
   - 竞争格局剧变
   - 财务危机信号（现金耗尽、违约）
2. 评估各风险事件的严重程度和影响。

### Step 6 · 退出进展追踪（Exit Progress）

1. 各项目退出可能性评估：
   - IPO 路径（预计时间表、窗口期）
   - M&A 路径（潜在买方、谈判进展）
   - 续投/回购可能性
2. 更新退出预期时间表。

### Step 7 · 生成 Portfolio 监控报告

调用 `terminal` 执行 Python 脚本生成 Markdown 报告，可导出为 PDF。

报告结构：
1. **Portfolio 概览**：项目数量、总投资、当前估值、整体 IRR / MOIC
2. **各项目表现明细**：分项目 KPI、财务表现、估值变动
3. **风险事件汇总**：按严重程度分级
4. **退出进展**：各项目退出路径与时间表
5. **下阶段行动计划**：具体待办事项

---

## 输出格式

- 优先输出 Markdown 报告（分 sections，结构清晰）
- 如需 PDF，调用 `terminal` 执行脚本转换
- 如需 Excel，调用 `terminal` 执行 Python 脚本（openpyxl）生成 .xlsx 详细数据表
- 标注所有数据来源和截止日期
- 标注"仅供参考，不构成投资建议"

---

## 常见陷阱（pitfalls）

1. **数据不完整**：部分项目未及时更新数据，导致 Portfolio 整体数字失真。
2. **估值方法不一致**：各项目使用不同估值方法，未统一导致不可比。
3. **风险事件漏报**：未能及时捕捉 Portfolio 项目风险事件，错过干预窗口。
4. **忽略 LP 报告合规要求**：报告格式和数据披露需符合基金协议约定。
5. **退出预期过于乐观**：将潜在退出视为确定事件，高估收益。

---

## 验证方法（verification）

- [ ] Portfolio 所有项目均有数据（无遗漏）
- [ ] 估值方法标注清楚，Level 1/2/3 分类合理
- [ ] IRR / MOIC 计算逻辑正确（基于时间加权）
- [ ] 风险事件按严重程度分级（High / Medium / Low）
- [ ] 退出预期有明确依据（非主观假设）
- [ ] 报告格式符合 LP 协议约定
- [ ] 人工复核签字记录
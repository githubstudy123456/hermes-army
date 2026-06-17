# skill: financial-private-equity · ic-memo

> 投资委员会备忘录 · Investment Committee Memo

## 基本信息

- **name**: ic-memo
- **description**: 起草私募股权投资委员会（IC）备忘录，结构化呈现投资机会概览、商业逻辑、财务模型、估值、风险点及投资建议，供投委会决策参考。
- **trigger**: 当用户提及"IC Memo"、"投资委员会备忘录"、"IC Memorandum"、"投资备忘录"、"investment committee memo"时触发。

---

## 触发条件

- 用户输入包含 IC Memo / 投资委员会备忘录 / IC Memorandum / 投资建议书
- 尽调完成度 ≥ 80%，准备提交投委会审批
- 投资项目需要正式上会

---

## 执行步骤

### Step 1 · 收集与整理 IC 材料（web + terminal）

1. 汇总项目来源与背景（deal sourcing story）。
2. 整理初筛评分卡结论。
3. 汇总尽调各模块核心发现（业务/财务/法律/运营）。
4. 确认投资亮点与主要风险点。

### Step 2 · 投资机会概览（Investment Opportunity Overview）

1. **公司基本信息**：
   - 公司名称、总部所在、成立时间
   - 所处行业与赛道定位
   - 核心产品/服务与客户价值主张
2. **投资亮点（Investment Highlights）**：
   - 市场机会（TAM/增速）
   - 差异化壁垒
   - 团队实力
   - 财务表现（营收/增速/利润率）
   - 估值吸引力

### Step 3 · 投资逻辑（Investment Thesis）

1. **为什么是现在（Why Now）**：
   - 市场窗口
   - 催化剂事件
2. **为什么是这个标的（Why This Company）**：
   - 差异化竞争优势
   - 团队执行能力
   - 可规模化潜力
3. **为什么是我们（Why Us / Value Add）**：
   - 基金行业资源
   - 投后赋能计划

### Step 4 · 财务模型与估值（Financial Model & Valuation）

1. **预测模型假设**：
   - 收入假设（量价拆解、CAGR）
   - 利润率假设（逐步收敛至行业均值）
   - CapEx / D&A 假设
2. **估值方法**（多方法交叉验证）：
   - DCF（敏感性分析：WACC × Terminal Growth）
   - LBO（以目标回报率为输入反推价格）
   - Comps（EV/Revenue、EV/EBITDA、P/S）
3. 输出估值区间与中位数。
4. 使用 `terminal` 执行 Python 脚本生成财务模型摘要和估值表。

### Step 5 · 投资条款（Deal Terms）

1. 投资金额、持股比例、估值。
2. 投资轮次（Primary / Secondary）。
3. 治理权利（Board seat、Veto rights）。
4. 退出路径预期（Exit routes & timeline）。

### Step 6 · 风险分析（Risk Analysis）

1. **已知风险**：
   - 市场风险、竞争风险、技术风险、监管风险
   - 尽调中发现的关键问题及缓解措施
2. **尾部风险**：
   - 下行情景（Downside Case）敏感性
   - 最坏情况下的损失估算

### Step 7 · 投资建议与决策（Recommendation）

1. 明确投资建议（Approve / Reject / Defer）。
2. 关键条款优先级（Must-have vs. Nice-to-have）。
3. 下一步行动（后续跟进、条款谈判、监管审批）。

### Step 8 · 生成 IC Memo 文档

调用 `terminal` 执行 Python 脚本生成结构化 Markdown 文档，可导出为 PDF。

---

## 输出格式

- 输出完整 IC Memo Markdown 文档（结构化 sections）
- 如需 PDF，调用 `terminal` 执行脚本转换
- 标注所有假设前提和数据来源
- IC Memo 必须包含：执行摘要、投资逻辑、估值、风险、投资建议

---

## 常见陷阱（pitfalls）

1. **过度乐观**：投资亮点堆砌，缺乏对风险的诚实披露。
2. **估值区间过窄**：未充分考虑假设不确定性，估值点估计而非区间。
3. **投资逻辑不清晰**：未能清晰回答"为什么投"和"为什么现在"。
4. **忽略基金策略匹配**：好项目不一定符合本基金的投资策略和规模。
5. **格式不专业**：IC Memo 结构混乱或缺少关键 sections，影响投委会决策效率。

---

## 验证方法（verification）

- [ ] IC Memo 结构完整（执行摘要 + 各必含 sections）
- [ ] 估值方法 ≥ 2 种（DCF / LBO / Comps）
- [ ] 估值区间合理性（与市场 Comps 一致）
- [ ] 风险披露完整（已知风险 + 尾部风险）
- [ ] 投资建议与数据逻辑一致
- [ ] 无内幕信息（所有数据为公开或已授权）
- [ ] 人工复核签字记录
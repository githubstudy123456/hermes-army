# skill: financial-analysis · lbo-model

> 杠杆收购模型 · LBO

## 基本信息

- **name**: lbo-model
- **description**: 搭建 LBO 模型，输入交易结构（收购价、杠杆倍数）、债务条款（利率、摊销计划），输出 IRR、MOIC、DPI 等回报指标，支持敏感性分析。
- **trigger**: 当用户提及"LBO"、"杠杆收购"、"私募股权回报"、"IRR"、"MOIC"时触发。

---

## 触发条件

- 用户输入包含 LBO / 杠杆收购 / 私募回报 / IRR / MOIC / leveraged buyout
- 分析师请求搭建或审查 LBO 模型

---

## 执行步骤

### Step 1 · 确定交易结构（web + terminal）

1. 收集交易基本信息：
   - 收购价格（Purchase Price / Enterprise Value）
   - 股权投入（Equity Contribution）
   - 债务结构：Senior Secured / Term Loan / High Yield Bond，比例和金额
   - 杠杆倍数（Net Debt/EBITDA，通常 4x–7x）
2. 从公开来源获取债务利率、摊销期限、Mandatory Prepayments 条款。

### Step 2 · 搭建利润表与现金流表

1. 基于目标公司历史财务数据（web 抓取），预测 5–7 年 P&L：
   - 收入增速假设
   - EBITDA Margin 假设（逐步改善或稳定）
   - D&A、利息支出、税率
2. 构建现金流表：
   ```
   EBITDA
   - CapEx
   - ΔNWC
   - Interest Paid
   - Taxes Paid
   = Unlevered FCF
   - Mandatory Debt Repayment
   = Free Cash Flow to Equity (debt paydown后)
   ```

### Step 3 · 搭建债务还款计划

1. 基于不同债务层级（Senior → Junior）确定还款优先级。
2. 使用 Cash Sweep 模型（超额现金优先偿还高等级债务）。
3. 记录每期末：未偿本金余额、利息支出、当期还款额。

### Step 4 · 计算回报指标

| 指标 | 公式 |
|---|---|
| IRR | 使 NPV(FCF to Equity) = 0 的折现率 |
| MOIC | 期末 Equity Value / 期初 Equity Contribution |
| DPI | 已分配收益（Distributions）/ 投入本金 |
| TVPI | DPI + 未实现收益 / 投入本金 |
| Payback Period | 累计正现金流回收所需年数 |

### Step 5 · 退出情景分析

1. 设定退出年份（通常第 5 或 7 年）。
2. 退出估值方法：
   - EV/EBITDA 退出倍数（行业均值）
   - 或 DCF 隐含价值
3. 输出不同退出倍数下的 IRR / MOIC 表。

### Step 6 · 敏感性分析

输出 2D 敏感性表（退出倍数 × EBITDA 增速 vs. IRR）。

---

## 输出格式

- 优先输出 Markdown 表格（交易结构摘要 + 回报指标）
- 如需 Excel，调用 `terminal` 执行 Python 脚本（openpyxl）生成 .xlsx，含债务计划、现金流表、回报计算表
- 标注"仅供参考，不构成投资建议"

---

## 常见陷阱（pitfalls）

1. **杠杆假设激进**：使用过高 Net Debt/EBITDA 倍数（如 > 8x），忽视行业周期性。
2. **还款计划不现实**：假设债务按最大额度偿还，但实际受限于财务约束条款（Covenant）。
3. **IRR 计算错误**：混淆 FCFF 和 FCFE，或使用简单算术平均而非真实现金流时间加权。
4. **退出倍数过于乐观**：参照牛市顶峰倍数，忽略行业均值回归。
5. **忽略费用和税**：未计入 OID、Tail、 Arrangement Fee 或 Prepayment Penalty。

---

## 验证方法（verification）

- [ ] Purchase Price 勾稽 EV = Equity + Net Debt
- [ ] 期末债务余额 + 已偿金额 = 期初债务总额（Debt Schedule 平衡）
- [ ] IRR ≥ 目标回报率（Hurdle Rate），否则标注红色预警
- [ ] EBITDA 预测期初值与历史数据一致
- [ ] 敏感性分析覆盖合理倍数范围（6x–12x EV/EBITDA）
- [ ] 人工复核签字记录
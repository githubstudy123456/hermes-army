# skill: financial-analysis · dcf-model

> 现金流折现模型 · DCF

## 基本信息

- **name**: dcf-model
- **description**: 基于公司历史财务数据，搭建 DCF 模型（FCFF 或 FCFE），输入 WACC、Terminal Growth Rate、永续增长率假设，输出 Equity Value 与每股价值区间。
- **trigger**: 当用户提及"DCF"、"现金流折现"、"内在价值"、"估值模型"、"discounted cash flow"时触发。

---

## 触发条件

- 用户输入包含 DCF / 现金流折现 / 内在价值 / discounted cash flow / equity valuation
- 分析师请求搭建或审查 DCF 模型

---

## 执行步骤

### Step 1 · 收集历史财务数据（web）

1. 通过公开来源获取过去 5 年三张表核心数据：
   - 收入（Revenue）及增速
   - EBITDA、EBIT
   - 折旧摊销（D&A）、资本支出（CapEx）、净营运资本（NWC）变动
   - 税率、利息支出
   - 总股本、净债务（Net Debt）
2. 确认数据口径（GAAP vs. Non-GAAP），标注假设。

### Step 2 · 预测未来 5–10 年现金流

1. **收入假设**：基于行业增速 + 公司市场份额 + 产品管线给定收入 CAGR 假设。
2. **利润率假设**：EBITDA Margin 假设（逐步向可比公司均值收敛）。
3. 计算 FCFF：
   ```
   EBIT × (1 - Tax Rate)
   + D&A
   - ΔNWC
   - CapEx
   = FCFF
   ```
4. 若搭建 FCFE，还需减去净利息支出并加上净借款变动。

### Step 3 · 确定折现参数

| 参数 | 取值参考 |
|---|---|
| WACC | 同行业公司 Unlevered Beta → Levered Beta → Ke + Kd(1-T)×D/A |
| Terminal Growth Rate | 长期 GDP 增速或行业增速（通常 2%–3%） |
| 折现年数 | 5 或 10 年（显性预测期）+ 永续价值 |

### Step  Dcf-model · Terminal Value

1. Gordon Growth Model：
   ```
   TV = FCFF_n × (1 + g) / (WACC - g)
   ```
2. 也可使用 EV/EBITDA 退出倍数作为交叉验证。

### Step 5 · 计算 Equity Value

1. 折现所有现金流至现值（NPV）。
2. Equity Value = PV of FCFF + PV of Terminal Value - Net Debt
3. 每股价值 = Equity Value / 稀释后总股本

### Step 6 · 敏感性分析

输出 2D 敏感性表（WACC × Terminal Growth Rate vs. 每股价值）。

---

## 输出格式

- 优先输出 Markdown 表格（关键假设 + 结果摘要）
- 如需 Excel，调用 `terminal` 执行 Python 脚本（openpyxl）生成 .xlsx，含三张表钩稽关系
- 标注所有假设前提

---

## 常见陷阱（pitfalls）

1. **WACC 假设不合理**：使用行业均值但忽略公司特定杠杆/风险溢价。
2. **Terminal Growth Rate 过高**：超过永续增速上限（通常 ≤ WACC - 2%），导致 TV 虚高。
3. **NWC 假设粗糙**：假设 NWC 占收入比例恒定，但实际存在季节性和结构性变化。
4. **忽略净债务时点**：用期末净债务而非平均净债务折现，导致误差。
5. **未做稀释股数调整**：摊薄股份数应使用 Treasury Stock Method。

---

## 验证方法（verification）

- [ ] 历史数据与财报一致（可交叉验证）
- [ ] FCFF = EBIT×(1-T) + D&A - ΔNWC - CapEx 公式勾稽平衡
- [ ] WACC 处于行业合理区间（8%–15%）
- [ ] Terminal Value ≤ 总 PV 的 60%（否则模型过度依赖 TV）
- [ ] 敏感性分析覆盖关键假设范围
- [ ] 人工复核签字记录
# skill: financial-analysis · comps-analysis

> 三张表横向对比 · 可比公司分析

## 基本信息

- **name**: comps-analysis
- **description**: 选取可比公司，提取并横向对比收入/EBITDA/净利润三张表核心指标，计算 EV/EBITDA、EV/Revenue、P/E 等估值倍数，输出 Comps Table。
- **trigger**: 当用户提及"comps"、"可比公司"、"估值对比"、"三张表对比"时触发。

---

## 触发条件

- 用户输入包含 comps / 可比公司 / 估值倍数 / comparables
- 分析师请求横向对比同业公司财务数据

---

## 执行步骤

### Step 1 · 确定目标公司与行业

1. 明确目标公司（target）及所在行业（GICS 分类）。
2. 确认可比公司池（comps universe）：同一行业、同类产品、相似商业模式的上市公司。
3. 列出 5–8 家可比公司候选。

### Step 2 · 抓取财务数据（web）

1. 使用 `web` 工具从公开来源抓取：
   - 资本市场数据（Capital IQ / Bloomberg / Yahoo Finance）
   - 券商研报、年度财报、IPO 招股书
2. 提取字段（TTM 或最近财年）：
   - Revenue, EBITDA, EBIT, Net Income, TEV, Equity Value
   - 收入增速 YoY, EBITDA Margin, Net Margin
3. 如数据存在口径差异，标注假设前提（如 TTM vs. FY1 vs. LTM）。

### Step 3 · 计算估值倍数

对每家可比公司计算以下倍数（建议用 TTM 或 NTM）：

| 倍数 | 公式 |
|---|---|
| EV/EBITDA | Enterprise Value ÷ EBITDA |
| EV/Revenue | Enterprise Value ÷ Revenue |
| EV/EBIT | Enterprise Value ÷ EBIT |
| P/E | Price per Share × Shares Out ÷ Net Income |
| P/B | Price per Share × Shares Out ÷ Book Value |
| EV/FCF | Enterprise Value ÷ FCF |

> 使用加权平均（median）或均值作为中心趋势指标，标注高/低异常值。

### Step 4 · 输出 Comps Table

生成结构化表格，包含：

```
| Ticker | Company | Market Cap | EV | Revenue (TTM) | EBITDA (TTM) | EV/EBITDA | EV/Revenue | P/E |
|--------|---------|------------|----|---------------|--------------|------------|------------|-----|
| AAPL   | Apple   | xxx        | xxx| xxx           | xxx          | xx.xx      | xx.xx      | xx.x|
```

### Step 5 · 分析与输出

1. 解读各倍数分布（25th/50th/75th percentile）。
2. 结合目标公司质量/增长性，给出隐含估值区间。
3. 注明数据来源、日期、假设前提。
4. 标注"仅供参考，不构成投资建议"。

---

## 输出格式

- 优先以 Markdown table 输出
- 如需 Excel，调用 `terminal` 执行 Python 脚本（openpyxl/xlsxwriter）写入 .xlsx
- 关键数字保留 2 位小数

---

## 常见陷阱（pitfalls）

1. **口径不一致**：TTM vs. LTM vs. FY 数据混用，导致跨公司对比失真。
2. **异常值干扰**：选用高杠杆公司（EV 被债务扭曲）拉偏中位数；需剔除极端值。
3. **过时数据**：使用季度数据未 annualize，或引用超过 3 个月未更新的公开数据。
4. **忽略稀释效应**：未考虑期权/可转债稀释，导致 Equity Value 低估。
5. **缺失权重调整**：跨行业混用中位数而非加权均值，未考虑规模差异。

---

## 验证方法（verification）

- [ ] 可比公司池覆盖目标公司所在 GICS 行业至少 4 家
- [ ] 所有倍数计算使用同一时间口径（TTM 或 FY NTM）
- [ ] EV 勾稽 Market Cap + Net Debt 一致
- [ ] 输出表格包含 Source 和 Date 标注
- [ ] 关键结论有人工复核记录
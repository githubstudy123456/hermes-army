---
name: financial-analysis
description: 财务分析模型工作台 — 覆盖可比公司分析（Comps）、现金流折现模型（DCF）、Excel 财务模型审计三大模块。
version: 0.1
owner: hermes-finance
tags: [financial-analysis, comps, dcf, lbo, valuation, model-audit, investment-banking]
created: 2026-06-15
trigger: 当主人要求"comps"、"可比公司"、"DCF"、"现金流折现"、"财务模型审计"时自动激活
---

# Financial Analysis · 财务分析模型工作台

## 核心定位

统一的财务分析模型工作台，覆盖可比公司分析（Comps）、现金流折现模型（DCF）、Excel 财务模型审计三大模块，支持投行/PE 分析场景。

---

## 模块菜单

| 模块 | Skill 章节 | 适用触发词 |
|------|-----------|-----------|
| 可比公司分析 | [§可比公司分析](#可比公司分析) | `comps`、`可比公司`、`估值对比`、`三张表对比` |
| DCF 模型 | [§DCF 模型](#dcf-模型) | `DCF`、`现金流折现`、`内在价值`、`discounted cash flow` |
| Excel 财务模型审计 | [§Excel 财务模型审计](#excel-财务模型审计) | `财务模型审计`、`excel审计`、`模型质量检查` |

---

## 可比公司分析

### 触发条件
- 用户输入包含 comps / 可比公司 / 估值倍数 / comparables
- 分析师请求横向对比同业公司财务数据

### 执行步骤
**Step 1 · 确定目标公司与行业**
1. 明确目标公司（target）及所在行业（GICS 分类）
2. 确认可比公司池（comps universe）：同一行业、同类产品、相似商业模式的上市公司
3. 列出 5–8 家可比公司候选

**Step 2 · 抓取财务数据（web）**
- 使用 `web` 工具从公开来源抓取：
  - 资本市场数据（Capital IQ / Bloomberg / Yahoo Finance）
  - 券商研报、年度财报、IPO 招股书
- 提取字段（TTM 或最近财年）：
  - Revenue, EBITDA, EBIT, Net Income, TEV, Equity Value
  - 收入增速 YoY, EBITDA Margin, Net Margin
- 如数据存在口径差异，标注假设前提（如 TTM vs. FY1 vs. LTM）

**Step 3 · 计算估值倍数**
| 倍数 | 公式 |
|---|---|
| EV/EBITDA | Enterprise Value ÷ EBITDA |
| EV/Revenue | Enterprise Value ÷ Revenue |
| EV/EBIT | Enterprise Value ÷ EBIT |
| P/E | Price per Share × Shares Out ÷ Net Income |
| P/B | Price per Share × Shares Out ÷ Book Value |
| EV/FCF | Enterprise Value ÷ FCF |

**Step 4 · 输出 Comps Table**
```
| Ticker | Company | Market Cap | EV | Revenue (TTM) | EBITDA (TTM) | EV/EBITDA | EV/Revenue | P/E |
|--------|---------|------------|----|---------------|--------------|------------|------------|-----|
```

**Step 5 · 分析与输出**
1. 解读各倍数分布（25th/50th/75th percentile）
2. 结合目标公司质量/增长性，给出隐含估值区间
3. 注明数据来源、日期、假设前提
4. 标注"仅供参考，不构成投资建议"

### Pitfalls
1. 口径不一致：TTM vs. LTM vs. FY 数据混用
2. 异常值干扰：选用高杠杆公司拉偏中位数，需剔除极端值
3. 过时数据：使用季度数据未 annualize
4. 忽略稀释效应：未考虑期权/可转债稀释

### Verification
- [ ] 可比公司池覆盖目标公司所在 GICS 行业至少 4 家
- [ ] 所有倍数计算使用同一时间口径
- [ ] EV 勾稽 Market Cap + Net Debt 一致
- [ ] 输出表格包含 Source 和 Date 标注

---

## DCF 模型

### 触发条件
- 用户输入包含 DCF / 现金流折现 / 内在价值 / discounted cash flow / equity valuation
- 分析师请求搭建或审查 DCF 模型

### 执行步骤
**Step 1 · 收集历史财务数据（web）**
- 通过公开来源获取过去 5 年三张表核心数据
- 确认数据口径（GAAP vs. Non-GAAP），标注假设

**Step 2 · 预测未来 5–10 年现金流**
- 收入假设：基于行业增速 + 公司市场份额 + 产品管线给定收入 CAGR 假设
- 利润率假设：EBITDA Margin 假设（逐步向可比公司均值收敛）
- 计算 FCFF：
  ```
  EBIT × (1 - Tax Rate)
  + D&A
  - ΔNWC
  - CapEx
  = FCFF
  ```

**Step 3 · 确定折现参数**
| 参数 | 取值参考 |
|---|---|
| WACC | 同行业公司 Unlevered Beta → Levered Beta → Ke + Kd(1-T)×D/A |
| Terminal Growth Rate | 长期 GDP 增速或行业增速（通常 2%–3%） |
| 折现年数 | 5 或 10 年（显性预测期）+ 永续价值 |

**Step 4 · Terminal Value**
- Gordon Growth Model：
  ```
  TV = FCFF_n × (1 + g) / (WACC - g)
  ```
- 也可使用 EV/EBITDA 退出倍数作为交叉验证

**Step 5 · 计算 Equity Value**
1. 折现所有现金流至现值（NPV）
2. Equity Value = PV of FCFF + PV of Terminal Value - Net Debt
3. 每股价值 = Equity Value / 稀释后总股本

**Step 6 · 敏感性分析**
- 输出 2D 敏感性表（WACC × Terminal Growth Rate vs. 每股价值）

### Pitfalls
1. WACC 假设不合理：使用行业均值但忽略公司特定杠杆/风险溢价
2. Terminal Growth Rate 过高：超过永续增速上限，导致 TV 虚高
3. NWC 假设粗糙：假设 NWC 占收入比例恒定
4. 忽略净债务时点：用期末净债务而非平均净债务折现
5. 未做稀释股数调整：摊薄股份数应使用 Treasury Stock Method

### Verification
- [ ] 历史数据与财报一致
- [ ] FCFF = EBIT×(1-T) + D&A - ΔNWC - CapEx 公式勾稽平衡
- [ ] WACC 处于行业合理区间（8%–15%）
- [ ] Terminal Value ≤ 总 PV 的 60%
- [ ] 敏感性分析覆盖关键假设范围

---

## Excel 财务模型审计

### 触发条件
- 用户要求审计 Excel 财务模型的质量和逻辑正确性
- 触发词：`财务模型审计`、`excel审计`、`模型质量检查`

### 执行步骤
**Step 1 · 接收模型文件**
- 通过 `file` 读取 Excel 文件
- 通过 `terminal` 执行 openpyxl 脚本解析结构

**Step 2 · 结构扫描**
- 检查 Sheet 命名和顺序（Assumptions / Income Statement / Balance Sheet / Cash Flow / DCF / Sensitivity）
- 识别关键假设参数位置
- 识别公式驱动单元格 vs 硬编码数值

**Step 3 · 三张表钩稽验证**
- PL → BS → CF 联动关系验证
- Balance Sheet 配平检查（总资产 = 总负债 + 股东权益）
- 关键比率（毛利率/EBITDA Margin/负债率）趋势合理性

**Step 4 · 公式审计**
- 检查跨 sheet 引用是否正确
- 检查循环引用
- 检查是否有 hard-coded 常数（应引用 Assumptions sheet）

**Step 5 · 输出审计报告**
```
# Excel 财务模型审计报告

模型名称：{filename}
审计日期：{date}

【结构完整性】
- Sheet 数量：X（标准：6-8）
- 缺失 Sheet：[列出缺失的标准 Sheet]

【三张表钩稽】
- Balance Sheet 配平：✅ / ❌
- PL→BS→CF 联动：✅ / ❌

【公式质量】
- 硬编码假设数量：X
- 跨 Sheet 引用正确率：X%
- 循环引用：✅ 存在 / ❌ 无

【问题列表】
| 位置 | 问题类型 | 描述 | 建议 |
|------|---------|------|------|

【结论】
✅ 通过 / ❌ 需修改后重新提交
```

### Pitfalls
1. 只检查语法不检查逻辑
2. 忽略跨 Sheet 引用错误
3. 未检查 Balance Sheet 配平
4. 硬编码假设未标记

### Verification
- [ ] Balance Sheet 配平
- [ ] 三张表联动关系正确
- [ ] 无循环引用
- [ ] 假设参数引用 Assumptions sheet（无硬编码）
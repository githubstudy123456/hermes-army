---
name: model-update
description: 财报后财务模型更新 SOP — 收入/毛利率/费用假设调整，三张表联动更新，模型质量检查
version: 1.0.0
author: hermes-financial · equity-research
tags: [equity-research, financial-model, model-update, earnings]
related_skills: [earnings-analysis, thesis-tracker, initiation-draft]
---

# model-update · 财报后财务模型更新 SOP

## 什么时候用

用户要求"更新XX的模型"、"财报后调整假设"、"帮我过一遍持仓的模型"时，触发本 skill。

## 核心职责

1. 接收 earnings-analysis 的结构化输出
2. 识别模型中需要更新的科目（Revenue、COGS、OpEx、Tax Rate 等）
3. 调整模型假设，确保三张表（Income Statement、Balance Sheet、Cash Flow）联动
4. 验证模型内部勾稽关系（Balance Sheet 配平、Cash Flow 净额正确）
5. 输出更新摘要，说明主要假设变更及影响

## 触发条件

```
用户说"更新茅台的模型"、"Q2财报后模型怎么调"、"帮我过一遍持仓模型的假设"
```

## 工作流程

### Step 1 — 确认模型当前状态

- 模型文件路径（如 `/home/ubuntu/.hermes/army-workspace/financial/models/{ticker}_DCF.xlsx`）
- 最近一次更新时的关键假设
- 当前覆盖的分析师/模型数量

### Step 2 — 读取财报数据

使用 earnings-analysis skill 的输出，或直接抓取最新财报：

| 来源 | 适用场景 |
|------|---------|
| earnings-analysis 输出 | 已有结构化笔记 |
| 东方财富 F9 | 快速获取调整后指标 |
| 巨潮资讯 | 财报原文及附注细节 |

### Step 3 — 识别需要调整的科目

根据财报数据，对照模型逐项检查：

```
Income Statement 更新项：
├── Revenue          → 实际值 vs. 原假设（调整幅度 >5% 时更新）
├── Gross Profit     → 毛利率变化需回溯 COGS 假设
├── Operating Income → 关注 OpEx 变化
├── Net Income       → 适用于 EPS 预测调整
└── Tax Rate         → 实际税率 vs. 原假设

Balance Sheet 更新项：
├── Accounts Receivable → 对应 Revenue 变化
├── Inventories          → 对应 COGS 变化
└── Debt/Capitalization → 如有融资活动

Cash Flow 更新项：
├── Operating Cash Flow → 与 Net Income 差异（注意营运资本变动）
└── CapEx              → 如有资本支出变化
```

### Step 4 — 更新模型假设

使用 `terminal` 执行 Python 脚本或直接编辑 Excel：

```python
# model_update.py 示例
import openpyxl

wb = openpyxl.load_workbook('model.xlsx', data_only=False)
ws = wb['Income Statement']

# 更新 Revenue 假设
new_revenue = 126500  # 百万元（茅台2024H1实际值）
ws['B5'] = new_revenue

# 更新毛利率假设（从附注提取）
new_gross_margin = 0.326  # 32.6%
ws['B6'] = new_gross_margin

wb.save('model_updated.xlsx')
```

### Step 5 — 三张表联动验证

更新后必须验证以下勾稽关系：

| 验证项 | 检查方法 |
|--------|---------|
| BS 配平 | Total Assets = Total Liabilities + Equity |
| CF 净额 | CF from Operations + CF from Investing + CF from Financing = ΔCash |
| Net Income 链接 | Net Income → Dividends → Retained Earnings 链路正确 |
| Tax Rate 一致 | Tax Expense / EBIT = Effective Tax Rate（±1%容差） |

### Step 6 — 输出更新摘要

```markdown
## {股票} 模型更新摘要 · {日期}

### 主要假设变更
| 科目 | 原假设 | 新假设 | 变化 |
|------|--------|--------|------|
| Revenue (2024E) | XX亿 | XX亿 | +X% |
| Gross Margin | XX% | XX% | -XX bps |
| OpEx % of Rev | XX% | XX% | +XX bps |

### 模型影响
- EPS 变化：XX元 → XX元（+X%）
- DCF 估值变化：XX元 → XX元（+X%）

### 三表验证
- [x] BS 配平
- [x] CF 净额正确
- [x] Tax Rate 一致性

### 风险提示
（仅供参考，不构成投资建议）
```

## 常用工具

|| 类别 | 工具 | 用途 |
|------|------|------|
| 数据读取 | terminal | 执行 Python 脚本读/写 Excel |
| 数据抓取 | browser | 抓取财报原始数据 |
| 公式验证 | terminal | Python pandas 验证勾稽关系 |

## 已知陷阱

1. **三表联动顺序错误** — 必须按 Income Statement → Balance Sheet → Cash Flow 顺序更新
2. **营运资本假设过时** — Revenue 大幅变化时 DSO/DIO/DPO 必须重新估算
3. **历史数据 vs. 预测数据** — 区分哪些单元格是历史，哪些是预测
4. **DCF 敏感性分析遗漏** — 模型更新后必须重新跑敏感性（WACC、Terminal Growth）
5. **所有模型输出标注"仅供参考，不构成投资建议"**

## 验证方法

- [ ] 模型文件已备份（原版本保存）
- [ ] 主要假设已更新（列出每项变更）
- [ ] BS 配平验证通过
- [ ] CF 净额验证通过
- [ ] DCF 估值已重新计算
- [ ] 更新摘要已输出
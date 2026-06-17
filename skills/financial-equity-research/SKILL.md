---
name: financial-equity-research
description: 股票基本面研究工作台 — 覆盖财报提取与分析、模型更新、首发覆盖报告、投资主题追踪四大模块，支持 A股/港股/美股基本面研究全流程。
version: 0.1
owner: hermes-financial
tags: [equity-research, earnings, financial-model, initiation, thesis-tracker, stock-analysis, a-share]
created: 2026-06-15
trigger: 当主人要求"分析财报"、"更新模型"、"覆盖报告"、"投资主题追踪"、"持仓诊断"时自动激活
---

# Financial Equity Research · 股票基本面研究工作台

## 核心定位

统一的股票基本面研究工作台，覆盖财报提取与分析、模型更新、首发覆盖报告、投资主题追踪四大模块，支持 A股/港股/美股基本面研究全流程。

**免责声明**：所有输出必须标注"仅供参考，不构成投资建议"。

---

## 模块菜单

| 模块 | Skill 章节 | 适用触发词 |
|------|-----------|-----------|
| 财报提取与分析 | [§财报提取与分析](#财报提取与分析) | `分析XX的Q2财报`、`提取腾讯2024年报`、`财报季来了` |
| 财务模型更新 | [§财务模型更新](#财务模型更新) | `更新茅台的模型`、`Q2财报后模型怎么调`、`持仓模型假设` |
| 首发覆盖报告 | [§首发覆盖报告](#首发覆盖报告) | `写茅台的覆盖报告`、`首发覆盖`、`投研报告` |
| 投资主题追踪 | [§投资主题追踪](#投资主题追踪) | `追踪茅台的投资逻辑`、`主题兑现`、`持仓 thesis` |

---

## 财报提取与分析

### 触发条件
```
用户说"分析XX的Q2财报"、"提取腾讯2024年报关键数据"、"财报季来了帮我过一遍持仓"
```

### 执行步骤
**Step 1 · 确定数据源**
| 数据需求 | 首选来源 |
|---------|---------|
| A股财报原文 | 巨潮资讯 (cninfo.com.cn) |
| 港股/美股财报 | 东方财富 (eastmoney.com) |
| 一致预期/分析师预期 | 东方财富 F9 页面 |
| 新闻/业绩预告 | 巨潮资讯新闻公告 |

**Step 2 · 抓取财报**
使用 `browser` 工具访问：
```
东方财富：https://em.eastmoney.com/qixh/list?code=SH600519（茅台示例）
巨潮资讯：https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&plate=sh&stockCode=600519
```
执行 `browser_console` JS 提取关键数据。

**Step 3 · 提取关键指标表格**
```javascript
const rows = document.querySelectorAll('table tbody tr');
const metrics = [];
rows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length >= 4) {
    metrics.push({
      item: cells[0]?.textContent?.trim(),
      current: cells[1]?.textContent?.trim(),
      priorYear: cells[2]?.textContent?.trim(),
      yoyChange: cells[3]?.textContent?.trim()
    });
  }
});
JSON.stringify(metrics);
```

**Step 4 · 对比一致预期**
从东方财富 F9 页面提取分析师一致预期数据：
```
https://em.eastmoney.com/qixh/estimate?code=SH600519
```

**Step 5 · 输出结构化笔记**
```markdown
## {股票名称} {年份}{Q1/Q2/Q3/Q4} 财报分析

### 核心指标
| 指标 | 实际值 | 一致预期 | 超出/低于 |
|------|--------|---------|---------|
| Revenue | XX亿 | XX亿 | +X% |
| EPS | XX元 | XX元 | +X% |
| EBITDA | XX亿 | XX亿 | +X% |

### 关键变化
- 收入增长驱动因素：
- 毛利率变化：
- 费用率变化：

### Guidance 解读
- 下季度指引：
- 全年指引：

### 风险提示
（仅供参考，不构成投资建议）
```

### 已知陷阱
1. A股财报季节性 — 季报(4/7/10月)、半年报(8月)、年报(次年4月)
2. 口径不一致 — 境内/境外准则下净利润可能不同
3. 预期数据滞后 — 分析师一致预期可能未及时更新
4. 非经常性损益 — 关注扣非净利润

### Verification
- [ ] 数据源URL已记录
- [ ] 关键指标已提取（Revenue、EPS、Net Profit至少三项）
- [ ] 输出格式符合结构化笔记模板
- [ ] 已标注免责声明

---

## 财务模型更新

### 触发条件
```
用户说"更新茅台的模型"、"Q2财报后模型怎么调"、"帮我过一遍持仓模型的假设"
```

### 执行步骤
**Step 1 · 确认模型当前状态**
- 模型文件路径（如 `/home/ubuntu/.hermes/army-workspace/financial/models/{ticker}_DCF.xlsx`）
- 最近一次更新时的关键假设

**Step 2 · 识别需要调整的科目**
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

Cash Flow 更新项：
└── Operating Cash Flow → 与 Net Income 差异
```

**Step 3 · 三张表联动验证**
| 验证项 | 检查方法 |
|--------|---------|
| BS 配平 | Total Assets = Total Liabilities + Equity |
| CF 净额 | CF from Operations + CF from Investing + CF from Financing = ΔCash |
| Tax Rate 一致性 | Tax Expense / EBIT = Effective Tax Rate（±1%容差） |

**Step 4 · 输出更新摘要**
```markdown
## {股票} 模型更新摘要 · {日期}

### 主要假设变更
| 科目 | 原假设 | 新假设 | 变化 |
|------|--------|--------|------|
| Revenue (2024E) | XX亿 | XX亿 | +X% |

### 模型影响
- EPS 变化：XX元 → XX元（+X%）
- DCF 估值变化：XX元 → XX元（+X%）

### 三表验证
- [x] BS 配平
- [x] CF 净额正确
```

### 已知陷阱
1. 三表联动顺序错误 — 必须按 Income Statement → Balance Sheet → Cash Flow 顺序更新
2. 营运资本假设过时 — Revenue 大幅变化时 DSO/DIO/DPO 必须重新估算
3. DCF 敏感性分析遗漏 — 模型更新后必须重新跑敏感性

### Verification
- [ ] 模型文件已备份
- [ ] BS 配平验证通过
- [ ] DCF 估值已重新计算

---

## 首发覆盖报告

### 触发条件
```
用户说"写茅台的覆盖报告"、"帮我起草XX的首发覆盖"、"新开仓了XX，需要覆盖"
```

### 执行步骤
**Step 1 · 信息收集**
使用 `browser` 和 `web` 收集公司概况、行业数据、财务历史、分析师预期、近期新闻、竞争对手对比。

**Step 2 · 报告结构生成**
```markdown
# {股票名称}（{代码}）首发覆盖报告

**报告日期：** {日期}
**评级：** 增持/中性/减持
**目标价：** XX元（较当前价上涨空间 XX%）
**当前价：** XX元

## 投资亮点
（3-5个核心亮点）

## 核心投资逻辑
### 1. 业务模式与市场定位
### 2. 竞争优势/催化剂
### 3. 财务预测
| 指标 | 2024E | 2025E | 2026E |
|------|-------|-------|-------|
### 4. 估值分析
- DCF 估值：XX元
- EV/EBITDA：XX倍（行业平均 XX倍）

## 风险因素
1. 风险1
2. 风险2

## 附录：关键数据来源
| 数据 | 来源 | 链接 |
|------|------|------|

---
**免责声明：** 本报告仅供参考，不构成投资建议。
```

### 已知陷阱
1. 数据过时 — 报告必须注明数据日期
2. 估值方法不当 — 不同行业适用不同估值方法
3. 风险因素过于泛化 — 风险要与公司业务直接相关

### Verification
- [ ] 报告结构完整（六段式标准格式）
- [ ] 关键数据有来源链接
- [ ] 已包含免责声明

---

## 投资主题追踪

### 触发条件
```
用户说"追踪茅台的投资逻辑"、"帮我过一遍持仓 thesis"、"主题兑现得怎么样了"
```

### 执行步骤
**Step 1 · 建立 Thesis 档案**
```markdown
## {股票} 投资主题档案

### 核心 Thesis
（1-3句话概括投资逻辑）

### 关键假设
| 假设 | 预期 | 监控指标 | 阈值 |
|------|------|---------|------|
| 假设1 | XX | KPI1 | ±X% |

### 催化剂清单
| 催化剂 | 预期时间 | 状态 |
|--------|---------|------|
| 催化剂1 | X月 | 已兑现/进行中/待验证 |
```

**Step 2 · 定义监控指标**（每只股票 3-7 个）
| 股票类型 | 典型监控指标 |
|---------|------------|
| 消费（茅台） | 批条价格、动销数据、库存周期 |
| 科技（腾讯） | 游戏流水、广告收入、To B收入增速 |
| 银行（招行） | NIM、不良率、拨备覆盖率 |
| 新能源（宁德） | 装机量、产能利用率、原材料成本 |

**Step 3 · Thesis 状态判断**
| 状态 | 定义 | 行动 |
|------|------|------|
| **强化** | ≥3个关键指标朝有利方向 | 维持/加仓考虑 |
| **维持** | 关键指标基本符合预期 | 持续监控 |
| **弱化** | ≥3个关键指标朝不利方向 | 减仓考虑 |
| **待验证** | 催化剂尚未兑现 | 等待下一催化剂节点 |

**Step 4 · 输出追踪报告**
```markdown
## {股票} 主题追踪报告 · {日期}

### Thesis 状态：{强化/维持/弱化/待验证}

### 关键指标追踪
| 指标 | 上期 | 本期 | 变化 | 阈值 | 状态 |
|------|------|------|------|------|------|
| KPI1 | XX | XX | +X% | ±5% | ✅正常/⚠️偏离 |

### 催化剂进度
- [x] 催化剂1（已兑现）
- [ ] 催化剂2（进行中）

### 综合判断
（基于指标和催化剂的综合分析）
```

### 已知陷阱
1. 指标与 Thesis 错配 — 确保每个 KPI 直接支撑 Thesis
2. 阈值设置过宽/过严 — 5%-10% 是常见参考范围
3. 单一指标主导 — 避免被一个指标带偏

### Verification
- [ ] 每只持仓股票都有 Thesis 档案
- [ ] 最新指标数据已获取并记录日期
- [ ] 追踪报告已输出
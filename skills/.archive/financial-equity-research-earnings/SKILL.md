---
name: earnings-analysis
description: 财报关键数据提取与结构化 — 季报/年报关键指标提取、EPS/Revenue/EBITDA 对比、guidance 解读
version: 1.0.0
author: hermes-financial · equity-research
tags: [equity-research, earnings, financial-analysis, quarterly-report]
related_skills: [model-update, thesis-tracker, initiation-draft]
---

# earnings-analysis · 财报关键数据提取

## 什么时候用

用户要求分析某只股票的财报（季报/年报）、提取关键财务指标、对比市场预期、或解读 guidance 时，触发本 skill。

## 核心职责

1. 从东方财富（eastmoney）或巨潮资讯（cninfo）抓取财报原文
2. 提取关键指标：EPS、Revenue、EBITDA、Net Income、Operating Margin
3. 对比 Wall Street 一致预期（EPS/Revenue）
4. 解读管理层 guidance（下一季度/全年）
5. 输出结构化笔记（便于 model-update 和 thesis-tracker 复用）

## 触发条件

```
用户说"分析XX的Q2财报"、"提取腾讯2024年报关键数据"、"财报季来了帮我过一遍持仓"
```

## 工作流程

### Step 1 — 确定数据源

| 数据需求 | 首选来源 |
|---------|---------|
| A股财报原文 | 巨潮资讯 (cninfo.com.cn) |
| 港股/美股财报 | 东方财富 (eastmoney.com) |
| 一致预期/分析师预期 | 东方财富 F9 页面 |
| 新闻/业绩预告 | 巨潮资讯新闻公告 |

### Step 2 — 抓取财报

使用 `browser` 工具访问：

```
东方财富：https://em.eastmoney.com/qixh/list?code=SH600519（茅台示例）
巨潮资讯：https://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&plate=sh&stockCode=600519
```

执行 `browser_console` JS 提取关键数据：

```javascript
// 提取财报关键数据
const data = {
  reportDate: document.querySelector('.report-date')?.textContent,
  revenue: document.querySelector('[data-field="revenue"]')?.textContent,
  eps: document.querySelector('[data-field="eps"]')?.textContent,
  netProfit: document.querySelector('[data-field="netProfit"]')?.textContent,
  guidance: document.querySelector('.guidance-text')?.textContent
};
JSON.stringify(data);
```

### Step 3 — 提取关键指标表格

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

### Step 4 — 对比一致预期

从东方财富 F9 页面提取分析师一致预期数据：

```
https://em.eastmoney.com/qixh/estimate?code=SH600519
```

### Step 5 — 输出结构化笔记

输出格式：

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
- （仅供参考，不构成投资建议）
```

## 常用工具

|| 类别 | 工具 | 用途 |
|------|------|------|
| 数据获取 | browser | 东方财富/巨潮资讯抓取 |
| 数据提取 | browser_console JS | 提取财报表格数据 |
| 搜索 | web | 搜索财报新闻、分析师预期 |

## 已知陷阱

1. **A股财报季节性** — 季报(4/7/10月)、半年报(8月)、年报(次年4月)，数据源开放时间不同
2. **口径不一致** — 境内/境外准则下净利润可能不同，提取时注明准则类型
3. **预期数据滞后** — 分析师一致预期可能未及时更新，注明数据日期
4. **非经常性损益** — 关注扣非净利润，避免被一次性损益误导
5. **所有输出必须标注"仅供参考，不构成投资建议"**

## 验证方法

- [ ] 数据源URL已记录
- [ ] 关键指标已提取（Revenue、EPS、Net Profit至少三项）
- [ ] 提取数据与原始财报文字一致（交叉验证1-2项）
- [ ] 输出格式符合结构化笔记模板
- [ ] 已标注免责声明
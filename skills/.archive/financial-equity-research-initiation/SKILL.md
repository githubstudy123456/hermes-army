---
name: initiation-draft
description: 首发覆盖报告（Initiation Report）草稿 — 投资评级、目标价、核心逻辑、风险因素
version: 1.0.0
author: hermes-financial · equity-research
tags: [equity-research, initiation, coverage, report, equity-research]
related_skills: [earnings-analysis, model-update, thesis-tracker]
---

# initiation-draft · 首发覆盖报告草稿

## 什么时候用

用户要求"写一篇XX的首发覆盖"、"帮我起草一个覆盖报告"、"新开仓股票需要覆盖报告"时，触发本 skill。

## 核心职责

1. 基于公开信息撰写首发覆盖报告草稿
2. 包含投资评级、目标价、核心投资逻辑、风险因素
3. 涵盖行业概览、公司定位、竞争优势、财务预测、估值分析
4. 输出格式符合卖方研究报告标准（可作为 memo 初稿）
5. **所有报告必须标注"仅供参考，不构成投资建议"**

## 触发条件

```
用户说"写茅台的覆盖报告"、"帮我起草XX的首发覆盖"、"新开仓了XX，需要覆盖"
```

## 工作流程

### Step 1 — 信息收集

使用 `browser` 和 `web` 收集以下信息：

| 信息类别 | 来源 |
|---------|------|
| 公司基本情况 | 东方财富公司概况页 |
| 行业数据 | 东方财富行业板块数据 |
| 财务历史 | 巨潮资讯历年财报 |
| 分析师预期 | 东方财富 F9 一致预期 |
| 近期新闻 | 巨潮资讯新闻/公告 |
| 竞争对手对比 | 东方财富行业对比 |

### Step 2 — 提取公司核心数据

```javascript
// 提取公司概况
const companyProfile = {
  name: document.querySelector('.company-name')?.textContent,
  ticker: document.querySelector('.stock-code')?.textContent,
  industry: document.querySelector('.industry')?.textContent,
  marketCap: document.querySelector('.market-cap')?.textContent,
  pe: document.querySelector('.pe-ratio')?.textContent,
  dividendYield: document.querySelector('.dividend-yield')?.textContent
};
JSON.stringify(companyProfile);
```

### Step 3 — 撰写报告草稿

报告结构（标准卖方格式）：

```markdown
# {股票名称}（{代码}）首发覆盖报告

**报告日期：** {日期}
**评级：** 增持/中性/减持
**目标价：** XX元（较当前价上涨空间 XX%）
**当前价：** XX元

---

## 投资亮点

（3-5个核心亮点，一句话一条）

## 核心投资逻辑

### 1. 业务模式与市场定位
（公司做什么、市场规模、竞争格局）

### 2. 竞争优势/催化剂
（护城河、增长驱动因素）

### 3. 财务预测
| 指标 | 2024E | 2025E | 2026E |
|------|-------|-------|-------|
| Revenue (亿) | XX | XX | XX |
| EPS (元) | XX | XX | XX |
| YoY | XX% | XX% | XX% |

### 4. 估值分析
- DCF 估值：XX元
- EV/EBITDA：XX倍（行业平均 XX倍）
- PE：XX倍（行业平均 XX倍）
- 目标价依据：{估值方法}

## 风险因素

1. 风险1
2. 风险2
3. 风险3

## 附录：关键数据来源

| 数据 | 来源 | 链接 |
|------|------|------|
| 财报数据 | 巨潮资讯 | URL |
| 行业数据 | 东方财富 | URL |
| 一致预期 | 东方财富 | URL |

---

**免责声明：** 本报告仅供参考，不构成投资建议。投资者需自行承担投资风险。
```

### Step 4 — 估值计算（简要）

```python
# dcf_estimate.py 示例
# 如需计算目标价，执行简单 DCF 或相对估值

wacc = 0.10  # 10% WACC
terminal_growth = 0.03  # 3% 永续增长率
free_cash_flows = [12.5, 14.2, 16.1]  # 未来3年FCF（亿）

# Terminal Value
tv = free_cash_flows[-1] * (1 + terminal_growth) / (wacc - terminal_growth)

# DCF Sum
dcf_value = sum([fcf / (1 + wacc)**(i+1) for i, fcf in enumerate(free_cash_flows)])
dcf_value += tv / (1 + wacc)**3

print(f"DCF估值: {dcf_value:.1f}亿元")
```

### Step 5 — 输出最终草稿

确认草稿包含：
- [ ] 公司名称、代码、评级、目标价、当前价
- [ ] 3-5 个投资亮点
- [ ] 业务模式、市场定位、竞争优势
- [ ] 3 年财务预测
- [ ] 估值方法和目标价
- [ ] 主要风险因素
- [ ] 数据来源和链接
- [ ] 免责声明

## 常用工具

|| 类别 | 工具 | 用途 |
|------|------|------|
| 数据获取 | browser | 东方财富/巨潮资讯抓取公司信息 |
| 数据提取 | browser_console JS | 提取公司概况和行业数据 |
| 搜索 | web | 搜索行业研报、新闻 |
| 估值计算 | terminal | 执行 Python 脚本计算 DCF/相对估值 |

## 已知陷阱

1. **数据过时** — 报告必须注明数据日期，财务数据优先用最新季报/年报
2. **估值方法不当** — 不同行业适用不同估值方法（消费用 PE/DCF，科技用 PS，银行用 PB）
3. **风险因素过于泛化** — 风险要与公司业务直接相关，不是套话
4. **评级标准不清** — 明确评级定义（增持 = 跑赢基准 X%以上）
5. **所有报告必须标注"仅供参考，不构成投资建议"**

## 验证方法

- [ ] 报告结构完整（六段式标准格式）
- [ ] 关键数据有来源链接
- [ ] 估值方法与公司业务匹配
- [ ] 财务预测数字自洽（Revenue 增长与行业增速匹配）
- [ ] 风险因素具体化
- [ ] 已包含免责声明
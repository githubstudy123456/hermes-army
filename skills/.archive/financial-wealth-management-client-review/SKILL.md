---
name: client-review
description: 客户账户定期review — 持仓诊断、风险评估、表现归因、建议生成
version: 1.0.0
author: hermes-financial · wealth-management
tags: [wealth-management, client-review, portfolio-diagnostic, risk-assessment]
related_skills: [rebalancing, tax-loss-harvest, financial-plan]
---

# client-review · 客户账户定期review

## 什么时候用

用户要求"review客户账户"、"过一遍客户持仓"、"帮我看看这个客户账户表现如何"时，触发本 skill。

## 核心职责

1. 诊断客户账户持仓结构（资产类别、行业、地区分布）
2. 评估风险指标（波动率、最大回撤、夏普比率）
3. 表现归因（收益来源 vs 大盘基准）
4. 识别需要 rebalancing 或 tax-loss-harvest 的机会
5. 生成客户会议 briefing pack

## 触发条件

```
用户说"帮我review这个客户账户"、"过一遍王总的持仓"、"客户账户表现分析"
```

## 工作流程

### Step 1 — 获取账户数据

使用 `web` 工具从以下来源获取持仓数据：

| 数据需求 | 首选来源 |
|---------|---------|
| 持仓明细（股票/债券/基金） | 券商客户报告 PDF |
| 实时行情 | 东方财富/雪球 |
| 基准指数行情 | Yahoo Finance / 东方财富 |
| 客户信息（风险偏好、期限） | CRM 或会议纪要 |

### Step 2 — 持仓结构分析

使用 `terminal` 运行 Python 分析：

```python
import pandas as pd
import numpy as np

# 读取持仓数据
# df = pd.read_csv('portfolio.csv')  # columns: ticker, shares, cost_basis, current_price

# 计算持仓权重
df['market_value'] = df['shares'] * df['current_price']
df['weight'] = df['market_value'] / df['market_value'].sum()

# 计算未实现盈亏
df['unrealized_pnl'] = (df['current_price'] - df['cost_basis']) * df['shares']
df['return_pct'] = (df['current_price'] / df['cost_basis'] - 1) * 100

# 按资产类别汇总（需先标注 asset_class 列）
asset_summary = df.groupby('asset_class').agg(
    market_value=('market_value', 'sum'),
    unrealized_pnl=('unrealized_pnl', 'sum')
).assign(weight=lambda x: x['market_value'] / x['market_value'].sum())

print(asset_summary.to_string())
```

### Step 3 — 风险指标计算

```python
# 获取历史净值数据（假设有 daily_returns Series）
# 计算风险指标
volatility = daily_returns.std() * np.sqrt(252)  # 年化波动率
max_drawdown = (daily_returns.cumsum() / daily_returns.cumsum().cummax() - 1).min()
sharpe_ratio = (annual_return - 0.03) / volatility if volatility > 0 else 0  # 假设无风险利率3%

print(f"年化波动率: {volatility:.2%}")
print(f"最大回撤: {max_drawdown:.2%}")
print(f"夏普比率: {sharpe_ratio:.2f}")
```

### Step 4 — 表现归因 vs 基准

```python
# 计算组合 vs 基准的超额收益
portfolio_return = (end_value / start_value - 1) * 100
benchmark_return = (benchmark_end / benchmark_start - 1) * 100
excess_return = portfolio_return - benchmark_return

print(f"组合收益: {portfolio_return:.2f}%")
print(f"基准收益: {benchmark_return:.2f}%")
print(f"超额收益: {excess_return:.2f}%")
```

### Step 5 — 生成 Review 报告

输出格式：

```markdown
## 客户账户 Review — {客户姓名} {日期}

### 账户概览
| 指标 | 值 |
|------|-----|
| 总市值 | XX万元 |
| 本年收益 | +X.X% |
| vs 基准 | +X.X% |
| 年化波动率 | X.X% |
| 最大回撤 | X.X% |

### 持仓结构
- 股票：XX% | 债券：XX% | 基金：XX% | 现金：XX%
- 前五大持仓：XXX(XX%)、XXX(XX%)、XXX(XX%)、XXX(XX%)、XXX(XX%)

### 风险评估
- 风险等级：{保守/稳健/积极/激进}
- 集中度风险：{无/存在}（单一标的 >20%）
- 行业集中度：{无/存在}（单一行业 >30%）

### 机会识别
- Rebalancing 机会：{有/无} — {描述}
- Tax-Loss Harvest 机会：{有/无} — {描述}

### 建议
1. {建议1}
2. {建议2}

### 备注
- 仅供参考，不构成投资建议
- 所有建议需客户本人确认并由持牌顾问审核
```

## 常用工具

| 类别 | 工具 | 用途 |
|------|------|------|
| 数据获取 | web | 行情数据、新闻 |
| 数据获取 | terminal (Python) | 计算持仓、风险指标 |
| 文件读写 | terminal (Python) | 读取客户持仓CSV |

## 已知陷阱

1. **数据滞后** — 持仓数据可能有T-1延迟，注明数据截止日
2. **成本基础不准确** — 多次买入时需用 FIFO/Average cost，注明成本计算方法
3. **风险指标假设** — 年化波动率基于历史数据，不代表未来；需注明数据区间
4. **客户风险偏好不匹配** — 持仓风险等级需与客户风险测评匹配
5. **所有输出必须标注"仅供参考，不构成投资建议"**

## 验证方法

- [ ] 账户总市值与各持仓汇总一致（误差 <1%）
- [ ] 持仓权重合计 = 100%
- [ ] 风险指标已标注数据区间和计算方法
- [ ] 报告包含"仅供参考，不构成投资建议"
---
name: financial-wealth-management
description: 财富管理顾问工作台 — 覆盖客户账户 Review、财务计划制定、组合再平衡、税务亏损抵减四大模块，支持财富管理客户全生命周期服务。
version: 0.1
owner: hermes-financial
tags: [wealth-management, client-review, financial-plan, rebalancing, tax-loss-harvest, asset-allocation]
created: 2026-06-15
trigger: 当主人要求"客户账户review"、"财务计划"、"组合再平衡"、"税务亏损抵减"时自动激活
---

# Financial Wealth Management · 财富管理顾问工作台

## 核心定位

统一的财富管理顾问工作台，覆盖客户账户 Review、财务计划制定、组合再平衡、税务亏损抵减四大模块，支持财富管理客户全生命周期服务。

**免责声明**：所有输出必须标注"仅供参考，不构成投资建议"。

---

## 模块菜单

| 模块 | Skill 章节 | 适用触发词 |
|------|-----------|-----------|
| 客户账户 Review | [§客户账户 Review](#客户账户-review) | `review客户账户`、`过一遍客户持仓`、`客户账户表现分析` |
| 财务计划制定 | [§财务计划制定](#财务计划制定) | `帮我制定一个财务计划`、`退休规划`、`教育金规划`、`资产配置` |
| 组合再平衡 | [§组合再平衡](#组合再平衡) | `检查rebalance阈值`、`组合偏离目标多少`、`需要rebalance吗` |
| 税务亏损抵减 | [§税务亏损抵减](#税务亏损抵减) | `帮我看看有没有可以抵税的亏损`、`Tax-loss harvesting`、`有没有亏本的持仓` |

---

## 客户账户 Review

### 触发条件
```
用户说"帮我review这个客户账户"、"过一遍王总的持仓"、"客户账户表现分析"
```

### 执行步骤
**Step 1 · 获取账户数据**
使用 `web` 工具从券商客户报告、东方财富、雪球获取持仓明细和实时行情。

**Step 2 · 持仓结构分析**
```python
df['market_value'] = df['shares'] * df['current_price']
df['weight'] = df['market_value'] / df['market_value'].sum()
df['unrealized_pnl'] = (df['current_price'] - df['cost_basis']) * df['shares']
df['return_pct'] = (df['current_price'] / df['cost_basis'] - 1) * 100
```

**Step 3 · 风险指标计算**
```python
volatility = daily_returns.std() * np.sqrt(252)  # 年化波动率
max_drawdown = (daily_returns.cumsum() / daily_returns.cumsum().cummax() - 1).min()
sharpe_ratio = (annual_return - 0.03) / volatility  # 假设无风险利率3%
```

**Step 4 · 表现归因 vs 基准**
```python
portfolio_return = (end_value / start_value - 1) * 100
benchmark_return = (benchmark_end / benchmark_start - 1) * 100
excess_return = portfolio_return - benchmark_return
```

**Step 5 · 输出 Review 报告**
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

### 风险评估
- 风险等级：{保守/稳健/积极/激进}
- 集中度风险：{无/存在}

### 机会识别
- Rebalancing 机会：{有/无}
- Tax-Loss Harvest 机会：{有/无}
```

### 已知陷阱
1. 数据滞后 — 持仓数据可能有T-1延迟，注明数据截止日
2. 成本基础不准确 — 多次买入时需用 FIFO/Average cost
3. 客户风险偏好不匹配 — 持仓风险等级需与客户风险测评匹配

### Verification
- [ ] 账户总市值与各持仓汇总一致（误差 <1%）
- [ ] 持仓权重合计 = 100%
- [ ] 报告包含"仅供参考，不构成投资建议"

---

## 财务计划制定

### 触发条件
```
用户说"帮我制定一个财务计划"、"退休规划怎么做"、"教育金规划"、"资产配置建议"
```

### 生命周期阶段判断
```python
def get_life_stage(age):
    if age < 35:
        return {'stage': '积累期', 'equity_ratio': 0.80, 'bond_ratio': 0.15, 'cash_ratio': 0.05}
    elif age < 50:
        return {'stage': '巩固期', 'equity_ratio': 0.65, 'bond_ratio': 0.25, 'cash_ratio': 0.10}
    elif age < 60:
        return {'stage': '高峰期', 'equity_ratio': 0.45, 'bond_ratio': 0.35, 'cash_ratio': 0.20}
    else:
        return {'stage': '退休期', 'equity_ratio': 0.25, 'bond_ratio': 0.50, 'cash_ratio': 0.25}
```

### 退休规划计算
```python
def calc_retirement(target_amount, years, annual_savings, expected_return=0.07):
    future_value_of_savings = sum(
        annual_savings * (1 + expected_return) ** (years - i)
        for i in range(1, years + 1)
    )
    gap = target_amount - future_value_of_savings
    monthly_savings_needed = gap / (years * 12) if years > 0 and gap > 0 else 0
    return {'target_amount': target_amount, 'gap': gap, 'monthly_savings_needed': monthly_savings_needed}
```

### 输出 Financial Plan 报告
```markdown
## 财务计划 — {客户姓名} {日期}

### 客户基本信息
| 项目 | 值 |
|------|-----|
| 姓名 | {张三} |
| 年龄 | {40}岁 |
| 所处阶段 | {巩固期} |
| 净资产 | {400}万元 |

### 生命周期评估
- **当前阶段**：巩固期（35-50岁）
- **建议风险偏好**：积极-稳健
- **投资期限**：约20年

### 财务目标
| 目标 | 目标金额 | 目标年份 | 距离年限 | 优先级 |
|------|---------|---------|---------|--------|
| 退休规划 | 1,000万 | 2045 | 19年 | 最高 |

### 资产配置建议
| 资产类别 | 建议金额 | 占比 | 适配产品 |
|---------|---------|------|---------|
| 权益类 | 260万 | 65% | 股票型基金、指数ETF |
| 固定收益 | 100万 | 25% | 债券基金、银行理财 |
| 现金类 | 40万 | 10% | 货币基金 |

### 执行计划
| 优先级 | 行动 | 时间节点 |
|--------|------|---------|
| 1 | 建立紧急储备金 | 即时 |
| 2 | 偿还高息负债 | 3个月内 |
```

### 已知陷阱
1. 假设收益率 — 历史收益不代表未来，建议使用保守假设（5-7%）
2. 通胀影响 — 长期规划需考虑通胀（建议3%年通胀假设）
3. 流动性需求 — 避免将短期资金投入长期资产

### Verification
- [ ] 生命周期阶段判断正确
- [ ] 资产配置比例合计 = 100%
- [ ] 已标注免责声明

---

## 组合再平衡

### 触发条件
```
用户说"检查rebalance阈值"、"组合偏离目标多少"、"需要rebalance吗"
```

### 阈值触发逻辑
| 阈值类型 | 触发条件 | 默认值 |
|---------|---------|--------|
| 单项资产偏离 | |asset_weight - target_weight| > 5% | 5% |
| 整体偏离度 | sqrt(Σ(asset_i - target_i)²) > 10% | 10% |
| 强制再平衡 | 任意单项偏离 > 10% | 10% |

### 偏离度计算
```python
def calc_drift(current, target):
    drift = np.array([current.get(a, 0) for a in target]) - np.array([target[a] for a in target])
    max_drift = np.max(np.abs(drift))
    overall_drift = np.sqrt(np.mean(drift**2))
    return {'max_drift': max_drift, 'overall_drift': overall_drift}
```

### 再平衡交易计算
```python
def calc_rebalance(current, target, total_value, min_trade=0.01):
    diff = np.array([target[a] for a in target]) - np.array([current.get(a, 0) for a in target])
    # 正=买入，负=卖出
    # 金额 = diff * total_value
```

### 输出 Rebalancing 报告
```markdown
## 组合再平衡分析 — {日期}

### 阈值设置
| 阈值类型 | 触发值 | 当前状态 |
|---------|-------|---------|
| 单项偏离 | >5% | {触发/未触发} |

### 偏离度详情
| 资产类别 | 目标权重 | 当前权重 | 偏离度 |
|---------|---------|---------|--------|

### 再平衡建议
| 交易 | 方向 | 金额 |
|------|------|------|
| 卖出股票 | 卖出 | -25万 |
| 买入债券 | 买入 | +25万 |
```

### 已知陷阱
1. 税费影响 — 卖出时有资本利得税（中国A股：盈利部分收取20%）
2. 冲击成本 — 大额交易会冲击市场价格，需分批执行
3. 最小交易量 — A股100股起

### Verification
- [ ] 偏离度计算正确（current + drift = target）
- [ ] 再平衡交易后各资产权重等于目标权重
- [ ] 已标注免责声明

---

## 税务亏损抵减

### 触发条件
```
用户说"帮我看看有没有可以抵税的亏损"、"Tax-loss harvesting机会"、"有没有亏本的持仓可以卖出抵税"
```

### 中国税务规则要点
| 项目 | 规则 |
|------|------|
| 税率 | 个人 A 股资本利得税：20% |
| 亏损抵扣 | 2023年起可抵扣综合所得（试点政策） |
| 基金规则 | 同股票规则，赎回时确认盈亏 |

### 浮亏持仓识别
```python
portfolio['unrealized_pnl'] = (portfolio['current_price'] - portfolio['cost_basis']) * portfolio['shares']
portfolio['return_pct'] = (portfolio['current_price'] / portfolio['cost_basis'] - 1) * 100
loss_positions = portfolio[portfolio['unrealized_pnl'] < 0].sort_values('unrealized_pnl')
```

### 节税估算
```python
TAX_RATE = 0.20
loss_positions['tax_saving'] = -loss_positions['unrealized_pnl'] * TAX_RATE
total_tax_saving = -loss_positions['unrealized_pnl'].sum() * TAX_RATE
```

### 输出 Tax-Loss Harvest 报告
```markdown
## Tax-Loss Harvest 机会分析 — {日期}

### 中国税务规则摘要
- **A股资本利得税率**：20%（个人）
- **亏损抵扣规则**：2023年起可抵扣综合所得（试点政策）

### 当前账户浮亏持仓
| 持仓 | 浮亏金额 | 亏损比例 | 可抵扣税额（估算） |
|------|---------|---------|-----------------|
| 贵州茅台 | -10,000元 | -5.6% | ~2,000元 |

### Harvest 建议
| 操作 | 持仓 | 亏损金额 | 估算节税 | 优先级 |
|------|------|---------|---------|--------|
| 卖出 | 贵州茅台 | 10,000元 | ~2,000元 | 高 |

### 节税估算
- 总可收割浮亏：{XX,XXX}元
- 估算节税金额（20%税率）：{X,XXX}元
```

### 已知陷阱
1. 政策不确定性 — 中国资本利得税规则可能调整
2. 跨品种亏损 — 股票亏损不能抵扣ETF/债券盈利
3. 申报时间 — 需在当年报税季完成申报

### Verification
- [ ] 浮亏计算正确（cost_basis vs current_price）
- [ ] 节税估算基于正确税率（20%）
- [ ] 已标注免责声明
- [ ] 建议客户寻求专业税务顾问
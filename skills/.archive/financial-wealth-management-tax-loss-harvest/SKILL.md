---
name: tax-loss-harvest
description: 税务亏损抵减（中国税务规则）— 亏损识别、抵减策略、wash-sale规则、节税估算
version: 1.0.0
author: hermes-financial · wealth-management
tags: [wealth-management, tax-loss-harvest, china-tax, capital-gain]
related_skills: [client-review, rebalancing, financial-plan]
---

# tax-loss-harvest · 税务亏损抵减

## 什么时候用

用户要求"帮我看看有没有可以抵税的亏损"、"Tax-loss harvesting机会"、"有没有亏本的持仓可以卖出抵税"时，触发本 skill。

## 核心职责

1. 识别账户中处于浮亏状态的持仓（未实现亏损）
2. 计算潜在税前抵扣额度（中国A股：资本利得税20%）
3. 提示 wash-sale 规则限制（中国暂无正式wash-sale规则，但需关注跨品种亏损）
4. 结合客户税务居民身份提供节税建议
5. 生成 Tax-Loss Harvest 机会报告

## 触发条件

```
用户说"帮我看看有没有可以抵税的亏损"、"Tax-loss harvesting机会"、"有没有亏本的持仓可以卖出抵税"
```

## 中国税务规则要点

### A股资本利得税规则（2024现行）

| 项目 | 规则 |
|------|------|
| 税率 | 个人：20%（部分免税额度待政策明确） |
| 亏损抵扣 | 只可抵扣当年的资本利得，无法跨年抵扣（2023年前规则） |
| 2023新规 | 个人证券交易亏损额度可用于抵扣工资薪金等综合所得（试点） |
| 基金赎回 | 同上规则，赎回时确认盈亏 |
| 债券 | 企业债/国债的利息和转让规则不同 |

### 关键限制

1. **跨品种亏损** — 股票亏损不能直接抵扣ETF/基金的盈利，需分别计算
2. **持有期** — 持有超过1年的股票，股息红利可免税（差异化税收）
3. **特定限制品种** — 合格境外机构投资者（QFII）规则不同

## 工作流程

### Step 1 — 获取浮亏持仓

使用 `web` 或 `terminal`（读文件）获取：

```python
import pandas as pd

# 持仓数据（示例）
# columns: ticker, name, shares, cost_basis, current_price, asset_class
portfolio = pd.DataFrame({
    'ticker': ['600519', '000858', '510310'],
    'name': ['贵州茅台', '五粮液', ['沪深300ETF'],
    'shares': [100, 200, 10000],
    'cost_basis': [1800.0, 180.0, 3.8],
    'current_price': [1700.0, 150.0, 3.5],
    'asset_class': ['stock', 'stock', 'fund']
})

# 计算浮盈亏
portfolio['market_value'] = portfolio['shares'] * portfolio['current_price']
portfolio['cost_total'] = portfolio['shares'] * portfolio['cost_basis']
portfolio['unrealized_pnl'] = portfolio['market_value'] - portfolio['cost_total']
portfolio['return_pct'] = (portfolio['current_price'] / portfolio['cost_basis'] - 1) * 100

# 筛选浮亏持仓
loss_positions = portfolio[portfolio['unrealized_pnl'] < 0].copy()
loss_positions = loss_positions.sort_values('unrealized_pnl')
print(loss_positions[['name', 'unrealized_pnl', 'return_pct']].to_string())
```

### Step 2 — 计算税前抵扣额度

```python
# 中国A股资本利得税率
TAX_RATE = 0.20

# 计算各浮亏持仓的潜在抵扣额度
loss_positions['tax_saving'] = -loss_positions['unrealized_pnl'] * TAX_RATE

print("\n可抵扣亏损持仓:")
print(loss_positions[['name', 'unrealized_pnl', 'tax_saving']].to_string())

total_loss = -loss_positions['unrealized_pnl'].sum()
total_tax_saving = loss_positions['tax_saving'].sum()
print(f"\n总浮亏: {total_loss:.2f}万元")
print(f"潜在税前抵扣额度: {total_tax_saving:.2f}万元")
```

### Step 3 — 识别 Wash-Sale 风险

```python
def check_wash_sale_risk(ticker, asset_class, recent_trades, days=30):
    """
    检查wash-sale风险（中国虽无正式规则，但需关注短期亏损重复产生）
    若30天内买入相同标的，亏损可能无法抵扣（假设规则存在时）
    """
    # 检查近期是否有相同ticker/同资产类别的买入
    same_ticker = recent_trades[
        (recent_trades['ticker'] == ticker) & 
        (recent_trades['action'] == '买入') &
        (recent_trades['days_ago'] < days)
    ]
    
    same_asset = recent_trades[
        (recent_trades['asset_class'] == asset_class) & 
        (recent_trades['action'] == '买入') &
        (recent_trades['days_ago'] < days)
    ] if asset_class == 'stock' else pd.DataFrame()
    
    risk = len(same_ticker) > 0 or len(same_asset) > 0
    return risk, same_ticker, same_asset

# 示例
# recent_trades = pd.DataFrame(...) # 近期交易记录
# risk, _, _ = check_wash_sale_risk('600519', 'stock', recent_trades)
```

### Step 4 — 节税估算与策略

```python
def estimate_tax_saving(harvest_list, tax_rate=0.20):
    """
    估算节税金额
    harvest_list: 拟收割亏损的持仓列表 [{ticker, loss}]
    """
    total_loss = sum([h['loss'] for h in harvest_list])
    tax_saving = total_loss * tax_rate
    return total_loss, tax_saving

# 示例：收割3只亏损股票
harvest_candidates = [
    {'ticker': '600519', 'name': '贵州茅台', 'loss': 10000},
    {'ticker': '000858', 'name': '五粮液', 'loss': 6000},
]

total_loss, tax_saving = estimate_tax_saving(harvest_candidates)
print(f"总浮亏: {total_loss:.0f}元")
print(f"估算节税（20%税率）: {tax_saving:.0f}元")
```

### Step 5 — 输出 Tax-Loss Harvest 报告

```markdown
## Tax-Loss Harvest 机会分析 — {日期}

### 中国税务规则摘要
- **A股资本利得税率**：20%（个人）
- **亏损抵扣规则**：2023年起可抵扣综合所得（试点政策，详见当年规定）
- **基金规则**：同股票规则，赎回时确认盈亏

### 当前账户浮亏持仓
| 持仓 | 浮亏金额 | 亏损比例 | 可抵扣税额（估算） |
|------|---------|---------|-----------------|
| 贵州茅台 | -10,000元 | -5.6% | ~2,000元 |
| 五粮液 | -6,000元 | -16.7% | ~1,200元 |

### Wash-Sale 风险检查
| 持仓 | 30天内买入同标的 | 风险提示 |
|------|----------------|---------|
| 贵州茅台 | 无 | ✓ 无风险 |
| 五粮液 | 无 | ✓ 无风险 |

### Harvest 建议
| 操作 | 持仓 | 亏损金额 | 估算节税 | 优先级 |
|------|------|---------|---------|--------|
| 卖出 | 贵州茅台 | 10,000元 | ~2,000元 | 高 |
| 卖出 | 五粮液 | 6,000元 | ~1,200元 | 高 |

### 节税估算
- 总可收割浮亏：{XX,XXX}元
- 估算节税金额（20%税率）：{X,XXX}元
- 注意事项：节税金额需结合客户全年资本利得综合计算

### 执行建议
1. {优先级最高建议}
2. {注意事项}

### 备注
- 仅供参考，不构成投资建议
- 中国税务规则复杂且可能有政策调整，建议客户咨询专业税务顾问
- 亏损抵扣需在当年报税时申报，请关注申报截止日期（通常5月31日）
```

## 常用工具

| 类别 | 工具 | 用途 |
|------|------|------|
| 数据获取 | web | 行情数据、最新税务政策 |
| 计算 | terminal (Python) | 浮亏计算、节税估算 |
| 文件读写 | terminal | 读取持仓数据、保存报告 |

## 已知陷阱

1. **政策不确定性** — 中国资本利得税规则可能调整，需关注最新政策
2. **跨品种亏损** — 股票亏损不能抵扣ETF/债券盈利
3. **持有期影响** — 1年以上股票分红免税，亏损抵减策略需考虑持有期
4. **申报时间** — 需在当年报税季完成申报，逾期可能丧失抵扣资格
5. **所有输出必须标注"仅供参考，不构成投资建议"**
6. **建议客户咨询专业税务顾问**

## 验证方法

- [ ] 浮亏计算正确（cost_basis vs current_price）
- [ ] 节税估算基于正确税率（20%）
- [ ] 已提示税务政策不确定性
- [ ] 已标注免责声明
- [ ] 建议客户寻求专业税务顾问
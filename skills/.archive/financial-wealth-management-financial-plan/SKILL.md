---
name: financial-plan
description: 财务计划制定（生命周期模型）— 目标设定、需求分析、资产配置、退休规划、教育金规划
version: 1.0.0
author: hermes-financial · wealth-management
tags: [wealth-management, financial-plan, life-cycle, retirement-planning, asset-allocation]
related_skills: [client-review, rebalancing, tax-loss-harvest]
---

# financial-plan · 财务计划制定

## 什么时候用

用户要求"帮我制定一个财务计划"、"退休规划"、"教育金规划"、"资产配置建议"时，触发本 skill。

## 核心职责

1. 收集客户财务信息（收入、支出、资产、负债、目标）
2. 基于生命周期模型评估客户所处阶段
3. 分析客户财务需求（退休、教育、购房、传承）
4. 生成个性化资产配置建议
5. 提供分阶段执行计划

## 触发条件

```
用户说"帮我制定一个财务计划"、"退休规划怎么做"、"教育金规划"、"资产配置建议"
```

## 生命周期模型

### 人生阶段划分

| 阶段 | 年龄范围 | 特征 | 风险偏好 | 资产配置逻辑 |
|------|---------|------|---------|------------|
| 积累期 | 22-35岁 | 收入增长、开始储蓄 | 积极 | 权益为主（80%+），定投为主 |
| 巩固期 | 35-50岁 | 收入高峰期、家庭责任 | 积极-稳健 | 权益60-70%，债券20-30% |
| 高峰期 | 50-60岁 | 财富峰值、临近退休 | 稳健 | 权益40-50%，债券30-40% |
| 退休期 | 60岁+ | 收入减少、依赖储蓄 | 保守 | 债券50%+，权益<30%，保留现金 |

### 财务目标分类

| 目标类型 | 时间跨度 | 优先级 | 适配工具 |
|---------|---------|--------|---------|
| 应急储备 | 即时 | 最高 | 货币基金、银行理财 |
| 退休规划 | 10-30年 | 最高 | 长期投资、保险 |
| 教育金 | 5-20年 | 高 | 教育金储蓄、基金定投 |
| 购房规划 | 3-10年 | 中 | 中短期理财 |
| 传承规划 | 长期 | 中 | 保险、信托 |

## 工作流程

### Step 1 — 收集财务信息

使用 `web` 或 `terminal`（读文件）获取客户数据：

```python
# 客户财务信息（示例）
client_info = {
    'name': '张三',
    'age': 40,
    'annual_income': 100,      # 年收入（万元）
    'annual_expense': 50,      # 年支出（万元）
    'total_assets': 500,       # 总资产（万元）
    'total_liabilities': 100,  # 总负债（万元）
    'net_worth': 400,          # 净资产（万元）
    'risk_tolerance': '积极',  # 风险偏好
    'investment_horizon': 20,   # 投资期限（年）
    'goals': [
        {'type': 'retirement', 'target_year': 2045, 'amount': 1000},
        {'type': 'education', 'target_year': 2030, 'amount': 200},
        {'type': 'emergency', 'amount': 50}
    ]
}
```

### Step 2 — 生命周期阶段判断

```python
def get_life_stage(age):
    """根据年龄判断生命周期阶段"""
    if age < 35:
        return {
            'stage': '积累期',
            'equity_ratio': 0.80,
            'bond_ratio': 0.15,
            'cash_ratio': 0.05,
            'description': '收入增长期，建议定投权益类资产'
        }
    elif age < 50:
        return {
            'stage': '巩固期',
            'equity_ratio': 0.65,
            'bond_ratio': 0.25,
            'cash_ratio': 0.10,
            'description': '收入高峰期，适当增加债券配置'
        }
    elif age < 60:
        return {
            'stage': '高峰期',
            'equity_ratio': 0.45,
            'bond_ratio': 0.35,
            'cash_ratio': 0.20,
            'description': '临近退休，逐步转向稳健'
        }
    else:
        return {
            'stage': '退休期',
            'equity_ratio': 0.25,
            'bond_ratio': 0.50,
            'cash_ratio': 0.25,
            'description': '退休生活期，保本为主'
        }

stage = get_life_stage(client_info['age'])
print(f"客户处于：{stage['stage']}")
print(f"建议配置：权益{stage['equity_ratio']:.0%} | 债券{stage['bond_ratio']:.0%} | 现金{stage['cash_ratio']:.0%}")
```

### Step 3 — 退休规划计算

```python
def calc_retirement(target_amount, years, annual_savings, expected_return=0.07):
    """
    计算退休规划
    target_amount: 退休目标金额（万元）
    years: 距离退休年限
    annual_savings: 每年储蓄（万元）
    expected_return: 预期年化收益率
    """
    future_value_of_savings = 0
    for i in range(1, years + 1):
        future_value_of_savings += annual_savings * (1 + expected_return) ** (years - i)
    
    gap = target_amount - future_value_of_savings
    monthly_savings_needed = gap / (years * 12) if years > 0 and gap > 0 else 0
    
    return {
        'target_amount': target_amount,
        'years': years,
        'expected_return': expected_return,
        'projected_savings': future_value_of_savings,
        'gap': gap,
        'monthly_savings_needed': monthly_savings_needed
    }

retirement_plan = calc_retirement(
    target_amount=client_info['goals'][0]['amount'],
    years=client_info['goals'][0]['target_year'] - 2026,
    annual_savings=client_info['annual_income'] - client_info['annual_expense']
)
print(f"退休目标: {retirement_plan['target_amount']}万元")
print(f"预期储蓄: {retirement_plan['projected_savings']:.0f}万元")
print(f"缺口: {retirement_plan['gap']:.0f}万元")
print(f"每月需多储蓄: {retirement_plan['monthly_savings_needed']:.0f}万元")
```

### Step 4 — 紧急储备金规划

```python
def calc_emergency_fund(annual_expense, months=6):
    """
    计算紧急储备金需求
    通常建议 3-6个月支出
    """
    monthly_expense = annual_expense / 12
    emergency_fund = monthly_expense * months
    return emergency_fund

emergency = calc_emergency_fund(client_info['annual_expense'], months=6)
print(f"建议紧急储备金: {emergency:.0f}万元（{months}个月支出）")
```

### Step 5 — 资产配置建议

```python
def generate_asset_allocation(stage, net_worth, goals):
    """
    基于生命周期生成资产配置建议
    """
    # 基础配置
    equity = net_worth * stage['equity_ratio']
    bond = net_worth * stage['bond_ratio']
    cash = net_worth * stage['cash_ratio']
    
    # 紧急储备金（优先从现金中提取）
    emergency_fund = calc_emergency_fund(client_info['annual_expense'], 6)
    investable_cash = cash - emergency_fund
    
    allocation = {
        '权益类': {'amount': equity, 'ratio': stage['equity_ratio'], 'products': ['股票型基金', '指数ETF']},
        '固定收益': {'amount': bond, 'ratio': stage['bond_ratio'], 'products': ['债券基金', '银行理财']},
        '现金及等价物': {'amount': cash, 'ratio': stage['cash_ratio'], 'products': ['货币基金', '短期理财']},
        '紧急储备金': {'amount': emergency_fund, 'ratio': emergency_fund/net_worth, 'products': ['货币基金']}
    }
    
    return allocation

allocation = generate_asset_allocation(stage, client_info['net_worth'], client_info['goals'])
print("\n资产配置建议:")
for category, info in allocation.items():
    print(f"  {category}: {info['amount']:.0f}万元 ({info['ratio']:.0%}) - {', '.join(info['products'])}")
```

### Step 6 — 输出 Financial Plan 报告

```markdown
## 财务计划 — {客户姓名} {日期}

### 客户基本信息
| 项目 | 值 |
|------|-----|
| 姓名 | {张三} |
| 年龄 | {40}岁 |
| 所处阶段 | {巩固期} |
| 净资产 | {400}万元 |
| 年收入 | {100}万元 |
| 年支出 | {50}万元 |
| 风险偏好 | {积极} |

### 生命周期评估
- **当前阶段**：巩固期（35-50岁）
- **阶段特征**：收入高峰期，家庭责任增加
- **建议风险偏好**：积极-稳健
- **投资期限**：约20年

### 财务目标
| 目标 | 目标金额 | 目标年份 | 距离年限 | 优先级 |
|------|---------|---------|---------|--------|
| 退休规划 | 1,000万 | 2045 | 19年 | 最高 |
| 教育金 | 200万 | 2030 | 4年 | 高 |
| 紧急储备 | 50万 | 即时 | - | 最高 |

### 退休规划分析
- **退休目标**：1,000万元
- **预期储蓄积累**：约{XXX}万元（假设年化7%）
- **资金缺口**：约{XXX}万元
- **建议**：每月额外储蓄约{XX}万元，或调整退休目标

### 资产配置建议
| 资产类别 | 建议金额 | 占比 | 适配产品 |
|---------|---------|------|---------|
| 权益类 | 260万 | 65% | 股票型基金、指数ETF |
| 固定收益 | 100万 | 25% | 债券基金、银行理财 |
| 现金类 | 40万 | 10% | 货币基金 |
| 其中紧急储备 | 25万 | 6% | 货币基金（优先提取） |

### 执行计划
| 优先级 | 行动 | 时间节点 | 说明 |
|--------|------|---------|------|
| 1 | 建立紧急储备金 | 即时 | 存入货币基金，6个月支出 |
| 2 | 偿还高息负债 | 3个月内 | 优先偿还利率>6%的负债 |
| 3 | 启动教育金定投 | 1个月内 | 每月{XX}元，4年积累200万 |
| 4 | 退休账户定投 | 1个月内 | 每月{XX}元，复利增长 |

### 分阶段里程碑
- **第1年**：紧急储备金到位，负债清零
- **第5年**：教育金目标达成，退休账户积累{XX}万
- **第10年**：净资产达{XX}万，目标进度{XX}%
- **第20年**：退休目标达成

### 备注
- 仅供参考，不构成投资建议
- 本计划基于当前财务状况和假设条件，实际结果可能不同
- 建议定期（每年）复盘并调整计划
- 所有建议需由持牌理财顾问审核
```

## 常用工具

| 类别 | 工具 | 用途 |
|------|------|------|
| 数据获取 | web | 通胀率、预期收益率查询 |
| 计算 | terminal (Python) | 复利计算、资产配置优化 |
| 文件读写 | terminal | 读取客户数据、保存计划 |

## 已知陷阱

1. **假设收益率** — 历史收益不代表未来，建议使用保守假设（5-7%）
2. **通胀影响** — 长期规划需考虑通胀（建议3%年通胀假设）
3. **税收变化** — 税务规则可能调整，影响实际收益
4. **流动性需求** — 避免将短期资金投入长期资产
5. **所有输出必须标注"仅供参考，不构成投资建议"**
6. **建议定期复盘调整（建议每年一次）**

## 验证方法

- [ ] 客户信息完整（年龄、收入、支出、资产、负债、目标）
- [ ] 生命周期阶段判断正确
- [ ] 退休规划计算逻辑正确（复利公式验证）
- [ ] 资产配置比例合计 = 100%
- [ ] 紧急储备金已包含在配置中
- [ ] 已标注免责声明
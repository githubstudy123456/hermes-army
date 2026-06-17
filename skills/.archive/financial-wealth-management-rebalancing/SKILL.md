---
name: rebalancing
description: 组合再平衡 — 阈值触发检测、偏离度计算、再平衡建议生成（含成本分析）
version: 1.0.0
author: hermes-financial · wealth-management
tags: [wealth-management, rebalancing, portfolio, threshold-trigger]
related_skills: [client-review, tax-loss-harvest, financial-plan]
---

# rebalancing · 组合再平衡

## 什么时候用

用户要求"检查是否需要rebalance"、"帮我看看组合偏离目标配置"、"触发rebalance阈值了吗"时，触发本 skill。

## 核心职责

1. 获取客户当前持仓与目标配置
2. 检测各资产类别偏离度
3. 判断是否触发再平衡阈值（默认阈值：单一资产偏离 >5% 或整体偏离 >10%）
4. 计算最优再平衡交易（考虑税费、最小交易量）
5. 输出可执行的再平衡建议

## 触发条件

```
用户说"检查rebalance阈值"、"组合偏离目标多少"、"需要rebalance吗"
```

## 阈值触发逻辑

### 默认阈值规则

| 阈值类型 | 触发条件 | 默认值 |
|---------|---------|--------|
| 单项资产偏离 | |asset_weight - target_weight| > 5% | 5% |
| 整体偏离度 | sqrt(Σ(asset_i - target_i)²) > 10% | 10% |
| 强制再平衡 | 任意单项偏离 > 10% | 10% |
| 时间再平衡 | 距上次再平衡 > N个月 | 3个月 |

### 判断流程

```
输入：当前权重[], 目标权重[], 阈值参数
输出：是否触发再平衡 + 偏离度报告

1. 计算每项偏离度 = |current_i - target_i|
2. 判断 max(偏离度) > 单项阈值？ → 触发
3. 计算整体偏离度 = sqrt(Σ偏离度²)
4. 判断整体偏离度 > 整体阈值？ → 触发
5. 输出触发结果 + 各资产偏离详情
```

## 工作流程

### Step 1 — 获取持仓与目标配置

使用 `web` 或 `terminal`（读文件）获取：

```python
# 当前持仓（当前权重）
current_weights = {
    '股票': 0.60,
    '债券': 0.25,
    '黄金': 0.05,
    '现金': 0.10
}

# 客户目标配置
target_weights = {
    '股票': 0.55,
    '债券': 0.30,
    '黄金': 0.05,
    '现金': 0.10
}

# 账户总市值（万元）
total_value = 500  # 500万
```

### Step 2 — 计算偏离度

```python
import numpy as np

def calc_drift(current, target):
    """计算偏离度"""
    assets = list(target.keys())
    current_arr = np.array([current.get(a, 0) for a in assets])
    target_arr = np.array([target[a] for a in assets])
    
    drift = current_arr - target_arr
    abs_drift = np.abs(drift)
    
    # 单项最大偏离
    max_drift = np.max(abs_drift)
    max_asset = assets[np.argmax(abs_drift)]
    
    # 整体偏离度（RMS）
    overall_drift = np.sqrt(np.mean(drift**2))
    
    return {
        'assets': assets,
        'current': current_arr,
        'target': target_arr,
        'drift': drift,
        'abs_drift': abs_drift,
        'max_drift': max_drift,
        'max_asset': max_asset,
        'overall_drift': overall_drift
    }

result = calc_drift(current_weights, target_weights)
print(f"最大单项偏离: {result['max_asset']} {result['max_drift']:.1%}")
print(f"整体偏离度: {result['overall_drift']:.1%}")
```

### Step 3 — 阈值判断

```python
SINGLE_THRESHOLD = 0.05   # 5%
OVERALL_THRESHOLD = 0.10   # 10%
FORCED_THRESHOLD = 0.10   # 10%

triggered = []
if result['max_drift'] > SINGLE_THRESHOLD:
    triggered.append(f"单项偏离触发: {result['max_asset']} 偏离 {result['max_drift']:.1%}")
if result['overall_drift'] > OVERALL_THRESHOLD:
    triggered.append(f"整体偏离触发: {result['overall_drift']:.1%}")
if result['max_drift'] > FORCED_THRESHOLD:
    triggered.append(f"强制再平衡触发: {result['max_asset']} 偏离 {result['max_drift']:.1%}")

if triggered:
    print("⚠️ 再平衡触发!")
    for t in triggered:
        print(f"  - {t}")
else:
    print("✓ 无需再平衡")
```

### Step 4 — 计算再平衡交易

```python
def calc_rebalance(current, target, total_value, min_trade=0.01):
    """
    计算再平衡交易建议
    min_trade: 最小交易比例（低于此值忽略）
    """
    assets = list(target.keys())
    current_arr = np.array([current.get(a, 0) for a in assets])
    target_arr = np.array([target[a] for a in assets])
    
    diff = target_arr - current_arr  # 正=买入，负=卖出
    
    trades = []
    for i, asset in enumerate(assets):
        if abs(diff[i]) >= min_trade:
            trade_value = diff[i] * total_value
            trades.append({
                'asset': asset,
                'action': '买入' if diff[i] > 0 else '卖出',
                'weight_change': f"{diff[i]:+.1%}",
                'value': f"{trade_value:+.0f}万",
                'new_weight': f"{target_arr[i]:.1%}"
            })
    
    return trades

trades = calc_rebalance(current_weights, target_weights, total_value)
print("\n再平衡建议:")
for t in trades:
    print(f"  {t['action']} {t['asset']}: {t['weight_change']} ({t['value']}) → 目标权重 {t['new_weight']}")
```

### Step 5 — 输出 Rebalancing 报告

```markdown
## 组合再平衡分析 — {日期}

### 阈值设置
| 阈值类型 | 触发值 | 当前状态 |
|---------|-------|---------|
| 单项偏离 | >5% | {触发/未触发} |
| 整体偏离 | >10% | {触发/未触发} |
| 强制再平衡 | >10% | {触发/未触发} |

### 偏离度详情
| 资产类别 | 目标权重 | 当前权重 | 偏离度 |
|---------|---------|---------|--------|
| 股票 | 55% | 60% | +5% |
| 债券 | 30% | 25% | -5% |
| 黄金 | 5% | 5% | 0% |
| 现金 | 10% | 10% | 0% |

### 再平衡建议
| 交易 | 方向 | 金额 | 说明 |
|------|------|------|------|
| 卖出股票 | 卖出 | -25万 | 减持至目标权重 |
| 买入债券 | 买入 | +25万 | 增持至目标权重 |

### 成本估算
- 交易佣金：约 XX元（假设万一）
- 印花税：股票卖出收取0.1%（A股）
- 冲击成本：{估算}

### 执行建议
1. {优先级最高的操作}
2. {其次}

### 备注
- 仅供参考，不构成投资建议
- 再平衡需考虑客户现金流需求和税收影响
- 建议由持牌顾问审核后执行
```

## 常用工具

| 类别 | 工具 | 用途 |
|------|------|------|
| 数据获取 | web | 行情数据、交易成本查询 |
| 计算 | terminal (Python) | 偏离度计算、再平衡优化 |
| 文件读写 | terminal | 读取客户配置、保存报告 |

## 已知陷阱

1. **阈值设置** — 不同客户风险偏好不同，需个性化设置阈值
2. **税费影响** — 卖出时有资本利得税（中国A股：盈利部分收取20%），需估算税后收益
3. **冲击成本** — 大额交易会冲击市场价格，需分批执行
4. **最小交易量** — A股100股起，债券有最小申购门槛
5. **所有输出必须标注"仅供参考，不构成投资建议"**

## 验证方法

- [ ] 偏离度计算正确（current + drift = target）
- [ ] 再平衡交易后各资产权重等于目标权重
- [ ] 交易金额与账户总市值匹配
- [ ] 已标注免责声明
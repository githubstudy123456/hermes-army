# AML Check · 反洗钱核查

## 基本信息

- **Skill Name**: financial-operations-aml-check
- **Description**: 交易级反洗钱监控，识别可疑交易模式，触发警报并生成 SAR（可疑交易报告）
- **Trigger Keywords**: `aml`, `aml check`, `反洗钱`, `可疑交易`, `sanctions screening`
- **Category**: operations

## 核心步骤

### Step 1: 交易数据采集

- 通过 `web` 获取交易监控系统数据
- 通过 `file` 读取交易记录（CSV/Excel）
- 通过 `terminal` 加载 pandas 分析

### Step 2: 可疑交易识别

```
FATF 可疑交易指标（红旗）：
1. 频繁大额现金存入
2. 快速转入转出（分层）
3. 关联方非正常价交易
4. 跨境资金流动与声明不符
5. 复杂股权结构隐藏受益人
6. 交易对手为高风险司法区
7. 异常时间段高频交易
```

### Step 3: 制裁名单实时筛查

```
筛查层级：
1. 全名匹配（Exact Match）
2. 模糊匹配（Phonetic/Algebraic）
3. 别名匹配（AKA）
4. 机构名匹配（Entity）
5. 地理匹配（高风险地区）
```

### Step 4: 风险评分模型

```python
def aml_risk_score(tx, customer_profile):
    score = 0
    # 金额异常
    if tx.amount > customer_profile.median * 10:
        score += 30
    # 交易对手风险
    if tx.counterparty in high_risk_countries:
        score += 25
    # 交易模式异常
    if is_structuring(tx):
        score += 40
    # PEP 关联
    if customer.is_pep:
        score += 20
    return score  # >阈值 → 触发 SAR
```

### Step 5: SAR 生成与上报

- 生成可疑交易报告（Suspicious Activity Report）
- 提交至合规部门
- 保留审计日志（至少 5 年）

## 工具配置

- **web**: 查询制裁数据库、监管机构接口
- **terminal**: Python 实时计算 + 规则引擎
- **file**: 读取交易数据、输出 SAR 报告

## Pitfalls

1. 假阳性过高导致警报疲劳
2. 制裁名单更新时差
3. 加密货币交易盲点
4. 隐私法规限制信息共享

## 验证方法

- 规则命中率在合理区间（1-5%）
- 每条警报有完整调查链
- SAR 上报及时（24-48h 内）
- 合规官签字确认
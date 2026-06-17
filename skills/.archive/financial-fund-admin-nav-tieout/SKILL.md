# NAV Tie-out · 基金净值对齐

## 基本信息

- **Skill Name**: financial-fund-admin-nav-tieout
- **Description**: 基金净值（NAV）核对，验证基金资产净值与托管行/估值系统数据一致性
- **Trigger Keywords**: `nav tieout`, `nav`, `净值核对`, `基金净值`, `fund valuation`
- **Category**: fund-admin

## 核心步骤

### Step 1: 数据采集

- 通过 `web` 获取基金估值系统导出数据
- 通过 `file` 读取托管行提供的 NAV 报告
- 通过 `terminal` 加载 pandas DataFrame

### Step 2: NAV 计算公式

```
基金净值（NAV）= (总资产 - 总负债) / 份额总数

其中：
- 总资产 = 股票持仓市值 + 债券公允价值 + 现金及等价物 + 应收款项
- 总负债 = 应付账款 + 借款 + 应付税费 + 其他应付款
- 份额总数 = 发起人份额 + 投资人份额（含流动性限制）
```

### Step 3: 逐行对账

| 字段 | 估值系统 | 托管行 | 差异容差 |
|---|---|---|---|
| 股票持仓 | A | B | ±0.01% |
| 债券市值 | A | B | ±0.05% |
| 现金 | A | B | ±0 |
| NAV/份额 | A | B | ±0.001 |

### Step 4: 差异处理

- 百分比差异 > 阈值 → 标记为 Break
- 绝对金额差异 > 容差 → 发起调查
- 生成 `NAV Reconciliation Report`

## 工具配置

- **web**: 获取估值系统数据
- **terminal**: Python 计算引擎（pandas/numpy）
- **file**: 读取托管行 Excel、输出 NAV 报告

## Pitfalls

1. 估值方法不一致（收盘价 vs 收盘均价的差异）
2. 汇率折算时点不同
3. 非流动性资产定价困难
4. 期货/期权标记至结算日

## 验证方法

- NAV 百分比差异 < 0.1%
- 资产负载表平衡（总资产 = 总负债 + 净资产）
- 份额数据交叉验证
# Break Trace · 账目差异溯源

## 基本信息

- **Skill Name**: financial-fund-admin-break-trace
- **Description**: 对账差异溯源，追踪差异根因至原始凭证/交易节点
- **Trigger Keywords**: `break trace`, `差异溯源`, `break investigation`, `账目差异`, `追账`
- **Category**: fund-admin

## 核心步骤

### Step 1: 接收差异清单

- 读取 GL Recon 输出的 `break list`（CSV/Excel）
- 解析差异类型：金额差异、方向差异、缺失条目

### Step 2: 反向追溯

```
追溯路径：
Transaction ID → Journal Entry → Source Document → Counterparty → Booking Agent
```

### Step 3: 差异分类

| 类型 | 描述 | 典型根因 |
|---|---|---|
| Timing | 时间性差异 | 跨期录入、递延确认 |
| Value | 数值性差异 | 汇率换算、四舍五入 |
| Cut-off | 截断差异 | 报表日未达账项 |
| Entry Error | 录入错误 | 金额/方向录入错误 |
| System | 系统性差异 | 接口丢包、转换失误 |

### Step 4: 输出调查报告

- 差异清单 + 根因分析 + 修复建议
- 提交审批流（通过/争议/待调）

## 工具配置

- **web**: 查询交易平台数据源
- **terminal**: Python 数据处理 + 图数据库遍历
- **file**: 读取历史凭证、输出调查报告

## Pitfalls

1. 跨系统数据不一致（多数据源交叉验证）
2. 根因多样性（需穷举可能）
3. 凭证丢失（需标记待补）

## 验证方法

- 每条差异有明确根因结论
- 修复建议可执行
- 审计跟踪链完整
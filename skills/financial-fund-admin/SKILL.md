---
name: financial-fund-admin
description: 基金行政管理工作台 — 覆盖 GL 总账对账、账目差异溯源、月结流程、基金净值（NAV）核对四大模块，支持基金管理日常运营。
version: 0.1
owner: hermes-finance
tags: [fund-admin, gl-recon, break-trace, month-end-close, nav-tieout, accounting, reconciliation]
created: 2026-06-15
trigger: 当主人要求"GL对账"、"差异溯源"、"月结"、"NAV核对"时自动激活
---

# Financial Fund Admin · 基金行政管理工作台

## 核心定位

统一的基金行政管理工作台，覆盖 GL 总账对账、账目差异溯源、月结流程、基金净值（NAV）核对四大模块，支持基金管理日常运营。

---

## 模块菜单

| 模块 | Skill 章节 | 适用触发词 |
|------|-----------|-----------|
| GL 总账对账 | [§GL 总账对账](#gl-总账对账) | `gl recon`、`总账对账`、`科目余额核对` |
| 账目差异溯源 | [§账目差异溯源](#账目差异溯源) | `差异溯源`、`break trace`、`break investigation` |
| 月结流程 | [§月结流程](#月结流程) | `month end close`、`月结`、`月末结账` |
| 基金净值核对 | [§基金净值核对](#基金净值核对) | `nav tieout`、`净值核对`、`fund valuation` |

---

## GL 总账对账

### 触发关键词
`gl recon`, `gl-recon`, `ledger reconciliation`, `总账对账`, `科目余额核对`

### 核心步骤
**Step 1: 数据采集**
- 通过 `web` 获取 GL 主账数据（科目余额表）
- 通过 `file` 读取子账/辅助账导出文件（Excel/CSV）
- 通过 `terminal` 执行 Python 脚本加载数据

**Step 2: 自动差异检测**
```
差异类型：
1. 金额差异（Amount Break）：|GL余额 - 子账余额| > 阈值（默认 0.01）
2. 方向差异（Direction Break）：GL借方 vs 子账贷方
3. 缺失条目（Missing Item）：子账有记录但GL无匹配
4. 重复条目（Duplicate）：同一交易在GL出现多次
```

核心检测逻辑（Python）：
```python
def detect_breaks(gl_df, sub_df, threshold=0.01):
    merged = gl_df.merge(sub_df, on=['account_id','period'], how='outer', indicator=True)
    diff = abs(merged['gl_balance'] - merged['sub_balance'])
    breaks = merged[diff > threshold].copy()
    breaks['break_type'] = breaks['_merge'].map({
        'left_only': 'GL_ONLY',
        'right_only': 'SUB_ONLY',
        'both': 'AMOUNT_MISMATCH'
    })
    return breaks
```

**Step 3: 生成调节表** — 按科目分组，标记未清项（Open Items），输出 CSV/Excel
**Step 4: 差异溯源** — 追溯至原始凭证号，识别差异产生环节

### Pitfalls
1. 币种不一致导致假差异（需统一折算）
2. 日期区间不匹配（对账周期需对齐）
3. 科目层级汇总导致重复计算
4. 历史数据截断丢失

### Verification
- 调节表 Total = 0（借贷方平衡）
- 输出文件行数与差异数一致
- 人工复核关键科目（银行、应收、应付）

---

## 账目差异溯源

### 触发关键词
`break trace`, `差异溯源`, `break investigation`, `账目差异`, `追账`

### 核心步骤
**Step 1: 接收差异清单**
- 读取 GL Recon 输出的 `break list`（CSV/Excel）
- 解析差异类型：金额差异、方向差异、缺失条目

**Step 2: 反向追溯**
```
追溯路径：
Transaction ID → Journal Entry → Source Document → Counterparty → Booking Agent
```

**Step 3: 差异分类**
| 类型 | 描述 | 典型根因 |
|---|---|---|
| Timing | 时间性差异 | 跨期录入、递延确认 |
| Value | 数值性差异 | 汇率换算、四舍五入 |
| Cut-off | 截断差异 | 报表日未达账项 |
| Entry Error | 录入错误 | 金额/方向录入错误 |
| System | 系统性差异 | 接口丢包、转换失误 |

**Step 4: 输出调查报告** — 差异清单 + 根因分析 + 修复建议，提交审批流

### Pitfalls
1. 跨系统数据不一致（多数据源交叉验证）
2. 根因多样性（需穷举可能）
3. 凭证丢失（需标记待补）

### Verification
- 每条差异有明确根因结论
- 修复建议可执行
- 审计跟踪链完整

---

## 月结流程

### 触发关键词
`month end close`, `month-end`, `月结`, `月末结账`, `month close`

### 核心步骤
**Step 1: 预结检查（Pre-Close）**
- 验证所有日记账已过账
- 银行调节表完成
- 未清项清理至合理水平

**Step 2: 应计处理（Accruals）**
```
标准应计项：
1. 利息应计：债券应收利息、贷款利息
2. 费用应计：管理费、托管费
3. 税费用计：增值税、企业所得税
4. 薪酬应计：工资、奖金
```

**Step 3: Roll-Forward（余额结转）**
- 将期末余额结转至下期期初
- 验证：期初 + 本期增减 = 期末
- 更新科目余额表

**Step 4: 差异分析** — 与预算/预测对比，与上期同期对比（YoY），重大差异标注并解释

**Step 5: 月结报告**
```
月结报告内容：
1. 试算表（Trial Balance）
2. 银行调节汇总
3. 关键科目变动分析
4. 未清项清单
5. 应计调整汇总
6. 结账状态确认
```

### Pitfalls
1. 跨期调整未完全释放
2. 关联方交易未抵消
3. 汇率使用错误时点
4. 隐藏透支未处理

### Verification
- 试算表借贷平衡
- 所有科目余额合理
- 无异常负余额（除现金）
- 月结里程碑完成签字确认

---

## 基金净值核对

### 触发关键词
`nav tieout`, `nav`, `净值核对`, `基金净值`, `fund valuation`

### 核心步骤
**Step 1: 数据采集**
- 通过 `web` 获取基金估值系统导出数据
- 通过 `file` 读取托管行提供的 NAV 报告
- 通过 `terminal` 加载 pandas DataFrame

**Step 2: NAV 计算公式**
```
基金净值（NAV）= (总资产 - 总负债) / 份额总数

其中：
- 总资产 = 股票持仓市值 + 债券公允价值 + 现金及等价物 + 应收款项
- 总负债 = 应付账款 + 借款 + 应付税费 + 其他应付款
- 份额总数 = 发起人份额 + 投资人份额（含流动性限制）
```

**Step 3: 逐行对账**
| 字段 | 估值系统 | 托管行 | 差异容差 |
|---|---|---|---|
| 股票持仓 | A | B | ±0.01% |
| 债券市值 | A | B | ±0.05% |
| 现金 | A | B | ±0 |
| NAV/份额 | A | B | ±0.001 |

**Step 4: 差异处理**
- 百分比差异 > 阈值 → 标记为 Break
- 绝对金额差异 > 容差 → 发起调查
- 生成 `NAV Reconciliation Report`

### Pitfalls
1. 估值方法不一致（收盘价 vs 收盘均价的差异）
2. 汇率折算时点不同
3. 非流动性资产定价困难
4. 期货/期权标记至结算日

### Verification
- NAV 百分比差异 < 0.1%
- 资产负载表平衡（总资产 = 总负债 + 净资产）
- 份额数据交叉验证
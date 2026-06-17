# Month-End Close · 月结流程

## 基本信息

- **Skill Name**: financial-fund-admin-month-end-close
- **Description**: 标准月结流程，支持应计、roll-forward、差异分析，生成月结报告
- **Trigger Keywords**: `month end close`, `month-end`, `月结`, `月末结账`, `month close`
- **Category**: fund-admin

## 核心步骤

### Step 1: 预结检查（Pre-Close）

- 验证所有日记账已过账
- 银行调节表完成
- 未清项清理至合理水平

### Step 2: 应计处理（Accruals）

```
标准应计项：
1. 利息应计：债券应收利息、贷款利息
2. 费用应计：管理费、托管费
3. 税费用计：增值税、企业所得税
4. 薪酬应计：工资、奖金
```

### Step 3: Roll-Forward（余额结转）

- 将期末余额结转至下期期初
- 验证：期初 + 本期增减 = 期末
- 更新科目余额表

### Step 4: 差异分析

- 与预算/预测对比
- 与上期同期对比（YoY）
- 重大差异标注并解释

### Step 5: 月结报告

```
月结报告内容：
1. 试算表（Trial Balance）
2. 银行调节汇总
3. 关键科目变动分析
4. 未清项清单
5. 应计调整汇总
6. 结账状态确认
```

## 工具配置

- **web**: 获取财务系统数据
- **terminal**: Python 计算 + Excel 自动化
- **file**: 读取科目余额表、输出月结报告

## Pitfalls

1. 跨期调整未完全释放
2. 关联方交易未抵消
3. 汇率使用错误时点
4. 隐藏透支未处理

## 验证方法

- 试算表借贷平衡
- 所有科目余额合理
- 无异常负余额（除现金）
- 月结里程碑完成签字确认
# GL Recon · 总账对账

## 基本信息

- **Skill Name**: financial-fund-admin-gl-recon
- **Description**: 总账（General Ledger）对账，发现科目余额与子账/辅助账差异，生成调节表
- **Trigger Keywords**: `gl recon`, `gl-recon`, `ledger reconciliation`, `总账对账`, `科目余额核对`
- **Category**: fund-admin

## 核心步骤

### Step 1: 数据采集

- 通过 `web` 获取 GL 主账数据（科目余额表）
- 通过 `file` 读取子账/辅助账导出文件（Excel/CSV）
- 通过 `terminal` 执行 Python 脚本加载数据

### Step 2: 自动差异检测

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
    # Join on transaction_id / account_id
    merged = gl_df.merge(sub_df, on=['account_id','period'], how='outer', indicator=True)
    
    # 金额差异
    diff = abs(merged['gl_balance'] - merged['sub_balance'])
    breaks = merged[diff > threshold].copy()
    
    # 标记差异类型
    breaks['break_type'] = breaks['_merge'].map({
        'left_only': 'GL_ONLY',
        'right_only': 'SUB_ONLY', 
        'both': 'AMOUNT_MISMATCH'
    })
    return breaks
```

### Step 3: 生成调节表

- 按科目分组输出 `Reconciliation Report`
- 标记未清项（Open Items）
- 输出 CSV/Excel 格式

### Step 4: 差异溯源

- 追溯至原始凭证号
- 识别差异产生环节（录入/传输/计算）

## 工具配置

- **web**: 数据接口获取 GL 数据
- **terminal**: Python 计算引擎（pandas/openpyxl）
- **file**: 读取 Excel/CSV，输出调节表

## Pitfalls

1. 币种不一致导致假差异（需统一折算）
2. 日期区间不匹配（对账周期需对齐）
3. 科目层级汇总导致重复计算
4. 历史数据截断丢失

## 验证方法

- 调节表 Total = 0（借贷方平衡）
- 输出文件行数与差异数一致
- 人工复核关键科目（银行、应收、应付）
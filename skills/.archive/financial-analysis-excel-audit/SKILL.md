# skill: financial-analysis · excel-audit

> Excel 勾稽关系审计 · QC 检查

## 基本信息

- **name**: excel-audit
- **description**: 对 Excel 财务模型进行系统性审计，检查公式链接、环形引用、隐藏行列、假设与输出一致性，输出 QC 报告并标记潜在风险点。
- **trigger**: 当用户提及"Excel 审计"、"模型 QC"、"公式检查"、"勾稽关系"、"模型审查"时触发。

---

## 触发条件

- 用户上传 Excel 文件并要求审计
- 用户输入包含 excel-audit / 模型 QC / 勾稽关系 / formula check / model review
- 分析师提交模型初稿后要求交叉复核

---

## 执行步骤

### Step 1 · 接收并打开文件

1. 接收用户上传的 .xlsx / .xlsm 文件。
2. 使用 Python（openpyxl）读取文件结构：
   - Sheet 列表
   - 每 Sheet 行/列数
   - 命名区域（Named Ranges）
   - 关键链接（外部引用）

### Step 2 · 审计公式完整性

1. 遍历所有单元格，识别：
   - 公式类型：`=IF`, `=SUM`, `=VLOOKUP`, `=INDEX/MATCH`, `=XIRR`, `=NPV`
   - 环形引用（circular references）
   - 跨 Sheet 引用（外部链接）
   - 硬编码常量（应作为假设输入而非写死）
2. 检查关键钩稽：
   - **三张表联动**：Income Statement 净利润 → Balance Sheet 留存收益 → Cash Flow Statement 期初现金
   - **Balance Sheet 平衡**：Assets = Liabilities + Equity（误差容忍 ±1）
   - **EV 勾稽**：Market Cap + Net Debt = Enterprise Value

### Step 3 · 检查假设区与输出区隔离

1. 识别假设输入区（Assumptions / Inputs）：
   - 收入增速、WACC、Terminal Growth、EBITDA Margin 等
   - 标注为"输入项"（硬编码数字）
2. 识别输出区（Outputs / Valuation）：
   - IRR、NPV、每股价值、EV/EBITDA 倍数
3. 确认假设区变动能正确传导至输出区（无断层）。

### Step 4 · 标记异常与风险点

| 风险类型 | 检查逻辑 |
|---|---|
| 环形引用 | 公式 A 引用 B，B 引用 A |
| 除零错误 | 分母为零或为空 |
| 硬编码假设 | 数值写死在公式格而非假设输入格 |
| 缺失链接 | 空白格但相邻格有公式（可能遗漏公式） |
| 口径不一致 | 不同 Sheet 使用不同财年或 TTM 定义 |
| 敏感度缺失 | 关键输出缺少敏感性分析表 |

### Step 5 · 生成 QC 报告

输出 Markdown 格式报告，包含：

```
## Excel Audit Report

### 文件信息
- 文件名: xxx.xlsx
- Sheets: 3（Income Statement, Balance Sheet, Cash Flow）
- 公式总数: xxx | 硬编码: xxx

### 风险摘要
| # | 位置 | 类型 | 描述 | 严重性 |
|---|------|------|------|--------|
| 1 | Sheet1!C25 | 环形引用 | 与 C30 互引 | 🔴 高 |
| 2 | Assumptions!D12 | 硬编码 | WACC 应为输入格 | 🟡 中 |

### 勾稽验证
- [✅] Balance Sheet 平衡（误差 ±1）
- [❌] EV 勾稽不一致（偏差 2%）
- [✅] 三张表联动正确

### 建议修复项
1. 将 Assumptions!D12 改为公式引用 WACC 输入格
2. 消除 Sheet2!E45 环形引用
...
```

---

## 工具说明

- 使用 `terminal` 执行 Python 脚本（openpyxl）进行文件解析和审计
- 如需实时协作，使用 Excel 插件（SMARTX 或 AuditXL）辅助

---

## 常见陷阱（pitfalls）

1. **只检查公式不检查假设**：模型可以公式自洽但假设本身不合理。
2. **忽略隐藏 Sheet**：敏感信息或历史版本藏在隐藏 Sheet 中。
3. **未测试假设变动传导**：只审静态模型，未验证假设改动后输出是否正确更新。
4. **轻信平衡检查通过**：BS 平衡不等于三张表联动正确（可能通过其他方式强行平衡）。
5. **未记录修改轨迹**：审计报告未标注修改建议来源，分析师无法复现。

---

## 验证方法（verification）

- [ ] 所有 Sheet 公式已遍历，无遗漏
- [ ] Balance Sheet 平衡误差在 ±1 以内
- [ ] 无环形引用（circular reference）存在
- [ ] 三张表联动关系验证通过
- [ ] QC 报告包含文件信息、风险摘要、修复建议
- [ ] 人工复核签字记录
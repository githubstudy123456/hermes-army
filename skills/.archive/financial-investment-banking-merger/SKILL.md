# Skill: Merger Model · 并购模型搭建

## 基本信息

| 字段 | 内容 |
|------|------|
| name | merger-model |
| description | 投资银行并购模型（Merger Model / LBO Model）搭建，支持合并双方 DCF、EPS accretion/dilution、Synergy 分析，输出 Excel 模型 |
| trigger | "搭建并购模型"、"LBO 模型"、"合并模型"、"EPS 分析" |
| category | investment-banking |
| toolsets | web, terminal |

---

## 工作流程（Steps）

### Step 1 · 确定模型类型与假设
- 明确交易类型：**并购模型**（Merger Model）还是 **LBO 模型**（Leveraged Buyout）
- 收集交易假设：
  - 收购价格 / EV
  - 股权比例 / 现金 vs 股票对价
  - 融资结构（债务/股权比例）
  - 折现率（WACC）
  - 协同效应（Cost Synergy + Revenue Synergy）

### Step 2 · 收集财务数据
- 通过 `web` 抓取标的公司及收购方公开财务数据（年报、季报）
- 使用 `terminal` 读取现有 Excel 模型（如有）
- 整理 LTM / NTM 关键财务指标

### Step 3 · 构建模型框架（Excel）

#### 3.1 合并双方历史财务数据
- 收入、EBITDA、净利润、资产负载表
- 计算历史增长率、利润率趋势

#### 3.2 交易假设（Deal Assumptions）
```
- Purchase Price / EV
- Equity Value
- Net Debt (at closing)
- Purchase Price Multiple (EV/EBITDA)
- Consideration Mix (Cash % / Stock %)
- Share price (for stock consideration)
```

#### 3.3 合并后财务预测（Pro Forma）
- 加总双方收入/成本（消除关联交易）
- 叠加协同效应（分年导入）
- 计算合并后 EBITDA、Net Income

#### 3.4 估值计算
- **DCF**：WACC 折现未来5至十年 FCF
- **EPS Accretion/Dilution**：合并后 EPS 变化率
- **LBO 退出分析**：IRR、MOM、MOIC

#### 3.5 敏感性分析（Sensitivity）
- 关键变量：WACC、Terminal Growth Rate、Synergy Amount
- 输出双轴敏感性矩阵

### Step 4 · 生成 Excel 文件
- 使用 `terminal` 执行 openpyxl/xlsxwriter 脚本
- 多 sheet 结构：Assumptions / Income Statement / Balance Sheet / DCF / Sensitivity / Summary
- 公式链接而非硬编码数值
- 添加关键指标颜色标注（红色=负面，绿色=正面）

### Step 5 · 模型 QC 与验证
- 交叉核对所有公式
- 确认 Balance Sheet 配平
- 验证 EPS accretion/dilution 计算逻辑
- 确认无具体投资建议

---

## 工具调用示例

```python
# 生成 Merger Model Excel（含多个 Sheet）
python3 << 'EOF'
import xlsxwriter

wb = xlsxwriter.Workbook("Merger_Model_v1.xlsx")

# Sheet 1: Deal Assumptions
ws1 = wb.add_worksheet("Deal_Assumptions")
headers = ["Parameter", "Value", "Unit"]
for col, h in enumerate(headers):
    ws1.write(0, col, h)
ws1.write(1, 0, "Purchase Price")
ws1.write(1, 1, "=1000")  # 示例值
ws1.write(1, 2, "USD mm")

# Sheet 2: Pro Forma Income Statement
ws2 = wb.add_worksheet("Pro_Forma_IS")
ws2.write(0, 0, "LTM Revenue")
ws2.write(0, 1, "=Deal_Assumptions!B1*0.5")  # 示例公式

# Sheet 3: DCF
ws3 = wb.add_worksheet("DCF")
ws3.write(0, 0, "WACC")
ws3.write(0, 1, "0.09")
ws3.write(1, 0, "Terminal Growth Rate")
ws3.write(1, 1, "0.025")

wb.close()
EOF
```

---

## 常见陷阱（Pitfalls）

1. **公式硬编码**：所有数值须由公式驱动，避免手动输入计算结果
2. **协同效应过于乐观**：Synergy 须分年导入，保守假设（75% realization）
3. **WACC 设置不合理**：参考可比公司 Unlevered Beta + Target D/E 结构
4. **Balance Sheet 不配平**：资产 = 负债 + 权益，须自动平衡
5. **忽略税务影响**：D&A 摊销、Goodwill 摊销须纳入模型
6. **退出假设不现实**：LBO 须验证 5 年内 IRR 是否符合基金回报要求

---

## 验证步骤（Verification）

- [ ] Balance Sheet 配平（资产 = 负债 + 权益）
- [ ] EPS accretion/dilution 计算逻辑正确
- [ ] DCF 终端价值公式无错误（Gordon Growth Model）
- [ ] 敏感性分析表格数值联动
- [ ] 无具体买卖建议语言
- [ ] 所有假设参数标注在 Assumptions sheet
- [ ] 模型可读性强，有注释说明关键假设
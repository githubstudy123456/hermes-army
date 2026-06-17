# Skill: CIM Draft · 机密信息备忘录起草

## 基本信息

| 字段 | 内容 |
|------|------|
| name | cim-draft |
| description | 投资银行 CIM（Confidential Information Memorandum）起草工具，输入公司概述/财务数据/行业背景，输出结构化备忘录草稿 |
| trigger | "起草 CIM"、"生成 Confidential Information Memorandum"、"撰写并购备忘录" |
| category | investment-banking |
| toolsets | web, terminal |

---

## 工作流程（Steps）

### Step 1 · 交易背景收集
- 明确标的方（Target）名称、所在行业、主营业务
- 通过 `web` 抓取公司官网、新闻稿、年报、监管文件
- 搜索近期同类交易（Precedent Transactions）价格区间

### Step 2 · 财务数据整理
- 调用 `terminal` 执行 Python 脚本，读取 Excel 财务模型
- 提取关键指标：收入/EBITDA/净利润/总资产/净负债
- 计算 EV/EBITDA、EV/Revenue 等估值倍数
- 如需可比公司（Comps），通过 `web` 抓取 Capital IQ / Bloomberg 数据

### Step 3 · 行业与竞争格局分析
- 通过 `web` 抓取行业报告、第三方研究（如 PitchBook、FactSet）
- 分析市场份额、主要竞争者、进入壁垒
- 整理行业关键趋势（增长驱动因素、监管环境）

### Step 4 · CIM 结构大纲生成
按投资银行标准 CIM 格式组织内容：

```
1. Executive Summary
2. Transaction Summary
3. Company Overview
4. Industry Overview
5. Financial Performance
6. Valuation Analysis
7. Investment Highlights / Competitive Advantages
8. Risk Factors
9. Appendix（财务模型、交易 Comparables）
```

### Step 5 · 输出 Word/PowerPoint
- 使用 `terminal` 调用 python-docx 生成 `.docx` 文件
- 或通过 python-pptx 生成配套 PPT 演示页
- 文件输出至工作目录，标注"草稿·需人工复核"

---

## 工具调用示例

```python
# 读取 Excel 财务数据
python3 << 'EOF'
import openpyxl
wb = openpyxl.load_workbook("target_model.xlsx", data_only=True)
ws = wb["Summary"]
for row in ws.iter_rows(values_only=True):
    print(row)
EOF
```

```python
# 生成 CIM Word 文档
python3 << 'EOF'
from docx import Document
doc = Document()
doc.add_heading("Confidential Information Memorandum", 0)
# ... 填充各章节
doc.save("CIM_Draft_v1.docx")
EOF
```

---

## 常见陷阱（Pitfalls）

1. **数据时效性**：财务数据须标注截止日期，避免使用超过12个月未经更新的数字
2. **估值倍数引用错误**：确保分子（EV）=市值+净负债，分母用 LTM EBITDA
3. **保密标注缺失**：所有草稿必须标注"CONFIDENTIAL — FOR DISCUSSION PURPOSES ONLY"
4. **竞争信息未经核实**：行业数据需交叉比对至少两个来源
5. **格式不一致**：表格、图表编号需与正文引用一致

---

## 验证步骤（Verification）

- [ ] 封面有公司名称、交易类型、日期、保密声明
- [ ] Executive Summary 不超过2页，核心投资亮点≥3条
- [ ] 估值部分列出至少3种方法（DCF、Comps、Precedents）
- [ ] 所有数据有来源标注（脚注或 Appendix）
- [ ] 无具体买卖建议或投资承诺语句
- [ ] 文档页眉含"CONFIDENTIAL"字样
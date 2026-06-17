# Skill: Teaser Builder · 交易概要（Teaser）制作

## 基本信息

| 字段 | 内容 |
|------|------|
| name | teaser-builder |
| description | 投资银行 Teaser（交易概要）快速生成工具，用于向潜在买家/投资人简要展示交易亮点，不含敏感财务细节 |
| trigger | "制作 Teaser"、"生成交易概要"、"创建保密备忘录封面" |
| category | investment-banking |
| toolsets | web, terminal |

---

## 工作流程（Steps）

### Step 1 · 收集交易公开信息
- 确认标的方名称、交易类型（出售/融资/合作）
- 通过 `web` 搜索公司近期新闻、行业地位、主营业务概述
- 确认交易是否公开（已公告/匿名求购）

### Step 2 · 提炼核心投资亮点
按优先级排列（不超过6条）：
1. 市场规模与增速
2. 行业地位（市占率、排名）
3. 核心财务指标（LTM 收入/EBITDA 范围）
4. 增长驱动因素
5. 独特竞争优势
6. 交易结构提示（股权/资产出售）

> **注意**：Teaser 不得包含具体 EBITDA 数字、EV、交易价格

### Step 3 · 行业概览
- 通过 `web` 抓取行业市场规模、增长率、主要趋势
- 整理行业主要参与者（不点名标的具体竞争对手）
- 引用权威来源（IMF、行业协会、头部投行研报）

### Step 4 · 生成 Teaser 文档
标准结构：

```
[Company Logo Area]
CONFIDENTIAL TEASER — [Company Name]
[Date]

1. Investment Highlights（投资亮点）
   - Bullet points（不超过6条）

2. Transaction Overview（交易概览）
   - 交易类型
   - 标的方所在地
   - 行业

3. Market Overview（市场概览）
   - 行业规模 + 增速
   - 行业趋势

4. Contact Information
   - 银行联系人（姓名、邮箱、电话）
```

### Step 5 · 输出 PowerPoint / PDF
- 使用 `terminal` 调用 python-pptx 生成单页或两页 Teaser PPT
- 通过 reportlab 或 fpdf 生成 PDF 版本
- 输出标注"STRICTLY CONFIDENTIAL — FOR DISCUSSION PURPOSES ONLY"

---

## 工具调用示例

```python
# 生成 Teaser PowerPoint
python3 << 'EOF'
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
title = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(1))
title.text_frame.text = "CONFIDENTIAL TEASER"
# ... 填充内容
prs.save("Teaser_v1.pptx")
EOF
```

---

## 常见陷阱（Pitfalls）

1. **泄露敏感数据**：严禁出现具体 EBITDA、EV、交易价格、利润率数字
2. **过度宣传**：避免使用"绝佳机会"、"不可错过"等主观措辞
3. **信息来源不明**：行业数据须标注来源（研究机构/投行研报）
4. **格式简陋**：Teaser 代表银行形象，字体/排版需专业
5. **联系人信息错误**：确保银行联系人邮箱、电话准确无误

---

## 验证步骤（Verification）

- [ ] 无具体 EBITDA、EV、交易价格、精确利润率数据
- [ ] 包含"STRICTLY CONFIDENTIAL"标注
- [ ] 投资亮点不超过6条，每条不超过2行
- [ ] 行业数据有来源脚注
- [ ] 联系人信息完整（姓名、机构、邮箱、电话）
- [ ] 输出格式为 PPT 或 PDF，外观专业
---
name: financial-investment-banking
description: 投资银行交易工作台 — 覆盖 CIM 起草、交易进度追踪、并购模型搭建、Teaser 制作四大模块，支持投行交易全生命周期。
version: 0.1
owner: hermes-finance
tags: [investment-banking, cim, deal-tracker, merger-model, lbo, teaser, m&a, transaction]
created: 2026-06-15
trigger: 当主人要求"起草CIM"、"交易追踪"、"并购模型"、"Teaser"时自动激活
---

# Financial Investment Banking · 投资银行交易工作台

## 核心定位

统一的投资银行交易工作台，覆盖 CIM 起草、交易进度追踪、并购模型搭建、Teaser 制作四大模块，支持投行交易全生命周期（从初步接触到交割）。

---

## 模块菜单

| 模块 | Skill 章节 | 适用触发词 |
|------|-----------|-----------|
| CIM 起草 | [§CIM 起草](#cim-起草) | `起草CIM`、`Confidential Information Memorandum`、`并购备忘录` |
| 交易进度追踪 | [§交易进度追踪](#交易进度追踪) | `追踪交易进度`、`deal tracker`、`交易待办清单` |
| 并购模型搭建 | [§并购模型搭建](#并购模型搭建) | `搭建并购模型`、`LBO模型`、`合并模型`、`EPS分析` |
| Teaser 制作 | [§Teaser 制作](#teaser-制作) | `制作Teaser`、`交易概要`、`保密备忘录封面` |

---

## CIM 起草

### 触发条件
"起草 CIM"、"生成 Confidential Information Memorandum"、"撰写并购备忘录"

### 执行步骤
**Step 1 · 交易背景收集**
- 明确标的方（Target）名称、所在行业、主营业务
- 通过 `web` 抓取公司官网、新闻稿、年报、监管文件
- 搜索近期同类交易（Precedent Transactions）价格区间

**Step 2 · 财务数据整理**
- 调用 `terminal` 执行 Python 脚本，读取 Excel 财务模型
- 提取关键指标：收入/EBITDA/净利润/总资产/净负债
- 计算 EV/EBITDA、EV/Revenue 等估值倍数

**Step 3 · 行业与竞争格局分析**
- 通过 `web` 抓取行业报告、第三方研究
- 分析市场份额、主要竞争者、进入壁垒

**Step 4 · CIM 结构大纲生成**
```
1. Executive Summary
2. Transaction Summary
3. Company Overview
4. Industry Overview
5. Financial Performance
6. Valuation Analysis
7. Investment Highlights / Competitive Advantages
8. Risk Factors
9. Appendix
```

**Step 5 · 输出 Word/PowerPoint**
- 使用 `terminal` 调用 python-docx 生成 `.docx`
- 或通过 python-pptx 生成配套 PPT
- 文件标注"草稿·需人工复核"

### Pitfalls
- 数据时效性：财务数据须标注截止日期
- 估值倍数引用错误：确保分子（EV）= 市值+净负债，分母用 LTM EBITDA
- 保密标注缺失：所有草稿必须标注"CONFIDENTIAL — FOR DISCUSSION PURPOSES ONLY"
- 竞争信息未经核实：行业数据需交叉比对至少两个来源

### Verification
- [ ] 封面有公司名称、交易类型、日期、保密声明
- [ ] Executive Summary 不超过2页，核心投资亮点≥3条
- [ ] 估值部分列出至少3种方法（DCF、Comps、Precedents）
- [ ] 所有数据有来源标注
- [ ] 文档页眉含"CONFIDENTIAL"字样

---

## 交易进度追踪

### 触发条件
"追踪交易进度"、"更新交易状态"、"管理 deal tracker"、"交易待办清单"

### 交易阶段标准定义
| 阶段 | 英文 | 状态 |
|------|------|------|
| 1 | Pre-Mandate / Pitch | 争取承揽阶段 |
| 2 | Mandate Awarded | 正式获委托 |
| 3 | NDA Signed | 保密协议签署 |
| 4 | Preliminary Materials Shared | 初步材料分发 |
| 5 | First Round Bid / LOI | 第一轮报价/意向书 |
| 6 | Due Diligence | 尽职调查 |
| 7 | Final Bid / SPA Negotiation | 最终报价/协议谈判 |
| 8 | Signing | 签约 |
| 9 | Regulatory Approval | 监管审批 |
| 10 | Closing | 交割 |

### 执行步骤
**Step 1 · 初始化交易档案**
- 创建交易档案编号（Deal Code）：格式 `[行业]-[年份]-[序号]`
- 收集基础信息：标的方名称、交易类型、交易规模、预计时间表、客户联系人

**Step 2 · 追踪里程碑与待办事项**
- 按阶段拆解关键里程碑（Milestones）
- 创建待办清单（To-Do Items）：任务描述、负责人、截止日期、优先级、完成状态

**Step 3 · 文档版本管理**
- 记录每份关键文档的版本历史
- 存储路径规范化：`/deals/[Deal_Code]/docs/[Document_Name]/`

**Step 4 · 生成进度报告**
- 按需生成 Deal Status Report（Excel）
- 标注"INTERNAL USE ONLY — STRICTLY CONFIDENTIAL"

### Pitfalls
- 阶段定义不统一：团队须使用统一的阶段定义
- 逾期事项未及时升级：标记为 Blocked 的事项须立即通知项目经理
- 敏感信息泄露：Tracker 须标注"CONFIDENTIAL"
- 更新不及时：每次交易会议后24小时内须更新 tracker

### Verification
- [ ] Deal Code 唯一，命名规范
- [ ] 所有10个阶段均有记录
- [ ] 待办清单包含负责人和截止日期
- [ ] 最近更新日期不超过7天

---

## 并购模型搭建

### 触发条件
"搭建并购模型"、"LBO 模型"、"合并模型"、"EPS 分析"

### 执行步骤
**Step 1 · 确定模型类型与假设**
- 明确交易类型：并购模型（Merger Model）还是 LBO 模型
- 收集交易假设：收购价格/EV、股权比例/现金 vs 股票对价、融资结构、WACC、协同效应

**Step 2 · 收集财务数据**
- 通过 `web` 抓取标的公司及收购方公开财务数据
- 使用 `terminal` 读取现有 Excel 模型

**Step 3 · 构建模型框架（Excel）**
- 合并双方历史财务数据
- 交易假设（Deal Assumptions）
- 合并后财务预测（Pro Forma）
- 估值计算：DCF、EPS Accretion/Dilution、LBO 退出分析
- 敏感性分析（Sensitivity）

**Step 4 · 生成 Excel 文件**
- 多 sheet 结构：Assumptions / Income Statement / Balance Sheet / DCF / Sensitivity / Summary
- 公式链接而非硬编码数值

### Pitfalls
1. 公式硬编码：所有数值须由公式驱动
2. 协同效应过于乐观：Synergy 须分年导入，保守假设（75% realization）
3. WACC 设置不合理：参考可比公司 Unlevered Beta + Target D/E 结构
4. Balance Sheet 不配平：资产 = 负债 + 权益
5. 忽略税务影响：D&A 摊销、Goodwill 摊销须纳入模型

### Verification
- [ ] Balance Sheet 配平
- [ ] EPS accretion/dilution 计算逻辑正确
- [ ] DCF 终端价值公式无错误
- [ ] 敏感性分析表格数值联动

---

## Teaser 制作

### 触发条件
"制作 Teaser"、"生成交易概要"、"创建保密备忘录封面"

### 执行步骤
**Step 1 · 收集交易公开信息**
- 确认标的方名称、交易类型（出售/融资/合作）
- 通过 `web` 搜索公司近期新闻、行业地位、主营业务概述

**Step 2 · 提炼核心投资亮点**（不超过6条）
1. 市场规模与增速
2. 行业地位（市占率、排名）
3. 核心财务指标（LTM 收入/EBITDA 范围）
4. 增长驱动因素
5. 独特竞争优势
6. 交易结构提示

> **注意**：Teaser 不得包含具体 EBITDA 数字、EV、交易价格

**Step 3 · 行业概览**
- 通过 `web` 抓取行业市场规模、增长率、主要趋势
- 整理行业主要参与者（不点名标的具体竞争对手）

**Step 4 · 生成 Teaser 文档**
```
[Company Logo Area]
CONFIDENTIAL TEASER — [Company Name]
[Date]

1. Investment Highlights
2. Transaction Overview
3. Market Overview
4. Contact Information
```

**Step 5 · 输出 PowerPoint / PDF**
- 使用 `terminal` 调用 python-pptx 生成 PPT
- 通过 reportlab 或 fpdf 生成 PDF 版本
- 输出标注"STRICTLY CONFIDENTIAL — FOR DISCUSSION PURPOSES ONLY"

### Pitfalls
1. 泄露敏感数据：严禁出现具体 EBITDA、EV、交易价格、利润率数字
2. 过度宣传：避免使用"绝佳机会"、"不可错过"等主观措辞
3. 信息来源不明：行业数据须标注来源
4. 格式简陋：Teaser 代表银行形象，字体/排版需专业

### Verification
- [ ] 无具体 EBITDA、EV、交易价格、精确利润率数据
- [ ] 包含"STRICTLY CONFIDENTIAL"标注
- [ ] 投资亮点不超过6条
- [ ] 行业数据有来源脚注
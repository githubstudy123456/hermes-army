# Skill: Deal Tracker · 交易进度管理

## 基本信息

| 字段 | 内容 |
|------|------|
| name | deal-tracker |
| description | 投资银行交易进度追踪工具，管理从初步接触到交割的全流程节点、待办事项、文档版本及各方联系人 |
| trigger | "追踪交易进度"、"更新交易状态"、"管理 deal tracker"、"交易待办清单" |
| category | investment-banking |
| toolsets | web, terminal |

---

## 工作流程（Steps）

### Step 1 · 初始化交易档案
- 创建交易档案编号（Deal Code）：格式 `[行业]-[年份]-[序号]`（如 `TMT-2026-001`）
- 收集基础信息：
  - 标的方名称、交易类型（出售/收购/融资）
  - 交易规模（粗略范围，不含精确价格）
  - 预计时间表（LOI / 尽调 / 签约 / 交割）
  - 客户联系人（银行内部 + 客户双方）

### Step 2 · 定义交易阶段（Deal Stages）
标准投行交易阶段：

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

### Step 3 · 追踪里程碑与待办事项
- 按阶段拆解关键里程碑（Milestones）
- 创建待办清单（To-Do Items）：
  - 任务描述、负责人、截止日期、优先级
  - 完成状态（Pending / In Progress / Done / Blocked）
- 通过 `terminal` 写入/更新 Excel 或 CSV tracker

### Step 4 · 文档版本管理
- 记录每份关键文档的版本历史：
  - 文档名称、版本号（v1/v2/draft/final）、上传日期、变更说明
- 存储路径规范化：`/deals/[Deal_Code]/docs/[Document_Name]/`

### Step 5 · 生成进度报告
- 按需生成 Deal Status Report（Excel）：
  - 当前阶段、整体进度百分比
  - 里程碑完成情况
  - 未完成待办 + 逾期事项
  - 各方联系人列表
- 标注"INTERNAL USE ONLY — STRICTLY CONFIDENTIAL"

### Step 6 · 监控与提醒
- 通过 `web` 监控公开信息（新闻、监管文件）捕捉交易动态
- 如发现重大更新（客户管理层变动、监管信号），标记并通知负责人

---

## 工具调用示例

```python
# 初始化/更新 Deal Tracker Excel
python3 << 'EOF'
import xlsxwriter
from datetime import datetime

wb = xlsxwriter.Workbook("Deal_Tracker_TMT-2026-001.xlsx")

# Sheet 1: Deal Overview
ws1 = wb.add_worksheet("Deal_Overview")
overview = [
    ["Deal Code", "TMT-2026-001"],
    ["Target", "[Target Name]"],
    ["Transaction Type", "M&A Sell-side"],
    ["Current Stage", "Due Diligence"],
    ["Banker", "[Banker Name]"],
    ["Last Updated", datetime.now().strftime("%Y-%m-%d")],
]
for i, (k, v) in enumerate(overview):
    ws1.write(i, 0, k)
    ws1.write(i, 1, v)

# Sheet 2: Milestones
ws2 = wb.add_worksheet("Milestones")
headers = ["Milestone", "Stage", "Status", "Due Date", "Owner"]
for col, h in enumerate(headers):
    ws2.write(0, col, h)
milestones = [
    ["NDA Executed", "3", "Done", "2026-01-15", "Legal"],
    ["LOI Submitted", "5", "Done", "2026-02-20", "[Banker]"],
    ["Data Room Opened", "6", "In Progress", "2026-03-01", "IT"],
    ["Final Bid Deadline", "7", "Pending", "2026-04-15", "[Banker]"],
    ["Signing", "8", "Pending", "2026-05-30", "Legal"],
    ["Closing", "10", "Pending", "2026-07-31", "All"],
]
for row, m in enumerate(milestones, 1):
    for col, val in enumerate(m):
        ws2.write(row, col, val)

# Sheet 3: To-Do List
ws3 = wb.add_worksheet("To_Do_List")
todo_headers = ["Task", "Priority", "Owner", "Due Date", "Status"]
for col, h in enumerate(todo_headers):
    ws3.write(0, col, h)
todos = [
    ["Prepare CIM final draft", "High", "[Banker]", "2026-03-10", "In Progress"],
    ["Update comps analysis", "Medium", "[Analyst]", "2026-03-12", "Pending"],
    ["Coordinate site visit", "High", "[Banker]", "2026-03-05", "Pending"],
]
for row, t in enumerate(todos, 1):
    for col, val in enumerate(t):
        ws3.write(row, col, val)

wb.close()
print("Deal tracker created: Deal_Tracker_TMT-2026-001.xlsx")
EOF
```

---

## 常见陷阱（Pitfalls）

1. **阶段定义不统一**：团队须使用统一的阶段定义，避免沟通歧义
2. **逾期事项未及时升级**：标记为 Blocked 的事项须立即通知项目经理
3. **敏感信息泄露**：Tracker 须标注"CONFIDENTIAL"，不得通过非安全渠道传输
4. **更新不及时**：每次交易会议后24小时内须更新 tracker
5. **文档版本混乱**：同一文档多个版本时，保留历史版本，新版本标注日期

---

## 验证步骤（Verification）

- [ ] Deal Code 唯一，命名规范
- [ ] 所有10个阶段均有记录（即使某些阶段不适用）
- [ ] 待办清单包含负责人和截止日期
- [ ] 文档版本记录完整，无版本丢失
- [ ] 最近更新日期不超过7天
- [ ] 无具体交易价格或敏感财务细节泄露
- [ ] 输出文件标注"CONFIDENTIAL"字样
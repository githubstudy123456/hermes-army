---
name: hermes-director
description: 爱马仕军团部门主管 Profile 批量创建 SOP — SOUL.md + config.yaml + cron job 三件套
version: 1.0.0
author: Hermes Agent
tags: [hermes, profile, department-director, active-monitoring, feishu, cron]
related_skills: [hermes-agent]
---

# hermes-director · 爱马仕军团部门主管创建 SOP

## 什么时候用

用户要求新建一个爱马仕军团部门主管 profile 时（hermes-xxx），执行这个 SOP。

## 完整工作流（3件套，缺一不可）

> **每个部门必须有 SOUL.md + config.yaml + toolsets 三件套。** toolsets 必须根据部门专业职责配置，不是通用工具堆砌。cron job 是可选的，只有当用户明确要求或部门职责涉及定时监测时才创建。

## Anthropic 三pillars标准（2026-06-14确立）：
1. **独立 soul** — 专职边界清晰，不越权
2. **专用工具链** — 只配本领域需要的工具，不是什么都干
3. **垂直工作流** — 只干本领域的事，不横向扩张

违反任意一条，该部门的专业性就不成立。

**实践验证（2026-06-14）：**
- 金融部（hermes-financial）按模板：7垂直领域（equity-research/financial-analysis/fund-admin/investment-banking/private-equity/wealth-management/operations）× 11专职Agent → 成功创建26个skills并注册
- 法律部（hermes-legal）按模板：9垂直领域（corporate/commercial/employment/ip/litigation/privacy/product/regulatory/ai-governance）× 各专职Agent → 成功创建21个skills并注册
- skills 目录结构：每个skill含 `SKILL.md` + `config.yaml`，放置 `~/.hermes/skills/` 下自动注册，无需手动添加到profile config
- 验证命令：`hermes skills list` 确认所有skills已识别（显示local/enabled状态）
- 批量创建用 `delegate_task` 并行分发，每个子任务负责一个垂直领域的多个skills

### Step 1 — 创建 Profile 目录和 SOUL.md

```bash
mkdir -p /home/ubuntu/.hermes/profiles/hermes-{name}/
```

创建 `SOUL.md`，内容结构：

```
# SOUL.md — 部门名称

你是**X部**，负责[一句话核心职责]。

## 核心职责

[具体工作范围，3-6条]

## 当前优先任务

1. [immediate next action]
2. ...

## 工作流程

1. 接收需求
2. [具体步骤]
3. 汇报 commander

## 常用工具（仅本部门专用，通用工具不写）

| 类别 | 工具 | 用途 |
|------|------|------|
|      |      |      |

## 重要原则

- 原则A
- 原则B

## 部门工具链（toolsets 配置）

> **Anthropic 三pillars标准：独立 soul + 专用工具链 + 垂直工作流。**
> 工具链必须与部门职责严格匹配，不是通用工具堆砌。

| 工具类型 | 配置 | 说明 |
|---------|------|------|
| 基础工具 | `terminal file browser web session_search` | 研究类部门通用 |
| 专业 skill | [待根据部门调研后补充] | 需调研 Anthropic 同领域官方 skill 后配置 |
| cron job | [按需] | 仅当部门有主动监测职责时创建 |

**调研顺序（专业部门必须先做）：**
1. 查 Anthropic 官方仓库（anthropics/financial-services、anthropics/claude-for-legal）
2. 列出该领域所有 agent + vertical-plugin + skill
3. 挑选与本部门职责最匹配的几个
4. 将选中的 skill name 填入 config.yaml 的 toolsets 字段
```

### Step 2 — 创建 config.yaml（toolsets 是核心）

从 `~/.hermes/profiles/hermes-dev/config.yaml` 复制，然后改以下字段：

```yaml
name: hermes-{name}
```

**toolsets 字段必须根据部门专业职责配置，不是通用工具堆砌：**

| 部门类型 | 核心 toolsets | 说明 |
|---------|--------------|------|
| **研究类**（political/economic/ai-lab/data-science/industry-research） | `terminal file browser web session_search` | 去掉 vision |
| **金融部**（hermes-financial） | `terminal file browser web session_search` | 加专业金融 skill（如 financial-data/sec-filing-reader） |
| **法务部**（hermes-legal） | `terminal file browser web session_search` | 加 legal-research/contract-analyzer |
| **技术支撑**（devops/security） | `terminal file browser web delegation` | 加 cronjob |
| **内容/战略**（content/marketing） | `terminal file browser vision` | 去 skills/session_search |
| **通用执行**（dev/pm/qa） | `terminal file browser delegation` | 默认配置 |

**Anthropic 金融部/法律部 toolsets 参考（2026-06-14）：**
- 金融部（financial-services）：11个专职 agent（pitch-agent/market-researcher/earnings-reviewer/model-builder 等）+ 7个垂直 skill bundles（equity-research/wealth-management/investment-banking 等）
- 法律部（claude-for-legal）：11个垂直领域（commercial-legal/corporate-legal/ip-legal/privacy-legal 等）

**如果该部门有专业职责，必须先调研同领域 Anthropic 官方 skill/agent，再决定 toolsets 组合。** 不能闭眼配通用工具。

```yaml
toolsets:
- hermes-cli
- messaging
- delegation
- terminal
- file
- skills
- browser
- vision
- web
- session_search
```

根据部门类型调整：
- **研究类**（political/economic/ai-lab/data-science/industry-research）：加 `cronjob`，去掉 `vision`
- **技术支撑**（devops/security）：加 `cronjob`
- **内容/战略**（content/marketing/legal/life）：去掉 `skills` 和 `session_search`，加 `vision`

** approvals.mode规则**：
- `auto` — 日常执行部门（默认）
- `manual` — 研究类部门（political/economic/industry-research 等）

---

### Step 3（可选）— 创建 Cron Job

仅当用户明确要求，或部门职责涉及定时主动监测时，才创建 cron job。

使用 `cronjob` 工具（action=create）：
- `name`: "hermes-{name} · 主动监测"
- `prompt`: 角色设定 + 监测来源 + 触发条件 + 推送格式 + 推送目标
- `schedule`: "every 30m"（默认，可调整）
- `deliver`: `feishu:oc_c6883cd907e4d226736d87ce9c6c6d79`（**必须是飞书群 ID，不得设为 origin**）
- `skills`: ["web-browse"]

---

## 指令缩写约定（重要）

当用户说"研究的我要123"或类似编号式指令时，**直接映射执行，不需要二次确认**：

| 用户指令 | 含义 |
|----------|------|
|研究的我要1 | AI Lab（hermes-ai-lab） |
|研究的我要2 | Data Science（hermes-data-science） |
|研究的我要3 | Industry Research（hermes-industry-research） |
|研究的我要123 | 研究类全部三个：AI Lab + Data Science + Industry Research |
|技术的我要23 | DevOps + Security |
|技术的我要123 | 全部技术部门：DevOps + Security + Platform Engineering |
|全部都要 | 所有已选部门 |

直接执行，不再说"你确认一下"或"对吗"。只有当指令模糊时才澄清。

---

## ⚠️ 关键工作流原则

### 先广后细（所有高管通用工作流）

**第一阶段（广）：收集所有输出**
1. 复述确认：用自己的话复述任务目标和交付标准
2. 拆解派发：给下属下达**具体可执行指令**（含明确交付物、格式、截止标准）
3. 等回报：不做预判，让每个 agent 充分输出
4. 汇总合并：收集所有产出，不删减，全部汇总

**第二阶段（细）：过滤与深化**
5. 专业判断：按下属专业领域过滤噪声、识别重点
6. 补充深化：对重要结论追问细节，让对应下属补充
7. 整合输出：形成有主次的完整产出，汇报 commander

> **原则：先让执行层充分表达，高管再做判断和过滤。**
> 此工作流适用于所有高管（COO/CFO/CIO/CLO/CTO），创建新高管 profile 时必须同步写入 SOUL.md。

### 方案沟通规则（commander 专用）

Commander 收到主人指令后：
1. **确认理解**：用自己的话复述主人意图，对有歧义的地方提问
2. **提出方案**：给出初步分工建议，说明为什么这样拆
3. **明确边界**：交付物的格式、粒度、截止标准
4. **等主人确认**：确认后再派发给下属高管

各高管收到指令后，同样要先复述确认再执行，不清楚就先问。

### 指令缩写约定

当用户说"研究的我要123"时，**直接映射执行，不需要二次确认**：

| 用户指令 | 含义 |
|----------|------|
|研究的我要1 | AI Lab（hermes-ai-lab） |
|研究的我要2 | Data Science（hermes-data-science） |
|研究的我要3 | Industry Research（hermes-industry-research） |
|研究的我要123 | 研究类全部三个 |
|技术的我要23 | DevOps + Security |
|技术的我要123 | 全部技术部门 |

直接执行，不再说"你确认一下"。只有当指令模糊时才澄清。

### 通用原则

**用户的新问题优先于未完成的任务。**

如果用户突然问了一个新问题（如"XX网站调研"），立即处理新问题，不要被之前会话中未完成的任务带跑。如果之前的工作很重要，先简短确认状态，再处理新问题，或者把之前的工作留到新会话。

判断标准：用户发了一条完全独立的消息，就是一个独立任务，不要跨任务传染。

## 目录结构

```
~/.hermes/profiles/hermes-{name}/
├── SOUL.md          # 使命、职责、触发条件、格式
├── config.yaml      # profile 配置
└── MEMORY.md        # 可选，部门私有记忆

~/.hermes/{name}-reports/   # 推送报告存档目录
```

## 推送目标（固定）

- 飞书群：`oc_c6883cd907e4d226736d87ce9c6c6d79`
- DM 主人（通过飞书 gateway）
- 本地存档：`~/.hermes/{name}-reports/`

## ⚠️ 开始前必读

**区分系统：hermes ≠ openclaw（龙虾军团）**

| 系统 | 根目录 | 成员 | 用途 |
|------|--------|------|------|
| Hermès | `~/.hermes/profiles/` | commander(CEO) + 4高管 + 研究部 + 4执行部门 + 技术支撑，共约24个profile | 爱马仕军团（主人直接管，CEO=commander） |
| OpenClaw | `~/.openclaw/agents/` | lobster-ceo/cfo/dev/pm/qa/content/marketing/fullstack + main | 龙虾军团（独立运作） |

**任何架构汇报、profile 新建、cron job 操作前，必须先确认是哪套系统。混用会严重误导主人。**

---

## SOUL.md 结构规范（2026-06-11确立版）

每个部门的 SOUL.md 必须包含以下章节：

```
# SOUL.md — 部门名称
## 核心职责
## 工作范围
## 工作流程
## 当前优先任务
## 常用工具        ← 表格格式（见下方）
## 重要原则
```

**常用工具表格格式（已确立标准）：**

```markdown
## 常用工具

| 类别 | 工具 | 用途 |
|------|------|------|
|      |      |      |
```

- 每行一个工具，类别/工具/用途三列
- 只写该部门**独有**的工具，通用项（terminal/file/browser/delegation 等）不写
- 工具名称具体到工具名或 skill 名（如 `Playwright`、`SlowMist Agent Security`、`Python(pandas)`）
- 最后一个工具行后无需空行，直接接下一节

**Skills 章节已废除**——专业硬技能直接写入常用工具表格，无需单独章节。

**审批级别规则：**
- `auto` — 技术/执行类部门（devops/security/product/marketing 等）
- `manual` — 研究类部门（political/economic/ai-lab/data-science/industry-research/advisor/legal 等），5级审批过滤

## 已知陷阱

1. **cron job 内容要用 cronjob 工具创建**，不要手动写 shell 脚本
2. **job ID 要记入 memory**，方便后续更新/删除
3. **推送格式必须固定**，每次都一样，方便主人快速识别
4. **触发条件要具体**（如"上证涨跌超2%"），不要模糊（"市场大波动"）
5. **禁止事项必须列**，防止部门"越界"
6. **⚠️ deliver 目标必须设为飞书群 ID**：`oc_c6883cd907e4d226736d87ce9c6c6d79`（每日订阅群）。设为 `origin` 会推回 DM 而非群，且不容易被发现——**每次创建或更新 job 后必须验证 deliver 字段**
7. **hermes 和 openclaw 是两套独立系统**，绝不能混为一谈。汇报架构时先确认系统归属
8. **⚠️ 用户新问题优先于未完成任务**：用户发一条独立消息时，立即处理新问题，不要被之前未完成的任务带跑
9. **⚠️ 上下文传染**：如果正在处理 A 任务时用户突然问 B，先简短确认 A 状态，再处理 B，或者把 A 留到新会话

## 已创建的部门（截至2026-06-17）

> **Toolsets 列标注该部门专属配置（不是通用堆砌）。** 专业部门必须调研 Anthropic 同领域官方 skill/agent 后再配置。

### 决策层（2026-06-17调整）

> **重要架构变更（2026-06-17）：** hermes-ceo 已撤销（职责并入 commander），hermes-cmo 已撤销（职责重新分配）。最终架构：commander(CEO) + COO + CFO + CIO + CLO + CTO。

| 部门 | 类型 | SOUL+Config | 说明 |
|------|------|-------------|------|
| commander | 决策/CEO | ✓ | 总指挥兼 CEO，统领全军团，只做：拆解任务、派发部门、跟踪进度、汇总汇报 |
| hermes-coo | 高管 | ✓ | 首席运营官（2026-06-17新建） |
| hermes-cfo | 高管 | ✓ | 首席财务官（2026-06-17新建） |
| hermes-cio | 高管 | ✓ | 首席信息官（2026-06-17新建，掌馆 collector/data-science/ai-lab） |
| hermes-clo | 高管 | ✓ | 首席法务官，仅管法律合规（2026-06-17新建） |
| hermes-cto | 高管 | ✓ | 首席技术官（2026-06-17新建） |

### 执行层

| 部门 | 类型 | SOUL+Config | toolsets | Cron Job |
|------|------|-------------|---------|---------|
| hermes-content | 执行 | ✓ | | |
| hermes-marketing | 执行 | ✓ | | |
| hermes-pm | 执行 | ✓ | | |
| hermes-qa | 执行 | ✓ | | |
| hermes-fullstack | 执行 | ✓ | | |

### 研究层

> **2026-06-17 调整：** hermes-collector / hermes-data-science / hermes-ai-lab 划归 CIO 管辖。其余研究部门（political/economic/market/life/advisor/reviewer/industry-research）留在研究层，向 commander 汇报。

| 部门 | 类型 | SOUL+Config | toolsets | Cron Job |
|------|------|-------------|---------|---------|
| hermes-political | 研究 | ✓ | terminal file browser web session_search | `27433eb6e582` |
| hermes-economic | 研究 | ✓ | terminal file browser web session_search | |
| hermes-market | 研究 | ✓ | terminal file browser web session_search | |
| hermes-life | 研究 | ✓ | terminal file browser web session_search | |
| hermes-advisor | 研究 | ✓ | | |
| hermes-reviewer | 审核 | ✓ | | |
| hermes-industry-research | 研究 | ✓ | terminal file browser web session_search | |

### 技术支撑层

| 部门 | 类型 | SOUL+Config | toolsets | Cron Job |
|------|------|-------------|---------|---------|
| hermes-architect | 技术 | ✓ | | |
| hermes-dev | 技术 | ✓ | | |
| hermes-dev-frontend | 技术 | ✓ | | |
| hermes-dev-backend | 技术 | ✓ | | |
| hermes-dev-3d | 技术 | ✓ | | |
| hermes-test | 技术 | ✓ | | |
| hermes-devops | 技术 | ✓ | terminal file browser web delegation | `74d5513aa5c8` |
| hermes-security | 技术 | ✓ | terminal file browser web delegation | `a03aceab37d6` |

### CIO 直辖（信息与AI）

| 部门 | 类型 | SOUL+Config | toolsets |
|------|------|-------------|---------|
| hermes-collector | 信息收集 | ✓ | web browser terminal file |
| hermes-data-science | 数据科学 | ✓ | terminal file browser web session_search |
| hermes-ai-lab | AI研发 | ✓ | terminal file browser web session_search |

### 汇报架构（2026-06-17确立，方案B：commander = CEO）

```
commander（CEO）— 只做：拆解任务、派发部门、跟踪进度、汇总汇报
├── COO  → hermes-content / hermes-marketing / hermes-pm / hermes-qa
├── CFO  → hermes-financial
├── CIO  → hermes-collector / hermes-data-science / hermes-ai-lab
├── CLO  → hermes-legal
└── CTO  → hermes-architect / hermes-fullstack / hermes-dev-frontend / hermes-dev-backend / hermes-dev-3d / hermes-test / hermes-devops / hermes-security
```

> ⚠️ **最新架构（2026-06-17）**：见 `references/architecture-2026-06-17.md`，包含完整架构图、高管边界、Profile 创建检查清单、hermes-collector 定位说明。
>
> ⚠️ **多Agent协作工作台（2026-06-17）**：见 `references/multi-agent-workflow-refs.md`，GitHub高星项目调研结果，含 agency-orchestrator YAML workflow 格式、Task Bus 模式、三人组审核 pipeline。


> Skills 列标注的为该部门专属 SKILL.md，不在全局 skills 列表中重复。

---

## 部门协作工作台 · 多Agent编排模式（2026-06-17确立）

爱马仕军团四层架构（执行层→秘书→高管→CEO）天然支持多agent协作编排。以下是从 GitHub 高星项目提炼的最佳实践。

### 核心编排模式

**模式A：YAML Workflow（agency-orchestrator格式）**
参考 `jnMetaCode/agency-orchestrator` 的 department-collab workflow：

```yaml
name: "CEO 组织架构协作"
steps:
  - id: ceo_analyze          # 第一层：CEO分析决策
    role: "project-management/project-manager-senior"
    task: |
      分析需求，决定调动哪些部门...
    output: ceo_decision

  - id: engineering_dept      # 第二层：部门并行（条件触发）
    role: "engineering/engineering-software-architect"
    task: |
      你是工程部负责人。CEO 给了以下指示：
      {{ceo_decision}}
      ...
    depends_on: [ceo_analyze]
    condition: "{{ceo_decision}} contains 工程部"  # 只在涉及该部门时触发
    output: engineering_report

  - id: marketing_dept        # 另一部门并行
    role: "marketing/marketing-social-media-strategist"
    depends_on: [ceo_analyze]
    condition: "{{ceo_decision}} contains 市场部"
    output: marketing_report

  - id: ceo_decision_final    # 第三层：CEO汇总
    role: "support/support-executive-summary-generator"
    task: |
      综合所有部门报告做最终决策...
    depends_on: [engineering_dept, marketing_dept, ...]
    depends_on_mode: any_completed  # 全部或任意完成均可
```

**关键字段说明：**
- `condition`：条件触发，实现"只跑涉及的部门"——相关部门才启动
- `depends_on_mode: any_completed`：允许只完成部分部门（如 HR 不涉及时）
- `output`：该步骤的输出变量名，供后续步骤引用 `{{output_var}}`

**模式B：Task Bus（hermes-agent-control-room）**
参考 `shannhk/hermes-agent-control-room`：

```
Agent Control Room = side control plane（文档/规则/注册表）
Orchestrator       = 可选的前门 agent，负责分发和汇总
Specialists        = 各领域专职 Hermes agent
Task Bus           = 交接台（inbox/working/outbox/archive）
```

**模式C：Executor→Reviewer→Challenger（agent-team-plugin）**
每个任务跑三人组对抗审核：

```
Executor（执行）→ Reviewer（审核）→ Challenger（质疑）
                     ↓
              秘书层审核（只放行通过结果）
```

对应 Hermès 的：执行层（Executor）→ 秘书审核（Reviewer）→ 高管统筹（Challenger 判断方向）

### Hermès 协作工作台设计

```
主人指令 → commander 分析决策
    ↓
按 condition 路由到涉及的高管（COO/CFO/CIO/CLO/CTO）
    ↓
高管派发给执行层（先广后深）
    ↓
秘书严格审核（Executor→Reviewer 模式）
    ↓
高管汇总本部门报告
    ↓
commander 整合 → 输出完整决策文档
```

**协作工作台四要素：**
1. **统一入口**：commander 分析后路由分发，不涉及的部门不触发
2. **部门并行**：相关部门的执行层并行展开，互不阻塞
3. **严格审核**：秘书层逐条审核，不过关的打回重做
4. **汇总输出**：commander 收集所有报告，输出完整决策文档

### 相关GitHub项目

| 项目 | Stars | 用途 |
|------|-------|------|
| jnMetaCode/agency-orchestrator | 15k+ | YAML workflow 编排器，含部门协作模板 |
| jnMetaCode/agency-agents-zh | 15k+ | 216个专家角色，18个部门覆盖 |
| shannhk/hermes-agent-control-room | 588 | Hermes专用控制室+Task Bus模板 |
| ducdmdev/agent-team-plugin | ⭐⭐ | Executor→Reviewer→Challenger三人组 pipeline |
| johntimothybailey/skill-harbor | ⭐⭐ | 团队skill声明式治理引擎 |

---

## 快速提取网页表格数据的技巧

对复杂表格（大量行、分页），用 `browser_console` 直接跑 JS 比 snapshot/scroll 快：

```javascript
const rows = document.querySelectorAll('table tbody tr');
const data = [];
rows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length >= 7) {
    data.push({
      name: cells[2]?.textContent?.trim().replace(/\s+/g, ' '),
      marketCap: cells[4]?.textContent?.trim(),
      price: cells[5]?.textContent?.trim(),
      change24h: cells[7]?.textContent?.trim()
    });
  }
});
JSON.stringify(data);
```

提取后直接解析，比反复操作 DOM 快 5-10 倍。

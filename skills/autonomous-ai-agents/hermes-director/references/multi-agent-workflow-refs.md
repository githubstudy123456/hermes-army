# 多Agent协作工作流 · GitHub参考项目（2026-06-17）

## 核心发现

### agency-orchestrator ⭐15k — 最直接对标
**URL**: https://github.com/jnMetaCode/agency-orchestrator

YAML workflow 编排器，核心 workflow 格式：

```yaml
steps:
  - id: step_name
    role: "path/to/role-file"      # 从 agency-agents 角色库引用
    task: |                         # 完整任务描述，含 {{变量}} 插值
      ...
    output: output_var              # 供后续步骤引用
    depends_on: [prev_step_id]      # 依赖前置步骤
    condition: "{{var}} contains X" # 条件触发
    depends_on_mode: all_completed | any_completed
```

**关键 workflow 文件（department-collab/）：**
- `ceo-org-delegation.yaml` — CEO分析→部门并行→汇总决策
- `incident-response.yaml` — 故障分类→分流→复盘
- `hiring-pipeline.yaml` — 招聘流程

**安装**：`npm install -g agency-orchestrator`

### agency-agents-zh ⭐15k — 216个专家角色
**URL**: https://github.com/jnMetaCode/agency-agents-zh

18个部门覆盖，每个角色独立 SOUL.md + 工作流。工程/设计/营销/金融/法务/HR/游戏/供应链等。

**部门目录**：
```
engineering/   # 35个工程专家（安全/架构/前端/后端/DevOps/SRE...）
marketing/      # 社媒/SEO/内容/增长
product/        # 产品经理/数据分析
finance/        # 投资/财务分析
legal/          # 法律顾问
hr/             # 招聘/员工关系
design/         # UI/UX/品牌设计
...
```

### hermes-agent-control-room ⭐588 — Hermes专用
**URL**: https://github.com/shannhk/hermes-agent-control-room

专门给 Hermes Agent 用的控制室模板。核心理念：

```
one agent → direct specialists → orchestrator → automated agent team
```

配套 Task Bus 模式：`/srv/agent-bus`（inbox/working/outbox/archive）

**文件结构**：
- `SOUL.md`（身份）+ `AGENTS.md`（业务能力）+ `IDENTITY.md`（简介）
- 支持多 agent 协作编排

### agent-team-plugin ⭐⭐ — 三人组审核pipeline
**URL**: https://github.com/ducdmdev/agent-team-plugin

每个任务跑：`Executor → Reviewer → Challenger` 三人组对抗审核。直接对应 Hermès 秘书审核层。

### skill-harbor ⭐⭐ — 团队skill治理
**URL**: https://github.com/johntimothybailey/skill-harbor

用 `harbor-manifest.json` 声明式管理团队所有 skills 的同步分发。底层调用 `skillfish` + `skill-porter`。

---

## 搜索关键词备忘

```
multi-agent workflow team collaboration
agent orchestration workflow department
team workspace agent orchestration
agentic workflow collaboration space
hermes multi-agent orchestration
```
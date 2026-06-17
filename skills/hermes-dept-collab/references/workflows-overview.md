# Hermès 协作工作流速查

## 五套工作流总览

| 工作流 | 触发场景 | 阶段数 | 核心节点 |
|--------|----------|--------|----------|
| `ceo-org-delegation.yaml` | 任何跨部门复杂指令 | 4 | 意图分析 → 各部门执行 → 秘书审核 → Commander决策 |
| `incident-response.yaml` | 故障/安全/合规事件 | 4 | 分类定级 → 紧急处理 → 秘书审核 → 复盘 |
| `product-launch.yaml` | 新产品/功能发布 | 6 | 规划 → 准备 → 审批 → 发布 → 复盘 |
| `marketing-campaign.yaml` | 品牌/效果/私域/联名活动 | 5 | 策略 → 执行准备 → 审核 → 活动 → 复盘 |
| `code-review.yaml` | 代码合并请求 | 4 | 变更分析 → 多维审查 → 秘书审核 → 合并决策 |

## 共同行为规范

- **必须接活**：节点收到任务立即执行，不推活
- **做不了输出升级报告**（不是跳过）：写明问题 + 已尝试方案 + 需要什么支持
- **必须引用上游文档**：每个节点第一件事读 `input_doc` 并在产出中引用
- **秘书是强制门禁**：产出不经秘书审核不进入下一阶段
- **condition 控制激活**：只触发涉及的部门，无关节点不执行
- **升级报告直达**：不被中间层拦截，直接上报决策节点

## 文档命名规范

```
[任务名]/[部门]/[节点ID]_[类型]_[日期].md
例：coo_user_research_成果.md
    incident_clo_security_emergency_升级报告.md
```

## 升级报告模板

```markdown
# [节点ID] 升级报告

## 节点信息
- 节点ID：
- 负责人：
- 上游文档：

## 遇到的问题
-

## 已尝试的方案
-

## 需要什么支持
-
```

## 各工作流关键路径

### ceo-org-delegation（通用指令）
```
Commander意图分析
    ↓
COO执行用户研究 ─┐
CTO执行技术分析   ├─→ 各自秘书审核 ─┐
CIO执行数据/AI分析 │                │
CFO执行财务测算   │                ├──→ Commander汇总决策
CLO执行合规分析  ─┘                │
                          各高管汇报 ↗
```

### incident-response（故障）
```
CTO分类定级（P0/P1/P2/P3）
    ↓ 路由
后端 → cto/backend_emergency
前端 → cto/frontend_emergency
基础设施 → cto/infra_emergency
安全 → clo/security_emergency
合规 → clo/compliance_emergency
P0/P1额外 → coo/ops_impact（业务影响）
    ↓
秘书审核（cto/clo/coo各自）
    ↓
CTO复盘（时间线+根因+改进项）
```

### product-launch（产品上线）
```
COO产品规划
    ↓
CTO技术准备 ─┐
COO运营准备  ├─→ 各自秘书审核 ─┐
CIO数据准备  │               │
CLO法务准备  │               ├──→ CTO上线审批 ─→ 执行发布 ─→ COO复盘
CFO财务准备 ─┘               │
                          各高管汇报 ↗
```

### marketing-campaign（营销活动）
```
COO营销策略
    ↓
COO创意内容 ─┐
CTO技术支撑  ├─→ 各自秘书审核 ─┐
CIO数据追踪  │               │
CLO法务合规  │               ├──→ COO执行活动 ─→ COO复盘
CFO预算审批 ─┘               │
                          各高管汇报 ↗
```

### code-review（代码审查）
```
CTO变更分析
    ↓ 条件路由
必做：code_quality_review
条件：architecture_review（重构/新功能）
条件：security_review（安全/登录/支付）
条件：compliance_review（用户数据）
    ↓
cto-secretary审核CTO所有产出
clo-secretary审核合规产出
    ↓
CTO合并决策（批准/拒绝/需修改）
```

## 文件位置

```
~/.hermes/skills/hermes-dept-collab/
├── SKILL.md                              # 协作框架说明
├── workflows/
│   ├── dept-activation.yaml              # 入口路由
│   ├── ceo-org-delegation.yaml            # 通用指令分发
│   ├── incident-response.yaml             # 故障响应
│   ├── product-launch.yaml               # 产品上线
│   ├── marketing-campaign.yaml           # 营销活动
│   └── code-review.yaml                  # 代码审查
└── references/
    └── workflows-overview.md             # 本文件
```

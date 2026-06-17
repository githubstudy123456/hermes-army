# 龙虾军团完整流水线 — 每小时整点调度

## 核心流程

```
每小时的整点
  ↓
commander（调度中心）读取 TODO.md
  ↓
market → product → architect → dev(frontend/3d/backend) → test
  ↓
产品经理审查界面（UI 必须过 lobster-product）
  ↓
测试验收（lobster-test）
  ↓
更新 TODO.md + 写夜间日志
```

## 每小时调度规则

- **整点执行**：cron job `8ea3e57a3060`，schedule `0 0-7 * * *`（0点-7点每小时）
- **产品经理审查**：任何 UI 改动完成后，必须通过 delegate_task 调度 lobster-product 审查
- **审查不通过**：继续修，直到 product 满意为止
- **本地日志**：`/home/ubuntu/.hermes/army-workspace/04-开发实现/{项目}/night-dev-log-YYYYMMDD-HH.txt`

## 流水线各环节职责

| 环节 | profile | 职责 |
|------|---------|------|
| 调度 | commander | 读 TODO、分配任务、协调各方 |
| 市场 | lobster-market | 需求收集、竞品分析、技术趋势 |
| 产品 | lobster-product | PRD、界面设计、用户体验把关 |
| 架构 | lobster-architect | 技术方案、数据模型、API 设计 |
| 前端 | lobster-dev-frontend | UI/动画/交互（必须过 product） |
| 3D | lobster-dev-3d | Three.js/物理场景/渲染 |
| 后端 | lobster-dev-backend | API/数据层 |
| 测试 | lobster-test | 功能测试、性能测试、体验测试 |

## 界面审查规则（产品经理把关）

```
dev 完成 UI 改动
  → delegate_task → lobster-product 审查
  → product 通过？ 否 → 打回 dev 重修
  → product 通过？ 是 → 通知 commander
  → commander 调度 test 测试
  → test 通过 → 更新 TODO
```

## 文件位置

- 流水线定义：`/home/ubuntu/.hermes/army-workspace/物理平台开发流水线.md`
- 待办任务：`/home/ubuntu/.hermes/army-workspace/TODO.md`
- 开发工作区：`/home/ubuntu/.hermes/army-workspace/04-开发实现/{项目}/{角色}/`
- 夜间日志：`/home/ubuntu/.hermes/army-workspace/04-开发实现/{项目}/night-dev-log-*.txt`

## Cron Job 管理

创建：
```
cronjob action=create name=物理平台夜间自动开发 \
  schedule="0 0-7 * * *" \
  prompt="你是龙虾军团指挥官。每小时执行完整流水线..." \
  skills=["systematic-debugging", "task-closure-sop"] \
  deliver=local
```

删除：`cronjob action=remove job_id=XXX`

查看：`hermes cron list`

## 陷阱

1. **产品经理审查不可跳过**：UI 改动没有经过 lobster-product 确认，不算完成
2. **每小时整点调度**：不是整点不触发，触发后各角色并行执行
3. **夜间只开发不做决策**：遇到需要用户确认的问题，写入日志等待白天反馈
---
name: cron-audit
description: 对 Hermes Agent 所有 cron 定时任务进行系统性审计。检查任务状态、推送目标、是否接入部门工作流、是否有秘书审核门禁。输出分级问题报告和修复建议。
triggers:
  - "主人说'审核一下定时任务'"
  - "检查所有 cron 任务"
  - "审计定时任务"
  - 需要了解有哪些 cron 在跑时
---

# Cron 任务审计工作台

## 何时使用

- 主人要求"审核一下定时任务"
- 需要全面了解系统中有哪些自动化任务在跑
- 发现推送失败、内容异常，需要检查 cron 配置
- 每次大规模调整部门架构后，重新梳理任务归属

## 执行步骤

### 第一步：盘点任务清单

```bash
cronjob list
```

获取完整任务列表，记录：
- job_id / name / schedule
- last_run_at / last_status / last_delivery_error
- deliver 目标（feishu:xxx / weixin:xxx / local）
- skill 是否配置（影响任务质量）

### 第二步：分类

按职能将任务分为 6 类：

| 类别 | 说明 |
|------|------|
| 情报监控 | 政治/经济/金融/法律监控 |
| 技术运维 | DevOps/Security/AI Lab/Data Science |
| 内容运营 | 时尚/游戏/生活/活动/深圳 |
| 生活管理 | 学习/运动/提醒 |
| 飞书推送 | 日报/周报/月报/年报 |
| 系统运维 | 会话清理/微信监控/Trojan检测 |

### 第三步：检查状态

重点关注：
- `last_delivery_error` 非空 → 推送失败，需标记 P0
- `last_status` 非 ok → 执行异常
- `last_run_at` 距离现在过远 → 任务可能已停止

### 第四步：对照部门架构

检查每个任务是否：
1. 接入对应部门的 DAG 工作流
2. 有秘书审核门禁（secretary review）
3. 推送到正确的飞书群

**部门归属参考：**

| 任务类型 | 应归属部门 | 应有审核 |
|---------|-----------|---------|
| hermes-political | CLO | CLO-secretary 或 CRO |
| hermes-economic | CFO | CFO-secretary 或 CRO |
| hermes-legal | CLO | CLO-secretary |
| hermes-financial | CFO | CFO-secretary |
| DevOps/Security | CTO | CTO-secretary |
| AI Lab / Data Science | CIO | CIO-secretary |
| 时尚/游戏/活动 | COO | COO-secretary 或 CRO |
| 日报/周报/月报/年报 | CRO | CRO-secretary 终审 |

### 第五步：分级输出

按严重程度分三级：

**🔴 P0 — 立即修复**
- 推送失败反复重试
- 情报无部门审核路由
- 涉及主人核心权益的配置错误

**🟡 P1 — 尽快修复**
- 报告无秘书审核门禁
- delivery=local 但应有推送
- prompt 质量退化

**🟢 P2 — 可延后**
- 可归入更大工作流但未接入
- 重复功能可合并
- 可优化减少任务数量

### 第六步：输出报告

按以下格式输出：

```
## 📊 Cron 任务审计报告

### 分类总览
| 类别 | 数量 | 接入工作流 | 有秘书审核 |
|------|------|----------|-----------|

### 🔴 P0 问题
### 🟡 P1 问题
### 🟢 P2 问题

### 修复优先级表
| 优先级 | 任务名 | 问题 | 修复方式 |
```

## 陷阱

1. **不要只列问题** — 每个问题都要给出修复方向
2. **delivery_error=null 不代表成功** — 还要看 last_status
3. **delivery=local 不一定是错** — 可能是故意设计，先问主人
4. **WeChat 推送失败** — 不一定修得了，看主人意愿
5. **新建部门（如CRO）** — 执行层可能还是空的，不要假设它能工作

## 飞书群组 ID 对照（2026-06-17）

```
oc_c6883cd907e4d226736d87ce9c6c6d79  → 日报群
oc_605cb68f2814b7fef2336ae15b7982bd  → 周报群
oc_bd20e92437df496f958a38958d48b92a  → 月报群
oc_675ed9bc27aa367fdca299e332b8da1c  → 年报群（飞书新建群）
oc_08f6cb45cf9c2132e7ee86fd6fb5dec9 → Hermès 组织群
```

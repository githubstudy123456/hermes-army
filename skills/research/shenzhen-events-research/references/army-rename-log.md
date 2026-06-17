# 爱马仕军团更名记录 · 2026-06-09

## 背景
主人明确要求：lobster army → 爱马仕军团，profile 命名统一改 hermes。

## 执行操作

### 1. Profile 目录批量重命名
18个 profile 目录 `lobster-xxx` → `hermes-xxx`：
```
hermes-advisor, hermes-architect, hermes-ceo, hermes-cfo,
hermes-content, hermes-dev, hermes-dev-3d, hermes-dev-backend,
hermes-dev-frontend, hermes-fullstack, hermes-legal, hermes-life,
hermes-market, hermes-marketing, hermes-pm, hermes-product,
hermes-qa, hermes-test
```

### 2. 配置文件内容替换
替换 SOUL.md / config.yaml 中的：
- `lobster-` → `hermes-`
- `龙虾军团` → `爱马仕军团`

### 3. 关键文件同步更新
- `~/.hermes/knowledge_base.md`
- `~/.hermes/memories/USER.md`
- `~/.hermes/memories/MEMORY.md`
- `~/.hermes/memory/MEMORY.md`

### 4. 未改动（历史记录）
以下文件含 lobster 引用但**未改动**（历史产出/日志）：
- `~/.hermes/cron/output/*.md` — 定时任务历史输出
- `~/.hermes/army-workspace/产出/*.md` — 工作产出记录
- `~/.hermes/army-workspace/物理平台开发流水线.md` — 项目文档
- skills 中的 lobster-director 引用文件

## 新增部门
待建：
- `hermes-political` — 政治研究部
- `hermes-economic` — 经济研究部

主人需求：**主动监测 + 重大事件即时推送**，不等 cron。

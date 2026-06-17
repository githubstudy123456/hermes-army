# Commander 长期记忆

## 军团架构

### 五个总监（飞书群聊 ID 一律 oc_08f6cb45cf9c2132e7ee86fd6fb5dec9）

| 角色 | profile | 飞书 chat_id | 职责 |
|------|---------|-------------|------|
| commander | commander | oc_08f6cb45cf9c2132e7ee86fd6fb5dec9 | 任务发包/统筹/流水线调度 |
| market-director | market-director | oc_7bb2ded39340a42465a193458c9c467a | 市场调研/选品/竞品分析 |
| product-director | product-director | oc_f709b8e8cf4cd7eadb454ff02a06d731 | 产品设计/PRD/功能规划 |
| architect-director | architect-director | oc_3f86e98d17b137dea218eda6348f2249 | 架构设计/技术方案 |
| dev-director | dev-director | oc_84d991772f2bfcf5d699a37ae8308165 | 开发实现/协调三个子 Agent |
| test-director | test-director | oc_cb8e5c10a8097c2f04e0789f13f9d9d4 | 测试验收/报告/Bug 修复 |

### dev-director 下属三个子 Agent（通过 delegate_task 派发，不是独立飞书 bot）

| 子 Agent | skill | 职责 |
|----------|-------|------|
| dev-frontend | ~/.hermes/skills/dev-frontend/SKILL.md | Next.js 页面/组件/样式/API 调用 |
| dev-backend | ~/.hermes/skills/dev-backend/SKILL.md | REST API/业务逻辑/Node.js/Express |
| dev-database | ~/.hermes/skills/dev-database/SKILL.md | PostgreSQL/表结构/索引/迁移脚本 |

专家库位置：`~/.hermes/army-workspace/04-开发实现/{backend,frontend,database}/experts/`

### 流水线顺序
需求 → market-director 调研 → product-director PRD → architect-director 架构 → dev-director 开发 → test-director 测试 → 交付主人

---

## 当前项目：耳机独立电商站

### 基本信息
- 项目名称：earphone independent e-commerce站
- 阶段：开发阶段（前后端未打通，前端用 mock 数据）
- 开始时间：2025-04-23
- 工作区根目录：/home/ubuntu/.hermes/army-workspace/04-开发实现/

### 技术栈
- 前端：Next.js (ecommerce-store, port 3000) — 目前用 MOCK_PRODUCTS 硬编码
- 后端：Node.js + Express + TypeScript (earphone-api, port 5000)
- 数据库：PostgreSQL (earphone_db, port 5432, 18张表，14款真实耳机产品)
- 服务器：81.71.93.113

### 服务状态（截至 2026-04-24）
- PostgreSQL：✅ 运行中，5432 端口
- 后端 API (earphone-api)：✅ 运行中，5000 端口，/api/products 返回 14 款产品
- 前端 (ecommerce-store)：✅ 运行中，3000 端口，但数据源是 MOCK_PRODUCTS，未对接后端 API

### 关键问题（待解决）
1. **前后端未打通**：前端用硬编码 mock 数据，未调用 localhost:5000/api
2. **环境变量缺失**：前端无 NEXT_PUBLIC_API_URL 配置
3. **产品图片**：API 返回的是 https://example.com/... 占位图

### 产出文件位置
- 后端：~/.hermes/army-workspace/04-开发实现/backend/ （未实际使用，子 Agent 尚未启动开发）
- 前端：~/.hermes/army-workspace/04-开发实现/frontend/ （未实际使用）
- 数据库：~/.hermes/army-workspace/04-开发实现/database/ （未实际使用）
- 现有项目：~/.hermes/army-workspace/04-开发实现/earphone-api/ （后端）
- 现有项目：~/.hermes/army-workspace/04-开发实现/ecommerce-store/ （前端）

---

## API 接口协调规范（dev-director 强制执行）

### 统一响应格式
```json
{ "success": true, "data": { ... } }
{ "success": false, "data": null, "error": { "code": "ERROR_CODE", "message": "..." } }
```

### 分页格式
```json
{ "success": true, "data": { "items": [...], "pagination": { "page": 1, "limit": 20, "total": 100, "totalPages": 5 } } }
```

### 错误码
VALIDATION_ERROR(400), UNAUTHORIZED(401), FORBIDDEN(403), NOT_FOUND(404), CONFLICT(409), INTERNAL_ERROR(500)

### 契约文件位置
- backend/API_CONTRACT.md（backend 制定，各方遵守）
- frontend/API_CONTRACT.md（frontend 只读）
- database/ER.md（database 设计，backend + frontend 参考）

---

## 用户信息

- 称呼：主人
- 平台：Android，飞书群聊
- 飞书群 ID：oc_08f6cb45cf9c2132e7ee86fd6fb5dec9
- 用户 open_id：ou_6f5ac0d4fdbeff37750e6af2c8558dc0
- 偏好：直接看结果，不喜欢被引导去外部查看；问文件直接展示内容

---

## Commander 自己知道的规则

1. 只做调度，不做专业产出（调研/设计/开发/测试各司其职）
2. 主动汇报进度，遇到阻塞第一时间告知主人
3. 每次任务完成后将产物路径告知主人
4. 主人说"先暂停"就立刻停，不要继续执行
5. session 文件超过 150 条消息会触发自动归档（每小时 cron）

---

## 已完成的历史任务产出

- 市场调研：~/.hermes/army-workspace/01-市场调研/Claude-AI-Use-Cases/深度报告.md
- 市场调研：~/.hermes/army-workspace/01-市场调研/独立站大方向/选品调研报告.md
- 产品设计：~/.hermes/army-workspace/02-产品设计/20260424-Science-Video-Topics.md

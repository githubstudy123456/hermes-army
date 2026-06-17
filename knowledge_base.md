# 知识库

> 解决不了问题时先查这里，不用浪费启动 token。

---

## 部门架构 — 爱马仕军团 Hermes Army

**飞书 group chat:** `oc_8c4fa359fd2f4278307a435ee3826dac`（爱马仕军团群）
**gateway:** single-app mode，appId `cli_a9522c26da7ddbca`，每个 member 是 separate appId，需配置 multi-account 路由（type: route binding）
**调度方式:** 通过 commander 统一派发任务，不需要独立 gateway

> 注：profile 代号仍用 hermes-*（如 hermes-ceo），但对主人统一称"爱马仕军团 Hermes Army"

### 核心 7 部门

| 部门 | 代号 | 职责 |
|------|------|------|
| CEO | hermes-ceo | 战略决策、组织管理、资本运作 |
| 开发总监 | hermes-dev | 接收产品需求 → 编写代码 → 自测 → 交付测试 |
| 产品总监 | hermes-pm | 需求文档、优先级排序、跨部门协调 |
| 测试总监 | hermes-qa | 测试用例、缺陷报告、质量保障 |
| 内容总监 | hermes-content | 内容策划、文案创作、品牌表达 |
| 市场总监 | hermes-market | 市场调研、竞品分析、营销增长 |
| 全栈总监 | hermes-fullstack | 前后端开发、系统架构、技术攻关 |

### 支撑部门

| 部门 | 代号 | 职责 |
|------|------|------|
| CFO | hermes-cfo | 财务战略、融资、投资者关系 |
| 法务总监 | hermes-legal | 法律合规、知识产权 |
| 架构总监 | hermes-architect | 技术架构设计、技术选型 |
| 产品设计总监 | hermes-product | 把调研报告转化为 PRD |
| 市场调研总监 | hermes-marketing | 市场规模、用户、竞争格局分析 |
| 测试验收总监 | hermes-test | 制定测试计划、执行测试、报告缺陷 |
| 生活管家 | hermes-life | 健康、饮食、个人成长、生活质量 |
| 决策参谋 | hermes-advisor | 信息分辨、方案制定、战略支持 |

### 开发专项

| 部门 | 代号 | 职责 |
|------|------|------|
| 前端开发总监 | hermes-dev-frontend | React/Next.js/Tailwind，物理可视化 UI |
| 后端开发总监 | hermes-dev-backend | Next.js API Routes、Supabase、支付 |
| 3D开发总监 | hermes-dev-3d | Three.js/WebGL，沉浸式 3D 场景 |

### commander

| 项目 | 内容 |
|------|------|
| 代号 | commander |
| 飞书 appId | （需补充） |
| 职责 | 6 Profile 研发军团统一调度，向各 director 派发任务 |

---

## 技能能力

### 爬虫/数据采集

| 方案 | 状态 | 说明 |
|------|------|------|
| curl/requests | 可用 | 最轻量，成功率低 |
| scrapling | 已装+验证 | CLI工具，需browserforge，静态页面可用，HackerNews被反爬拦 |
| bb-browser | 已调研 | 真实Chrome+登录态+篡改猴，10分钟写适配器 |
| playwright | 有skill | playwright-browser-automation |
| browser-use | 未测 | 需Playwright+模型，较重 |

### AI/模型能力

| 工具 | 状态 | 说明 |
|------|------|------|
| mmx（MiniMax CLI） | 已装+认证 | CN平台，`mmx vision /path/to/image.jpg` 可用 |
| Hermes vision_analyze | 可用 | 内置图片识别 |
| claude（CLI） | 可用 | via acp_command |

### 技能列表

- `teaching-platform` — 学科网对标多科目教学平台
- `server-operations` — 服务器运维全集
- `japan-server` — 日本服务器操作手册（207.56.226.147）
- `clawhub-skill-research` — ClawHub Skill 调研workflow
- `playwright-browser-automation` — 浏览器自动化
- `github-pr-workflow` / `github-code-review` / `github-repo-management`
- `feishu-cron-push` — 飞书定时内容推送
- `slowmist-agent-security` — SlowMist 安全审计框架
- `openclaw-imports/gaokao-mentor` — 高考志愿填报顾问

---

## 主人项目

存放于 `~/.hermes/projects/`，一个项目一个 .md 文件。

### anthropic-financial-services.md（待处理）

- **来源:** github.com/anthropics/financial-services，Stars 20.8k
- **定位:** 金融服务业 AI Agent 系统（投行、PE、Equity Research、财富管理）
- **核心模块:** 9个 Agent（Pitch/Meeting Prep/Market Researcher/Earnings Reviewer/Model Builder/Valuation Reviewer/GL Reconciler/Month-End Closer/Statement Auditor/KYC Screener）
- **部署:** Claude Cowork 插件 或 Managed Agents API
- **潜在用途:** 拆出 DCF/LBO model skill、GL Recon 工作流

---

## teaching-platform

- 路径: `/home/ubuntu/teaching-platform/`
- 框架: Flask，多科目
- 主人公网部署地址: 丢失，需问主人要
- UI偏好: ◀ ▶ 图标按钮（无文字），不喜欢深层嵌套菜单
- 可迁移技术（来自 physics-visual-platform）: Three.js 3D模型、分步动画讲解、交互参数滑块

---

## 日本服务器

| 项目 | 内容 |
|------|------|
| IP | 207.56.226.147 |
| SSH | `ssh -i ~/.ssh/japan root@207.56.226.147`，密钥认证，密码已禁用 |
| 代理协议 | VLESS + REALITY（Xray），UUID: b831381d-6324-4d53-ad4f-8cda48b30811 |
| 代理端口 | 443（走 CloudFront HTTPS） |
| 伪装目标 | www.amazon.com:443 |
| PPTX 源文件 | `/tmp/hermes/pptx/` |
| JSON 输出 | `/data/baidu-library/files/` |
| 转换脚本 | `/tmp/hermes/find_json.py` |
| Flask 服务 | 端口 5001 |
| 已知坑 | SSH subprocess 传中文参数会失败，用 cat+grep 绕过 |

---

## 重大会议提醒

| 会议 | 时间 |
|------|------|
| 二十一大 | 2027年秋（每5年党代会） |
| 每年12月 | 中央经济工作会议 |
| 每年3月 | 全国两会（政协3日/人大5日开幕） |
| 每月 | 政治局会议 |

---

## 环境与工具

| 项目 | 内容 |
|------|------|
| 知识库位置 | `~/.hermes/knowledge_base.md` |
| 项目存放 | `~/.hermes/projects/` |
| Skills | `~/.hermes/skills/` |
| 日本服务器 | 207.56.226.147 |
| 订阅群 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 组织群 | oc_08f6cb45cf9c2132e7ee86fd6fb5dec9 |
| GitHub 调研 Cron | job_id `57ffe58e5447`，每小时整点跑 |

---
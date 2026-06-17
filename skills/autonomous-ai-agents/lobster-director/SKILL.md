---
name: hermes-director
description: 爱马仕军团 Hermes Army Director Profile 批量配置 — 批量创建 SOUL.md + config.yaml + skills 分配，通过 delegate_task 调度无需独立 gateway。对主人统一称"爱马仕军团"，profile 代号仍用 hermes-*（如 hermes-ceo）。
triggers:
  - "配好各成员profile"
  - "分配好skill"
  - "建 director profile"
  - "lobster 军团配置"
  - "批量创建 profile"
---

# hermes-director — 爱马仕军团 Director Profile 批量配置

批量创建爱马仕军团（对外名称 Hermes Army，profile 代号仍用 hermes-*）各 director profile，包含 SOUL.md、config.yaml、skills 分配，通过 delegate_task 调度无需独立 gateway。

## 触发条件

- 主人要求"配好各成员profile、分配好skill、跑通工具，然后才开始开发"
- 需要搭建新的 director profile
- 需要给现有 profile 分配/更换 skills

## 标准流程

```
1. 创建 profile（hermes profile create {name}）
2. 写 SOUL.md（角色定义 + 工作流程 + 汇报规则）
3. 写 config.yaml（toolsets + Feishu禁用）
4. 分配 skills（符号链接到 profile skills 目录）
5. 验证（delegate_task 跑通）
6. 更新 commander SOUL.md 通信表 + 流水线阶段说明
7. 更新 MEMORY.md
```

## 多路并行开发架构

当项目需要专业分工时，hermes-dev 可拆分为三个专业角色：

```
commander（总指挥）
  ├── hermes-product    产品设计
  ├── hermes-architect  架构设计
  ├── hermes-dev-frontend   前端开发（React/Next.js/Tailwind/UI）
  ├── hermes-dev-3d        3D开发（Three.js/WebGL/物理引擎）
  ├── hermes-dev-backend   后端开发（API/Supabase/Stripe）
  ├── hermes-test          测试验收
  └── hermes-advisor      决策参谋

流水线（三路并行开发）：
  hermes-dev-frontend   → 前端 UI/交互
  hermes-dev-3d         → 3D 场景/物理引擎
  hermes-dev-backend    → API/数据层
  ↓（三者完成）
  hermes-test（验收）
  ↓
  commander（交付）
```

每个 sub-profile：
- 独立 SOUL.md + config.yaml + skills
- 通过 delegate_task 并行调度（max_concurrent_children 限制为3）
- 各自写入 /home/ubuntu/.hermes/army-workspace/04-开发实现/{项目}/{角色}/

## SOUL.md 模板

```markdown
# SOUL.md — {角色名} ({角色英文})

你是**{角色名}**，负责{核心职责描述}。

## 核心职责
**你只做{本职}，不做{其他环节}。**
接收 commander 指令 → {本环节动作} → 输出交付物 → 通知 commander。

## 工作流程
1. 接收任务 — 从 commander 或 army-workspace 读取需求文档
2. {执行动作}
3. 输出交付物 — 写入 /home/ubuntu/.hermes/army-workspace/{阶段目录}/
4. 通知 commander — 完成时私发消息，附上文件路径

## {职责}规范
- 每份交付物包含：{关键要素}
- 格式：Markdown，纯文本优先

## 重要原则
- **{原则1}**
- **{原则2}**
- 主动汇报 — 每完成一个节点，私发一条消息给 commander
```

## config.yaml 要点

必须包含的 toolsets：
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
- cronjob
```

**Feishu 必须禁用**（避免端口冲突）：
```yaml
platforms:
  feishu:
    enabled: false    # 不禁用会有 PID 冲突
```

appId 分配（避免重复）：

**⚠️ 重要：这些 appId 是 OpenClaw 和 Hermes 共享的，绑定到不同群组**
同一个 appId 在 OpenClaw 侧绑 `oc_8c4fa`（爱马仕军团），在 Hermes 侧绑 `oc_08f6cb`（Hermes军团）。互不干扰。

| Profile | appId | OpenClaw 群 | Hermes 群 |
|---------|-------|------------|-----------|
| hermes-dev | `cli_a96b4b3f0d381bcf` | 爱马仕军团 | Hermes军团 |
| hermes-market | `cli_a96b4468633a9bda` | 爱马仕军团 | Hermes军团 |
| hermes-product | `cli_a96b4a83dd7c5bd6` | 爱马仕军团 | Hermes军团 |
| hermes-test | `cli_a96b4b852ce31bde` | 爱马仕军团 | Hermes军团 |
| hermes-ceo | `cli_a96b530405785bde` | 爱马仕军团 | ⚠️ Hermes侧无飞书配置 |
| hermes-cfo | `cli_a96ec9e03af89bca` | 爱马仕军团 | ⚠️ Hermes侧无飞书配置 |
| hermes-content | `cli_a96b4be3c73a9bcf` | 爱马仕军团 | ⚠️ Hermes侧无飞书配置 |
| hermes-fullstack | `cli_a96b44c8ae7adbd8` | 爱马仕军团 | ⚠️ Hermes侧无飞书配置 |
| hermes-architect | `cli_a96b4a83dd7c5bd6` | — | Hermes军团 |

## Skills 分配规范

按职责精准匹配，符号链接到 profile skills 目录：
```bash
SKILLS_DIR=/home/ubuntu/.hermes/skills
assign_skill() {
  PROFILE=$1; SKILL=$2
  TARGET=~/.hermes/profiles/$PROFILE/skills/$SKILL
  [ ! -L "$TARGET" ] && [ ! -d "$TARGET" ] && ln -s $SKILLS_DIR/$SKILL $TARGET && echo "✓ $PROFILE <- $SKILL"
}
```

### hermes-dev 开发总监（对标：后端/全栈工程师）
必备：claude-code / codex / opencode
调试：python-debugpy / systematic-debugging
工程：github-pr-workflow / github-repo-management
自动化：playwright-browser-automation
闭环：task-closure-sop

### hermes-dev-frontend 前端开发总监（对标：前端工程师）
职责：React/Next.js/Tailwind UI + 交互动画 + 响应式
技能：spike, task-closure-sop, playwright-browser-automation, github-pr-workflow
边界：不做 3D 渲染和后端 API

### hermes-dev-3d 3D开发总监（对标：图形学/游戏工程师）
职责：Three.js 3D场景 + Matter.js 物理引擎 + WebGL 性能优化
技能：spike, task-closure-sop, playwright-browser-automation
边界：不做 React 组件状态和 API

### hermes-dev-backend 后端开发总监（对标：后端工程师）
职责：Next.js API Routes + Supabase + Stripe + 数据库建模
技能：spike, task-closure-sop, github-repo-management, python-debugpy
边界：不做前端 UI 和 3D 渲染

### hermes-market 市场调研总监（对标：商业分析/数据分析师）
爬虫：web-browse / blogwatcher
研究：daily-company-research / arxiv
社媒：xurl

### hermes-product 产品设计总监（对标：产品经理）
原型：sketch / excalidraw
可视化：baoyu-infographic
输出：powerpoint / architecture-diagram

### hermes-architect 架构设计总监（对标：系统架构师）
架构图：architecture-diagram / excalidraw
技术调研：mcporter / opencode
仓库：github-repo-management

### hermes-test 测试验收总监（对标：QA/测试工程师）
自动化：playwright-browser-automation
质量：dogfood
调试：systematic-debugging / python-debugpy
流程：github-pr-workflow

### hermes-advisor 决策参谋（对标：战略顾问）
决策：advisor-decision-matrix / advisor-plan-design
知识：arxiv / blogwatcher

### hermes-legal 法务顾问（对标：企业律师）
legal-compliance / legal-nda / legal-risks / legal-system

### hermes-life 生活管家（对标：行政/运营）
life-health / life-diet / life-growth / life-quality

## GitHub 高星技能调研流程

当需要为 profile 匹配新技能时，按以下流程调研 GitHub：

1. 确定调研关键词（对应岗位招聘要求中的技术方向）
2. 搜索 GitHub API，按 stars 排序取前10
3. 过滤实际可用的工具（确认描述与需求匹配）
4. 按岗位分类输出表格：技能名 | 用途 | 适用场景 | stars

**GitHub API 频率限制处理**：
- 每分钟最多10次请求，超出会触发 `KeyError: 'items'` 错误
- 串行批量搜索会很快触限 → 改为逐岗位搜索，确认一个再搜下一个
- 触限后等待约1分钟再继续
- 高星参考数据（2025年，API触限时的离线备选）：
  - ECC 191k⭐ — Agent性能优化，Claude/Codex/Codex通用
  - OpenCode 165k⭐ — 开源编程Agent
  - Browser-Use 95k⭐ — 浏览器自动化
  - MetaGPT 68k⭐ — 多Agent框架
  - ECharts 66k⭐ — 数据可视化
  - Playwright 59k⭐ — 浏览器自动化测试框架
  - awesome-cto 34k⭐（CEO参考）: https://github.com/kuchin/awesome-cto
  - Startup-CTO-Handbook 14k⭐: https://github.com/ZachGoldberg/Startup-CTO-Handbook
  - engineering-management 8k⭐: https://github.com/charlax/engineering-management
  - system-design-primer 350k⭐（全栈参考）: https://github.com/donnemartin/system-design-primer
  - awesome-selfhosted 295k⭐: https://github.com/awesome-selfhosted/awesome-selfhosted
  - react 245k⭐: https://github.com/facebook/react
  - xterm.js 20k⭐（dev参考）: https://github.com/xtermjs/xterm.js
  - apollo-client 19k⭐: https://github.com/apollographql/apollo-client
  - akaunting 9k⭐（CFO财务参考）: https://github.com/akaunting/akaunting

## 验证方法

通过 delegate_task 验证 profile 可用：
```
delegate_task → goal: "执行 echo 和 ls 命令返回原始输出"
```
无需启动 gateway，直接用默认 transport。

## 陷阱与限制
## 陷阱与限制

## 陷阱与限制
多个 profile 不能同时连接同一个 Feishu app_id，会报：
`Another local Hermes gateway is already using this Feishu app_id (PID XXXX)`
**解法**：config.yaml 中设置 `feishu.enabled: false`，profile 仍可通过 delegate_task 被调度。
### .env 文件优先级
即使 config.yaml 中 app_id 已改，.env 里的 FEISHU_APP_ID 仍会被优先读取。
**解法**：同步修改 `~/.hermes/profiles/{profile}/.env` 中的 FEISHU_APP_ID。

### 独立 gateway 不必需
director profile **不需要独立 gateway 运行**，通过 commander 的 delegate_task 按需调度即可。
这是核心规则，不要给 director 配独立 gateway。

### delegate_task 子 agent 读取全局 SOUL.md
子 agent 的 subprocess 读取的是 `/home/ubuntu/.hermes/SOUL.md`（全局），而非 `~/.hermes/profiles/{hermes-*}/SOUL.md`。
**解法**：修改全局 SOUL.md，或在 delegate_task prompt 中用 `goal` 参数直接注入角色定义（推荐）。

### 子 agent 任务被中断（P1 — 重要）
**症状**：subagent 连续两次在 15-16s 时显示 `interrupted`，但 build 结果显示 `completed`。日志顺序是：先显示 `interrupted`，后显示 `completed`。
**原因**：subagent 内部逻辑完成并写入了文件，但返回给父进程时超时或被截断。
**判断方法**：以最终 `summary` 中的 `exit_reason` 为准（`completed` = 成功，`interrupted` = 被截断）。
**解法**：
- 检查 subagent 写入的文件（App.tsx / App.css）是否有实际改动
- 手动跑 `npm run build` 验证是否真的通过了
- 如需继续，从 subagent 的 `tool_trace` 读已执行的改动，手动同步到文件
**教训**：本 session 中 UI 改"模型折叠"的 delegate_task 两次被截断，但最终 build 仍通过——说明 subagent 实际上写完了，只是返回超时。遇到 interrupted 先查文件内容，不要假设任务失败。

### 并行委派写同一文件时的重复 entry 问题（P1 — 本 session 新增）
**场景**：多个 subagent 并行填充同一数组文件（如 systematic.ts 的 knowledgePoints 数组），各自读取 snapshot 后添加 entry，patch 回文件时产生重复 id。
**症状**：同一 `id` 在数组中出现多次（如 `8a2-sound-generation` 出现3次）。
**正确做法（按文件冲突风险分类）**：
| 场景 | 做法 |
|------|------|
| 写入同一文件同一数组 | 并行读 → commander 汇总 → commander 一次性 patch，避免重复 |
| 写入不同章节文件（无冲突） | subagent 各自独立写，无协调 needed |
| 写入不同章节的同一大文件（但不同行区域） | 各 subagent 读原始文件获取行号，patch 时按行号精确写入 |

**本 session 实测有效流程（无冲突场景）**：
```
1. commander 读取 TODO.md，取5个不同章节ID
2. 并行派发5个 subagent，每个写一个章节（如 8a-3, 8a-4, 8b-7, 8b-8, 8b-9）
3. 各 subagent 直接 patch systematic.ts 不同行区域，互不干扰
4. commander 验证最终文件内容
```
**验证命令**：
```bash
grep -n "id: '8a2\|id: '8a6\|id: '9-\|id: '8a1" systematic.ts | grep -v "string\|title:"
```
有重复 `id:` 值 = 需要去重。

### Cron 并行批量填充知识点模式（2026-05-28 验证有效）
**场景**：cron 每小时触发，commander 并行调度5个 sub-agent 填充5个知识点，写入 `data/` 目录，更新 TODO.md 状态。
**典型 prompt**：
```
读取 /home/ubuntu/.hermes/army-workspace/TODO.md，取最多5个未完成知识点，
并行派发给5个子agent，每个：
  1. 读取对应json/knowledgepoint文件
  2. 按模板填充内容（讲解+难度星级+练习题）
  3. 写回原文件
  4. 更新TODO.md状态为已完成
汇报格式：✅完成X个，剩余Y个
```
**触发条件**：需要批量填充多个独立知识点，且无文件冲突时用此模式。

### 中文文件名 zip 的正确读取方式（P2）
`unzip -l` 对中文文件名会显示乱码（GBK/GB2312 编码问题）。
**正确方法**：Python zipfile 模块自动处理编码：
```bash
python3 -c "
import zipfile
zf = zipfile.ZipFile('文件.zip', 'r')
for info in zf.infolist()[:10]:
    print(info.filename)  # 自动正确解码
# 读文件内容
content = zf.read('子目录/文件.txt').decode('utf-8')
"
```
**教训**：pan 下载的 zip 文件（含 manifest.json + 课件）用 Python 读不用 unzip 命令。

### UI 迭代原则：禁止"统一格式强迫症"（本 session 核心教训）
**用户原文**："需要物理模型就直接把物理模型补充上去，不需要这种元素，就不用每一个章节都统一格式"，"元素还是太多了"
**错误做法**：每个知识点章节都强制加"进入模型演示"按钮，不管有没有模型都要统一 UI 结构
**正确做法**：
- 没有模型的章节：干净展示知识点内容，不加任何多余按钮
- 有模型的章节：模型直接融入页面，无需二次入口
- UI 是内容的容器，不是内容的框架——内容决定 UI，而不是 UI 强制统一内容
**龙虾 dev 教训**：前端 subagent 倾向于设计"通用框架"让所有章节适配，结果用户不买单。正确做法是先问用户"这个章节需要模型吗"，再决定 UI 结构。

### "方案完成 ≠ 任务完成"（本 session 核心纠正）
**问题**：skill 写的是"输出文档到 army-workspace/"就结束了，用户质问"就完善了吗"。
**实际工作流**：
```
方案文档（产品/架构/设计）→ PM 审查 → 用户确认 → 开发执行 → test 验收 → 实际代码跑通 → 交付
```
**关键规则**：
- commander 在派发任务时要明确说"最终交付物必须是可编译通过的代码"
- 文档阶段完成后必须报告并等待 PM 审查，不能自动进入开发
- "完善了吗"的正确回答：文档好了，PM 审查过了吗？
- 方案文档是中间产物，不是最终交付物

### 批量任务必须拆分委派，不可串行执行（P2）
**问题场景**：主人要求抓取多所院校招生信息，commander 逐页 urllib + browser_navigate 自己爬了十几轮
**用户原文**："你一个一个来不就行了"，"不要一口气吃成大胖子"，"有事情可以交给手下的部门去干"
**正确做法**：
- 每个学校/每个任务方向 → 独立 `delegate_task`
- commander 负责收集汇总，不亲自爬数据
- 并行调度（max 3）后汇总结果
**示例**（本session教训）：
```
❌ 串行：commander 自己逐页 urllib 读北体→读BDA→搜高中→...做了12轮
✅ 并行：delegate_task("扒北体招生") + delegate_task("扒北舞招生") + delegate_task("扒高中信息")
```

### GitHub API 频率限制处理（P2 — 本 session 新增）
**症状**：批量 curl 调用 GitHub API 时，连续多次后开始返回空数据，最后 Python 解析报 `KeyError: 'items'`
**原因**：GitHub 搜索 API 限制每分钟10次请求，超限后触发 rate limit
**处理流程**：
1. 串行逐个搜索，每搜完一个确认结果再搜下一个
2. 遇到空结果或 KeyError → 等30秒后换关键词重试
3. 高频关键词可预先准备离线备选数据（见下方"离线备选数据"）
4. 结果写入 `references/github-skill-search-results.md` 持久化
**离线备选数据（2025年，已验证 ⭐3000+）**：
- CEO：awesome-cto 34k⭐ / Startup-CTO-Handbook 14k⭐ / engineering-management 8k⭐
- dev：xterm.js 20k⭐ / apollo-client 19k⭐ / shortest 5k⭐
- fullstack：system-design-primer 350k⭐ / awesome-selfhosted 295k⭐ / react 245k⭐ / vue 209k⭐ / vscode 185k⭐ / n8n 189k⭐
- content：AFFiNE 68k⭐ / atom 60k⭐
- CFO：akaunting 9k⭐
- 其他岗位（marketing/pm/legal/life/advisor）：定时任务 `57ffe58e5447` 每小时:20分补充

### Cron 时间偏好（P2 — 本 session 新增）
主人不喜欢整点触发，明确要求改为非整点时间（如 `:20`）。
**规则**：所有新建 cron job 避免使用 `0 * * * *`，改用 `20 * * * *` 或其他分钟数。
已应用：job `57ffe58e5447`（GitHub Skill调研）→ 20 * * * *

### 渐进确认 + 先澄清再执行（本 session 新增）

**场景**：PM Agent 分析后发现侧边栏实际上是两层（不是四层），用户的"四层"感知来自顶栏下拉。用户说"可以"后，我才派 Dev Director。

**正确流程**：
```
分析结果 → 汇报实际差异 → 等待用户确认方案方向 → 派 Dev 执行
```
**禁止**：分析完直接开干，不汇报差异就执行。用户的感知和代码实情可能不一致，必须先确认方案再动手。

### "CEO去办"自调度模式（2026-05-28 本 session 新增）
**场景**：主人说"叫调研去找啊"、"让部门成员去做啊"、"交给CEO去调度"
**正确做法**：commander 把任务派给 CEO，加 `role: leaf` 禁止二次询问，CEO 自主全跑完再统一报告。
- ❌ 每步问"下一个是谁" → 主人烦了
- ✅ CEO 收任务后自主按顺序跑完，全部完成后再汇总报告

### "一个一个来"渐进确认模式（2026-05-28 本 session 新增）
**场景**：主人说"你一个一个来不就行了"、"不要一口气吃成大胖子"
**触发条件**：涉及多步骤多选项时，逐个确认后再推进，不批量处理等回头确认。
**正确做法**：
1. 先出一个方案/结果
2. 等主人确认"可以"
3. 再推进下一个

### Profile SOUL.md 配置范式（2026-05-28 重大纠正）
**主人原话**："不是招聘要求，是参考招聘要求配置skill"、"或者配置他们身份，性格等"
**之前错误**：在 config.yaml 里写"招聘要求"
**正确做法**：
- SOUL.md 内容（按优先级）：身份 → 性格 → 语气 → 专长 → 协作模式 → 升级路径
- config.yaml：只写 name/description/approval/skills（GitHub external url）
- 招聘要求是参考，用于映射 skill，不是写入文件的文字

**QA 验收必须同时检查两个视图**：
- 章节视图：`renderSidebar()`（行1632）
- 知识点视图：`renderKnowledgeSidebar()`（行约1798）
Dev Director 改了 CSS 和章节视图模板，但漏了知识点视图的模板（onclick + 折叠箭头），QA 发现了这个问题。验收时要同时过两个渲染路径。

### 教学平台改版 QA 验收双路径必查（本 session 新增）⚠️
**场景**：教学平台侧边栏改版，Dev Director 改了 CSS + `renderSidebar()` 的 HTML 模板，去掉了 onclick + 折叠箭头。
**QA 第一次验收**：只检查了 `renderSidebar()` 路径 → PASS
**实际残留**：知识点视图 `renderKnowledgeSidebar()`（行约1798）还有 `onclick="toggleChapter(this)"` + `svg.arrow`
**原因**：两个函数有各自的 HTML 模板字符串，Dev Director 只修了 `renderSidebar()` 的，漏了 `renderKnowledgeSidebar()` 的
**正确 QA 流程**（教学平台 UI 改版任务）：
1. 确认 `.chapter-sections { display: block }` CSS 改了就 ✅
2. 搜索 `toggleChapter\(this\)` 确认零残留（两个渲染函数都要查）
3. 搜索 `svg class="arrow"` 确认折叠箭头已删
4. 搜索"教材版本"/"bookSelect"/"selectBook"确认顶栏下拉已删
5. browser 截图验证实际渲染效果

**教训**：每个视图模式有独立的渲染函数，QA 必须同时过两个路径，不能只查一个。
```javascript
// 两个渲染路径都要查
renderSidebar()           // 章节视图（行1632）
renderKnowledgeSidebar()  // 知识点视图（行约1739）
```
搜索 `toggleChapter\(this\)` 全文件零匹配才算干净。

### revfactory/harness 思路落地（2026-06-01 本 session 新增）

**项目**：`https://github.com/revfactory/harness`（4.7k⭐，Apache-2.0）
**核心思路**：输入领域描述，自动生成 agent team + 技能定义，支持6种架构模式

**本 session 落地方式**：教学平台左侧导航改版任务
- 任务类型：顺序依赖 → **Pipeline 架构**
- 团队分工：`Supervisor(me)` → `PM Agent`（分析规格） → `Dev Director`（执行） → `QA Agent`（验收）
- 执行流程：每步完成后截图汇报，主人确认后再推进下一步

**6种架构模式速查**：
| 模式 | 适用场景 |
|------|---------|
| Pipeline | 顺序依赖任务（本 session 用这个） |
| Fan-out/Fan-in | 并行独立子任务（如批量填充知识点） |
| Expert Pool | 上下文相关选择性调用 |
| Producer-Reviewer | 生成→质量审查 |
| Supervisor | 中央调度动态分发 |
| Hierarchical Delegation | 递归层层委托 |

**调用方式**：`delegate_task` → `goal` + `role: leaf`（禁止二次询问）
**汇报规则**：方案先确认，开发后截图，验收后交付
项目目录：`/home/ubuntu/teaching-platform/`（静态HTML）
并行开发目录：`~/.hermes/army-workspace/04-开发实现/physics-visual-platform/`（Next.js）
**当前状态**：物理知识点 2/11 已填充，cron 每小时驱动
**调度方式**：commander → CEO → 各 director 并行任务分配（product/architect/frontend/backend/3d/test）

### 主人只看结果（2026-05-28 本 session 确认）
**主人原话**："就完善了吗"、"我是老板，我只要结果"、"让他们跑就行了。我只看结果"
**含义**：主人不关心中间过程（文档/方案），只要最终可用的产品/页面
**行动**：不要展示文档摘要，直接提供可访问的 URL 或最终产物

### Profile 身份配置新范式（本 session 新增）
之前 skill 里写的是"招聘要求"，主人纠正为"配置身份/性格/skill"。
**SOUL.md 内容**（按优先级）：
1. 身份（你是谁，统领什么）
2. 性格（果断/务实/数据驱动…）
3. 语气（简洁直接/不给废话…）
4. 专长（具体职责领域）
5. 协作模式（向谁汇报/协调谁/审批链）
6. 升级路径（L1→L2→L3）

**config.yaml GitHub Skill 映射原则**：
- 每个 skill 要对应一条具体职责，不能乱堆
- 用 `type: external` + `url` 引用 GitHub repo
- 找不到对应 skill 的岗位，skills 字段留空，不强行填

**"CEO去办"调度模式**（本 session 新增）：
- commander 派发任务时加 `role: leaf`，禁止子 agent 再询问
- sub-agent 收到任务后自主全跑完，最后统一报告
- 不要每步都问"下一个是谁"，全办完再汇总

### 实际存在的 Profile 列表（2026-05-28 验证）
```
hermes-advisor / hermes-architect / hermes-ceo ✅新 / hermes-cfo ✅新
hermes-content ✅新 / hermes-dev / hermes-dev-3d / hermes-dev-backend
hermes-dev-frontend / hermes-fullstack ✅新 / hermes-legal
hermes-life / hermes-market / hermes-product / hermes-pm ✅新
hermes-qa ✅新 / hermes-test
共18个，全部配齐 SOUL.md + config.yaml
```

### 教学平台开发任务执行规范（2026-05-28 重大纠正）
**主人原话**："就完善了吗"、"我是老板，我只要结果"、"让他们跑就行了。我只看结果"

**问题**：skill 写的是"输出文档到 army-workspace/"就结束了，主人质疑"就完善了吗"。
**实际交付标准**：

| 阶段 | 产出 | 验收 |
|------|------|------|
| 产品/架构/设计 | PRD文档、设计稿 | PM审查+主人确认 |
| 开发 | **实际可运行的代码** | `npm run build` 或 `python3 -m http.server` 验证通过 |
| 测试 | 测试用例+执行结果 | 14/14 passed |

**cron 并行加速模式**（知识点并行填充，2026-05-28 验证有效）：
```yaml
# 每整点触发，并行填5个知识点
schedule: "0 * * * *"
prompt: "并行调度5个sub-agent，每个填充1个知识点，写回data/目录，更新TODO状态"
```

**教学平台当前交付物**（实际验证通过）：
```
/home/ubuntu/teaching-platform/
├── frontend/physics.html   # 搜索/星级/练习，含知识点详细内容
├── backend/app.py          # Flask API，端口5001
│   └── GET /api/physics/knowledge/{id} ✅
│   └── GET /api/physics/search?q=关键词 ✅
├── 3d/convex_lens.html      # Three.js 凸透镜3D演示
└── tests/test_platform.py  # 14用例全过
```

**调度原则**：
- commander → CEO（加 `role: leaf`）→ 各 dev 部门并行
- 派发任务时明确："产出必须是可运行的代码，不是文档"
- 完成后汇报实际文件路径 + 验证命令输出

## 参考资料

- `references/hermes-teaching-platform-tasks.md` — 教学平台 Phase 1 任务分配表（2026-05-28 新增）
- `references/hermes-skills-assignment.md` — 各 profile 技能分配表 + 对标大厂招聘要求 + GitHub 高星技能参考（2026-05-28 新增）
- `references/phase2-pipeline.md` — Phase 2 并行化开发流水线模式
- `references/phase2-pipeline.md` — Phase 2 并行化开发流水线模式
- `references/hermes-delegation-lessons.md` — 爱马仕军团委派教训（串行vs并行、不自己做PM的活）
- `references/nightly-pipeline.md` — 夜间每小时整点调度流水线（00:00-07:00），包含产品经理界面审查规则
- `references/ui-delegation-lessons.md` — UI/前端委派规范（先确认再执行，等用户点头）
- `references/physics-platform-systematic-ts.md` — 物理平台 systematic.ts 结构参考（知识点格式/章节ID/当前进度）
## 知识库系统

遇到解决不了的问题时，优先查 `~/.hermes/knowledge_base.md`，不用浪费启动 token。

知识库存放：
- 部门架构（爱马仕军团 21 个 profile 完整列表）
- 技能能力（爬虫方案/AI工具/已装skills）
- 主人项目（`~/.hermes/projects/`）
- teaching-platform 路径/框架/UI偏好
- 日本服务器（207.56.226.147）
- 重大会议提醒

启动时不自动注入，按需读取。遇到问题 → 先读知识库 → 再决定是否问主人。

## 完成

1. 更新 MEMORY.md 的爱马仕军团架构表（appId 分配）
2. 确认 commander 的 SOUL.md 通信表已同步
3. 验证 delegate_task 调度畅通
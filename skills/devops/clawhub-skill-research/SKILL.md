---
name: clawhub-skill-research
description: 从 ClawHub 搜索、调研、评估 skills 并分配给 lobster 军团成员的完整工作流。适用于：当主人要求"去 ClawHub 找相关 skills，整理后交我审阅，再分配给各部门"时使用。包含代理确认、搜索技巧、内容查看、格式对比、技能分配全流程。
---

# ClawHub + GitHub Skill 研究与分配工作流

## 触发条件
主人要求去 ClawHub 或 GitHub 搜索相关 skills → 整理审阅 → 分配给 lobster 军团成员。

---

## 工作流程

### 路径A：ClawHub 搜索

#### 第一步：确认代理

某些 ClawHub 功能需要外网。先检查代理：

```bash
# 检查代理是否可用（代理是 socks5 协议）
curl -s --connect-timeout 5 -x socks5://127.0.0.1:10809 https://www.google.com -o /dev/null -w "%{http_code}"
# 返回 200 = 可用；超时 28 = 不可用
```

当前服务器代理端口：**10809**（socks5）

> 完整代理诊断流程（包括 HTTP/SOCKS/Trojan 协议判断）见 `server-operations` skill 的「代理/中转诊断」章节。

---

### 第二步：搜索 Skills

```bash
# 向量搜索（推荐，用空格分隔多关键词效果好）
npx clawhub search "company investment research business finance" 2>&1 | grep -E "^[a-z]" | head -30

# 分部门搜索
npx clawhub search "qa testing quality assurance"
npx clawhub search "marketing content social media"
npx clawhub search "developer coding software engineering"
npx clawhub search "product manager research"
npx clawhub search "ceo executive strategy"
```

关键词技巧：
- 搜索多个相关词效果比单一关键词好（空格分隔）
- 匹配度分数在 0.8 以上的可以纳入候选（实测分数是 4 位数如 4.400，不是小数 0.4）

**实际输出解析**（2026-05-11 实测）：
```
npx clawhub search "productivity" 2>&1
```
输出格式为多行描述块，每行一条结果，格式是：`slug  @owner  标题  (分数)`。过滤时直接 `head -N` 取前 N 条即可，不需要用正则过滤。用 `inspect <slug>` 看单条 metadata。

注意：`clawhub search` 有时只输出 `- Searching` 就结束（可能是网络问题或查询无结果），遇到这种情况换其他关键词重试。

---

### 第三步：预览 Skill 内容（不安装）

```bash
# 查看 metadata（描述、下载量、版本）
npx clawhub inspect <slug> 2>&1 | head -30

# 安装到临时目录预览完整内容
mkdir -p /tmp/skill-inspect && cd /tmp/skill-inspect
npx clawhub install <slug> 2>&1 | tail -3
# 路径: /home/ubuntu/.openclaw/workspace/skills/<slug>/
```

注意：用 `clawhub view` 会报错，应该用 `clawhub inspect` 或 `clawhub install`。

---

### 第四步：对比现有流程

将 ClawHub skill 的框架与现有日报/报告格式对比，找出：
- **已有**（现有日报已覆盖）
- **缺少**（现有日报没有，需要补充）
- **更好**（ClawHub 的方法比现有更优，可以替换）

---

### 第五步：整理审阅文档交给主人

格式：按部门分组，列出每个 skill 的：
- slug（clawhub.ai/xxx 链接格式）
- 描述（从 inspect 结果来）
- 匹配度（从搜索分数来）
- 推荐分配对象

纯文本格式，**不用 markdown 表格**（飞书不渲染）。

---

### 第六步：安装并分配

主人审阅确认后，用以下命令安装：

```bash
# 安装到 lobster 工作区
cd ~/.openclaw/workspace-lobster-<role>/
npx clawhub install <slug> --dir skills
```

---

### 路径B：GitHub 搜索（无需代理）

当主人说"按大厂招聘要求来找"时，用 GitHub API 直接搜：

```bash
# 搜索高星仓库，按 stars 排序
curl -s "https://api.github.com/search/repositories?q=<关键词>+stars:>3000&sort=stars&per_page=10" \
  | python3 -c "import json,sys; data=json.load(sys.stdin)
  for r in data.get('items',[]): print(f\"★{r['stargazers_count']:>6} | {r['name']} | {r['language']} | {r['description']}\")"
```

常用关键词方向：
- 招聘/技术栈调研：`software engineer requirements go java python spring boot kubernetes`
- AI Coding Agent：`AI codegen agent claude code generation stars:>5000`
- 浏览器自动化：`playwright browser automation agent stars:>2000`
- 多Agent框架：`multi-agent framework AI workflow stars:>3000`
- 数据可视化：`data visualization charts dashboard stars:>5000`
- 系统架构/微服务：`microservices system design architecture stars:>2000`
- DevOps/CI-CD：`kubernetes argocd cicd gitops stars:>2000`
- Figma/设计：`figma API design system component library stars:>2000`
- RAG/知识库：`rag retrieval knowledge graph stars:>3000`
- API文档：`API design documentation OpenAPI stars:>3000`

输出后按岗位分类整理成表：技能名 | 用途 | 适用场景 | stars，交给主人审阅后分配。

---

## 已知限制

1. **WAF 拦截**：东方财富、同花顺等财经网站有阿里云 WAF，curl 和普通浏览器会被拦截。可尝试 Playwright 绕过，或改用可直接访问的数据源。

2. **ClawHub inspect 不返回完整内容**：只返回 metadata，要看完整 SKILL.md 必须安装到临时目录。

3. **飞书消息不支持 markdown 表格**：所有输出用纯文本列表格式。

4. **部分 skill 收费**：如 `dev-productivity-bundle` 标注 ¥149/套，安装前先确认价格。

5. **搜索可能无输出**：网络波动时 clawhub search 只输出 `- Searching` 就结束，换关键词重试即可。

---

## 相关文件
- 已安装的 company-investment-research：`/home/ubuntu/.openclaw/workspace/skills/company-investment-research/`
- lobster 各工作区：`~/.openclaw/workspace-lobster-{ceo,cfo,dev,pm,qa,content,marketing,fullstack}/`
- **Cron 多任务数据管道模式**（多个 cron job 串联收集→汇总）：`references/cron-data-pipeline.md`

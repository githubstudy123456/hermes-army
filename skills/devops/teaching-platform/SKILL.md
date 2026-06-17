---
name: teaching-platform
title: 教学平台开发
description: 学科网对标的多科目在线教学平台，章节视图+知识点视图双模式，逐科接入内容。
---

# 教学平台开发

## 概述

对标学科网的多科目在线教学平台，路径 `/home/ubuntu/teaching-platform/`，开发服务器 `localhost:18081`。
核心原则：**逐个确认工作流** — 每步做完截图汇报，用户确认后再推进下一步。

## 平台核心架构

```
/home/ubuntu/teaching-platform/
├── index.html              # 主入口（纯静态，所有逻辑内联）
├── frontend/
│   ├── physics.html   # 物理知识点详细页（搜索/星级/练习）
│   └── math.html      # 数学知识点详细页（含培优模块，2026-06-02）
├── backend/app.py         # Flask API，端口5001
│   └── GET /api/{subject}/index    # 章节索引
│   └── GET /api/{subject}/chapter/{id}  # 章节详情
│   └── GET /api/{subject}/knowledge/{id}  # 知识点详情
│   └── GET /api/{subject}/brain-map/{grade}  # 脑图
│   └── GET /api/{subject}/search?q=关键词  # 搜索
│   └── GET /api/{subject}/stars     # 星级数据
│   └── GET /api/{subject}/all       # 全部知识点列表
├── 3d/convex_lens.html     # Three.js 凸透镜3D演示
├── tests/test_platform.py # 测试套件
└── data/
    ├── subjects.json       # 学科列表
    └── {科目}/
        ├── index.json      # 章节索引
        ├── {id}.json       # 单节内容
        ├── stars.json      # 星级数据
        └── brain-map/      # 脑图文件
            └── {年级}.json  # LIST格式知识点脑图
```

**后端启动验证**：
```bash
cd /home/ubuntu/teaching-platform/backend && python3 app.py &
curl http://localhost:5001/api/physics/knowledge/1-1  # 验证返回JSON
```

**⚠️ 部署关键：nginx root ≠ 源码目录**
- 源码目录：`/home/ubuntu/teaching-platform/frontend/math.html`
- nginx root：`/var/www/teaching-platform/frontend/`
- 新增前端文件必须同时复制到 nginx root：
```bash
sudo cp /home/ubuntu/teaching-platform/frontend/{文件名} /var/www/teaching-platform/frontend/
sudo chown www-data:www-data /var/www/teaching-platform/frontend/{文件名}
```
- 后端 `app.py` 不提供静态文件服务，静态文件由 nginx 从 `/var/www/teaching-platform/` 直接提供

**数据文件说明：**
- `index.json` — 章节结构，每节含 `id`/`name`，用于渲染侧边栏目录
- `stars.json` — 星级数据，按教材分册组织（如"八年级上册"/"八年级下册"/"九年级全册"），每个知识点 id 对应 1-5 星
- `{id}.json` — 单节内容文件，id 格式如 `5-1`（第五章第1节），字段结构见下方"数据结构"节

## 双视图模式

平台支持两个视图，通过顶部「📖 章节 / 🧠 知识点」切换按钮切换：

**视图切换变量**：
```javascript
let viewMode = 'chapter';  // 'chapter' 或 'knowledge'
```

**切换函数**（直接调用，不要模拟按钮点击）：
```javascript
switchView('knowledge')   // 切换到知识点视图
switchView('chapter')    // 切回章节视图
```

### 章节视图（默认）

左侧两层目录：章节（可折叠）→ 知识点列表。星级显示在每节左侧。年级只顶部显示一次。

### 知识点视图（🧠）

按学科分类体系聚合所有知识点：
- 加载 `data/taxonomy.json` 获取该学科的分类（力学/热学/光学/电学/声学等）
- 遍历 `index.json` 中所有章节的所有 `知识点` 标题
- 用分类关键词匹配决定归属分类
- 每条知识点显示：标题 + 所属章节名 + 星级

**知识点视图侧边渲染函数**：
```javascript
async function renderKnowledgeSidebar() {
  // 遍历 chapterIndex 中所有章节文件，收集知识点
  for (const ch of chapters) {
    for (const sec of sections) {
      const data = await fetch(`data/${currentSubject}/${sec['id']}.json`);
      // 每个知识点的 title + 星级 + 所属章节
    }
  }
  // 按 taxonomy.json 的 keywords 匹配分类
}
```

**加载单个知识点**：
```javascript
async function loadKnowledgePoint(sectionId, pointTitle, el)
function renderKnowledgePoint(point, sectionData, sectionId)
```

## 数据结构（完整按星级分层）

每个 `{id}.json` 的完整字段：

```json
{
  "id": "7-1",
  "name": "第一节 压强",
  "star": 5,

  "引入": { "类比说明": "...", "生活场景": [...] },
  "知识点": [
    {
      "title": "一、压力的作用效果",
      "讲解": "...",
      "关键公式": "p = F/S",
      "生活实例": [...],
      "小实验": { "描述": "...", "配图": "..." }
    }
  ],
  "小结": { "要点": [...], "记忆口诀": "..." },

  "练习":    [{ "question": "...", "options": [...], "answer": 0, "analysis": "..." }],
  "易错题":  [{ "question": "...", "options": [...], "answer": 0, "analysis": "..." }],
  "压轴题":  [{ "question": "...", "options": [...], "answer": 0, "analysis": "..." }]
}
```

### 典型问题结构（章节级）

在 `{id}.json` 中，`典型问题` 放在 `小结` 之后，每个章节可以有 2-4 道：

```json
"典型问题": [
  {
    "question": "汽车急刹车时乘客往前冲，为什么？",
    "分析": "刹车时车减速，但乘客身体因惯性保持原运动状态...",
    "相关知识点": ["7-1", "7-2"],
    "典型模型": "惯性现象模型"
  }
]
```

### 知识点级扩展（重要知识点后）

在 `知识点` 对象的 `讲解` 之后，可选加：

```json
{
  "title": "三、牛顿第一定律",
  "讲解": "...",
  "相关知识点": [
    { "id": "7-2", "name": "二力平衡" },
    { "id": "7-3", "name": "摩擦力" }
  ],
  "典型模型": [
    {
      "name": "光滑斜面滑块模型",
      "描述": "物块沿光滑斜面下滑，不计摩擦，加速度 a = g sinθ",
      "应用场景": "分析斜面运动中力与运动状态的关系"
    }
  ]
}
```

**何时加**：
- 典型问题：每章至少 2 道，放在 `小结` 之后
- 知识点级扩展：只加在重点知识点的 `讲解` 之后（不是每个知识点都加）

**星级内容策略**：

| 星级 | 知识讲解 | 基础练习 | 易错题 | 压轴题 |
|------|---------|---------|--------|--------|
| ⭐1-2 | ✅ 精简版 | ✅ 3题 | ❌ | ❌ |
| ⭐3 | ✅ 完整版 | ✅ 5题 | 标题+空状态 | ❌ |
| ⭐4 | ✅ 完整版 | ✅ 5题 | ✅ 3-4题 | ❌ |
| ⭐5 | ✅ 完整版 | ✅ 5题 | ✅ 4题 | ✅ 2题 |

**练习题渲染逻辑**（renderQuiz）：
```javascript
const star = currentSectionStar;  // 用全局变量，不是 data['star']
// 易错题：star >= 3 显示标题，star >= 4 才提供内容
// 压轴题：star >= 5 才显示
// 各模块题目用不同前缀 id：'basic-0', 'error-0', 'hard-0'
```

**提交答案函数**（submitAnswer）按前缀路由：
```javascript
quizIdx.startsWith('basic-')  → currentSectionData['练习']
quizIdx.startsWith('error-') → currentSectionData['易错题']
quizIdx.startsWith('hard-')   → currentSectionData['压轴题']
```

## 学科分类体系（taxonomy.json）

路径 `data/taxonomy.json`，按学科定义分类和关键词匹配规则：

```json
{
  "物理": {
    "categories": [
      { "id": "mechanics", "name": "力学", "keywords": ["运动", "力", "压强", "浮力", "功", "机械"] },
      { "id": "optics", "name": "光学", "keywords": ["光", "反射", "折射", "成像", "色散"] },
      { "id": "electricity", "name": "电学", "keywords": ["电路", "电流", "电压", "电阻", "欧姆", "电功率"] },
      ...
    ]
  }
}
```

关键词精确匹配知识点的 `title`，匹配到则归入该分类，否则归入"其他"。

## 章节星级数据（stars.json）

路径 `data/{科目}/stars.json`，按教材分册结构：

```json
{
  "八年级上册": {
    "第一章 机械运动": { "1-1": 2, "1-2": 3, "1-3": 4, "1-4": 2 }
  },
  "八年级下册": {
    "第七章 压强": { "7-1": 5, "7-2": 5, "7-3": 4 }
  }
}
```

星级含义：5=高频必考 / 4=重要 / 3=常规 / 2=一般 / 1=了解。

## 日本服务器数据方案
## Japan 服务器数据方案
**架构**：Japan 服务器（`207.56.226.147`，密钥 `~/.ssh/japan`）存储所有教学资料，本地 teaching-platform 读取。

**SSH 连接方式**：
```bash
ssh -i ~/.ssh/japan root@207.56.226.147
```

**数据路径**：`/data/baidu-library/files/初中物理/`

**文件结构**（每章节下分4个子目录）：
```
第9章-压强/
├── 知识点/ (.docx 知识清单，有学生版/教师版)
├── PPT/    (.pptx 课件，含原卷版/解析版)
├── 练习/   (.docx 习题，有学生版/教师版)
└── 测试/   (.docx 单元测试，有原卷版/解析版)
```

**文件总量**：252 个，约 2.8G。格式：.docx/.pptx/.doc。

**SSH 稳定性注意**：有时 SSH 端口 22 会被临时阻断（Connection refused），重试即可恢复。

## 教学流程（4步，用户需求）

用户在 Japan 服务器有完整资料，要求 teaching-platform 实现完整教学流程：

```
① 课前预习 → 展示本节知识点概览（3D模型+文字）
② 讲知识点 → 配套 PPT 课件
③ 配练习   → 按难度★匹配练习题
④ 章节测试 → 章节综合测验
```

**前端新增模块**：
- 课前预习页 — 展示本节知识点概览，可嵌入 3D 模型
- PPT 播放页 — 内嵌 PPT 演示（.pptx 文件路径从 Japan 读）
- 练习/测试页 — 做题，提交后显示答案和解析

### 左侧目录改版（章节视图）

**目标**：侧边栏从四选一的下拉嵌套改为"年级顶部显示一次 + 侧边栏两层（章节→知识点）"。

**实际架构**（2026-06-01 实测纠正）：
```
顶栏：学科 | 教材版本 | 年级 | 册次     ← 年级在顶栏下拉
侧边栏：章节（默认全展开）→ 知识点       ← 只有两层
```

用户感受到"四层"是因为顶栏有4个下拉（学科/教材版本/年级/册次），与侧边栏的两层合计为4次选择操作。改版前必须先确认实际代码结构，不要凭用户描述直接动手。

**核心函数**：
- `renderSidebar()`（行1649-1690）— 渲染侧边栏章节→知识点两层
- `loadChapterIndex()`（行1621-1646）— 加载 index.json，调用 renderSidebar()
- `renderStars(id)` — 行内函数，为知识点渲染星级

**index.json 数据结构**：
```json
{
  "教材": "人教版",
  "学科": "初中物理",
  "年级": "八年级全册",
  "章节": [
    {
      "id": "ch1",
      "name": "第一章 机械运动",
      "知识点": [{"id": "1-1", "name": "第一节 长度与时间的测量"}, ...]
    }
  ]
}
```

**改版方案**（两个可并行做）：
- **方案A**：顶栏去掉"教材版本"下拉，变成：学科 → 年级 → 册次（三步）
- **方案B**：侧边栏章节默认全部展开（去掉折叠箭头），视觉更平铺

**执行流程**：先 PM Agent 分析 → 输出改版方案 → 主人确认 → Dev Director 执行 → QA 验收
（见 lobster-director skill 的 Pipeline 架构流程）

## 日本服务器数据架构（重要）

**当前架构**：日本服务器（`207.56.226.147`，密钥 `~/.ssh/japan`）存储所有教学资料，本地服务器只做展示。

**连接方式**：
```bash
ssh -i ~/.ssh/japan root@207.56.226.147
```

**数据库**（SQLite）：
- 路径：`/data/baidu-library/library.db`
- 表 `materials`：182条资料，含 subject/grade/volume/chapter/material_type/title/file_path 等字段
- 材料类型：PPT(60)、教案(28)、知识点(34)、测试(36)、练习(24)
- 源文件目录：`/data/baidu-library/files/初中物理/...`

**数据迁移待办**：日本服务器需要部署一个 Flask/Node API，本地通过 SSH 隧道访问，PPT 文件通过 API 获取或直接 scp 隧道传输。

## 截图验证标准流程

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
    context = browser.new_context(viewport={"width": 1280, "height": 960})
    page = context.new_page()

    page.goto("http://localhost:18081/index.html", timeout=10000, wait_until="networkidle")
    page.wait_for_timeout(3000)  # 等初始数据加载

    # 切换册次（直接调用JS，不要模拟UI点击）
    page.evaluate("selectVolume('下册')")
    page.wait_for_timeout(1500)

    # 查找特定章节（用 inner_text 匹配，不用元素索引）
    items = page.locator('.section-item').all()
    for item in items:
        if '7-1' in item.inner_text():
            item.click()
            break
    page.wait_for_timeout(1500)

    # 切换Tab（调用全局函数）
    page.evaluate("switchTab(document.querySelectorAll('.content-tab')[1])")
    page.wait_for_timeout(800)

    page.screenshot(path="/tmp/check.png", full_page=False)
    browser.close()
```

**内容文件格式**：见 `references/brain-map-format.md`（brain-map LIST 格式 vs 旧 DICT 格式详解）

## 当前物理内容文件清单（扩展至17章节）

路径：`references/physics-content-files.md`

包含：文件命名规范、扫描缺失文件的Python脚本、内容文件JSON格式（参照11-1）、当前全部知识点文件列表（截至2026-05-28，已达61+个文件）。

## 上传资料清单

路径：`references/uploaded-materials.md`
主人上传了八年级上册第1章的教学材料（教学设计/导学案/速记清单）。已提取文本存于 `docs/materials/8a-physics/extracted-text/`，可用于：填充知识点讲解内容、生成旁白稿、丰富导学案模块。

### systematic.ts 知识点充实流程（本 session 已验证）

从教学设计提取内容、填充 `src/data/systematic.ts` 中 `KnowledgePointDetail` 各字段的标准流程：

**目标文件**：`src/data/systematic.ts`（`knowledgePoints` 数组，每个 `KnowledgePointDetail` 对象）

**需填充的字段**（优先级从高到低）：
1. `definition` — 从教学设计的「定义/概念」部分提取，简洁、学生友好
2. `why` — 从「学情分析/教学重点/教学难点」提取，说明为什么重要
3. `howToUse` — 从「教学过程」中提取操作步骤（测量步骤、计算步骤、解题步骤）
4. `specialCases` — 从「例题/注意」中提取易忽略的边界情况
5. `mistakes` — 从「易错点/学生易错」中提取常见错误（至少3条）
6. `example.prompt` — 用教学设计中的「例题」作为题目
7. `example.solution` — 对应解析和步骤
8. `formula` / `unit` — 从公式和单位教学中提取

**已验证的章节文件映射**：
- `8a-1`（第1章 机械运动）→ 对应 `1.1`~`1.4` 教学设计
  - `8a1-unit-conversion` ↔ 1.1长度和时间的测量
  - `8a1-ruler-reading` ↔ 1.1刻度尺使用
  - `8a1-reference-frame` ↔ 1.2运动的描述
  - `8a1-speed` ↔ 1.3运动的快慢
  - `8a1-average-speed-experiment` ↔ 1.4速度的测量

**更新操作**：用 `patch` 工具对 `systematic.ts` 做精准替换，不要重写整个文件。每个 `KnowledgePointDetail` 对象独立更新。

**Build验证**：更新后执行 `npm run build` 确认无编译错误，再 `curl localhost:18081` 确认服务正常。

**delegate_task 限制**：若 ACP command 不可用，直接用 `terminal` + `patch` 工具手动更新。
主人上传了八年级上册第1章的教学材料（教学设计/导学案/速记清单）。已提取文本存于 `docs/materials/8a-physics/extracted-text/`，可用于：填充知识点讲解内容、生成旁白稿、丰富导学案模块。

## 典型问题与典型模型参考

路径：`references/typical-questions.md`

包含：章节级典型问题结构（示例7-1.json）、知识点级相关知识点+典型模型结构、字段说明、添加流程。

## 前端渲染说明

index.html 已完整实现三个新字段的渲染：

- **相关知识点**（`.related-section`）：知识点的 `讲解` 之后，蓝色胶囊标签展示
- **典型模型**（`.model-section`）：知识点的 `讲解` 之后，卡片式展示（名称+描述+适用场景）
- **典型问题**（`.problem-section`）：章节小结Tab底部，黄色卡片展示（题目+分析+关联知识点+典型模型）

对应CSS已添加（行号约685-730），包括 `.related-section`、`.related-tag`、`.model-section`、`.model-card`、`.problem-section`、`.problem-card` 等类。

渲染验证（Playwright）：
```python
# 切到"章节小结" tab 后检查
for item in page.locator('.section-item').all():
    if '牛顿第一定律' in item.inner_text():
        item.click()
page.locator('.content-tab').all()[2].click()  # 小结tab
content = page.inner_text('#contentBody')
assert '典型问题' in content
assert '相关知识点' in content
assert '典型模型' in content
```

## PPT 幻灯片模式（知识点讲解）

**阶段一（当前）**：纯文本 JSON → 幻灯片翻页
- 来自第一批量产转换（401个PPTX → JSON，文本提取）
- 每页：文本数组渲染为文字块，无图片/动画/格式
- 适合：有文本内容即可的场景

**阶段二（等 PPTX 重新上传）**：LibreOffice 渲染图片 → 幻灯片翻页
- 等主人重新上传原PPTX到 Japan
- 用 LibreOffice 渲染每页为 PNG 图片（保真原版式）
- 图片通过 API 提供给前端 `<img>` 展示
- 适合：课堂讲解（需要图片/图表/动画）

**幻灯片结构**（每知识点 5-7 页）：
| 页码 | 类型 | 内容 |
|------|------|------|
| 1 | 封面 | 知识点标题 + 章节名 + 星级 |
| 2 | 📖 讲解 | 讲解文字 + 关键公式 |
| 3 | ⚠️ 易错点 | 易错题列表 |
| 4 | 📐 典型例题 | 例题 + 答案分析 |
| 5 | ✏️ 课后练习 | 练习题列表 |
| 6+ | 题型（可选） | 重点题型分页 |

**交互**：
- 左下角 ◀ 按钮 / 右下角 ▶ 按钮（图标，无文字）
- 右下角页码 "2 / 5"
- 切换时淡入淡出（opacity transition，200ms）
- 首页时 ◀ 自动禁用，末页时 ▶ 自动禁用

**部署验证**：
```bash
# 确认 PPT 相关 JS 存在
grep -c 'buildPPTSlides\|renderPPTDeck' /home/ubuntu/teaching-platform/index.html
# 返回 > 0 则已部署

# 确认端口可访问
## Japan PPTX→JSON 转换状态（2026-06-01 实测）

**已完成**：401个PPTX → 纯文本JSON，存于 `/data/baidu-library/files/*.json`（扁平，无子目录）

**JSON结构**（每文件）：
```json
{
  "source": "/data/baidu-library/files/.../第一章+机械运动（单元复习课件）.pptx",
  "slides": [
    {"page": 1, "content": ["第一章    机械运动", "八年级上册", "人教版", "..."]},
    {"page": 2, "content": ["纪念币的直径", "细铜丝的直径", "..."]}
  ],
  "total": 66
}
```

**重要限制**：
- ❌ 无图片/动画/字体格式/图表
- ✅ 纯文本课堂讲解够用（翻页展示文字内容）
- 存储节省：2.9GB → 12KB（99.5%压缩）

**JSON查找方式**：文件名 = 原PPTX去掉 `.pptx`，SSH到Japan用 `find /data/baidu-library/files/ -maxdepth 1 -name '*.json'` 查找。

**前端幻灯片播放器**：渲染 `slides[].content` 文本数组，◀▶按钮翻页，每页淡入淡出（200ms）。原PPTX图文物料不可用。

**部署验证**：
```bash
# 确认 PPT 相关 JS 存在
grep -c 'buildPPTSlides\|renderPPTDeck' /home/ubuntu/teaching-platform/index.html
# 返回 > 0 则已部署
```

**关键发现（2026-06-01 实测）**：
- `app.run()` 是阻塞调用。`if __name__ == '__main__': app.run(...)` 之后的代码永远不会执行。Japan 路由必须写在 `if __name__` 之前。
- **Flask test_client 不走真实 server**：在代码里用 `with app.test_client() as client` 测试时，路由注册正常，但实际 `python3 app.py` 启动的端口 5001 服务是不同的进程。验证真实端口必须用 `curl` 或 Python `urllib`，不能用 test_client 的结果来推断端口行为。
- **curl vs urllib URL 编码差异**：对同样的 URL-encoded 路径，`curl` 有时返回 404 而 Python `urllib.request.urlopen` 返回 200。这是因为空格编码在不同 HTTP 客户端的处理方式不同。前端 JS 用 `encodeURIComponent()`（与 urllib 行为一致），所以接口本身没问题，只是 curl 的问题。
- Japan 上的脚本 `/tmp/hermes/parse_pptx_b64.py` 接收 **base64 编码的完整路径**，无 BASE 前缀拼接。直接 `base64.b64decode → zipfile.open`。
- 本地 Flask 需先 `base64.b64encode(full_path)` 再 SSH 传参，避免空格/中文被 shell 截断。
- SSH 直测验证：`ssh -i ~/.ssh/japan root@207.56.226.147 'python3 /tmp/hermes/parse_pptx_b64.py <b64path>'` 成功返回 27 页 JSON。

**⚠️ curl 兼容性注意**：对同样的 URL-encoded 路径，`curl` 有时返回 404 而 Python `urllib.request.urlopen` 返回 200。前端 JS 用 `encodeURIComponent()`（与 urllib 行为一致），所以接口本身没问题。不要用 curl 测试结果推断接口正确性。

**⚠️ PPTX 删除后图片丢失（2026-06-01 教训）**：
- 第一批 401 个 PPTX 被 python-pptx 提取为 JSON 后，原始 PPTX 已删除
- JSON 只含纯文本，图片/动画/字体格式全部丢失
- python-pptx 无法重建图片，只能渲染文字
- **后果**：纯文本 JSON 无法用于"讲给0基础的人听"的课堂，需要图片/图表/动画
- **解决方案**：等主人重新上传 PPTX，改用 LibreOffice 渲染为图片（保留原版式+图片）

**LibreOffice 图片渲染方案（Japan 已装好）**：
```bash
# Japan 上渲染单页 PPTX → PNG
libreoffice --headless --convert-to png --outdir /tmp/slides /path/to/file.pptx
# 生成 /tmp/slides/file.png（每页一张）

# 批量渲染（后台运行）
nohup libreoffice --headless --convert-to png --outdir /data/baidu-library/files/IMG /data/baidu-library/files/*.pptx &
```
- LibreOffice 在 Japan：`/usr/bin/libreoffice`
- pdftoppm（备选）：`/usr/bin/pdftoppm`（poppler-utils 已装）
- python-pptx 已安装：`python3 -m pip install python-pptx Pillow`（2026-06-01 实装）

**扁平知识树改版（核心，用户明确要求）**：
- 用户明确说：不喜欢深层嵌套菜单，当前人教版→年级→章节→知识点四层，要求改成"章节→知识点"两层，年级只顶部显示一次
- 顶栏下拉：学科 → 年级（八年级/九年级）→ 册次（上册/下册/全册）
- 侧边栏：章节名（可点击折叠）→ 知识点列表，两层，无年级维度
- 改版流程：PM Agent 分析 → 输出方案 → 主人确认 → Dev Director 执行 → QA 验收
- QA 必须同时验证章节视图 + 知识点视图，不能只测一个
```python
import urllib.request, urllib.parse, json
path = '初中物理/八年级/上册/第1章-机械运动/PPT/第1课时  长度的单位和测量.pptx'
url = f'http://localhost:5001/api/japan/pptx?path={urllib.parse.quote(path)}'
resp = urllib.request.urlopen(url, timeout=65)
data = json.loads(resp.read())
slides = data.get('slides', [])
print(f'共 {len(slides)} 页')  # 应返回 27
print(data['slides'][0]['texts'][:3])
```

**⚠️ curl 兼容性注意**：对同样的 URL-encoded 路径，`curl` 有时返回 404 而 Python `urllib.request.urlopen` 返回 200。前端 JS 用 `encodeURIComponent()`（与 urllib 行为一致），所以接口本身没问题。不要用 curl 测试结果推断接口正确性。

---

## 架构图

1. **当前架构（2026-06-13 更新）**：Nginx 反向代理 + Flask 后端
   - **公网入口**：`80` → Nginx（静态文件 + API 代理）
   - **静态文件**：`/var/www/teaching-platform/`（由 Nginx 直接服务）
   - **后端 API**：`Flask :5001`（被 Nginx 代理到 `/api/`）
   - **前端源码**：`/home/ubuntu/teaching-platform/`（开发用，需手动 cp 到 nginx root 部署）
   - **physics-visual-platform**：已删除（2026-06-13），其 Three.js/3D 技术可迁移到 teaching-platform

   **nginx 配置**（`/etc/nginx/sites-enabled/teaching-platform`）：
   ```
   :80 → /var/www/teaching-platform/（静态）
   :80/api/* → 代理到 127.0.0.1:5001/api/（Flask）
   ```
   
   **⚠️ 部署注意**：前端修改后必须同时 cp 到 nginx root：
   ```bash
   sudo cp /home/ubuntu/teaching-platform/frontend/{file} /var/www/teaching-platform/frontend/
   ```

2. **改侧边栏结构时需同时检查 renderSidebar() 和知识点视图渲染代码**：
   - `renderSidebar()`（行1632-1672）：章节视图的渲染模板
   - `renderKnowledgeSidebar()`（行约1798）：知识点视图的渲染模板（折叠箭头 + onclick 在这里也有）
   - **本 session 教训**：Dev Director 改了 CSS display:block 但没改知识点视图的 HTML 模板，导致知识点视图仍有折叠箭头。QA 验收时需同时验证两个视图。

3. **delegate_task 改完 index.html 后，必须验证所有渲染路径**：章节视图 + 知识点视图 + 搜索结果展示，三处都要过。
2. **公网访问 vs 本地**：用户说已托管到公网（81.71.93.113），但本地端口 18081 只监听 127.0.0.1，外网访问不到。没有找到 ngrok/cloudflared/frp 隧道工具。**实际排查**：用户浏览器看不到 PPT 效果是因为浏览器缓存了旧版，强制刷新（Ctrl+Shift+R）可解决
2. **下拉选项点击超时**：册次/年级下拉展开 `.dropdown-option` 后直接调用JS函数 `selectVolume('下册')`，不要模拟UI点击
3. **starsData异步**：`selectVolume()` 调用后 `starsData` 是异步重新获取的，需要等 `wait_for_timeout(1500)` 才能读到新值
4. **知识点视图加载慢**：因为要遍历所有章节文件发多个 fetch，需要等 `wait_for_timeout(3000)`
5. **星级来自全局变量**：`currentSectionStar` 在 `loadSection()` 时从 `data['star']` 赋值，不是从 `data['star']` 在各渲染函数里直接读
6. **知识点视图切换**：切换学科/教材/年级/册次时自动切回章节视图（因为 chapterIndex 重新加载）
7. **Playwright调试**：`page.evaluate()` 中 `innerText` 是属性不是方法，应用 `el.innerText`（无括号）
8. **lobster-dev 派错项目**：delegation 时必须明确写出完整路径 `/home/ubuntu/teaching-platform/index.html`，不能只写"教学平台"——上一轮因为没说清楚，lobster-dev 改成了 `physics-visual-platform`（Next.js 项目）而不是 `teaching-platform`（本任务目标）

## 新科目接入流程（已用数学验证，2026-06-02）

1. **准备 stars.json** — 按教材分册组织，每节有独立 ID（如 yw-1-1 = 第一章第1节）
2. **生成 index.json** — 从 stars.json 解析 chapter_num 构造章节 ID（不是直接用章节名），每章的 `知识点` 数组用 section ID 填充
3. **批量生成章节空壳** — 遍历 stars.json，对每个 section ID 生成 `{id}.json`（含 id/name/star/引入/知识点=[]）
4. **先写一个有内容的章节（如 11-1）** — 放在批量生成空壳之前，避免被覆盖
5. **建 brain-map 目录** — 每册一个 LIST 格式文件，供脑图展示（先做一册示范）
6. **后端 API** — 在 `backend/app.py` 物理路由块之后插入新科目路由（7条：index/chapter/knowledge/search/stars/all/brain-map）
7. **重启后端** — `kill` 旧进程 + `background=true` 启动新进程 + `curl` 验证
8. **前端** — 复制 `physics.html` 改科目名 + API endpoint + 数据路径，**同时加入培优模块Tab**
9. **部署到 nginx** — 必须同时 cp 到 `/var/www/teaching-platform/frontend/`
10. Playwright 截图验证
11. 用户验收

**⚠️ 批量生成技巧**：用 Python 脚本直接写 JSON 文件，不要逐个手动创建。section ID 从 stars.json 的 key（如 "yw-1-1"）解析。

**⚠️ 批量生成后端注意**：Flask 路由按插入顺序匹配（先插入先匹配）。确保物理路由在前、新科目路由在后。

**⚠️ 常见遗漏**：只建 data 文件不够，必须同时加后端 API 路由和前端页面。物理在 `backend/app.py` 有 8 条路由，`frontend/physics.html` 是前端入口。数学在 2026-06-02 前只有 data 文件，无 API 路由也无前端。

## 内容文件格式：brain-map 格式（当前标准）

主人明确要求：**选到一节时，点击"知识点"按钮能展示该节的知识点脑图**。

**标准格式**（brain-map list 结构，如 `17-1.json`）：
```json
[
  {
    "id": "17-1-1",
    "title": "磁现象与磁场",
    "type": "knowledge",
    "modelKind": "3d",        // "none" | "3d" — 是否需要3D模型
    "content": "磁现象来源于材料吸引铁、钴、镍等物质的性质。磁体具有磁性，磁体上磁性最强的部位叫磁极...",
    "summary": "磁体周围存在磁场，磁场方向为小磁针北极指向，磁感线可直观描述磁场。"
  },
  {
    "id": "17-1-2",
    "title": "地磁场",
    "type": "knowledge",
    "modelKind": "none",
    "content": "地球本身是一个巨大磁体，地球周围存在的磁场叫做地磁场。地磁场的N极在地球地理的南极附近...",
    "summary": "地球是一个巨大磁体，其周围存在地磁场，使指南针指向北方，保护地球免受宇宙射线损害。"
  },
  {
    "id": "17-1-3",
    "title": "电流的磁效应",
    "type": "knowledge",
    "modelKind": "3d",
    "content": "电流周围存在磁场，这就是电流的磁效应。奥斯特通过实验发现：通电导线周围存在磁场，磁场方向与电流方向有关...",
    "summary": "电流周围存在磁场（奥斯特实验），通过电磁铁可增强磁性并可控。"
  }
]
```

**字段说明**：
- `id`：格式 `{章节号}-{知识点序号}`，如 `17-1-3`
- `title`：知识点标题，简短
- `type`：固定为 `"knowledge"`
- `modelKind`：`"none"` 或 `"3d"` — 有3D模型（如电磁铁、凸透镜）用 `"3d"`
- `content`：详细讲解内容，200-500字，面向零基础学生
- `summary`：一句话总结，30-60字，便于脑图节点展示

**前端渲染**：每个节点渲染为脑图的一个子节点，缩进展示。点击节点展开详情。

**与旧格式的本质区别**：
- 旧格式（1-1.json 等）：DICT 结构，`{引入, 知识点[], 小结, 练习}` — 章节级汇总
- 新格式（17-1.json）：LIST 结构，`[{id, title, content, summary}]` — 知识点级脑图
- **brain-map 格式是当前新建内容的标准**

## 知识点重写优先级与顺序

主人指定顺序（按学科）：
> 语数英 → 物化生 → 政史地

主人指定年级章节顺序，逐个往上做：
> 先每科第一章第一节，再第二节……

**工作流**：
1. 按顺序取一节（如：物理第一章第1节）
2. 按 brain-map 格式生成知识点 list JSON
3. 提交主人校验
4. 有反馈则修改，无反馈则继续下一节
5. 用 lobster 批量生成剩余内容

**每节知识点数**：通常 3-5 个知识点（如物理 1-1 有 4 个：长度单位、长度的测量、时间的测量、误差）。

## PPT 幻灯片渲染方案（两阶段）

### 阶段一：纯文本 JSON（当前可用）
PPTX → python-pptx 纯文本提取 → JSON。401个文件已转换，存于 Japan `/data/baidu-library/files/*.json`。
- ❌ 无图片/动画/格式
- ✅ 翻页展示文字内容够用

### 阶段二：LibreOffice 渲染图片（等原 PPTX 重新上传）
主人说"讲给0基础的人听，光文字不够，要有图片"。等原 PPTX 重新上传后：
1. Japan 上执行：`libreoffice --headless --convert-to png --outdir /data/baidu-library/files/IMG *.pptx`
2. 前端 `<img src="API返回的图片URL">` 展示

**Japan 已具备条件**（2026-06-01 安装）：
- LibreOffice：`/usr/bin/libreoffice`
- pip + python-pptx + Pillow：已安装
- pdftoppm（备选）：已装

## 数学 data 文件状态（2026-06-02 更新）

**当前已完成的数学 data 文件（2026-06-02 session）**：
- `data/数学/index.json` — ✅ 正确的 index 结构（29章，每章含 nested 知识点数组）
- `data/数学/{id}.json` — ✅ 87个章节空壳文件（批量生成，1-1.json ~ 29-3.json）
- `data/数学/11-1.json` — ✅ 有完整内容（DICT格式，含引入+知识点+关键公式+生活实例）
- `data/数学/stars.json` — ✅ 已存在（29章节星级数据，87个节级ID）
- `data/数学/brain-map/八年级上册.json` — ✅ brain-map LIST格式（6个知识点）
- `backend/app.py` — ✅ 数学API路由已添加（7条：index/chapter/knowledge/search/stars/all/brain-map）
- `backend` 服务进程 — ✅ 已重启验证，API全部正常
- `frontend/math.html` — ✅ 新科目前端页面（含年级Tab+章节视图+培优模块），已同步到 nginx root

**⚠️ index.json 生成技巧**：不能用 stars.json 的 key 直接做章节 ID——stars.json 的 key 是章节名（"第一章 有理数"），需要从 section ID（"yw-1-1"）解析出 chapter_num 来构造正确的章节 ID。正确做法：
```python
# 从 stars.json 的第一 section key 解析 chapter num
first_section = list(sections.keys())[0]  # "yw-1-1"
chapter_num = first_section.split("-")[1]  # "1"
section_num = first_section.split("-")[2]  # "1"
chapter_id = f"{chapter_num}-{section_num}"  # "1-1"
```

**⚠️ 后端代码修改后必须重启服务**：Flask 在 `if __name__ == '__main__':` 中用 `app.run()` 启动是阻塞调用，修改 `app.py` 后必须 kill 旧进程再启动新进程才能生效。验证用 `curl`（不是 test_client），因为两者 URL 编码行为不同。

**⚠️ 批量生成会覆盖已有内容**：Python 批量生成脚本会重写所有 section JSON 文件（覆盖），所以必须先生成 index.json，再写一个有内容的章节（如 11-1.json），再批量生成空壳文件（脚本检查已存在则跳过已有内容的文件——需在脚本里加这个逻辑，避免覆盖已有完整内容）。

## 培优模块（2026-06-02 新增需求）

主人要求在前端 math.html（新科目前端的标准结构）增加"培优模块"——探讨相关知识点的问题（如拓展思考、竞赛级别问题、跨章节综合题）。

**培优模块位置**：放在知识点详细页Tab中，与"讲解/小结/练习"并列或作为子模块。

**内容方向**：
- 知识点的深度追问（"如果…会怎样？"）
- 竞赛级别的问题
- 跨章节综合应用
- 易混概念对比辨析

**渲染风格**：与原有知识点风格统一，培优标签可用金色/橙色突出。

## Japan 服务器 pip 安装（历史记录）

Japan 服务器默认无 pip，已用以下方法安装（2026-06-01）：
```bash
curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py
python3 -m pip install python-pptx Pillow
```
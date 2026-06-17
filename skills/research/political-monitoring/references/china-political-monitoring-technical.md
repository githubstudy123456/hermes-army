# 政治监测 · 技术笔记（2026-06 实测）

## gov.cn 三通道 + 联播页优先级

| 通道 | URL | 内容 | 稳定性 |
|------|-----|------|--------|
| 要闻列表 | `gov.cn/yaowen/liebiao/` | 头条/新闻报道 | ⚠️ urllib 超时 |
| 政策文件库 | `gov.cn/zhengce/zhengceku/gwywj/` | 国发/国办发/部门重要文件 | ⚠️ urllib 超时 |
| **联播页** | `gov.cn/lianbo/index.htm` | **新闻+政策文件统一视图** | ✅ Playwright CDP 4s |
| gov.cn 首页 | `gov.cn/` | 滚动要闻 | 可用 |

**推荐流程**：优先访问 `/lianbo/index.htm`，一次获取新闻报道+政策文件两类链接。
联播页会混合展示来自 `/yaowen/liebiao/` 和 `/zhengce/zhengceku/` 的文章。

## Playwright CDP 连接（唯一稳定方案）

urllib 直读 gov.cn 系列在 cron 环境超时/SSL 错误率 >50%。**唯一可靠方案**：

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://www.gov.cn/lianbo/index.htm", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(4000)  # 联播页需要4秒加载
    # 提取混合文章列表
    articles = page.eval_on_selector_all("a", "els => els.filter(e => e.href && e.href.includes('gov.cn/yaowen/liebiao') && e.href.includes('content_')).map(e => ({t:e.innerText.trim(),u:e.href}))")
    browser.close()
```

## 文章列表提取选择器

```python
# 联播页/要闻列表页（过滤出含 content_ID 的文章链接）
"els => els.filter(e => e.href && e.href.includes('gov.cn/yaowen/liebiao') && e.href.includes('content_')).map(...)"

# 政策文件库（过滤 zhengce 路径）
"els => els.filter(e => e.href && e.href.includes('gov.cn/zhengce') && e.href.includes('content_')).map(...)"
```

注意：不要用 `page.evaluate()`，它在 sandbox 环境报 `Illegal return statement`。

## 文章正文提取（按类型区分）

### 新闻报道类（/yaowen/liebiao/）
标题/正文选择器可用：
```python
title = page.eval_on_selector("h1, h2, .title", "el => el.innerText.trim()")
paragraphs = page.eval_on_selector_all("p", "els => els.map(e=>e.innerText.trim()).filter(t=>t.length>30)")
```

### 政策文件类（/zhengce/zhengceku/content_XXX）
`h1, h2, .title` 超时30s。**改用 inner_text 全页**：
```python
text = page.inner_text("body")
lines = [l.strip() for l in text.split('\n') if l.strip()]
title = lines[0]  # 通常是标题
content = '\n'.join(lines[1:50])  # 正文段落
```

## content_ID 语义

```
content_7072046 → 2026年6月14日 要闻第4篇（高ID=更新）
content_7072002 → 2026年6月11日 政策文件
content_7071979 → 2026年6月10日 政策文件
```

gov.cn content ID 递增规则：同一日多篇连续递增，ID越高越新。

## 关键词信号分类（原文判断）

**P1级（立即推送）**：
- 政治局、政治局会议、政治局常委
- 国发、国办发、中发、中办发
- 降准、降息（货币政策重大信号）
- 习近平（重要场合讲话）

**P2级（重要，摘要推送）**：
- 国务院常务会议
- 各部委联合发文（10部委以上）
- 重要领导人调研讲话

**P3级（一般政策，常规推送）**：
- 国务院部门文件（单部委或双部委）
- 地方政策（不入推送，除非重大）
- 一般会议/活动

## 推送文件命名规范

```
YYYY-MM-DD_P{priority}_{content_id}_{标题前15字}.txt
例：2026-06-15_P3_7072002_关于印发《推动新能源重卡规模化.txt
```

路径：`~/.hermes/political-reports/`

## 已知踩坑

1. **urllib 读 gov.cn 超时**：SSL兼容问题，浏览器CDP直连是唯一方案
2. **联播页 wait_for_timeout(3000)不够**：页面JS加载慢，设4000ms
3. **政策文件页标题选择器超时**：直接 `page.inner_text("body")` 全页读取
4. **gov.cn 搜索参数失效**：`?searchword=...` 重定向到首页，直接访问列表页
5. **content_ID 去重**：今日已有 content_ID 列表 → 跳过静默

## 新浪财经政经 API（补充来源）

当 gov.cn 不可用时作降级：
```python
url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&k=&num=20&page=1'
# lid=2517 → 国内财经政经（经济监测专用，非政治）
```

仅用于经济监测，P0/P1政治事件必须走 gov.cn。
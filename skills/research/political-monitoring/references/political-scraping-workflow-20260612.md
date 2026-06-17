# 政治监测采集工作流踩坑笔记（2026-06-12 实测）

## 核心结论

Bing `site:` 搜索在 cron 环境**完全失效**（每次返回 0 results）。gov.cn 直接 `browser_navigate()` 超时 60s。**唯一可靠方案**：Playwright CDP 导航 + 提取首页链接列表。

---

## 踩坑记录

### ❌ Bing `site:` 搜索 — 失效
```
Query: site:xinhuanet.com 政治局会议 -> 0 results
Query: site:gov.cn 国务院 文件 2026 -> 0 results
Query: site:people.com.cn 习近平 重要讲话 -> 0 results
```
- 所有 site: 查询返回 0 结果
- 原因：服务器环境下 Bing 返回空页面或触发滑块验证
- **结论**：政治监测 cron 放弃 Bing 搜索

### ❌ gov.cn 直接 navigate 超时
- `browser_navigate('https://www.gov.cn/lianbo/index.htm')` → 超时 60s
- `browser_navigate('https://www.gov.cn/site_7/6917580.htm')` → 404
- **绕过**：gov.cn 首页本身可访问（`www.gov.cn`），但子页面 URL 无法预测

### ❌ 新浪财经政经 API（lid=2517）
- 返回 20 条全为美股/SPACE X/港股资讯
- **不适合国内政策监测**，仅作财经市场情绪参考

---

## ✅ 可靠工作流（实测可行）

### Step 1: Playwright CDP 连接
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.new_page()
```

### Step 2: gov.cn 首页提取政策链接
```python
page.goto("https://www.gov.cn", timeout=30000, wait_until="domcontentloaded")
page.wait_for_timeout(3000)

items = page.eval_on_selector_all("a[href]",
    "els => els.filter(e=>e.href && e.innerText.length > 15 && e.innerText.length < 100 && e.href.includes('gov.cn')).slice(0,20).map(e=>({t:e.innerText.trim(),u:e.href}))")
```

### Step 3: people.com.cn 首页补充
```python
page.goto("https://www.people.com.cn/", timeout=30000, wait_until="domcontentloaded")
page.wait_for_timeout(3000)
```

### Step 4: 访问具体文章
```python
page.goto("http://politics.people.com.cn/n1/2026/0612/c1024-40738743.html",
    timeout=30000, wait_until="domcontentloaded")
page.wait_for_timeout(3000)
title = page.inner_text("h1")
body = page.inner_text("body")  # 不走 JS eval，直接拿 body
# 截取前 3000 字符去掉页眉页脚
```

---

## 已验证可用信息源

| 来源 | 路径 | 状态 |
|------|------|------|
| 中国政府网要闻列表 | `www.gov.cn/yaowen/liebiao/` | ✅ 稳定 |
| 中国政府网政策文件库 | `www.gov.cn/zhengce/xxgk/zzqx/` | ✅ 表格结构 |
| 新华网时政 | `www.xinhuanet.com/politics/` | ✅ |
| 新华网中央文件 | `www.news.cn/politics/zywj/index.htm` | ✅ |
| 中国政府网首页 | `www.gov.cn` | ✅ |
| 新浪财经API lid=2517 | `feed.mix.sina.com.cn/api/roll/get?lid=2517` | ❌ 仅美股 |

## 已确认不可用

| 路径 | 问题 | 替代 |
|------|------|------|
| `www.gov.cn/lianbo/index.htm` | 超时60s | `yaowen/liebiao/` |
| `www.gov.cn/site_7/xxxx.htm` | 404 | 从首页提取真实URL |
| Bing `site:` 查询 | 返回0结果 | 放弃搜索，直连站点 |

---

## 去重检查

已有报告位置：`~/.hermes/political-reports/`
- 文件命名格式：`2026-06-12_1230_political.txt`
- 检查逻辑：对比标题相似度 >70% 则跳过
---
name: xcrawl-news-gatherer
description: 网页抓取工具箱 - xcrawl / crawl4ai / firecrawl / scrapy+playwright / browser-use 对比选型。XCrawl Search/Scrape API 替代代理抓取网页内容，支持 JS 渲染页面和被墙站点。关键词搜索模式替代现有 RSS 轮询。
tags: []
related_skills: []
content: ---

# xcrawl-news-gatherer

网页抓取工具箱 - 按场景选型

---

## 工具对比速览

| 工具 | 费用 | 适合场景 | GitHub |
|------|------|----------|--------|
| **xcrawl** | 按 credit 付费，1000 credits = 个人用一个月 | 需要搜索 API、绕过反爬、JS 渲染页 | 商业 SaaS |
| **crawl4ai** | 免费开源 | LLM 专用，把网页转成 markdown | 30K+ stars |
| **scrapy + playwright** | 免费开源 | 复杂动态网站、需完整控制 | 成熟框架 |
| **firecrawl** | 国外 SaaS，免费额度够个人项目 | 整站爬取、sitemap 驱动 | 商业 SaaS |
| **browser-use** | 免费开源 | 让 LLM 操控真实浏览器做任务 | 50K+ stars |

---

## 一、xcrawl（按 credit 付费）

### 核心用途
XCrawl Search API：给定关键词，返回结构化搜索结果（标题/摘要/链接/来源），无需代理、不触发反爬。

### API 信息
- **基础 URL**: `POST https://run.xcrawl.com/v1/search`
- **Python SDK**: `pip install xcrawl-py`
- **认证**: `Authorization: Bearer <API_KEY>`
- **注册送 1000 credits**: https://xcrawl.com/?keyword=jtkhxssi
- **消耗**: ~2 credits/请求，1000 credits 够个人项目一个月

### Python SDK 正确用法（已知问题）

`xcrawl-py` SDK 内部用 urllib，不支持 SOCKS 代理。**推荐用 curl subprocess 方案（更可靠）：**

```python
import subprocess, json

API_KEY = "xc-YOUR_KEY"

def xcrawl_search(query, limit=5):
    body = json.dumps({"query": query, "limit": limit})
    cmd = [
        "curl", "-s", "--socks5-hostname", "127.0.0.1:10808",
        "-X", "POST", "https://run.xcrawl.com/v1/search",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", body,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    data = json.loads(r.stdout)
    if data.get("status") == "completed":
        return data.get("data", {}).get("data", [])
    return []
```

**SDK 已知坑：**
- `XcrawlClient.search({"query": ..., "limit": 5})` 参数是单个 dict，不是关键字参数
- 返回值是 plain dict，不是对象（`.results` 属性不存在，用 `resp.get("data",{}).get("data",[])`）
- Credits 实际消耗 **2 credits/请求**（不是文档说的 1）

**curl 方案已知坑：**
- `-H "Bearer $API_KEY"` = 缺少 `Authorization:` 前缀返回 403
- 必须用 `--socks5-hostname` 而不是 `-x socks5://`（DNS 也要走代理）

### Response 字段
| 字段 | 说明 |
|------|------|
| `search_id` | 任务 ID（可查询状态） |
| `status` | done / pending |
| `results[].title` | 结果标题 |
| `results[].url` | 结果链接 |
| `results[].description` | 摘要 |
| `results[].source` | 来源域名 |
| `results[].published_date` | 发布日期 |

### 接入现有脚本的方法

#### 方案 A：Search API 替代轮询（推荐用于新闻监控）
```python
import os
from xcrawl import XcrawlClient
client = XcrawlClient(api_key=os.environ.get("XCRAWL_API_KEY", "xc-YOUR_KEY"))

keywords = ["China politics news", "global economy", "US China relations"]
all_results = []
for kw in keywords:
    resp = client.search({"query": kw, "limit": 5})
    results = resp.get("data", {}).get("data", [])
    all_results.extend(results)
```

#### 方案 B：Scrape API 抓具体页面
用于抓取有 JS 渲染的页面。Scrape API 对反爬强的站点（Weibo/Twitter/Allkpop）返回空 content，此时应改用 Search API 绕过。

```python
scrape_resp = client.scrape("https://weibo.com/searchs?q=宋雨琦")
md = scrape_resp.get("markdown", "")
if not md:
    # 降级到 Search API
    search_resp = client.search({"query": "宋雨琦 微博", "limit": 5})
    results = search_resp.get("data", {}).get("data", [])
```

#### 方案 C：定时抓 + Webhook 回传
XCrawl 支持 webhook，配置后抓取完成自动回调 Hermes Agent，无需轮询。

### 替代现有脚本的场景
| 现有脚本 | XCrawl 优势 |
|---------|------------|
| `political-news.py`（BBC/观察者网） | Search API 搜关键词，绕过 BBC RSS 被墙问题 |
| `biz-news.py`（BBC+FT+36kr） | 36kr 无 RSS，Search API 可补 |
| `kpop-news.py`（Soompi RSS） | **XCrawl 是 K-pop 监控的救星**：Allkpop 被 Cloudflare 保护，RSS 抓不到；XCrawl Search API 可绕过 |

### K-pop 新闻监控实战参数（已验证）
| 目标 | 推荐 query | 备注 |
|------|-----------|------|
| aespa 巡演 | `"aespa 2026 world tour"` | 搜到 IG 官方帖子 |
| BLACKPINK 动态 | `"BLACKPINK 2026 news"` | Met Gala 2026 等 |
| NewJeans 回归 | `"NewJeans 2026 comeback"` | 成功绕过 Allkpop |
| IVE 巡演 | `"IVE 2026 tour"` | North America + Asia |
| Allkpop 头条 | `"site:allkpop.com K-pop 2026"` | 5 条结果，Cloudflare 绕过 |
| 微博热搜 | `"微博热搜 今日"` | 微博聚合页 |
| Twitter K-pop | `"K-pop 2026 site:twitter.com"` | 搜成员/官推 |

### 已知限制
- Search API 是**搜索引擎结果**，不是原页面内容；需要原页面详情用 Scrape API
- Scrape API 对反爬强的站点（Weibo/Twitter/Allkpop/Naver）返回空 content
- `location` 参数含 "CN" 或 "China" 会导致 Search API failed，不带 location 参数反而正常
- 国内访问 `run.xcrawl.com` 可能需要代理

---

## 二、crawl4ai（免费开源，30K+ stars）

LLM 专用爬虫，把网页转成干净的 markdown。

### 核心特点
- 把 HTML 转成 markdown，LLM 直接可读
- 支持 JS 渲染（内置 playwright）
- 速度快，适合批量抓取
- 免费，自托管

### 安装
```bash
pip install crawl4ai
# 或 docker
docker run -p 8000:8000 parrot研发中心/crawl4ai
```

### 基本用法
```python
from crawl4ai import WebCrawler

crawler = WebCrawler()
result = crawler.crawl("https://news.example.com/article")
print(result.markdown)  # 直接输出 markdown
print(result.json)      # 或结构化 JSON
```

### 适用场景
- 批量抓取文章/新闻转 markdown 给 LLM 处理
- 需要快速获取页面核心内容，不需要完整 HTML
- 替代 firecrawl 的免费方案

---

## 三、scrapy + playwright（免费，经典组合）

适合复杂动态网站，完整控制抓取流程。

### 核心特点
- scrapy：异步爬虫框架，分布式、管道处理
- playwright：浏览器自动化，处理 JS 渲染
- 两者结合：scrapy 负责调度，playwright 负责渲染
- 完全免费，自托管

### 安装
```bash
pip install scrapy playwright
playwright install chromium
```

### 基本架构
```python
import scrapy
from playwright.sync_api import sync_playwright

class DynamicPageSpider(scrapy.Spider):
    name = "dynamic_spider"
    
    def parse(self, response):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(response.url)
            page.wait_for_selector(".article-content")
            content = page.text_content(".article-content")
            yield {"text": content}
```

### 适用场景
- 需要完整爬虫功能（去重、存储、分布式）
- 复杂网站需登录、滑动验证
- 长期运行的抓取任务

---

## 四、firecrawl（国外 SaaS，免费额度够个人项目）

整站爬取专家，sitemap 驱动，适合做知识库。

### 核心特点
- 输入 URL，自动发现整站所有页面
- 输出 markdown / HTML
- 支持 JS 渲染
- 有免费额度，自托管也可用开源版本

### 安装 & 用法
```bash
npm install -g firecrawl-sdk
```

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-YOUR_KEY")
# 抓取整站
result = app.crawl_url("https://example.com", limit=10)
# 搜索
results = app.search("what is ai", limit=5)
```

### 适用场景
- 把网站内容导入知识库
- 批量抓取某话题相关内容
- 替代 LangChain 的 UnstructuredURLLoader

---

## 五、browser-use（免费开源，50K+ stars）

让 LLM 操控真实浏览器做任务，视觉+动作一体化。

### 核心特点
- LLM 直接控制浏览器完成多步任务
- 支持截图、点击、输入、滚动
- 适合需要"观察+决策+操作"的复杂场景
- 50K+ GitHub stars，增长迅猛

### 安装
```bash
pip install browser-use
```

### 基本用法
```python
from browser_use import Agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
agent = Agent(task="帮我搜一下今天天气，然后告诉我该穿什么", llm=llm)
result = agent.run()
```

### 适用场景
- 需要视觉判断的复杂任务（比爬虫更高级）
- 多步操作：登录 -> 搜索 -> 点击 -> 提取
- 替代人工操作：自动填表、自动抢购
- 需要实时观察页面状态的场景

### 与其他工具的区别
- **crawl4ai** = 读页面内容（一次性）
- **browser-use** = 做页面任务（多步交互）
- 如果只是抓文章 -> crawl4ai
- 如果需要像人一样操作浏览器 -> browser-use

---

## 选型决策树

```
需要干什么？
│
├── 批量抓文章/新闻，转 markdown 给 LLM
│   └── crawl4ai（免费，快）
│
├── 搜关键词，返回搜索结果列表
│   └── xcrawl Search API（按 credit）
│
├── 整站内容导入知识库
│   └── firecrawl（sitemap 驱动）
│
├── 复杂动态网站，需完整爬虫框架
│   └── scrapy + playwright（免费，功能全）
│
└── 需要像人一样操作浏览器（多步/视觉判断）
    └── browser-use（免费，50K stars）
```
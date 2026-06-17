---
name: kpop-news-push
description: "定时监控韩国女团最新动态并推送到飞书群。适用于 aespa、BLACKPINK、NewJeans、IVE、LE SSERAFIM、Red Velvet、TWICE 等韩团资讯推送场景。"
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [cron, feishu, kpop, 韩国女团, 新闻推送]
prerequisites:
  skills: []
---

# K-POP 女团资讯推送

定时搜索韩国女团最新动态并推送到飞书群。

## 触发条件

用户要求创建韩团资讯定时推送任务时使用，包括：
- "推送某女团最新消息"
- "每天/每周推送韩团资讯到飞书群"
- 任何涉及 aespa、BLACKPINK、NewJeans、IVE、LE SSERAFIM、Red Velvet、TWICE 的新闻推送需求

## 目标团体列表

```
aespa / BLACKPINK / NewJeans / IVE / LE SSERAFIM / Red Velvet / TWICE
```

## 搜索策略（2026年5月实测）

### 1. Bing 搜索 RSS（首选，实测有效）

**URL 模板：**
```
https://www.bing.com/search?q={团体名}+kpop&format=rss
```

使用 `Scrapling` + `StealthyFetcher`（headless Chrome）抓取，避免被 Cloudflare 拦截：

```python
from scrapling.fetchers import StealthyFetcher

GROUPS = [
    ('aespa', 'aespa'),
    ('BLACKPINK', 'BLACKPINK'),
    ('newjeans', 'NewJeans'),
    ('ive', 'IVE'),
    ('lesserafim', 'LESSERAFIM'),
    ('red velvet', 'Red+Velvet'),
    ('twice', 'TWICE'),
]

fetcher = StealthyFetcher()
url = f"https://www.bing.com/search?q={query}+kpop&format=rss"
page = fetcher.fetch(url, headless=True,
                     executable_path='/usr/bin/google-chrome',
                     browser_type='chromium', timeout=20000)
xml_text = page.body.decode('utf-8', errors='ignore')
```

**解析 RSS：**
```python
import xml.etree.ElementTree as ET
root = ET.fromstring(xml_text)
for item in root.findall('.//item'):
    title = item.find('title').text or ''
    link = item.find('link').text or ''
```

**去重逻辑：** 用 `link` 而非 `title[:50]` 去重（title 前50字符会误判跨组重复）。

### 2. Soompi RSS（次选，但实测返回空内容）

```
https://www.soompi.com/feed/
```

curl 可直连，但解析后 item 列表为空——Soompi 对无 User-Agent 的请求返回空内容。已不可靠。

### 3. 必须过滤的低质量来源

- `zhihu.com/question` — 知乎问答，非新闻
- `wikipedia.org` — 百科页面
- `shop.` / `music.com` — 周边/音乐商店
- `baidu.com` — 百度系（误匹配 BLACKPINK → 火绒安全）
- `allkpop.com` — Cloudflare 防护，Scrapling headless 也被拦截

### 4. 成员名搜索（某团无结果时的最后手段）

| 团体 | 成员名 |
|------|--------|
| BLACKPINK | Jisoo, Jennie, Lisa, Rosé |
| NewJeans | Minji, Hanni, Danielle, Haerin, Hyein |
| IVE | Wonyoung, Yujin, Gaeul, Rei, Liz, Leeseo |
| TWICE | Nayeon, Jeongyeon, Momo, Sana, Jihyo, Tzuyu |
| Red Velvet | Irene, Seulgi, Joy, Yeri, Wendy |
| aespa | Karina, Giselle, Winter, Ningning |

## 已知不可用来源（2026年5月实测）

| 来源 | 原因 |
|------|------|
| Allkpop (allkpop.com) | Cloudflare Bot Protection，Scrapling headless 也无法访问 |
| Soompi RSS | curl 有内容但 Python 解析为空 |
| Google News RSS | 完全无法直连（curl 返回 000） |
| Naver 新闻 | 返回网站框架，无实际数据 |
| 知乎 | 仅问答/百科内容，无实时新闻 |
| Bing 国际版 cn.bing.com | 会 302 重定向到国内版，污染结果 |

## 输出格式

去掉链接，只保留标题和日期：

```markdown
# 🇰🇷 韩国女团每周资讯
**推送时间：** {日期}
**来源：** Bing News（48小时内）

1. 【aespa】aespa announces 2026-27 World Tour across global cities
   📅 Fri, 01 May 2026 16:31:00 GMT

2. 【newjeans】如何看待newjeans宣布解除合约？
   📅 Tue, 28 Apr 2026 11:13:00 GMT
```

最多保留 50 条，按 link 去重后输出。

## Cron 调度配置

**推荐方式：脚本写文件 → cron 系统检测到新文件自动推送**

不要依赖 `cron run` 触发内容执行（`cron run` 只重新排期，不实际触发调度器）。

```bash
# cron job 配置
job_id: 6706b1d82b7d
schedule: "0 18 * * 6"  # 每周六下午6点
script: kpop-news.py     # 脚本写入 output 目录即可触发推送
deliver: feishu:oc_c6883cd907e4d226736d87ce9c6c6d79
```

**脚本写法：**
```python
OUTPUT_DIR = os.path.expanduser("~/.hermes/cron/output/6706b1d82b7d")
os.makedirs(OUTPUT_DIR, exist_ok=True)
# ... 抓取完成后 ...
with open(os.path.join(OUTPUT_DIR, f"{timestamp}.md"), 'w') as f:
    f.write(content)
print(content)  # stdout 也输出，供调试
```

**cron run 陷阱：**
- `cron run` 只是把任务重新加入调度队列，不会立即执行
- 实际触发要等 gateway 内置调度器下次 tick，或手动发消息让 gateway 唤醒

## 飞书群

目标群：`oc_c6883cd907e4d226736d87ce9c6c6d79`

## 网络环境说明

此服务器直连部分国际网络受限：
- Google News / Wikipedia / Allkpop — 无法直连
- Bing 搜索 RSS — 直连正常（cn.bing.com 会被重定向，用 www.bing.com）
- Soompi RSS — curl 有响应但 Python 解析为空
- 知乎 / 微博 — 可访问但内容非新闻

**不需要配置代理即可访问 Bing RSS。**

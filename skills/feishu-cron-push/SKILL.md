---
name: feishu-cron-push
description: 飞书群定时内容推送全集 — 城市活动、网站文章/周报、K-pop女团资讯。通用cron+爬虫+飞书推送模式。
tags: [cron, feishu, push, 爬虫, 内容聚合, 定时任务, 调研日报]
category: productivity
version: 1.0.1
---

# 飞书群定时内容推送

城市活动推送、网站文章/周报、K-pop女团资讯 — 三类定时内容推送到飞书群，共享相同的cron+爬虫+飞书推送模式。

---

## 飞书平台操作 — 底层 API 与消息机制

> 本节由 `feishu-messaging` 技能合并而来。飞书定时推送（上一节）和飞书底层操作（本节）共享相同的认证体系、文件上传逻辑和错误码。

### 认证（所有飞书API的通用起点）

```python
import urllib.request, json

APP_ID = "cli_a95612fc9ebddbc8"
APP_SECRET = "TBNvucvbHCHTeKqYtQ7PGfu1ANe0FSmb"

def get_feishu_token() -> str:
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode()).get("tenant_access_token", "")

token = get_feishu_token()
```

> ⚠️ **两种推送模式的区别（踩坑记录）：**
> - **Webhook 模式**（`/open-apis/bot/v2/hook/`）：机器人类型应用可用，但需要 chat_id 作为路径参数，且 content 格式不同。**已废弃**，使用会报 `19001 param invalid: incoming webhook access token invalid`。
> - **Tenant API 模式**（`/open-apis/auth/v3/tenant_access_token/` + `/open-apis/im/v1/messages`）：正确方式，所有脚本推送必须用这个。content 字段需要 `json.dumps({"text": text})` 双重序列化。

### 发送文件 — MEDIA标签（最简方式）

在回复中包含 `MEDIA:文件绝对路径` 标签，gateway 自动识别并发送文件：

```
这是文字内容...

MEDIA:/home/ubuntu/source/AI提示词库完整版.md
```

gateway 内部流程：`extract_media()` → `adapter.send_file(chat_id=source.chat_id, file_path=media_path)` → `FeishuAdapter.send_document()`

飞书/Telegram/Discord 均支持 MEDIA 标签机制。

### 发送文件 — curl三步上传

飞书文件发送必须分两步：**上传获取 file_key → 再发送消息**。

```bash
# 1. 获取 tenant access token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id": "cli_xxx", "app_secret": "xxx"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# 2. 上传文件，获取 file_key
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=stream" \
  -F "file_name=文件名.md" \
  -F "file=@/path/to/file;type=text/markdown" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['data']['file_key'])")

# 3. 发送文件消息（必须有 receive_id_type=chat_id 查询参数！）
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receive_id": "oc_group_chat_id", "msg_type": "file", "content": "{\"file_key\": \"'$FILE_KEY'\"}"}'
```

**⚠️ 关键坑：receive_id_type 参数必须作为查询参数，不加会报 `99992402 field validation failed`。**

### 创建文档（docx v1）

创建并写入云文档，支持 Markdown 转 Feishu 块格式：

```python
create_resp = json.loads(run_curl(
    "POST",
    "https://open.feishu.cn/open-apis/docx/v1/documents",
    headers=auth,
    data=json.dumps({"title": "文档标题"})
))
doc_id = create_resp["data"]["document"]["document_id"]
```

Markdown → Feishu 块格式（paragraph 块字段名是 `text`，不是 `paragraph`，与 Notion API 的核心区别）；每批最多 50 个 block。

### 群组 Bot 通信 — 找open_id和@mention

- 找 Bot 的 open_id：从 gateway 日志 `grep "oc_c6883cd907e4d226736d87ce9c6c6d79" /tmp/openclaw/openclaw-*.log | grep "received message from"`
- 发送时正确@mention格式：必须用 `<at user_id="ou_XXXX">BotName</at>` XML标签，纯文本 `@BotName` 无效
- Bot 不在群里导致 230002：改用 OpenClaw 的飞书账号发送

### 已知飞书 App ID 速查

| App | AppId | 用途 |
|-----|-------|------|
| Hermes | `cli_a95612fc9ebddbc8` | Hermes Agent 自己的飞书 bot |
| OpenClaw | `cli_a954ec0730b85bc9` | OpenClaw gateway |
| 龙虾军团 | `cli_a96b530405785bde` | lobster-ceo |
| lobster-dev | `cli_a96b4b3f0d381bcf` | |
| lobster-pm | `cli_a96b4a83dd7c5bd6` | |
| lobster-qa | `cli_a96b4b852ce31bde` | |
| lobster-content | `cli_a96b4be3c73a9bcf` | |
| lobster-marketing | `cli_a96b4468633a9bda` | |
| lobster-fullstack | `cli_a96b44c8ae7adbd8` | |
| lobster-cfo | `cli_a96ec9e03af89bca` | |

**大姐姐群** chat_id：`oc_c6883cd907e4d226736d87ce9c6c6d79`
**龙虾军团群** chat_id：`oc_8c4fa359fd2f4278307a435ee3826dac`

### 常见错误码

| code | 原因 |
|------|------|
| 1770001 | block 格式错误，检查是否用了 `text` 而非 `paragraph` |
| 99992402 | 每批超过 50 个 block，或缺少 receive_id_type 查询参数 |
| 10014 | APP_SECRET 无效 |
| 230002 | Bot 不在群组里 |
| 99992361 | open_id 属于另一个 app（cross app） |

---

## 通用飞书推送参数

| 参数 | 值 |
|------|-----|
| 目标群 | `oc_c6883cd907e4d226736d87ce9c6c6d79` |
| cron deliver | **`local`**（脚本自己调飞书 API，不走文件检测推送） |

> ⚠️ **所有格式化文本推送（日报/周报/精选）必须用 `deliver=local`**。cron 的 `deliver=feishu:oc_xxx` 走文件检测模式，飞书收到的是原始 markdown 而非渲染内容。用户看到的推送格式混乱、无法辨认粗体/分隔线等。**正确做法：cron job 的 `deliver` 改为 `local`，脚本末尾自行调用飞书 API 推送。**

## 通用故障排查

## 颜值体系每日推送 — beauty-daily-push

**触发：** 用户要求用颜值体系文档替换原有每日体态训练推送，或修改 cron 内容循环。

### 内容源 — 颜值体系7文档

```
~/.hermes/cache/documents/
├── doc_43df592c41e0_00颜值体系总览.md
├── doc_b5857bc5ddb7_01颜值原理解析.md
├── doc_c7f1a51e582b_02身材管理详解.md
├── doc_33aabb281d23_03皮肤护理详解.md
├── doc_2937558a98b2_04穿搭美学详解.md
├── doc_7d5013d1a2bf_05发型打理详解.md
└── doc_4471d0f1a3e2_06仪态气质详解.md
```

### 内容循环（纯星期逻辑，无状态文件）

```python
WEEKDAY_NAMES = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
TOPICS = [
    '面部保养',   # Mon/Wed/Fri
    '身材管理',   # Tue/Thu
    '仪态气质',   # Sat
    '复习总结',   # Sun
]
```

### 推送脚本路径

```
/home/ubuntu/.hermes/scripts/beauty-daily.py
```

Cron 任务 ID：`3623acc6233c`，每日 22:30 执行。推送目标群：`oc_c6883cd907e4d226736d87ce9c6c6d79`。

### 关键陷阱

- **不要用 state 文件记录日期** — 改用 `date.today().weekday()` 纯星期逻辑。state 文件 start_date 初始化容易错位（周末启动时 day 1≠周一）。
- **DAILY_CONTENT 直接内联在 CONTENT_CYCLE 里**，不要单独定义后在外层引用（数组越界风险）。
- **当前砍掉了穿搭(04)和发型(05)**，只保留面部/身材/仪态三维。如需恢复，在 TOPICS 和 CONTENT_CYCLE 中补回。
- ~~gaokao.cn URL 用错路径~~ → 文章是 `/art-news/{id}`，不是 `/art/{id}`
- ~~体育升学以为 gaokao.cn 有内容~~ → gaokao.cn 只覆盖艺术类，体育是独立体系

### gaokao.cn URL 结构规律（已验证踩坑）

当用户查询高考/艺考相关信息时，`browser_navigate` 直连 gaokao.cn 有效，但 URL 结构必须准确：

| 内容 | 正确路径 | 错误路径 |
|------|---------|---------|
| 艺考攻略文章 | `/art-news/{id}` | `/art/{id}`（404）|
| 艺考志愿页面 | `/art` | `/art-news` |
| 省控线工具 | 在 `/art` 页面内嵌 | — |
| 简章列表 | `/art-news?search=关键词` | — |
| 分类搜索 | `/art-news?category=舞蹈` | — |

**重要限制：**
- gaokao.cn 以**艺术类**为主，体育升学（体育统考/单招/高水平运动队）是独立体系，这里找不到详细数据
- 搜索结果页只返回简章列表，不返回文章详情（需要从列表中找 id 再进入）
- `urllib` 直连国内教育网站超时，用 `browser_navigate` 替代

### 体育升学信息源（gaokao.cn 没有的独立体系）

体育生高考和艺术生是两条完全不同的路径：

| 类型 | 说明 | 信息源 |
|------|------|--------|
| 体育统考（体育四项） | 100米+立定跳远+推铅球+800米，按综合分录取 | 各省教育考试院 |
| 运动训练单招 | 语文+数学+英语+政治（体育总局出题），专项测试 | 国家体育总局官网 |
| 高水平运动队 | 国家二级运动员证书+校测+高考 | 阳光高考网 |
| 体育类大学专业 | 体育教育/运动训练/运动康复/社会体育指导 | 各体育院校官网 |

掌上高考（gaokao.cn）**不覆盖**体育专业课详细内容。

---

## 城市活动推送 — city-event-push

**触发：** 用户要求找某城市活动、定时推送周末/假期活动。

### 核心数据源（2026-06实测）

| 来源 | 可靠性 | 说明 |
|------|--------|------|
| **豆瓣同城深圳（推荐）** | ⭐⭐⭐⭐ | `browser_navigate`逐页抓取，音乐/戏剧/喜剧/展览/演唱会分类全 |
| **票牛网 piaoniu.com** | ⭐⭐ | StealthyFetcher可抓，数据量偏少 |
| **豆瓣同城-购票直通车** | ⭐⭐⭐ | `selling`页面汇集近期热卖演出，补充演唱会信息 |
| **大麦网 damai.cn** | ⭐ | SSL握手超时，无法抓取 |
| **猫眼电影 maoyan.com** | ⭐⭐ | 需 Playwright，数据有限 |
| **Meetup 深圳** | ⭐⭐ |社交类活动（桌游/爬山等） |
| **深圳之窗** | ⭐⭐ | 需 Playwright 抓取 |
| **深圳政府 sz.gov.cn** | ⭐ | 政务公告，非文娱活动 |

❌ **不可用：** 大麦网(damai.cn) — SSL握手超时；深圳本地宝(sz.bendibao.com) — 超时；活动行(huodongxing.com) — 403封禁；百度搜索 — 验证码反爬无法绕过。

### 豆瓣分类URL模板（2026-06-07实测正常）

```
https://www.douban.com/location/{城市}/events/week-{类型}
```
类型值：all, music, comedy, drama, salon, party, film, exhibition, sports, travel, competition, course, kids

**深圳分类示例（2026-06实测可用）：**
```
https://www.douban.com/location/shenzhen/events/week-all        # 全部
https://www.douban.com/location/shenzhen/events/week-music     # 音乐
https://www.douban.com/location/shenzhen/events/week-drama      # 戏剧
https://www.douban.com/location/shenzhen/events/week-comedy     # 喜剧/脱口秀
https://www.douban.com/location/shenzhen/events/week-exhibition # 展览
https://www.douban.com/location/shenzhen/events/week-sports    # 运动
https://www.douban.com/location/shenzhen/events/week-1003     # 演唱会（子分类）
https://www.douban.com/location/shenzhen/events/week-1001     # 小型现场
https://www.douban.com/location/shenzhen/events/week-1002     # 音乐会
https://www.douban.com/location/shenzhen/events/week-1102     # 音乐剧（子分类）
https://www.douban.com/location/shenzhen/events/week-2201     # 脱口秀（子分类）
https://www.douban.com/location/shenzhen/events/selling        # 购票直通车（近期热卖演出）
```

> ⚠️ **`week-competition`（赛事）在深圳返回空，但体育类活动实际在 `week-sports` 下**（徒步/飞盘/羽毛球等大众运动，非职业赛事）。演唱会/大型演出出现在 `week-all` 底部的"购票直通车"区块，不是独立分类。

### 浏览器操作流程（豆瓣同城）

1. `browser_navigate(url)` → 进入豆瓣活动分类页（URL格式见上）
2. `browser_snapshot()` → 获取活动列表（需处理分页）
3. `browser_scroll(direction=down)` → 向下滚动加载更多内容
4. `browser_snapshot(full=true)` → 获取完整内容（处理 `... 293 more lines truncated`截断）
5.切换分类标签 → `browser_click(ref)` → 再 `browser_snapshot()` 获取切换后的内容

> ⚠️ **页面底部会出现 `... XXX more lines truncated`**，此时必须用 `browser_snapshot(full=true)` 获取完整内容，否则只能看到前半部分活动列表。

### 搜索关键词公式

**假期/节日活动首选：**
```
{城市} + {假期名称} + 假期/假日 + {年份} + 活动 + 推贴/地点/汇总
```
示例：`深圳+五一+假期+2026+活动+推贴+地点` → 16,200结果

**按类型并行搜索：**
- 社交类：`{城市} 社交活动 桌游 沙龙 聚会 联谊`
- 展览类：`{城市} 展览 艺术展 插画展 摄影展 科技展 漫展`
- 音乐/live：`{城市} 音乐 live 乐队 演唱会 音乐节`
- 创意市集：`{城市} 创意市集 文创市集 周末市集`

### 输出格式（一目了然型）

```
🎵 演唱会 / Live
• 凤凰传奇演唱会 | 至5月4日 | 大运中心 | 380元起
• Taylor Swift 霉霉专场 | 5月1日 | 深圳MAO Livehouse | 108元起

🔥 火秀 / 无人机表演
• 欢乐谷无人机天幕大秀 | 每晚20:40 | 南山欢乐谷 | 夜场180元

☕ 创意市集 / 咖啡节
• 第七届唤醒咖啡节 | 4/29-5/5 | 福田区OneAvenue卓悦中心 | 免费入场
```

每条活动四要素：**名称 | 时间 | 地点 | 票价**。总字数控制在500字以内。不发文件，一次性发群里。

---

## 网站文章周报推送 — website-digest-push

**触发：** 用户要求对某个网站/论坛/专题页面做定时内容聚合推送，包括"每周/每天推送XX网站的内容"、"把XX论坛的文章做成周报"。

### 多源并行抓取

多个同类站点并行fetch，合并去重，比单站更全。

### 过滤比摘要更重要

文章数量多时，逐篇抓摘要极慢。直接从列表页的标题+描述字段提取，控制抓取量为零。

### 标题去重

同一文章可能同时出现在两个站，用前30字做相似度去重。

### 主题分类

非时间线展示，而是按内容特征分类（如：新发售/爆火/业界动态）。关键词匹配即可，无需NLP。

### 爬虫脚本核心结构

```python
#!/usr/bin/env python3
"""网站内容周报 - 站点名"""

import urllib.request, re, html
from datetime import datetime, timedelta

def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; digest-bot/1.0)',
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8')

def parse_articles(html_content: str) -> list:
    """返回: [{'title', 'author', 'date', 'url'}]"""
    # 用 browser_snapshot 找到 HTML 结构后写正则
    pattern = r'<a href="…" title="([^"]+)"[^>]*>.*?([^-]+)\s*-\s*(\d{4}-\d{2}-\d{2})'
    articles = []
    for m in re.finditer(pattern, html_content, re.DOTALL):
        url, title, author, date = m.groups()
        articles.append({
            'title': html.unescape(title.strip()),
            'author': html.unescape(author.strip()),
            'date': date.strip(),
            'url': 'https://example.com' + url
        })
    return articles

def get_article_preview(url: str, max_chars: int = 300) -> str:
    """抓取文章前几段作为摘要"""
    try:
        h = fetch_url(url)
        paras = re.findall(r'<p[^>]*>(.*?)</p>', h, re.DOTALL)
        content = []
        for p in paras:
            text = re.sub(r'<[^>]+>', '', p).strip()
            text = html.unescape(text)
            if len(text) > 30:
                content.append(text)
        return '\n'.join(content[:3])[:max_chars] + '...'
    except Exception as e:
        return f'（摘要抓取失败: {e}）'
```

### 隐私/安全新闻推送 — 可用RSS源（2026-06实测）

| 来源 | RSS URL | 代理 | 状态 | 备注 |
|------|---------|------|------|------|
| **EFF (Electronic Frontier Foundation)** | `https://www.eff.org/rss/updates.xml` | ❌ 不需要 | ✅ 可用 | 隐私法规、政策倡导、美国监控项目进展 |
| **Krebs on Security** | `https://krebsonsecurity.com/feed/` | ❌ 不需要 | ✅ 可用 | 数据泄露、安全事件、勒索软件 |
| Troy Hunt / HIBP | `https://www.troyhunt.com/rss/` | 未知 | ❓ 未核实 | 数据泄露、密码安全 |
| 嘶吼 | `https://www.4hou.com/feed` | 未知 | ❓ 未核实 | 中文安全资讯 |
| Mozilla Blog | `https://blog.mozilla.org/en/feed/` | 未知 | ❓ 未核实 | 隐私工具更新 |

**已确认不可用（2026-06实测）：**
- ~~Wired RSS~~ — Cloudflare / JS反爬，返回页面碎片而非RSS
- ~~BleepingComputer~~ — Cloudflare 拦截，返回验证页
- ~~The Register~~ — Cloudflare 拦截
- ~~Ars Technica~~ — 404，RSS URL已变更
- ~~WIRED RSS (`wired.com/feed/rss`)~~ — 返回50条内容但都是非隐私类（电商/World Cup/Deal优惠券等泛内容），隐私相关条目寥寥无几且需大量过滤

**推荐抓取方式（curl直取 + 正则解析）：**
```python
import subprocess, re
r = subprocess.run(['curl', '-s', '--max-time', '15', '-A', 'Mozilla/5.0',
                   'https://www.eff.org/rss/updates.xml'],
                  capture_output=True, text=True, timeout=20)
raw = r.stdout
items = re.findall(r'<item>(.*?)</item>', raw, re.DOTALL)
for item in items:
    title = re.search(r'<title>([^<]+)</title>', item)
    link  = re.search(r'<link>([^<]+)</link>', item)
    date  = re.search(r'<pubDate>([^<]+)</pubDate>', item)
    if title and date and 'Jun 2026' in date.group(1):
        print(f"[{date.group(1)}] {title.group(1).strip()}")
        print(f"  -> {link.group(1).strip()}")
```

**Wired RSS过滤方法（若必须使用）：**
Wired的RSS包含大量非隐私内容（购物/World Cup/Deals等），过滤关键词：
```python
PRIVACY_KW = ['privacy', 'data breach', 'encrypt', 'surveill', 'personal data',
              'security', 'leak', 'hack', 'malware', 'biometric', 'facial recogn']
# 日期格式：'Fri, 12 Jun 2026 23:49:27 +0000'，过滤 Jun 7-13
# 提取后还需根据 title + description 中关键词二次筛选
```

### Cron 调度

推荐推送时间：
- **周六上午10点** — 周报最佳时间
- **周一上午9点** — 周度总结
- **每天上午8点** — 日报

---

## K-pop女团资讯推送 — kpop-news-push

**触发：** 用户要求推送aespa、BLACKPINK、NewJeans、IVE、LE SSERAFIM、Red Velvet、TWICE等韩团资讯。

### 目标团体

```
aespa / BLACKPINK / NewJeans / IVE / LE SSERAFIM / Red Velvet / TWICE
```

### 信息源（2026-05实测）

**主力 — XCrawl Search API（推荐）：**
**主力 — XCrawl Search API（via curl + 代理）：**
```python
# subprocess + curl --socks5-hostname 调 XCrawl Search API
# 覆盖 Allkpop/Twitter/Naver 等 Soompi RSS 覆盖不到的平台
# API Key: xc-w7ylEVsaYLNXlYYhOP1tEzthyljoAGVrUjQOwCtEKAFadgps
# 注册送 1000 credits，2 credits/查询，走 socks5://127.0.0.1:10808 代理
XCRAWL_SEARCH_URL = "https://run.xcrawl.com/v1/search"

def xcrawl_search(query, limit=5):
    body = json.dumps({"query": query, "limit": limit})
    cmd = [
        "curl", "-s", "--socks5-hostname", "127.0.0.1:10808",
        "-X", "POST", XCRAWL_SEARCH_URL,
        "-H", f"Authorization: Bearer {XCRAWL_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", body,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        if data.get("status") == "completed":
            return data.get("data", {}).get("data", [])
    return []
```

**备选 — Soompi 中文 RSS（via 代理）：**
```python
import urllib.request, xml.etree.ElementTree as ET, re

PROXY = "socks5://127.0.0.1:10808"

def fetch_soompi_rss():
    url = "https://ch.soompi.com/feed/"   # 中文版，非英文版
    proxy_handler = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with opener.open(req, timeout=15000) as resp:
        return resp.read().decode('utf-8', errors='ignore')
```

**翻译（XCrawl 英文结果 → 中文）：**
```python
import urllib.parse, subprocess, json

def translate_title(text):
    encoded = urllib.parse.quote(text[:100])
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
    cmd = ["curl", "-s", "--socks5-hostname", "127.0.0.1:10808",
           "-X", "GET", url, "--header", "User-Agent: Mozilla/5.0"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0 and result.stdout:
        data = json.loads(result.stdout)
        return "".join(item[0] for item in data[0] if item[0])
    return text
```

**注意：**
- Soompi 用 `ch.soompi.com` 而非 `www.soompi.com`（直接出中文）
- deep-translator 库不可用（无法访问谷歌翻译），必须用 `translate.googleapis.com` API
- 脚本 shebang 用 `#!/usr/bin/python3`（避免 hermes-agent venv 包隔离问题）

### 已确认不可用的来源（2026-05实测）

- ~~Allkpop — Cloudflare 拦截~~ → **已解决，XCrawl Search API 可绕过**
- **Kpop Herald** — 服务不可用（500 Error）
- **Soompi** — 直连不行，走 `socks5://127.0.0.1:10808` 代理 ✅

### 成员名搜索（某团无结果时的最后手段）

| 团体 | 成员名 |
|------|--------|
| BLACKPINK | Jisoo, Jennie, Lisa, Rosé |
| NewJeans | Minji, Hanni, Danielle, Haerin, Hyein |
| IVE | Wonyoung, Yujin, Gaeul, Rei, Liz, Leeseo |
| TWICE | Nayeon, Jeongyeon, Momo, Sana, Jihyo, Tzuyu |
| Red Velvet | Irene, Seulgi, Joy, Yeri, Wendy |
| aespa | Karina, Giselle, Winter, Ningning |

### 验证某明星/成员今天在某城市有无活动

→ 详见 `references/celebrity-event-discovery.md`

### 翻译方案（2026-05已修复）

XCrawl 搜索结果为英文，Soompi 已切到中文版（ch.soompi.com），
XCrawl 结果通过 `translate.googleapis.com`（curl 走代理）英译中。

翻译实现细节 → `references/translate-api-patterns.md`

### 输出格式

去掉链接，只保留标题和日期：

```markdown
# 🇰🇷 韩国女团每日资讯
**推送时间：** {日期}
**来源：** Soompi RSS（48小时内）

1. 【BLACKPINK】BLACKPINK's Lisa To Headline FIFA World Cup 2026 Opening Ceremony
   📅 Sat, 09 May 2026 05:47:52 +0000
```

---

## 国际政治要闻推送 — political-news-push

**触发：** 用户要求每日推送国际政治要闻、全球政治动态、中美关系/俄乌/中东等政治话题。

> **与 hermes-political 的区别：**
> - `political-news-push`：国际政治（BBC+观察者网），每天08:30定时推送
> - `hermes-political`：国内政策文件（政治局/国务院/两会），每30分钟事件驱动推送
> 两者互补，不重叠。

### 双源架构

- **BBC World News RSS**（英文，需代理）— 国际媒体视角
- **观察者网**（中文，Playwright 抓取）— 国内媒体视角

两个源 **交替混合**，比例约 2:1（2条 BBC → 1条 观察者网），确保国内视角不被单一国际源稀释。

### 信息源

**BBC World News RSS（via 代理）：**
```
https://feeds.bbci.co.uk/news/world/rss.xml
```
直连不通，需走 `socks5://127.0.0.1:10808` 代理。用 Python `urllib` + `ProxyHandler` 抓取，解析 `<item>` 提取 title/description/link/pubDate。

**观察者网（Playwright 抓取）：**
```
https://www.guancha.cn/internation/
```
国内新闻站 RSS 全部失效（404/反爬），但 Playwright headless Chrome 可以抓到。CSS 选择器：`h4 a, a[href*="/internation/"][href*=".shtml"]`，取前 12 条。

### 翻译方案

**Google Translate 免费接口（无需 API Key）：**
```
https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded_text}
```
走 `socks5://127.0.0.1:10808` 代理。JSON 响应格式：`[[[翻译文本, 原文, ...], ...], null, "en", ...]`，取 `result[0]` 拼接所有片段。单次限制约 500 字符。

### 政治内容过滤

**噪音词（标题含这些直接过滤）：**
```python
NOISE_PATTERNS = [
    'dog', 'dogs', 'puppy',           # 动物
    'chocolate', 'milka', 'candy',    # 食品
    'cruise', 'ship', 'norovirus', 'passenger', 'hantavirus',  # 游轮/病毒
    'everest', 'mount climb', 'climber', 'summit attempt',      # 登山
    'football', 'soccer', 'tennis', 'basketball', 'sport', 'match', 'game',  # 体育
    'festival', 'concert', 'music', 'award', 'oscar', 'grammy',  # 娱乐
    'weather', 'storm', 'hurricane', 'flood', 'earthquake',     # 气象
    'bitcoin', 'crypto', 'stock market', 'shares',              # 纯财经
    'instagram', 'tiktok', 'viral', 'recipe', 'cook', 'food',   # 社媒/美食
    'hotel', 'airbnb', 'travel', 'tourism',                    # 旅游
]
```

**政治关键词（标题含这些则保留）：**
包含政要名（trump/pulin/xi/zelensky 等）、国家/地区、战争/军事/外交/制裁/峰会等词汇。

### 中国重大会议提醒（内置日历）

political-news.py 内置了会议日历，临近时会自动插入提醒到日报顶部。提醒逻辑按月份触发：

| 月份 | 触发会议 |
|------|---------|
| 12月 | 中央经济工作会 + 中央农村工作会 |
| 2-3月 | 全国两会（3月3日政协/3月5日人大） |
| 1-3月（逢3结尾年份） | 三中全会（党代会次年，如2028） |
| 12-1月 | 中央外事工作会议 |

会议定义在脚本顶部 `MEETING_CALENDAR` 列表，每条包含：name / 次年时间 / 提醒提前天数 / 关键词 / 优先级 / 说明。

日报格式示例（12月或3月时会在顶部出现）：
```markdown
## 📅 中国重大会议提醒

⚠️ 【⭐⭐⭐⭐⭐】全国两会 临近！
提前量：约7天 | 3月3日（政协）/ 3月5日（人大）
聚焦：中国最高权力机关，每年一次，会期约10天

---
```

会议完整梳理文档：`/home/ubuntu/.hermes/scripts/china-meetings.md`

### Playwright 抓取国内新闻站（subprocess 临时文件法）

**坑：** subprocess 调用 Playwright 时，用 `python3 -c "..."` 传代码字符串会因引号转义失败。正确做法是**写临时 .py 文件再执行**。

```python
import tempfile, subprocess, os

code = (
    "import sys,json\n"
    "sys.path.insert(0,'/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages')\n"
    "from playwright.sync_api import sync_playwright\n"
    "with sync_playwright() as p:\n"
    "  b=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-blink-features=AutomationControlled'])\n"
    "  page=b.new_page(viewport={'width':1280,'height':900},user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',locale='zh-CN')\n"
    "  page.goto('https://www.guancha.cn/internation/',timeout=30000,wait_until='domcontentloaded')\n"
    "  page.wait_for_timeout(3000)\n"
    "  data=page.eval_on_selector_all('h4 a,a[href*=\"/internation/\"][href*=\".shtml\"]','function(es){var s={},r=[];for(var i=0;i<es.length;i++){var e=es[i],t=e.innerText.trim(),h=e.href||\"\";var k=t.substring(0,30);if(t.length>5&&t.length<100&&!s[k]&&h.indexOf(\"/internation/\")>-1){s[k]=true;r.push({text:t,href:h})}}return r.slice(0,12)}')\n"
    "  sys.stdout.write('GUANCHA_DATA:'+json.dumps(data))\n"
    "  b.close()\n"
)
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
tmp.write(code)
tmp.close()
try:
    r = subprocess.run(['/home/ubuntu/.hermes/hermes-agent/venv/bin/python3', tmp.name],
                      capture_output=True, text=True, timeout=60)
    out = r.stdout
    idx = out.find('GUANCHA_DATA:')
    if idx >= 0:
        data = json.loads(out[idx+len('GUANCHA_DATA:'):].strip())
finally:
    os.unlink(tmp.name)
```

### 两源交替混合算法

```python
MAX_ITEMS = 16  # 需要足够大让两源都有展示机会
bbc_list = [it for it in all_items if it['source'] == 'BBC World'][:16]
guancha_list = [it for it in all_items if it['source'] == '观察者网'][:8]
merged = []
bbc_idx, gc_idx = 0, 0
while len(merged) < MAX_ITEMS and (bbc_idx < len(bbc_list) or gc_idx < len(guancha_list)):
    if bbc_idx < len(bbc_list): merged.append(bbc_list[bbc_idx]); bbc_idx += 1
    if len(merged) >= MAX_ITEMS: break
    if bbc_idx < len(bbc_list): merged.append(bbc_list[bbc_idx]); bbc_idx += 1
    if len(merged) >= MAX_ITEMS: break
    if gc_idx < len(guancha_list): merged.append(guancha_list[gc_idx]); gc_idx += 1
    if len(merged) >= MAX_ITEMS: break
all_items = merged
```

### Cron 调度

```
30 8 * * *   # 每天 08:30 推送
```

- 目标群：`oc_c6883cd907e4d226736d87ce9c6c6d79`
- 脚本路径：`/home/ubuntu/.hermes/scripts/political-news.py`
- 工作目录：`/home/ubuntu/.hermes/scripts`
- **推送机制：脚本直接调飞书 API（tenant_access_token + im/v1/messages），deliver 设为 `local`**，不依赖文件落地检测。旧方案（写文件→cron检测→推送）飞书收到的是未渲染的原始文本，用户看不到格式化效果。

> ⚠️ **推送格式陷阱（2026-05已修复）：** cron 系统检测到文件后直接推送，飞书收到的是原始 markdown 而非渲染内容。政治/商业日报都是这个问题。**正确方案：脚本内部调飞书 `im/v1/messages` API 直接推送，cron job 的 `deliver` 改为 `local`**。

---

## 机器人/具身智能日报推送 — robot-news-push

**触发：** 用户要求推送机器人、具身智能、人形机器人、自动驾驶行业资讯，或类似"向AI那样做个机器人日报"。

### 信息源 + 翻译 + 网络

→ 详见 `references/robot-news-scraper.md`

### 关键技术决策（本 session 新增）

1. **翻译不用 urllib**：urllib 的 socks5 ProxyHandler 在代理场景下会报 `Connection refused`，必须用 `subprocess + curl` 替代
2. **Google Translate 不可用**：直连和 JP 代理都无法连通，改用 MyMemory 免费 API 直连
3. **日本代理仅用于新闻源兜底**：翻译直连 MyMemory，国际新闻源直连优先、超时用 JP 代理
4. **两级关键词过滤**：标题必须命中 `ROBOT_KW_TITLE` 之一；description 含 `ROBOT_KW_DESC` 可辅助入选，避免泛AI内容混入

### Cron 调度

```
0 9 * * *
```

- 目标群：`oc_c6883cd907e4d226736d87ce9c6c6d79`
- 脚本路径：`/home/ubuntu/.hermes/scripts/robot-news.py`

---

## 每周生活用品优惠精选推送 — weekly-deals-push

**触发：** 用户要求推送每周生活用品/零食饮料优惠、什么值得买好价精选，或定时优惠信息。

### 数据源

| 来源 | URL | 说明 |
|------|-----|------|
| 什么值得买 smzdm.com | `smzdm.com/fanli/haojia/{tab}/` | 好价排行榜，5个tab并行抓取 |

**Tab 分类：**
- `0/3/` = 食品家居
- `0/4/` = 日百母婴
- `0/5/` = 白菜
- `0/1/` = 时尚运动
- `0/2/` = 数码家电

### 抓取方式

Python Playwright（headless Chrome），通过**临时 .py 文件 subprocess** 调用。页面是无限滚动，必须滚动触发懒加载：

```python
page.goto(url, wait_until="domcontentloaded", timeout=30000)
page.wait_for_timeout(2000)
for _ in range(6):
    page.evaluate("window.scrollBy(0, 700)")
    page.wait_for_timeout(1200)
body_text = page.inner_text("body")
```

然后正则匹配 `价格行`（含 `X.XX元`）和前一条品名。

### 品类关键词过滤

DAILY_KEYWORDS 覆盖：纸品/清洁/粮油调味/口腔护理/洗护/女士护理/家居/零食饮料/方便速食/乳制品冰品 等。EXCLUDE_KEYWORDS 剔除洗衣机/冰箱/手机/电脑/茅台等大件/酒类。
### 输出格式

按品类分组（🧻 纸品/🧴 洗衣清洁/🫒 粮油调味/🥛 牛奶饮料/🍪 零食饼干 等），每类最多8条，**每条 name + price 合为一行**，不用两行使劲占篇幅。分类标题用 `【】`，不用 `====` 长分隔线。

```
🛒 本周生活用品优惠精选  2026-05-23
📡 来源：什么值得买 smzdm.com

【🫒 粮油/调味】
  鲁花 花生油6.08L  105.69元
  徐福记 减糖沙琪玛 526g  4.92元

【🥛 牛奶/饮料】
  黄天鹅可生食鸡蛋30枚  38.57元（需买2件）

【🥜 其他食品】
  认养一头牛 儿童冰淇淋 35g*4盒  13.9元（需买5件）

────────────────────────────────
📊 共收录 30 件优惠好物（共抓取 105 条）
💡 价格随时变化，购买前请确认
🔗 https://www.smzdm.com/fanli/haojia/
```

> ⚠️ **格式陷阱（2026-05修复）：** 旧格式每个分类用 `============` 分隔、每条占两行（品名单行 + `💰 价格` 单独一行），内容稀薄。正确做法：分类标题 `【】`，品名和价格合为一行 `品名  价格`，底部一条横线分隔统计信息。内容量提升3-4倍。

### Cron 调度

```
30 10 * * 6   # 每周六 10:30
```

- 目标群：`oc_c6883cd907e4d226736d87ce9c6c6d79`
- 脚本路径：`/home/ubuntu/.hermes/scripts/weekly-deals.py`
- 工作目录：`/home/ubuntu/.hermes/scripts`
- **推送机制：`deliver=local`，脚本内部直接调飞书 API**

> ⚠️ **推送格式陷阱（2026-05已修复）：** 同 political-news-push 和 business-news-push，`deliver=feishu:oc_xxx` 文件检测模式飞书收到未渲染原始文本。**正确方案：deliver 改为 `local`，脚本末尾调用 `feishu_send_text(report)` 直接推送。**

### 关键陷阱

1. **重复 import**：脚本头部已 import `re`/`datetime`，末尾添加飞书函数时不要再重复 import（导致 `import re` 在文件中部破坏已定义函数）
2. **文件保留作备份**：推送成功后仍写入 `~/.hermes/cron/output/weekly-deals-{date}.txt`，供人工核查
3. **Playwright 浏览器实例**：smzdm 页面需 headless Chrome，每次 `fetch_smzdm_feed` 内部 launch+close，不跨 tab 共享

---

## 每周生活选题推送 — weekly-life-topics-push

**触发：** 用户要求推送每周生活/文化体验类选题，或定时生活类内容周报。

### 数据源（2026-05实测）

| 来源 | URL | 代理 | 可靠性 |
|------|-----|------|--------|
| National Geographic Travel | `nationalgeographic.com/travel` | 必须 | ⭐⭐⭐⭐⭐ |
| Smithsonian Magazine | `smithsonianmag.com/` | 必须 | ⭐⭐⭐⭐ |
| BBC Travel | `bbc.com/travel` | 必须（慢，超时70s内） | ⭐⭐⭐⭐ |

> ⚠️ **CNN Traveler (cntraveler.com) 不稳定** — 主页有时 404，有时超时 30s 以上，已替换为 BBC Travel。

### 内容方向（主人定制，2026-06-16）

主人想要的不是"旅游攻略"，而是**探索世界多元文化，体验不同的生活方式**。核心是"世界各地的人如何生活"。

优先内容方向：
1. **旅居/数字游民** — 在世界各地旅居的人，生活/工作/社交方式
   - 例：巴厘岛数字游民、清迈生活成本、日本乡下长住、冰岛渔民
2. **跨文化生活体验** — 深入当地人的日常生活
   - 例：意大利慢生活、瑞士滑雪小镇、摩洛哥riad老宅、日本寺院修行
3. **另类生活方式** — 不走常规路的人
   - 例：帆船航海生活、房车流浪、极简主义隐居、隐居僧人生活
4. **本地深度探访** — 旅行中深入当地人群
   - 例：巴黎左岸艺术家群落、北欧渔村、冰岛火山洞穴

信息源关键词（搜索时用）：`digital nomad lifestyle`, `living abroad`, `local life immersive`, `traditional culture experience`, `alternative lifestyle`, `slow living`, `nomad community`

### 抓取方式

用 Python Playwright（headless Chrome），通过**临时 .py 文件 subprocess** 调用，不走 `python3 -c` 字符串（避免引号歧义）。CSS 选择器统一用 `h2 a, h3 a`。

```python
def playwright_fetch(url: str, css_selector: str, page_key: str, timeout: int = 60) -> list:
    script = f"""
import sys, json
sys.path.insert(0, '/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages')
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']
    )
    page = browser.new_page(
        viewport={{'width': 1280, 'height': 900}},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
    )
    page.goto('{url}', timeout=45000, wait_until='domcontentloaded')
    page.wait_for_timeout(5000)
    handles = page.query_selector_all('{css_selector}')
    results = []
    seen = {{}}
    for h in handles:
        try:
            text = h.inner_text().strip()
            href = h.get_attribute('href') or ''
            key = text[:25]
            if text and 15 < len(text) < 120 and href.startswith('http') and not seen.get(key):
                seen[key] = True
                results.append({{'text': text, 'href': href}})
                if len(results) >= 8: break
        except Exception: pass
    print('{page_key}:' + json.dumps(results))
    browser.close()
"""
    # 写入临时 .py 文件 → subprocess.run → 解析 stdout 中 page_key: 前缀
```

### 关键陷阱

1. **CSS 选择器单引号冲突**：f-string 里放 CSS 属性选择器时，`[data-component='card']` 会导致引号歧义。统一用双引号：`[data-component="card"]`
2. **超时兜底**：必须捕获 `subprocess.TimeoutExpired`，BBC Travel 等源响应慢，超时后不影响其他来源继续推送
3. **字段名统一**：Playwright 返回 `{'text', 'href'}`，主流程里用 `it.pop('text')` → `title`，`it.pop('href')` → `link`

### 过滤关键词

```python
LIFESTYLE_KW = [
    'culture', 'tradition', 'food', 'recipe', 'travel', 'destination',
    'local life', 'heritage', 'craft', 'artisan', 'festival', 'ritual',
    'architecture', 'community', 'indigenous', 'history', 'museum',
    'lifestyle', 'experience', 'immersive', 'authentic',
    '文化', '传统', '生活', '旅行', '体验', '建筑', '手工艺',
    '饮食', '节庆', '艺术', '历史', '民俗', '社区'
]
NOISE = ['crypto', 'bitcoin', 'stock', 'election', 'politic',
         'weather', 'storm', 'hurricane', 'earthquake',
         'coronavirus', 'covid', 'pandemic', 'vaccine']
```

### 推送机制（2026-05已修复）

AI生成内容 + 直接送飞书，**不用脚本抓取**：

```
cron job:
  deliver: feishu:oc_c6883cd907e4d226736d87ce9c6c6d79
  skills: []           ← 关键！不填 web/search，避免"Skill(s) not found"
  prompt: [AI搜索生成多元文化内容的指令]
```

cron 触发后，AI 搜索 BBC Travel / National Geographic / Smithsonian Magazine → 生成结构化中文内容 → 直接送飞书。输出格式包含"在哪里体验"、"内容简介"、"为什么有趣"、"适合形式"四个字段，质量远高于脚本抓取。

> ⚠️ **切勿填 `skills: ["web", "search"]`**：这是工具集名称，不是技能名，填了会导致任务以无工具状态运行返回 [SILENT]。必须写 `skills: []` 或留空。

> ⚠️ **`cron run` 只是重新排期，不立即执行**：实测 `cron run` 成功=任务被重排到"立即"，但实际内容推送依赖下一个调度tick。想立即验证格式，用 `send_message` 直接发测试消息到周报群。

**输出格式规范：** → `references/weekly-life-topics-format.md`

- 目标群：`oc_c6883cd907e4d226736d87ce9c6c6d79`
- 脚本路径：`/home/ubuntu/.hermes/scripts/weekly-life-topics.py`
- 工作目录：`/home/ubuntu/.hermes/scripts`
- **推送机制：`deliver=local`，脚本内部直接调飞书 API**

---

## 商界要闻日报推送 — business-news-push

**触发：** 用户要求每日推送商界/财经/科技商业新闻、股市/公司/科技动态。

### 双源架构（2026-05实测）

- **BBC Business RSS**（英文，需代理 `socks5://127.0.0.1:10808`）— 全球商业/财经
- **FT中文网 RSS** — 国内商业视角（**2026-05实测已404**，已暂时移除）

> 2026-05实测发现 BBC 直连被封，FT中文网 RSS 也返回 404。当前只保留了 BBC Business RSS，14条全来自 BBC。FT中文网恢复后可重新加入。

### 可用RSS源快速探测脚本

> **重要工作流：** 当 urllib/浏览器/rss 工具全部超时/失败时，用 curl 快速探测哪些 RSS 源还活着。
> 这个方法在 BBC/FT/WSJ 全部被墙的 2026-05 实测非常有效。

```bash
for url in \
  "https://feeds.a.dj.com/rss/RSSMarketsMain.xml" \
  "https://feeds.a.dj.com/rss/RSSWorldNews.xml" \
  "http://rss.sina.com.cn/news/china/focus15.xml" \
  "https://feeds.bbci.co.uk/news/business/rss.xml" \
  "https://www.ftchinese.com/rss/feed"; do
  code=$(curl -s --max-time 6 -o /dev/null -w "%{http_code}" -A "Mozilla/5.0" "$url")
  echo "$code $url"
done
```

**2026-05实测结果：**
| 来源 | HTTP Code | 状态 |
|------|-----------|------|
| `feeds.a.dj.com/rss/RSSMarketsMain.xml` | 200 | ✅ 可用 |
| `feeds.a.dj.com/rss/RSSWorldNews.xml` | 200 | ✅ 可用 |
| `rss.sina.com.cn/news/china/focus15.xml` | 200 | ✅ 可用 |
| `feeds.bbci.co.uk/news/business/rss.xml` | 000 (timeout) | ❌ 封禁 |
| `www.ftchinese.com/rss/feed` | 000 (timeout) | ❌ 封禁 |

### 信息源

**BBC Business RSS（需代理）：**
```
https://feeds.bbci.co.uk/news/business/rss.xml
```
走 `socks5://127.0.0.1:10808` 代理。用 Python `urllib` + `ProxyHandler` 抓取，解析 `<item>` 提取 title/description/link/pubDate。

**FT中文网 RSS（暂不可用）：**
```
https://www.ftchinese.com/rss/feed
```
2026-05 实测返回 404，暂从脚本中移除。恢复后将重新加入。

### 商业内容过滤

**噪音词（标题含这些直接过滤）：**
```python
NOISE_PATTERNS = [
    'recipe', 'cook', 'food', 'restaurant', 'festival', 'concert',
    'football', 'soccer', 'sport', 'game', 'match', 'weather',
    'dog', 'celebrity', 'gossip', 'instagram', 'tiktok viral',
    'wed', 'marriage', 'baby', 'birth',
]
```

**商业关键词（标题含这些则保留）：**
包含 business/company/market/trade/economy/finance/stock/tech/ai/ceo/ipo/merger 和中文关键词（商业/财经/股市/公司/企业/并购/上市/裁员/银行/关税 等）。

### Cron 调度

```
20 9 * * *   # 每天 09:20 推送
```

- 目标群：`oc_c6883cd907e4d226736d87ce9c6c6d79`
- 脚本路径：`/home/ubuntu/.hermes/scripts/business-news.py`
- 工作目录：`/home/ubuntu/.hermes/scripts`
- **推送机制：脚本直接调飞书 API（tenant_access_token + im/v1/messages），deliver 设为 `local`**，不依赖文件落地检测。

> ⚠️ **FT中文网 RSS 暂不可用（2026-05实测）：** `ftchinese.com/rss/feed` 返回 404，已从脚本中暂时移除。恢复后将重新加入。
>
> ⚠️ **推送格式陷阱（2026-05已修复）：** cron 系统检测到文件后直接推送，飞书收到的是原始 markdown 而非渲染内容。政治/商业日报都是这个问题。**正确方案：脚本内部调飞书 `im/v1/messages` API 直接推送，cron job 的 `deliver` 改为 `local`**。
>
> ⚠️ **推送机制必须直接调飞书 API**，不能用文件落地→检测→推送模式（飞书收到未渲染的原始文本）。脚本内部调用 `im/v1/messages` API 推送，`deliver` 设为 `local`。

---

1. **`skills` 参数填写 `["web", "search"]`** 是工具集名而非技能名，会导致任务以无工具状态运行，返回 [SILENT]。填写 `skills: []` 或不填。
2. **`cron run` 只是重新排期，不是立即执行**（2026-06-16 实测踩坑）：`cronjob run` 会把 `next_run_at` 更新为"立即"，但内容并没有推送。实际执行依赖于 cron 调度器的下一次 tick。如果想立即测试推送，必须用 `send_message` 工具直接发送到目标飞书群，或者等待下一个调度周期。**不要误以为 run 成功=推送成功**。
3. **推送验证土办法**：调用 `send_message` 发一条测试消息到目标群，收到 message_id 即表示 bot 有推送权限且群 ID 正确；没收到就说明 bot 不在群里或 chat_id 错误。
4. **内容必须是真实搜索结果，不得编造**：生成的内容必须标注来源（平台名+链接或"实测可用"）。搜索结果需实际执行，不能用"看起来合理"的内容代替。如果搜索失败，立即通知用户，不要生成虚假内容。
5. **脚本写文件触发推送**：脚本写入 `~/.hermes/cron/output/{job_id}/` 目录即可。
4. **删除 job 后必须验证**：仅调用 `cronjob remove` 不代表删除成功——必须立即用 `cronjob list` 确认该 job_id 已消失。这是已验证的工作流程。操作序列：

   ```
   1. cronjob remove job_id=XXX
   2. cronjob list  ← 必须执行，确认返回列表中不再有该 job
   3. 若仍在列表中 → 重新 remove
   ```

## 飞书群内容分频体系（主人定制）

主人建立了 4 群分频推送体系，各群有明确的内容定位和触发时间：

| 群 | chat_id | 定位 | 触发时间 |
|----|---------|------|----------|
| **日报群** | `oc_c6883cd907e4d226736d87ce9c6c6d79` | 每日/实时：调研日报、机器人日报、金融市场监控、每3天Trojan检测 | 每日定时 |
| **周报群** | `oc_605cb68f2814b7fef2336ae15b7982bd` | 每周汇总：政治/经济早晚报（1日2次）、游戏/时尚/生活选题/深圳活动/团队/安全/AI/数据/行业/法律周报等 | 每周 |
| **月报群** | `oc_bd20e92437df496f958a38958d48b92a` | 月度汇总：近3月学术科技/社政经济/文娱三大领域 + 未来3月定档大事件 | 每月30号 |
| **年报群** | `oc_675ed9bc27aa367fdca299e332b8da1c` | 年度汇总：近6月三大领域 + 未来1年定档大事件 | 每年2月1号 |

**内容分三大维度**：
1. **前沿学术/科技/工业**：大模型/AI、芯片、量子计算、生物医药、机器人等
2. **社会/政治/经济**：政策动向、宏观经济、A股/人民币、社会变化
3. **文娱**：体育（世界杯/F1/NBA）、K-pop、影视、动漫、游戏

文娱定档参考方向：世界杯（足球）、F1、NBA、网球四大满贯 → K-pop MAMA/MMA/金唱片 → 奥斯卡/戛纳/威尼斯 → TGA/Steam Awards/英雄联盟S赛 → Comiket/动漫

---

## 通用故障排查

### ⚠️ cronjob create 的 deliver 参数被忽略（必须两步操作）

**踩坑记录（2026-06-16 实测）：** `cronjob create` 调用时会**忽略 `deliver` 参数**，job 创建后 `deliver` 永远是 `origin`（即推回用户 DM），而非你传入的 `feishu:oc_xxx`。

**症状：** 新建 cron 任务推到了 DM 而非目标飞书群。

**正确工作流：必须两步：**

```python
# 第1步：创建任务（deliver 参数被忽略，创建后默认 origin）
cronjob create name="月报·文娱" schedule="0 10 30 * *" prompt="..." skills=["web-browse"]
# 创建成功后返回 job_id="88b5a7ca67df"，但 deliver="origin"

# 第2步（必须）：立即更新 deliver 为目标群
cronjob update job_id="88b5a7ca67df" deliver="feishu:oc_bd20e92437df496f958a38958d48b92a"
```

**验证：** `cronjob list` 查看 `deliver` 字段是否已更新为目标群地址。

### deliver 配置决定推送目标

**`deliver` 值决定 cron 任务结果去哪里：**
- `feishu:oc_xxx` → 推送指定飞书群 ✅
- `local` → 结果留在本地（脚本内部自行调飞书 API 推送）
- **`origin`** → 推回用户 DM（对话窗口）❌ 极易误配

**典型踩坑：** 新建 cron 任务时如果用了 `origin`（默认值或手动填错），内容会直接发到 DM 而不是订阅群。用户明确说过"别推送到这里"，所有主动推送内容一律走 `feishu:oc_c6883cd907e4d226736d87ce9c6c6d79`。

**当前已确认 deliver 有误的 job（2026-06-10 已修复）：**
| job_id | job 名称 | 原 deliver | 改后 |
|--------|---------|-----------|------|
| `27433eb6e582` | hermes-political · 国内政策监测 | `origin` | `feishu:oc_c6883cd907e4d226736d87ce9c6c6d79` |
| `df79fff69067` | hermes-economic · 经济监测 | `origin` | `feishu:oc_c6883cd907e4d226736d87ce9c6c6d79` |

**验证方法：** `cronjob list` 查看所有 job 的 `deliver` 字段，检查是否有 `origin`。

## 通用故障排查

1. **脚本写入文件但没有收到推送** — 先检查 cron job 的 `deliver` 设置。如果设为 `feishu:oc_xxx`，走的是文件检测模式，飞书收到的是未渲染的原始 markdown。**正确做法：deliver 设为 `local`，脚本自己调飞书 API 推送。**
2. **Job 名称相近混淆** — 本技能库有多个 job 都以"每周"开头：
   - `🛒 每周生活用品优惠精选` = `weekly-deals.py`（job `470ec95180bb`）
   - `⭐ 每周生活选题推送` = `weekly-life-topics.py`（job `6b1782f0b52b`）
   - `🎮 游戏周报` = `game-weekly-digest.py`
   - 确认方式：用 `cronjob list` 查看 `job_id` 配对
3. **飞书 token 相关报错** — 用 `tenant_access_token` 而非 webhook token。获取方式：`POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal` + `app_id`/`app_secret`。收到 `19001 param invalid: incoming webhook access token invalid` 说明用了 webhook 模式而非 API 模式。
4. **网络超时** — BBC Travel、smzdm 等站响应慢，超时设置要够大（BBC Travel goto timeout ≥70s），同时脚本内加 `subprocess.TimeoutExpired` 捕获，单源超时不影响其他源继续运行。

## 参考资料

- `references/feishu-message-format.md` — 飞书消息推送格式（含 content 双重序列化陷阱、两种推送机制对比、错误码排查）
- `references/lifestyle-content-directions.md` — 旅居/数字游民内容方向指南（主人定制内容方向，2026-06-16）
- `references/weekly-life-topics-format.md` — 每周生活选题输出格式规范（单条+加粗+序号，cron run行为踩坑）
- `references/workout-state-bug.md` — 体态训练 state 文件日期 bug 详解
- `references/beauty-daily.md` — 颜值体态内容循环逻辑
- `references/business-news-rss-sources.md` — 商界要闻 RSS 源实测记录
- `references/translate-api-patterns.md` — 翻译 API 方案对比
- `references/celebrity-event-discovery.md` — 查找明星城市活动的方法
- `references/robot-news-scraper.md` — 机器人资讯抓取方案

---

## 网络环境说明

此服务器直连部分国际网络受限：
- Google News / Wikipedia / Allkpop — 无法直连
- Soompi RSS / BBC World RSS / Reuters RSS — 直连不行，需走 `socks5://127.0.0.1:10808` 代理 ✅
- Google Translate 免费接口 — 直连不行，也需走代理 ✅
- Bing 搜索 RSS — 直连正常（用 www.bing.com，不用 cn.bing.com）
- 豆瓣 `douban.com` — 直接 browser_navigate 正常 ✅
- 知乎 / 微博 — 可访问但内容非新闻

**代理连通性检测：** curl 使用 `--socks5-hostname 127.0.0.1:10808` 而非 `-x socks5://`，才能让 DNS 也走代理（`-x socks5://` 只转发已解析的 IP，DNS 仍走本地）。返回 302 即表示代理可用。

**已确认可用的新闻 RSS 源（2026-05实测）：**
| 来源 | URL | 代理 |
|------|-----|------|
| BBC World | `https://feeds.bbci.co.uk/news/world/rss.xml` | 必须 |
| BBC Business | `https://feeds.bbci.co.uk/news/business/rss.xml` | 必须 |
| FT中文网 | `https://www.ftchinese.com/rss/feed` | 必须 |
| 36氪 | `https://36kr.com/feed` | 不需要 |
| Soompi | `https://www.soompi.com/feed/` | 必须 |

**国内新闻站（RSS全失效，慎用）：**
| 来源 | 状态 |
|------|------|
| 人民网/新华网 RSS | 404 |
| 澎湃新闻 | JS渲染，RSS失效 |
| 观察者网 RSS | JS反爬，需 Playwright |
| 腾讯/凤凰/新浪 RSS | 反爬/WAF |
| 华尔街见闻 RSS | 404 |

国内站如需抓取，优先 Playwright headless Chrome（见 political-news-push 章节）。

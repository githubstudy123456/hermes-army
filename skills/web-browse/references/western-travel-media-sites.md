# Western Travel & Culture Media: Site Accessibility (2026-06-05 Update)

> 以下为 2026年6月5日实测记录。本周确认：**curl 直连 RSS 是最稳定的采集方案**，BBC/Guardian 等大站 curl 超时但 RSS feed 不一定超时。

## ✅ 可靠采集方案（按优先级）

| 来源 | RSS URL | curl 状态 | 备注 |
|------|---------|-----------|------|
| **Condé Nast Traveler** | `https://www.cntraveler.com/feed/rss` | ✅ 200 | 文章质量高，文化/生活方式类多，每批30条 |
| **Bon Appétit** | `https://www.bonappetit.com/feed/rss` | ✅ 200 | 饮食文化、旅行文学类内容丰富 |
| **Monocle** | `https://monocle.com/feed/rss/` | ✅ 200 | 全球文化、设计、生活方式，质量极佳 |
| **NPR Culture** | `https://feeds.npr.org/1001/rss.xml` | ✅ 200 | 国际文化、人物故事 |

### ✅ 可直连（browser_navigate）

| 站点 | URL | 状态 | 备注 |
|------|-----|------|------|
| National Geographic Travel | `nationalgeographic.com/travel` | ✅ 可访问 | 文章深度高，但首页加载慢 |
| Smithsonian Magazine | `smithsonianmag.com/travel` | ✅ 可访问 | 深度人文叙事文章 |

## ❌ 已知不可访问（2026-06-05 实测）

| 站点 | 失败原因 | 替代方案 |
|------|---------|---------|
| BBC Travel (主页 + RSS) | curl 返回 000，超时 | 换 NPR / Monocle |
| The Guardian Travel | curl 返回 000，超时 | 换 Smithsonian |
| Atlas Obscura | Cloudflare Bot Protection（403） | 换 Smithsonian |
| Eater (root RSS) | 404（RSS 不在根路径） | 换 Bon Appétit |
| Smithsonian RSS | 404（无 RSS） | 用 browser_navigate 直连 |
| Travel + Leisure | 403 | 换 CNT RSS |
| Lonely Planet | 403 | 换 Monocle |
| Serious Eats | 403 | 换 Bon Appétit |

## 💡 推荐工作流（旅行/文化内容选题 cron 任务）

**最佳方案：用 Python urllib 直读 RSS + 正则解析**

```python
import urllib.request, re, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

sources = {
    "Condé Nast Traveler": "https://www.cntraveler.com/feed/rss",
    "Bon Appétit": "https://www.bonappetit.com/feed/rss",
    "Monocle": "https://monocle.com/feed/rss/",
}

for name, url in sources.items():
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        content = r.read().decode('utf-8', errors='ignore')
        items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
        for item in items[:15]:  # 前15条通常涵盖近7天
            title = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
            pub = re.search(r'<pubDate>(.*?)</pubDate>', item, re.DOTALL)
            desc = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
            cat = re.search(r'<category>(.*?)</category>', item, re.DOTALL)
            t = title.group(1).strip() if title else ""
            p = pub.group(1).strip()[:16] if pub else ""
            d = re.sub(r'<[^>]+>', '', desc.group(1).strip()) if desc else ""
            c = cat.group(1).strip() if cat else ""
            # 过滤低质量类目：Shopping / Deals & Rewards / Places to Stay
            # 保留：Inspiration / Culture / Food & Drink / Adventure / Women Who Travel
            print(f"[{p}] [{c}] {t}")
            print(f"  {d[:120]}")
```

**过滤逻辑**：RSS 文章通常按时间排序，前15条≈近7天内容。
- 排除类目：`Shopping`、`Deals & Rewards`、`Places to Stay`
- 保留类目：`Inspiration`、`Culture`、`Food & Drink`、`Adventure`、`Train Journeys`、`Women Who Travel`

## 🔑 验证记录（2026-06-05）

| URL | 状态 | 备注 |
|-----|------|------|
| `https://www.cntraveler.com/feed/rss` | ✅ 200 | 30条，文化/生活方式类约17条 |
| `https://www.bonappetit.com/feed/rss` | ✅ 200 | 30条，Culture 类约5条 |
| `https://monocle.com/feed/rss/` | ✅ 200 | ~5条/次，更新频率低但质量极高 |
| `https://feeds.npr.org/1001/rss.xml` | ✅ 200 | 新闻为主，文化相关内容需过滤 |
| `https://www.nationalgeographic.com/travel` | ✅ browser_navigate | 成功但慢（60s超时） |
| `https://www.bbc.com/travel` | ❌ curl 000，browser_navigate 超时 | — |
| `https://www.theguardian.com/travel` | ❌ curl 000 | — |
| `https://www.atlasobscura.com/atom.xml` | ❌ 403 Cloudflare | — |
| `https://www.eater.com/rss` | ❌ 404 | — |
| `https://www.smithsonianmag.com/rss/...` | ❌ 404 | — |
| `https://www.lonelyplanet.com/news/feed` | ❌ 403 | — |

## 📌 关键发现（2026-06-05）

1. **CNT RSS 是本轮最可靠来源**：30条内容中17条为文化/生活方式类，质量高且稳定
2. **Monocle 质量极佳但量少**：每次仅5条，更新周期约1-2天，适合深度定制
3. **BBC/Guardian 在服务器环境下完全无法访问**：不是超时，而是连接拒绝——说明是 IP 层面的阻断，不是临时性问题
4. **Atlas Obscura 有 Cloudflare**：浏览器也无法绕过，需要高级 stealth 模式
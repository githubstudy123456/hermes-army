---
name: fashion-luxury-newsletter
description: 每周/每日时尚奢侈品牌新闻采集 → 飞书/微信群推送。执行关键词搜索（5组并行）、多源内容抓取、中文摘要整理、按分类推送的全流程。
triggers:
  - "时尚奢侈品牌新闻"
  - "luxury fashion newsletter"
  - "每日时尚资讯"
  - "时尚新闻 推送"
  - "fashion news digest"
---

# Fashion & Luxury News Newsletter Skill

执行频率：每日 cron 或按需。

## 工作流程

### 第一步：并行 RSS 抓取（最可靠，先跑）

两个主力 RSS 源，返回结构化数据（标题+描述+日期），无需解析复杂 HTML：

```python
import urllib.request, re, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

rss_urls = [
    ('WWD', 'https://wwd.com/feed/'),
    ('Luxury Daily', 'https://www.luxurydaily.com/feed/'),
]
for name, url in rss_urls:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        content = r.read().decode('utf-8', errors='ignore')
    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    for item in items[:15]:
        title = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
        desc = re.search(r'<description>(.*?)</description>', item, re.DOTALL)
        pub = re.search(r'<pubDate>(.*?)</pubDate>', item, re.DOTALL)
        # ... extract and clean
```

### 第二步：备用中文来源（补充中国区内容）

中文来源通常 DNS 不稳定，建议用 Python urllib：

```python
cn_sources = [
    ('Vogue中国', 'https://www.vogue.com.cn/'),
    ('FashionNetwork中国', 'https://cn.fashionnetwork.com/news/'),
]
```

### 第三步：关键词搜索补充（发现新事件）

仅作为补充，不作为主力。使用 Python urllib 访问 Bing：

```python
searches = [
    ('met_gala', 'https://cn.bing.com/search?q=Met+Gala+2026+highlights&setlang=zh-CN'),
    # ⚠️ Bing 中文搜索结果质量差，会返回大量baike/词典内容
    # ⚠️ setlang=en 也不能完全解决本地化问题
]
```

### 第四步：内容筛选与分类

从收集到的条目中筛选：
- 去除 Dictionary/Baike 类垃圾结果
- 优先保留：品牌人事任命、重大Campaign、新品发布、合作联名、行业战略
- 按分类组织：品牌动态 / 人事 / 展会 / 运动时尚 / 球鞋潮牌 / 中国市场

### 第五步：输出格式

```
👜 国际时尚 · 奢侈品牌动态
2026年5月29日 · 每日资讯

---

【品牌动态】
**新闻标题**
摘要（2-3句），说明事件意义和背景。
来源：媒体名（日期）

---
```

## 已知问题 / 踩坑

**Fashion 新闻站大批量不可访问**：以下站点评测后 DNS 失败或返回错误，从备用列表移除：
- `elle.com` → DNS failure
- `elle.com.cn` → DNS failure  
- `marieclaire.com.cn` → DNS failure
- `highsnobiety.com` → 404
- `bof.com` → 404
- `fashionista.com` → 403
- `whowhatwear.com` → 返回空
- `thecut.com` → 404
- `byrdie.com` → 403
- `fashionweekonline.com` → 返回空
- `luxurysociety.com` → 404
- `jingdaily.com` → 404
- `hypebeast.com` → 返回空

**Luxury Daily 文章页 403**：Luxury Daily 的 RSS 能抓，但直接访问文章 URL 返回 403。依赖 RSS 摘要即可，不要尝试单独抓文章。

**Bing 搜索本地化严重**：即使指定 `setlang=en`，Bing 仍返回大量中文 baike/dictionary 结果。适合用于发现中文来源的链接，不适合作为英文新闻发现工具。

**curl | grep 不可靠**：终端 curl + grep 管道的正则匹配经常返回空，改用 Python urllib + execute_code 工具。

**百度搜索不可用**：严格滑块验证，服务器环境无法绕过。

## 可靠来源速查

| 来源 | URL | 状态 | 内容类型 |
|------|-----|------|----------|
| WWD | `https://wwd.com/feed/` | ✅ 可用 | 行业新闻、品牌动态、人事 |
| Luxury Daily | `https://www.luxurydaily.com/feed/` | ✅ 可用 | 奢侈品牌campaign、产品 |
| Vogue中国 | `https://www.vogue.com.cn/news/` | ✅ 可用 | 中文时尚资讯 |
| Vogue HK | `https://www.voguehk.com/` | ✅ 可用 | Met Gala等国际活动 |
| Rayli瑞丽 | `https://www.rayli.com.cn/` | ✅ 可用 | 中国明星/品牌报道 |
| Hypebeast CN | `https://hypebeast.cn/category/fashion` | ⚠️ 经常空 | 球鞋、潮牌 |

## 输出目标

目标群：`oc_c6883cd907e4d226736d87ce9c6c6d79`（每日订阅群）

推送方式：直接文本发群里，不发文件，单次推送。
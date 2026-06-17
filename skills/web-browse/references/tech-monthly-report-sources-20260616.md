# 科技月报信息来源验证（2026-06-16 实测，2026-06-16 补充）

## 实测结论

| 来源 | 稳定性 | 内容质量 | 备注 |
|------|--------|----------|------|
| **36kr RSS** `https://36kr.com/feed` | ✅ 稳定 | 科技商业一手资讯 | 本次主要来源，含多篇高质量文章 |
| **新浪财经 lid=2517** | ✅ 稳定 | ⚠️ 纯市场/财经 | 本次用于市场数据补充，不含科技进展 |
| **Hacker News Algolia API** | ✅ 稳定 | 国际AI/科技 | 本次补漏国际内容 |
| **Bing 搜索（中文）** | ✅ 稳定 | ⚠️ 过滤后可用 | 仅抽象概念效果好，品牌名大量返回官网/百科 |
| **Bing 搜索（英文）** | ✅ 稳定 | ⚠️ 过滤后可用 | 含大量词典/百科，需排除 |
| **Nature/Science RSS** | ❌ 404 | — | 目标URL不可用 |
| **36kr API** `/api/newsflash/index` | ❌ 无数据 | — | 返回空 |
| **知乎热搜 API** | ✅ 可用 | 娱乐为主 | 不适合科技月报 |
| **小红书/抖音热搜** | ❌ 需登录 | — | bb-browser 返回401 |

## 搜索质量分析

### 抽象概念搜索 → 相对有效
```
量子计算 突破 2026       → 返回知乎/行业分析文章 ✅
大模型 进展 2026        → 返回资讯文章 ✅
人形机器人 进展 2026     → 返回新闻 ✅
```
### 具体品牌/公司搜索 → 大量返回官网/百科（更新）
```
华为突破 2026           → 返回华为官网/百科 ❌
比亚迪 汽车 2026        → 返回比亚迪官网/汽车之家 ❌
大疆 新品 2026          → 返回大疆官网/汉典 ❌
特斯拉 Robotaxi 2026    → 返回汉典/字典 ❌
OpenAI GPT-5 2026       → 返回OpenAI官方/知乎教程 ❌（即使setlang=en）
NVIDIA Blackwell 2026   → 返回NVIDIA官方/驱动下载 ❌
Apple WWDC 2026         → 返回Apple官方/商店 ❌
```
**根本原因**：Bing 的品牌词索引以官网为主，新闻结果被挤压到第2页之后。

**解决方案**：
1. 搜索时加新闻限定词：`"OpenAI GPT-5 release 2026 news"`、`"NVIDIA Blackwell GPU announcement 2026"`
2. 换用 `bb-browser site google/search "OpenAI GPT-5 2026"`（搜索功能已损坏）或直接访问公司博客/RSS
3. **科技月报场景优先 36kr RSS**，Bing 仅作特定事件验证

### Bing `setlang=en` vs `setlang=zh-CN`（2026-06-16 新发现）
| 场景 | setlang=en | setlang=zh-CN |
|------|-----------|--------------|
| 中文关键词抽象概念 | ✅ 过滤后可用 | ⚠️ 政府网站污染 |
| 英文关键词抽象概念 | ✅ 过滤后可用 | ❌ 政府网站污染 |
| 品牌/公司名搜索 | ⚠️ 返回官网/百科 | ❌ 返回官网+政府污染 |
| **结论** | **一律用 `setlang=en`** | 避免使用 |

### 顶会日期搜索（2026-06-16 新发现）
```
ICML 2026 official site (icml.cc/2026) → HTTP 404 ❌
NeurIPS 2026 site → 返回2025年信息 ❌
CVPR 2026 site → 返回2025年信息 ❌
```
**解决方案**：
- 搜索 `"site:icml.cc 2026 conference date"` 定位
- 或用 `bb-browser site google/search "ICML 2026 date location"`（搜索功能已坏则换 Bing）
- 直接访问 conference organzier 的 general 页面（如 ICLR 的 `learnai.one`）

## 内容覆盖缺口

| 领域 | 是否有可靠来源 | 备注 |
|------|--------------|------|
| 中国科技工业进展 | ⚠️ 部分 | 36kr覆盖科技公司，但深度不如行业垂直站 |
| 国际AI/科技前沿 | ✅ | HN Algolia + 36kr可覆盖 |
| 学术进展（论文级）| ❌ | arXiv API需翻墙，无头环境不可用 |
| 国内政策文件 | ❌ | 新华网RSS失效，gov.cn搜索失效 |
| 量子/生物医药 | ⚠️ | Bing搜索抽象概念有效，但具体公司弱 |

## 推荐信息源组合（科技月报场景）

```python
# 1. 36kr RSS — 中文科技商业新闻（主力）
import urllib.request, re, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request('https://36kr.com/feed', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
    content = r.read().decode('utf-8', errors='ignore')
    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    for item in items[:15]:
        title_m = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
        # ...

# 2. 新浪财经政经 API — 市场数据（补充）
url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&num=20&page=1'
# 返回字段：ctime, title, url, intro
# ⚠️ 内容偏A股/港股市场，非科技政策或学术

# 3. HN Algolia — 国际AI/科技（补漏）
url = 'https://hn.algolia.com/api/v1/search?query=AI+model+breakthrough&tags=story&hitsPerPage=15'
# 支持关键词搜索，单次请求，速度快

# 4. Bing 搜索 — 特定事件（仅抽象概念）
from urllib.parse import quote
query = quote("量子计算 突破 2026")
url = f"https://www.bing.com/search?q={query}&setlang=zh-CN&count=10"
# 过滤：排除含'百度','百科','词典','翻译','汉典','维基','知乎','字典'的结果
```

## 已知失败来源（2026-06-16）

- `https://www.nature.com/natmachintell/rss` → HTTP 404
- `https://www.sciencedaily.com/rss/all/top/technology.xml` → HTTP 404
- 36kr `/api/newsflash/index` → 返回空JSON
- 知乎热搜 → 内容娱乐化，不适合科技月报
- 小红书/抖音热搜 → 需要登录态，bb-browser 返回401
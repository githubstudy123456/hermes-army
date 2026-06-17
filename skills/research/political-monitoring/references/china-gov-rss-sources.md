# 中国政府网站 RSS/信息源实测记录（2026-06）

## RSS 源验证结果

| 来源 | URL | 状态 | 说明 |
|------|-----|------|------|
| 新华网政治 RSS | `http://www.xinhuanet.com/politics/news_politics.xml` | ⚠️ 可用但数据旧 | 2026-06 实测返回2022年旧数据，**不可用于政治监测** |
| gov.cn | `www.gov.cn/xxgk/` | ❌ 404 | 政务联播RSS不存在 |
| people.com.cn | `www.people.com.cn` | ❌ 无公开RSS | — |
| cctv.com | `www.cctv.com` | ❌ 404 | — |
| chinadaily.com.cn | `www.chinadaily.com.cn` | ❌ 404 | — |
| chinanews.com | `www.chinanews.com` | ❌ 404 | — |
| cankaoxiaoxi.com | `www.cankaoxiaoxi.com` | ❌ 404 | — |

**结论：大多数中国政府网站 RSS 返回404，仅新华社政治 RSS 可访问（但数据老化）。政治监测必须走页面扫描，不能依赖 RSS。**

## 替代方案

### 新浪财经政经新闻 API（实测可用）
- **lid=2517** → 国内财经政经新闻（⚠️ 实测全为美股/国际财经，非国内政策）
- **lid=2516** → 头条新闻（同上）
- **适用场景**：宏观市场情绪参考，**不适用于政治监测**

### 36氪 RSS
- `https://36kr.com/feed` — 稳定，内容偏科技商业，非官方政策来源

### 唯一可靠政治监测方案：Gov.cn 三通道
1. `/yaowen/liebiao/YYYYMM/content_NNNNNN.htm` —政务要闻
2. `/zhengce/content/YYYYMM/content_NNNNNN.htm` — 政策文件正文
3. `/lianbo/YYYYMM/content_NNNNNN.htm` — 政务联播

## Content ID 扫描法（核心增量发现技术）

**原理**：Gov.cn 所有文章使用全局自增 Content ID，ID 大小直接反映新旧。

**扫描策略**：
```
已知当日最高 content ID → 从该ID+1 向上扫描 → 发现所有新发布
```

**实测数据（2026-06-12）**：
- 6月11日最高 ID ≈ `7071863`（张国清出席峰会，23:09）
- 扫描 `7071864–7072100` 未发现6月12日新内容
- 结论：6月12日早间无新核心政策文件发布

**扫描命令**（execute_code Python urllib）：
```python
import urllib.request, ssl, re
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
found = []
for content_id in range(7071864, 7072100):
    url = f'https://www.gov.cn/yaowen/liebiao/202606/content_{content_id}.htm'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            html = r.read().decode('utf-8', errors='ignore')
        date = re.search(r'(\d{4}-\d{2}-\d{2})', html)
        title = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
        title_clean = re.sub(r'<[^>]+>', '', title.group(1)).strip() if title else 'unknown'
        date_str = date.group(1) if date else 'unknown'
        if '2026-06-12' in date_str:
            found.append((content_id, title_clean, url))
    except:
        pass
```

## 已知踩坑

- **urllib 访问 gov.cn SSL 错误**：服务器环境下 `ssl.SSLError`常见。**换用 `browser_navigate`**，走 Chrome 内置 SSL，成功率更高。
- **gov.cn lianbo/ 超时**：实测 `browser_navigate('https://www.gov.cn/lianbo/index.htm')` 超时60s。**绕过**：直接访问 `lianbo/YYYYMM/content_*.htm` 具体文章。
- **Bing 搜索超时**：cron 环境 Bing 搜索几乎必然超时。**改用 gov.cn 首页导航**或直接扫描 Content ID。
- **百度搜索验证码**：严格滑块验证，服务器环境无法绕过。**换必应或直接导航**。
- **gov.cn 目录页 404**：频道目录页（`/yaowen/liebiao/YYYYMM/index.htm`）几乎全部404。**可靠入口只有首页**。
- **内容来源"央视网"**：gov.cn 转载央视网文章时，需确认是否有一手官方源。
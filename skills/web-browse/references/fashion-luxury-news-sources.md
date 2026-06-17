# 时尚·奢侈品新闻来源（已验证）

## 英文行业媒体

### Business of Fashion (BoF) ⭐ 首选
- 主页: `https://www.businessoffashion.com/`
- 文章页: `https://www.businessoffashion.com/articles/luxury/chanel-earnings-results-matthieu-blazy-return-to-growth/`
- **特点**: 标题摘要质量高，内容需付费墙，但首页摘要可直接抓取
- **工具**: `browser_navigate` + `browser_snapshot`（文章页）；`execute_code` urllib 直读首页效果差（JS 渲染）

### WWD (Women's Wear Daily)
- 主页: `https://wwd.com/`
- **特点**: JS 渲染严重，`execute_code` urllib 基本无法提取内容
- **工具**: `browser_navigate` + `browser_snapshot`

### Highsnobiety
- 主页: `https://www.highsnobiety.com/`
- 文章页: `https://www.highsnobiety.com/p/<slug>/`
- **特点**: 首页有标题列表；文章页 URL 不规律（slug 格式），直接 urllib 拼 URL 极易 404
- **工具**: `browser_navigate` 首页；`browser_navigate` + `browser_snapshot` 文章页

### Complex.com
- 主页: `https://www.complex.com/style/`
- **特点**: 首页有标题列表，文章 URL 可从首页快照中获取 href
- **工具**: `browser_navigate` + `browser_snapshot`

### Vogue (国际版)
- 主页: `https://www.vogue.com/`
- **特点**: 有付费墙，但部分内容可读
- **工具**: `browser_navigate`

## 中文时尚媒体

### Vogue 中国
- 主页: `https://www.vogue.com.cn/`
- **特点**: 中文内容，可直读；文章页 URL 格式 `/fashion/industry/news_<id>.html`
- **工具**: `execute_code` urllib 或 `browser_navigate`

### GQ 中国
- 主页: `https://www.gq.com.cn/`
- **特点**: 中文内容，首页内容需 JS 渲染

## 不可用来源（2026年5月验证）

| 来源 | 问题 |
|------|------|
| cn.bing.com | 返回字典/百科/知道结果，无新闻 |
| Fashionista.com | 403 Forbidden |
| SneakerNews.com | 403 Forbidden |
| bof.com/articles/* (直接 urllib) | 付费墙，只返回登录提示 |

## 搜索关键词策略

英文搜索（国际 Bing）:
```
https://www.bing.com/search?q=luxury+fashion+May+2026+news&setlang=en
https://www.bing.com/search?q=Paris+Fashion+Week+2026+highlights&setlang=en
```
⚠️ `cn.bing.com` 会返回中文内容（字典/百科），用 `www.bing.com/search?setlang=en` 替代

## BoF 首页典型输出（browser_snapshot）
```
heading "How Luxury Lost 50 Million Customers" [ref=e32]
paragraph: Price hikes, diminished quality, growing inequality...
heading "Shein's Everlane Acquisition, Explained"
paragraph: It's official: The fallen direct-to-consumer darling...
```
→ 直接提取 `<h3>` 标题 + 后接 `<p>` 摘要即可，无需翻页

## 采集优先级（cron 日报场景）

1. BoF 首页 `browser_navigate` → `browser_snapshot` — 主力来源
2. Highsnobiety 首页 `browser_navigate` → `browser_snapshot` — 补充潮牌/球鞋
3. Complex 首页 `browser_navigate` → `browser_snapshot` — 补充球鞋/联名
4. Vogue China `execute_code` urllib — 中文内容补漏

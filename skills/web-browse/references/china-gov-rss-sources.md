# 中国政府网站 RSS 源验证（2026-06 实测）

## 可用 RSS 源

| 站点 | URL | 状态 | 备注 |
|------|-----|------|------|
| 新华网时政 | `http://www.xinhuanet.com/politics/news_politics.xml` | ✅ 可用 | 300条，最全的政府/政治新闻来源 |
| 36kr RSS | `https://36kr.com/feed` | ✅ 可用 | 科技/财经新闻，稳定快速 |

## 已验证失效（404/超时）

| 站点 | URL | 失败时间 |
|------|-----|---------|
| 中国政府网 | `http://www.gov.cn/rss/politics.xml` | 404 |
| 人民网 | `http://paper.people.com.cn/rss/politics.xml` | 404 |
| 央视网 | `https://www.cctv.com/rss/politics.xml` | 404 |
| 中国日报 | `http://www.chinadaily.com.cn/rss/rss.xml` | 404 |
| 中国新闻网 | `https://www.chinanews.com/rss/news.xml` | 404 |
| 参考消息 | `http://www.cankaoxiaoxi.com/rss/politics.xml` | 404 |
| 新华网财经 | `http://www.xinhuanet.com/finance/rss.xml` | 404 |

## 新华网时政 RSS 特殊格式

**pubDate 格式**：无 `<![CDATA[]]>` 包裹，日期字符串紧跟前一个标签无换行。
```
<title><![CDATA[标题]]></title><author>www.xinhuanet.com</author><link>http://...<link>Wed,14-Dec-2022 11:37:37 GMT
```
注意 `</link>` 和日期之间没有换行，也没有 CDATA 包裹。

**推荐提取方式**：
```python
import re
# 提取日期
date_match = re.search(r'(\d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2})', item_text)
# 提取标题（标准 CDATA 格式）
title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item_text)
```

## 备选方案：browser_navigate

对于返回 404 的政府网站，直接用 `browser_navigate` 访问首页比 urllib 可靠：
```bash
browser_navigate https://www.gov.cn/
```
它走 Chrome 内置 SSL，不依赖系统证书，不会遇到 urllib 的 SSL 兼容问题。

## 政治政策监控推荐工作流

1. **首选**：`browser_navigate https://www.gov.cn/` — 政府网首页有时政要闻
2. **次选**：`http://www.xinhuanet.com/politics/news_politics.xml` — 新华网时政 RSS
3. **补漏**：36kr RSS `https://36kr.com/feed` — 科技/财经政策动态

注意：gov.cn 首页是动态渲染的 JS 内容，`browser_navigate` 快照可以提取，但 urllib 直读只能拿到空壳 HTML。
#热搜/爆火话题数据源验证（2026-06-08）

## 实时验证结果

| 来源 | 方案 | 结果 | 备注 |
|------|------|------|------|
| B站热搜 | `api.bilibili.com/x/web-interface/ranking/v2` | ❌ 静默返回空 | cron环境无头模式下数据为空，无报错 |
| 知乎热搜 | `api.zhihu.com/v4/hot-list` | ❌ 404 | API端点疑似变更 |
| 微博热搜 | `weibo.com/ajax/side/hotSearch` | ❌ 403/重定向 | 需要登录态 |
| 微博热搜 | `weibo.com/ajax/statuses/hot_band` | 未测 | — |
| Hacker News | Firebase IO API（先IDs再逐条） | ⚠️ 慢（>4s） | 两次请求，实测5条耗时4.6s |
| Hacker News | Algolia API | ✅ 成功，快速 | `https://hn.algolia.com/api/v1/search?query=&tags=story&hitsPerPage=5` |
| 36kr RSS | `https://36kr.com/feed` | ✅ 成功 | 中文科技新闻首选，标题+摘要+链接全有 |
| 知乎 | browser_navigate | ⚠️ 强制登录 | 需要已登录 Chrome CDP |
| 微博 | browser_navigate | ⚠️ 访客系统重定向 | 同样需要登录态 |

## 推荐 cron 环境工作流

```python
# 中文科技新闻 → 36kr RSS（最稳）
req = urllib.request.Request('https://36kr.com/feed', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
    content = r.read().decode('utf-8', errors='ignore')
    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    for item in items[:5]:
        title = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
        link = re.search(r'<link><!\[CDATA\[(.*?)\]\]>', item, re.DOTALL)
        print(title.group(1).strip(), link.group(1).strip())

# Hacker News → Algolia API（快速）
req = urllib.request.Request(
    'https://hn.algolia.com/api/v1/search?query=AI&tags=story&hitsPerPage=5',
    headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    d = json.loads(r.read())
    for hit in d['hits'][:5]:
        print(hit['title'])

# GitHub 新项目 → 按创建时间过滤
req = urllib.request.Request(
    'https://api.github.com/search/repositories?q=created:>2026-06-01&sort=stars&order=desc&per_page=5',
    headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github.v3+json'})
```

## K-pop 热搜局限

抖音热搜 API 的 `keyword=K-pop` 参数返回的是综合热搜而非 K-pop 专项，实际内容偏娱乐/体育/社会新闻。Reddit r/kpop 在 cron 环境超时。K-pop 精准热搜暂无可靠免费方案，Bing 搜索英文关键词会返回大量词典/百科结果需二次过滤。

## 待补充

- 抖音/小红书 K-pop 专项热搜（需 Playwright CDP 登录态）
- 微博热搜（需 Playwright CDP 登录态）
- 知乎热搜（需 Playwright CDP 登录态）
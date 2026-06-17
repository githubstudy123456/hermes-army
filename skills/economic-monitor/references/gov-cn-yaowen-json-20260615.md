# gov.cn 要闻 JSON 端点（2026-06-15 验证）

## 端点
```
https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json
```

## 响应格式
- 返回 400 条记录（按发稿时间倒序，最新在前）
- 每条字段：`DOCRELPUBTIME`、`TITLE`、`URL`
- URL 格式：`/yaowen/liebiao/202606/content_7072204.htm`（路径含年月，ID 越大越新）

## 过滤今日文章
```python
import urllib.request, json, ssl
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

today = datetime.now().strftime('%Y-%m-%d')
url = 'https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
    d = json.loads(r.read())
    items = d if isinstance(d, list) else d.get('result', d.get('data', []))

recent = [i for i in items if i.get('DOCRELPUBTIME', '')[:10] == today]
# recent[0] = 最新一条
```

## 优点
- 无需 Playwright/CDP，urllib 直调，~0.5s
- 字段干净（DOCRELPUBTIME/TITLE/URL），无需 HTML 解析
- 400 条全量返回，不遗漏边缘文章
- 过滤逻辑简单：`[:10] == today`

## 已知限制
- **政策文件端点不存在**：`/zhengce/liebiao/ZHENGCELIEBIAO.json` → HTTP 404
- gov.cn 三通道中只有 YAOWENLIEBIAO.json 可用，zhengce/liebiao 列表页需用 browser 工具提取
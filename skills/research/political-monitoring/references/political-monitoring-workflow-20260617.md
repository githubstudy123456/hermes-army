# 政治监测工作流笔记（2026-06-17）

## gov.cn YAOWENLIEBIAO.json 实测记录

**端点**: `https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json`
- 返回400条记录，每条含 `TITLE/URL/DOCRELPUBTIME`
- 按发稿时间倒序，无需分页（同一页面重复请求返回相同400条）
- **仅覆盖约1个月**（2026-05-16 ~ 2026-06-17），3个月以上历史数据无法通过此接口获取
- URL结构：`/yaowen/liebiao/202606/content_7072391.htm`（content ID = 年月+6位序号）

```python
import urllib.request, json, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.gov.cn/'})
with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
    d = json.loads(r.read().decode('utf-8'))
    items = d if isinstance(d, list) else d.get('result', d.get('data', []))

today = '2026-06-17'
today_items = [i for i in items if today in i.get('DOCRELPUBTIME', '')]
for i in today_items:
    print(f"[{i['DOCRELPUBTIME']}] {i['TITLE']}")
    print(f"  {i['URL']}")
```

## 2026-06-17 本次监测发现

| 级别 | 标题 | 来源 | 存档 |
|------|------|------|------|
| P2 | 习近平同缅甸总统敏昂莱会谈 | gov.cn | `political_20260617_0821.txt` |
| P2 | 习近平：一体推进教育科技人才体制机制改革 | 求是杂志 | `political_20260617_0821.txt` |
| P3 | 王毅同巴基斯坦副总理达尔通电话 | gov.cn | `political_20260617_0821.txt` |

## Playwright CDP 稳定性注意

`p.chromium.connect_over_cdp("http://localhost:19825")` 在 `execute_code` sandbox 中可能报 `ECONNREFUSED`（Chrome端口已在监听但进程不在同一网络命名空间）。稳定方案：
1. `terminal(background=True)` 启动 Chrome → `ss -tlnp | grep 19825` 确认
2. 每次 `page.goto()` 后及时 `page.close()`
3. 用 `context.new_page()` 而非依赖 `context.pages[0]`

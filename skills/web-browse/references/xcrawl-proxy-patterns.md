# XCrawl 代理调用实战手册

> 2026-05-15 实测结论，来源于 K-pop 资讯脚本升级调试过程。

---

## 正确的 curl 写法（唯一可信方案）

Python 标准库 `urllib` / `requests` 均不支持 SOCKS 代理（除非装 `PySocks` / `requests[socks]`）。用 `subprocess + curl` 才是稳定方案。

```python
import subprocess, json

API_KEY = "xc-你的key"
PROXY_HOST = "127.0.0.1"
PROXY_PORT = "10808"

def xcrawl_search(query, limit=5):
    body = json.dumps({"query": query, "limit": limit})
    cmd = [
        "curl", "-s", "--socks5-hostname", f"{PROXY_HOST}:{PROXY_PORT}",
        "-X", "POST", "https://run.xcrawl.com/v1/search",
        "-H", f"Authorization: Bearer {API_KEY}",   # ← 必须有 "Authorization: " 前缀
        "-H", "Content-Type: application/json",
        "-d", body,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    data = json.loads(r.stdout)
    if data.get("status") == "completed":
        return data.get("data", {}).get("data", [])
    return []
```

---

## 三个必知坑

### 坑1：Header 缺少前缀 → 403 Forbidden
```bash
# ❌ 错误 — 这样会返回 {"message":"Authorization required"}
-H "Bearer $API_KEY"

# ✅ 正确
-H "Authorization: Bearer $API_KEY"
```
症状：`{"message":"Authorization required","request_id":"..."}`

### 坑2：用了错误的 SOCKS 写法 → curl 返回空结果 / SDK 报 403
```bash
# ❌ 错误 — -x 只转发 TCP，DNS 走本地（被墙拦截）
-x "socks5://127.0.0.1:10808"

# ✅ 正确 — --socks5-hostname DNS 也走代理
--socks5-hostname 127.0.0.1:10808
```

### 坑3：SDK 返回的是 dict 不是对象
```python
# ❌ 照文档写的 — 报错 AttributeError: 'dict' object has no attribute 'results'
resp = client.search({"query": "...", "limit": 5})
print(resp.results[0].title)

# ✅ 实际返回值结构
resp = client.search({"query": "...", "limit": 5})
results = resp.get("data", {}).get("data", [])
```

---

## credits 消耗（实测）

- Search API：**2 credits/请求**（不是文档写的 1）
- Scrape API：未确认
- 注册送 1000 credits，约够 500 次搜索

---

## Search vs Scrape API 选择

| 需求 | 用哪个 | 备注 |
|------|--------|------|
| 搜新闻/关键词/多源汇总 | **Search API** | 绕过反爬、Cloudflare、被墙站点 |
| 抓具体页面 JS 渲染内容 | Scrape API | 国内服务器直连 XCrawl 可能 403，需代理 |
| 绕过 Allkpop Cloudflare | **Search API** | Scrape 会被拦，Search 无问题 |

---

## 国内服务器访问 XCrawl

国内服务器直连 `run.xcrawl.com` 会被 403。必须走代理。

代理检测：
```bash
curl -s --socks5-hostname 127.0.0.1:10808 \
  -X POST https://run.xcrawl.com/v1/search \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"test","limit":1}'
# 返回 {"status":"completed"...} 即代理可用
```

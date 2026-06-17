# gov.cn 政策监测技术手册

## 页面结构

### gov.cn 要闻列表页（yaowen/liebiao）
URL: `https://www.gov.cn/yaowen/liebiao/`

结构：表格型列表，每行含日期 + 标题 + 链接。直接抓取 `<a>` 标签过滤 `gov.cn/yaowen` URL。

### gov.cn 文章页
URL 格式: `https://www.gov.cn/yaowen/liebiao/YYYYMM/content_CONTENTID.htm`

**标题选择器规则**:
- 要闻类（content_7071948）→ `h1, h2, .title` ✅
- 政策文件类（zhengceku，content_7072002）→ `h1, h2, .title` 超时30s → `body.inner_text` ✅ 正常

**正文段落**: `page.eval_on_selector_all("p", "els => els.map(e=>e.innerText.trim()).filter(t=>t.length>30)")`

## Playwright 操作要点

### 连接已有 Chrome CDP
```python
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    page.goto(url, timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    title = page.inner_text("h1, h2, .title")
    text = page.inner_text("body")
    browser.close()
```

### `eval_on_selector_all` 表达式规则
**必须**: 单行箭头函数，无分号，无 return 关键字
```python
# ✅ 正确
"els => els.map(e=>({t:e.innerText.trim(),u:e.href}))"
# ✅ 正确
"els => els.filter(e=>e.offsetParent!==null).slice(0,30).map(e=>({t:e.innerText.trim(),u:e.href}))"
# ❌ 错误 — 多行含分号
# ❌ 错误 — 包含 return 语句
# ❌ 错误 — Unexpected token ')'
```

### 关键词扫描（yaowen/liebiao 列表页）
```python
anchors = page.eval_on_selector_all("a", "els => els.map(e=>({t:e.innerText.trim(),u:e.href})))")
keywords = ['政治局', '常委', '两会', '经济工作会', '国务院', '常务', '国发', '国办发', '中办发', '中发', '习近平', '李强']
for a in anchors:
    if 'gov.cn/yaowen' in a['u'] and len(a['t']) > 8:
        for kw in keywords:
            if kw in a['t']:
                found.append((kw, a['t'][:80], a['u']))
```

## 新浪财经政经 API（备用）
```python
import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&num=30&page=1'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
    content = r.read().decode('gbk', errors='ignore')
    d = eval(content.replace('false', 'False').replace('true', 'True').replace('null', 'None'))
    items = d.get('result', {}).get('data', [])
```

## 输出路径
`~/.hermes/political-reports/`（注意：不是 `army-workspace/political/`）

## 已推送文件去重检查
同时检查两种日期格式：
- `20260614_*`（旧格式）
- `2026-06-14*`（新格式）

## 已知踩坑
- gov.cn `yaowen/liebiao` 列表页用 `browser_navigate` 超时60s → 用 Playwright CDP
- gov.cn 政策文件页（zhengceku）`h1, h2, .title` 超时 → 用 `body.inner_text`
- `page.evaluate()` 含 return 语句 → 用 `page.inner_text("body")` 代替
- gov.cn 搜索参数 `?searchword=...` 重定向到首页 → 直接访问列表页提取链接

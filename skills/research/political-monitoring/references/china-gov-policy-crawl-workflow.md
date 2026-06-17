# gov.cn 政策抓取工作流

## Chrome CDP 启动（必须先行）

```bash
google-chrome --remote-debugging-port=19825 --user-data-dir=/tmp/chrome-debug --no-sandbox --headless
```

> 不要用 `&` 后台语法，会被 vet 拦截。用 `terminal(background=True)` 或确保进程持久化。

## 已知 gov.cn 超时陷阱

| URL Pattern | 问题 | 绕过方式 |
|------------|------|---------|
| `gov.cn/lianbo/index.htm` | 超时60s | 不访问列表页，从首页侧边栏"政务联播"区块提取文章链接 |
| `gov.cn/yaowen/liebiao/` | 超时60s | 直接访问具体文章 URL |
| `gov.cn/yaowen/liebiao/YYYYMM/content_*.htm` | 错误的年月直接跳转首页 | 验证：访问后检查 `page.url` 是否仍为目标 URL |
| `/zhengce/index.htm` | 超时 | 可用，但较慢 |

**Gov.cn 首页永远可访问**：`https://www.gov.cn/` — 包含要闻、最新政策、政策解读、政务联播四大区块，是所有文章链接的稳定来源。

## 完整工作流

### 1. 从首页提取文章列表

用 `browser_navigate` 打开 `https://www.gov.cn/`，从快照中提取：
- 标题 + 链接（来自 `h2`/`h3` 标题元素或列表项 `listitem`）
- 优先从"要闻"和"最新政策"区块提取
- 链接格式：`/yaowen/liebiao/YYYYMM/content_CONTENTID.htm` 或 `/zhengce/content/YYYYMM/content_*.htm`

### 2. 逐条访问文章

对每条链接用 `browser_navigate` 获取正文内容。超时设 30s。

### 3. 内容提取选择器

```python
# 标题
page.eval_on_selector("h1", "e => e.innerText")

# 正文段落（过滤30字符以上，排除页眉页脚噪音）
page.eval_on_selector_all("p", "els => els.map(e => e.innerText.trim()).filter(t => t.length > 30)")
```

### 4. 去重检查

文章 URL 中的 `content_CONTENTID.htm` 是唯一标识。
- 对比今日 `~/.hermes/political-reports/report_YYYY-MM-DD*.txt` 中已推送的 ID
- 相同 ID → 静默跳过
- 新 ID → 进入5关审核

### 5. 文章页 URL 格式

```
# 要闻/领导活动
https://www.gov.cn/yaowen/liebiao/YYYYMM/content_CONTENTID.htm

# 政策文件
https://www.gov.cn/zhengce/content/YYYYMM/content_CONTENTID.htm

# 政务联播
https://www.gov.cn/lianbo/YYYYMM/content_CONTENTID.htm
```

年月必须精确匹配成文日期，错误年月会直接跳转到 gov.cn 首页。

## 新浪财经备用 API（gov.cn 超时时的降级方案）

当 gov.cn 所有页面超时无法访问时，使用新浪财经政经新闻 API：

```python
import urllib.request, re, ssl
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&k=&num=20&page=1'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://finance.sina.com.cn'
})
with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
    content = r.read().decode('gbk', errors='ignore')
    d = eval(content.replace('false', 'False').replace('true', 'True').replace('null', 'None'))
    items = d.get('result', {}).get('data', [])

# 过滤最近5小时新闻
ts_now = datetime.now().timestamp()
recent = [i for i in items if ts_now - int(i.get('ctime', 0)) < 5 * 3600]

for item in recent:
    ts = datetime.fromtimestamp(int(item['ctime'])).strftime('%H:%M')
    print(f"[{ts}] {item['title']}")
```

**有效 lid**：`lid=2517`（国内财经政经），`lid=2516`（头条新闻）

> ⚠️ 新浪财经 lid=2517 全天候100%为美股/国际财经新闻，**不适合政治监测**，仅作宏观市场情绪参考。

## Gov.cn 搜索失效的正确绕过方式

**问题**：`https://www.gov.cn/?searchword=...&channelid=...` 会重定向到首页，搜索功能不可用。

**正确方式**：直接访问列表页，从页面提取文章链接：
- 要闻列表：`https://www.gov.cn/yaowen/liebiao/`
- 政务联播：`https://www.gov.cn/lianbo/`
- 最新政策：`https://www.gov.cn/zhengce/zuixin/`
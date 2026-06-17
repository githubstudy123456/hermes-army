# gov.cn 爬取技术细节（2026-06 实测）

## 可靠来源
- 要闻列别页：`https://www.gov.cn/yaowen/liebiao/` — 最全，实时更新
- 联播页：`https://www.gov.cn/lianbo/index.htm` — **cron环境超时60s，不可用**

## Playwright CDP 直连模板
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://www.gov.cn/yaowen/liebiao/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    articles = page.eval_on_selector_all("a", "els => els.filter(e => e.href and e.href.includes('gov.cn/yaowen/liebiao/202606')).slice(0,40).map(e => ({t:e.innerText.trim(),u:e.href}))")
```

## 标题选择器
| 页面类型 | 选择器 | 备注 |
|---------|-------|------|
| 要闻类（如content_7071948） | `page.inner_text("h1, h2, .title")` | ✅ 正常 |
| 政策文件类（zhengceku如content_7072002） | `page.inner_text("h1, h2, .title")` | 超时30s → 改用 `page.inner_text("body")` |
| 正文段落 | `page.eval_on_selector_all("p", "els => els.map(e=>e.innerText.trim()).filter(t=>t.length>30)")` | 过滤30字符以下导航/页脚干扰 |

## URL 格式与重定向陷阱
- 正确格式：`https://www.gov.cn/yaowen/liebiao/YYYYMM/content_CONTENTID.htm`
- 示例：`https://www.gov.cn/yaowen/liebiao/202606/content_7071845.htm`
- 错误年月（如`202506`）→ 直接跳转到首页 `https://www.gov.cn/`，正文内容丢失
- **验证方法**：访问后检查 `page.url`，若变成 `https://www.gov.cn/` 说明URL错误

## Content ID 结构（2026-06 实测）
- 格式：`_7071845`
- 语义：2026年6月11日发布
- 规律：ID越高越新；同日多篇连续递增
- 最新文章 ID 范围：`_7072011`（2026-06-13 晚）

## 新浪财经政经快讯（lid=2517）
```python
import urllib.request, ssl
from datetime import datetime
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&num=30&page=1'
req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://finance.sina.com.cn'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
    items = eval(r.read().decode('gbk', errors='ignore')).get('result',{}).get('data',[])
# 过滤90分钟内
recent = [i for i in items if datetime.now().timestamp() - int(i.get('ctime',0)) < 90*60]
```

## 去重检查
报告命名格式：`YYYY-MM-DD_HHMM_事件关键词.md`
今日已有推送查 `~/.hermes/political-reports/` 目录，对比标题相似度>70%则跳过。
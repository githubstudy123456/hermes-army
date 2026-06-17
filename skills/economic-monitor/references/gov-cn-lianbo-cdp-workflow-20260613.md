# gov.cn Monitoring Workflows (2026-06-14 Update)

## ⚠️ CRITICAL UPDATE: lianbo/index.htm Unreliable — NOT Primary

The June 13 reference called lianbo/index.htm the "recommended workflow." This is now **superseded**:
- **2026-06-14 18:45 session**: lianbo/index.htm timed out 60s (second consecutive failure)
- lianbo remains useful as a **secondary** when it does load (captures 政务联播 articles)
- **PRIMARY** is now yaowen/liebiao/ + `page.inner_text("body")` text-parsing

## Status Table (2026-06-14)

## PRIMARY: yaowen/liebiao/ + page.inner_text("body") — Verified 2026-06-14

**Why this works**: CDP selector engine doesn't align with Chinese government site DOM; `page.inner_text("body")` bypasses selector issues entirely. Extracts title+date pairs from full page text.

```python
from playwright.sync_api import sync_playwright
import re

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://www.gov.cn/yaowen/liebiao/", timeout=20000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    text = page.inner_text("body")

    # Extract title + date pairs: "文章标题\n2026-06-14"
    articles = re.findall(r'(.{5,80}?)\s+(2026-\d{2}-\d{2})', text)

    # Filter for economic keywords
    econ_keywords = ['贷款', 'M2', 'CPI', 'PPI', '人民币', '汇率', '房地产', '降准', '降息',
                     '证监会', '央行', '美联储', '出口', '机电', '新能源', '重卡', '三峡',
                     '水运', '基建', '农业', '应急', '十五五', '私募', '外资']
    for title, date in articles:
        if any(k in title for k in econ_keywords):
            print(f"[{date}] {title.strip()}")

    browser.close()
```

**Key discovery this session (2026-06-14 18:45)**: Full article list including 三峡水运新通道 extracted successfully via this method — confirmed the workflow.

## Article URL Format (verified)

| Type | Pattern | Example |
|------|---------|---------|
| 要闻/国常会 | `/yaowen/liebiao/YYYYMM/content_CONTENTID.htm` | `/yaowen/liebiao/202606/content_7071948.htm` |
| 政务联播 | `/lianbo/YYYYMM/content_CONTENTID.htm` | `/lianbo/202606/content_7072010.htm` |
| 政策文件 | `/zhengce/zhengceku/YYYYMM/content_CONTENTID.htm` | `/zhengce/zhengceku/202606/content_7072002.htm` |

## Content Extraction by Article Type

| Type | Title Selector | Paragraph Selector | Notes |
|------|---------------|-------------------|-------|
| 要闻 (yaowen) | `h1, h2, .title` ✅ | `p` (filter >30chars) ✅ | Fast, ~3s |
| 政务联播 (lianbo) | `h1, h2, .title` ✅ | `p` (filter >30chars) ✅ | Fast, ~3s |
| 政策文件 (zhengceku) | `h1, h2, .title` ❌ timeout | N/A | **Must use `body.inner_text`** |

### zhengceku workaround (verified 2026-06-13)

```python
page.goto("https://www.gov.cn/zhengce/zhengceku/202606/content_7072002.htm", 
          timeout=20000, wait_until="domcontentloaded")
page.wait_for_timeout(2000)

# Instead of page.inner_text("h1, h2, .title") which times out:
text = page.inner_text("body")  # Gets all text in ~3s
print(text[:6000])  # Full policy text, includes title in body

# Alternative: extract via eval_on_selector_all for specific sections
```

## Redirection Check

Always verify the article loaded correctly by checking `page.url`:

```python
page.goto(url, timeout=20000, wait_until="domcontentloaded")
if page.url == "https://www.gov.cn/":
    print("REDIRECTED - URL invalid for this content")
    # The YYYYMM path component must match the article's actual publish month
```

## Key Insight: Lianbo Page Unifies All Three Content Types

The lianbo/index.htm 政务联播 section links to articles across **all three URL patterns** in a single page load — 要闻, 政务联播, and 政策文件 (zhengceku) links all appear together. A single CDP scan with `a[href*='content_']` + keyword filter catches all three types simultaneously.

**Session 2026-06-14 01:07 verification**: All 16 today's articles (夏粮收获/新能源重卡40%渗透率/机电出口占六成/铁路旅客19亿人次/铁路投资2485亿/水利防洪应急/养老体系/技能大赛等) were discovered via links extracted from lianbo/index.htm, including the 新能源重卡 policy document at `zhengce/zhengceku/` URL — confirming the single-scan workflow is complete.

## Why lianbo/index.htm Works When yaowen/liebiao Doesn't

- `yaowen/liebiao/` redirects internally to a SPA that returns ancient article IDs only
- `lianbo/index.htm` is a static page with actual current article links in the 政务联播 block
- The lianbo page's link section contains full article URLs including `content_7072010` (very recent, 2026-06-13)
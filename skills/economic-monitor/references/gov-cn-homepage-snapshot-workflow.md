# gov.cn 首页快照法降级工作流

**验证时间**：2026-06-13
**验证结论**：✅ 可用（snapshot法 + CDP法均验证通过）

## 问题背景

gov.cn 联播列表页 `lianbo/index.htm` 超时60s，要闻列表页 `yaowen/liebiao/` 可加载但 article URL 无法提取。

## 方案一：CDP 提取法（推荐，2026-06-13 验证）

用 Playwright CDP 连接已有 Chrome，直接提取政务联播区块的链接列表，比 snapshot 文本解析更可靠：

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://www.gov.cn/", timeout=20000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # 提取政务联播/要闻链接
    links = page.eval_on_selector_all(
        "a[href*='/yaowen/liebiao/'], a[href*='/lianbo/']",
        "els => els.filter(e => e.offsetParent !== null).slice(0, 30).map(e => ({t: e.innerText.trim().slice(0, 30), u: e.href}))"
    )
    for l in links:
        print(f"{l['t']} → {l['u']}")

    browser.close()
```

输出示例（2026-06-13 验证）：
```
前5月我国机电产品出口占整体出口比重超六成 → https://www.gov.cn/lianbo/202606/content_7071984.htm
李强主持召开国务院常务会议 → https://www.gov.cn/yaowen/liebiao/202606/content_7071845.htm
住建部地下管网77万公里 → https://www.gov.cn/lianbo/202606/content_7071450.htm
```

## 方案二：首页快照法（降级备选）

`browser_navigate('https://www.gov.cn/')` 加载后读取 `.inner_text("body")`，从文本中解析当日要闻列表。

适用场景：深夜时段新浪财经全为国际新闻占位时，gov.cn 首页是唯一可靠的国内政策来源。

## 限制

gov.cn 首页快照不含政策文件全文（仅标题+链接），需二次 navigate 才能读取正文内容。
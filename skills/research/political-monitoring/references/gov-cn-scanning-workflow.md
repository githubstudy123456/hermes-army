# Gov.cn 三通道扫描工作流（2026-06 实测）

## 三通道入口

| 通道 | URL | 内容类型 | 实测条数 |
|------|-----|---------|---------|
| 联播 | `https://www.gov.cn/lianbo/index.htm` | 要闻汇总 | ~4条，与 yaowen 重叠 |
| 要闻列表 | `https://www.gov.cn/yaowen/liebiao/` | 最新政策/会议报道 | ~14条，主通道 |
| 政策文件库 | `https://www.gov.cn/zhengce/lists/` | 国发/国办发文件全文 | ~6条 |

## Playwright CDP 连接代码

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    # === 列表页抓取 ===
    page.goto("https://www.gov.cn/yaowen/liebiao/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    articles = page.eval_on_selector_all("a",
        "els => els.filter(e => e.href && e.href.includes('gov.cn/yaowen/liebiao/202') && e.innerText.trim().length > 5).slice(0,30).map(e => ({t: e.innerText.trim(), u: e.href}))")
    # 返回: [{"t": "标题", "u": "https://www.gov.cn/..."}, ...]

    # === 文章页抓取（要闻类） ===
    page.goto("https://www.gov.cn/yaowen/liebiao/202606/content_7071948.htm", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    text = page.inner_text("body")  # 全文文本

    # === 文章页抓取（政策文件类 zhengceku）===
    page.goto("https://www.gov.cn/zhengce/202606/content_7072002.htm", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    text = page.inner_text("body")  # h1/h2/.title 超时，用 body 代替

    # === 提取正文段落（过滤页脚干扰）===
    paras = page.eval_on_selector_all("p",
        "els => els.map(e=>e.innerText.trim()).filter(t=>t.length>30)")
    # 过滤 <30字符的导航/页脚文字

    browser.close()
```

## 内容 ID 规则

- URL格式：`https://www.gov.cn/yaowen/liebiao/YYYYMM/content_CONTENTID.htm`
- ID递增规律：`content_7071845` = 2026年6月11日发布，ID越高越新，同日多篇连续递增
- 验证 URL 正确性：访问后检查 `page.url`，若变成 `https://www.gov.cn/` 说明年月错误

## 选择器踩坑

| 页面类型 | 选择器 | 结果 |
|---------|--------|------|
| 要闻类（如 content_7071948） | `h1, h2, .title` | ✅ 正常 |
| 政策文件类 zhengceku（如 content_7072002） | `h1, h2, .title` | ❌ 超时30s |
| 政策文件类 zhengceku | `body.inner_text` | ✅ 正常（~5800字） |
| 正文段落（所有类型） | `p` + 长度过滤>30 | ✅ 去噪 |

## 去重检查

1. **通道间去重**：lianbo 和 yaowen/liebiao 有重叠，用 content_ID 唯一性过滤
2. **日内去重**：对比 `~/.hermes/political-reports/YYYY-MM-DD*` 下已有标题，相似度>70%跳过
3. **历史去重**：同 content_ID 只保留最新一次扫描

## 已知失败模式

- `urllib` 直读 gov.cn → SSL 错误，必须 Playwright CDP
- `browser_navigate` → 超时60s，必须 Playwright CDP
- 搜索参数 `?searchword=...` → 重定向到首页，搜索不可用
- 错误年月（如 `202506/content_7071845.htm`）→ 跳转到首页
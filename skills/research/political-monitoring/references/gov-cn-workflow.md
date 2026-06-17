# gov.cn 政治监测工作流

## 站点结构

| 通道 | URL | 可靠性 |
|------|-----|--------|
| 要闻列表 | `https://www.gov.cn/yaowen/liebiao/` | ✅ 稳定 |
| 政策文件库 | `https://www.gov.cn/zhengce/liebiao/` | ✅ 稳定 |
| 联播 | `https://www.gov.cn/lianbo/index.htm` | ⚠️ 超时60s，需Playwright CDP |
| 政策解读 | `https://www.gov.cn/zhengce/jiedu/` | ✅ 稳定 |

## 内容ID规则

gov.cn 文章页 URL：`https://www.gov.cn/yaowen/liebiao/YYYYMM/content_CONTENTID.htm`

**ID映射**（2026年6月实测）：
- `content_7071845` = 2026年6月11日（国常会要闻）
- `content_7071853` = 2026年6月12日
- `content_7071854` = 2026年6月12日
- `content_7071863` = 2026年6月12日
- `content_7071941` = 2026年6月13日
- `content_7071942` = 2026年6月13日
- `content_7071965` = 2026年6月13日
- `content_7071966` = 2026年6月13日
- `content_7071967` = 2026年6月12日
- `content_7071972` = 2026年6月12日
- `content_7071986` = 2026年6月12日
- `content_7071997` = 2026年6月13日
- `content_7072011` = 2026年6月13日
- `content_7072014` = 2026年6月13日
- `content_7072002` = 政策文件库（新能源重卡方案）

**规律**：ID越高越新，同日多篇连续递增。

**坑**：错误年月（如`202506`）访问会直接重定向到首页。

## Playwright CDP 提取模式

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    # 列表页
    page.goto("https://www.gov.cn/yaowen/liebiao/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    articles = page.eval_on_selector_all("a", "els => els.filter(e => e.href && e.href.includes('gov.cn/yaowen/liebiao')).slice(0,40).map(e => ({t:e.innerText.trim(),u:e.href}))")
    
    # 文章页（正文提取）
    page.goto("https://www.gov.cn/yaowen/liebiao/202606/content_7072011.htm", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    text = page.inner_text("body")  # 不超时
    
    browser.close()
```

## 选择器坑

| 页面类型 | 选择器 | 结果 |
|---------|--------|------|
| 要闻类 article页 | `h1, h2, .title` | ✅ 正常 |
| 政策文件类（zhengceku） | `h1, h2, .title` | ❌ 超时30s |
| 政策文件类（zhengceku） | `body.inner_text` | ✅ 正常（5804字） |

**政策文件类识别**：URL含 `/zhengce/zhengceku/` 或 `content_7072002` 等高ID政策文件。

## 关键词过滤

**立即推送（核心词）**：
- 政治局、常委、政治局会议
- 全国两会、政协、人大
- 中央经济工作会
- 国发、国办发、中发、中办发
- 国务院、常务会议
- 降准、降息、房地产（政策相关）
- 习近平（重要场合讲话）

**降权（P3/P4）**：
- 各部委（住建部/商务部/文旅部/工信部）
- 地方政府政策
- 一般会议/活动

## 新浪财经政经 API（备用）

`lid=2517` 全天候100%国际财经/市场新闻，**不可用于政治监测**。

仅作宏观市场情绪参考。
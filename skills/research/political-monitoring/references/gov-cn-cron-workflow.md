# gov.cn 政治监测 cron 工作流（2026-06 实测）

## Chrome 调试端口启动

```bash
google-chrome --remote-debugging-port=19825 --user-data-dir=/tmp/chrome-debug --no-sandbox --headless
```

**注意**：不要用 shell `&` 后台语法，会被 vet 拦截。用 `terminal(background=True)`。

## 三通道 URL

| 通道 | URL | 内容类型 |
|------|-----|---------|
| 要闻 | `https://www.gov.cn/yaowen/liebiao/` | 领导人活动、重要新闻 |
| 政策文件 | `https://www.gov.cn/zhengce/xgfc.htm` | 国发/国办发政策文件 |
| 联播 | `https://www.gov.cn/lianbo/index.htm` | 数据发布、联合公告 |

## Playwright CDP 连接模板

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://www.gov.cn/yaowen/liebiao/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # 提取文章链接（过滤含 content_ 的 gov.cn 链接）
    articles = page.eval_on_selector_all(
        "a",
        "els => els.filter(e => e.href && e.href.includes('gov.cn/yaowen/liebiao') && e.href.includes('content_')).slice(0,20).map(e => ({t:e.innerText.trim(),u:e.href}))"
    )

    # 获取文章正文（政策文件类用 body，要闻类用 h1, h2, .title）
    text = page.inner_text("body")  # 政策文件页 / zhengceku
    # text = page.inner_text("h1, h2, .title")  # 要闻页（部分超时）

    browser.close()
```

## 内容 ID 规则（2026-06 实测）

- `content_7071845` = 2026年6月11日发布，ID越高越新
- 同日多篇连续递增（如 7071845 → 7071846 → ...）
- URL 格式：`/YYYYMM/content_CONTENTID.htm`（如 `202606/content_7071845.htm`）
- **错误年月**（如 `202506`）访问会跳转到首页 → 访问后必须检查 `page.url`

## 已知踩坑（2026-06 实测）

### lianbo 直连超时
- `browser_navigate('https://www.gov.cn/lianbo/index.htm')` 超时60s
- **修复**：Playwright CDP connect_over_cDP，实测4秒响应

### article 页标题选择器超时
- 部分 zhengceku 政策文件页（如 `content_7072002.htm`）使用 `page.inner_text("h1, h2, .title")` 超时30s
- **修复**：对 zhengceku 政策页改用 `page.inner_text("body")` 一次性获取全页文本
  - 要闻类（content_7071948）→ `h1, h2, .title` ✅ 可用
  - 政策文件类（content_7072002）→ `body.inner_text` ✅ 正常（5804字）

### gov.cn 搜索重定向
- 搜索参数 `?searchword=...&channelid=...` 重定向到首页
- **正确方式**：直接访问 `/yaowen/liebiao/` 或 `/lianbo/` 列表页提取文章链接

### 新浪财经 RSS 不可用于政治监测
- lid=2517 返回内容全为美股/国际财经新闻，零条国内政策
- 仅作宏观市场情绪参考

## 推送格式模板

```
【P1 政策速报】[时间]
[文件/会议名称]
核心内容：[政策在说什么]
信号解读：[1-3句，说清楚对市场和普通人的影响]
来源：[官方来源链接]
━━━━━━━━━━━
```

## 去重检查

对比 `~/.hermes/political-reports/` 目录下今日已有推送：
- 标题相似度 >70% → 静默跳过
- 新内容 → 通过，写入输出文件

输出文件命名：`YYYY-MM-DD_HHMM_<级别>政策速报.md`
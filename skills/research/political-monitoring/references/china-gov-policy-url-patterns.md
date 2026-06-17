# 中国政府网站 gov.cn URL Patterns（2026-06 实测）

## 三通道内容结构

gov.cn 政策内容分为三个通道，URL格式不同：

### 1. 要闻通道（yaowen/liebiao）
- 列表页：`https://www.gov.cn/yaowen/liebiao/`
- 文章页：`https://www.gov.cn/yaowen/liebiao/YYYYMM/content_CONTENTID.htm`
- 示例：`202606/content_7071845.htm`（2026年6月11日发布）
- **Content ID 规律**：`_7071845` = 2026年6月11日，ID越高越新，同日多篇连续递增

### 2. 政策文件通道（zhengce）
- 列表页：`https://www.gov.cn/zhengce/index.htm`
- 文章页：`https://www.gov.cn/zhengce/content/YYYYMM/content_CONTENTID.htm`
- **国发/国办发文件用**：`/zhengce/content/` 前缀

### 3. 联播通道（lianbo）
- 列表页：`https://www.gov.cn/lianbo/index.htm`
- 文章页：`https://www.gov.cn/lianbo/YYYYMM/content_CONTENTID.htm`
- **数据/金融类内容**：人民币贷款、防汛应急响应等

## Content ID 去重法

```
content_7071845  →  2026年6月11日
content_7072011  →  2026年6月14日（今天）
ID每增加1 ≈ 发布时间增加数分钟到1小时
```

## URL 陷阱（踩坑记录）

1. **年月必须精确**：用错误的年月（如 `202506`）访问会直接跳转到首页
   - 验证方法：访问后检查 `page.url` 是否仍为目标URL，若变成 `https://www.gov.cn/` 说明URL错误

2. **gov.cn 搜索功能不可用**：`?searchword=...&channelid=...` 参数会重定向到首页
   - 正确方式：直接从列表页提取文章链接

3. **lianbo/index.htm 直连超时**：urllib 直连超时60s，**不可用**
   - 正确方式：Playwright CDP `connect_over_cdp("http://localhost:19825")`，实测4秒响应

4. **zhengceku 政策页标题选择器超时**：部分 `content_X.htm` 政策页用 `page.inner_text("h1, h2, .title")` 超时30s
   - 修复：对 zhengceku 政策页改用 `page.inner_text("body")` 一次性获取全页文本

## Playwright CDP 工作流（唯一可靠方式）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    page.goto("https://www.gov.cn/yaowen/liebiao/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    
    # 提取文章列表（过滤 gov.cn 站内链接）
    articles = page.eval_on_selector_all("a", 
        "els => els.filter(e => e.href && e.href.includes('gov.cn/yaowen/liebiao') && e.href.includes('202606')).slice(0,40).map(e => ({t:e.innerText.trim(),u:e.href}))")
    
    print(f"找到 {len(articles)} 条")
    for a in articles[:20]:
        print(f"  [{a['t'][:40]}] {a['u']}")
    
    browser.close()
```

## 正文提取选择器

| 页面类型 | 标题选择器 | 正文选择器 |
|---------|-----------|-----------|
| 要闻/联播页（yaowen/liebiao, lianbo） | `h1, h2, .title` ✅ | `p` 过滤30字符以上 ✅ |
| 政策文件页（zhengce/content_X.htm） | `body.inner_text` ✅（不能用h1选择器会超时） | `body` 一次性获取 |

## 已知踩坑（2026-06 实测）

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `lianbo/index.htm` urllib 超时60s | SSL兼容问题 | Playwright CDP 直连 |
| zhengceku 政策页标题超时30s | JS动态渲染 | `page.inner_text("body")` |
| URL 年月错误跳转首页 | gov.cn URL校验 | 访问后检查 `page.url` |
| gov.cn 搜索重定向 | 搜索功能不可用 | 从列表页提取链接 |
| 新华网 RSS 返回2022年旧数据 | RSS数据源损坏 | 改用 gov.cn 三通道 |
| `lid=2517` 全是财经/国际新闻 | 不是政治信息源 | 仅作市场情绪参考 |
# 中国政治监测 · 权威来源验证记录（2026-06）

## 已验证可用来源

### Gov.cn（中国政府网）— 首选
- **首页要闻**：`https://www.gov.cn/yaowen/liebiao/` — 领导人活动、会议报道
- **最新政策**：`https://www.gov.cn/zhengce/index.htm` — 国发/国办发文件列表
- **政务联播**：`https://www.gov.cn/lianbo/` — 各部委动态

**urllib 直读测试**：
- `/zhengce/index.htm` ✅ 无 SSL 错误，速度快（~12KB）
- `/lianbo/index.htm` ❌ 超时 60s，不可用
- 首页直接访问 ✅ 可用

### 新华社快讯
- 实时性高，重大事件首发
- 无 RSS，需 browser_navigate 或 Playwright

---

## 已验证不可用来源（2026-06 实测）

### 新华网政治 RSS
- **URL**：`https://www.xinhuanet.com/politics/news_politics.xml`
- **状态**：❌ 返回 300 条，全部是 2022 年旧数据，完全不可用
- **原因**：RSS 源多年未更新

### 新浪财经 lid=2517
- **URL**：`https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&k=&num=20&page=1`
- **状态**：❌ 返回内容100% 是美股/国际财经新闻（SpaceX IPO、欧洲央行加息等）
- **实测**：清晨/午后/晚间多时段 20/20 条均为国际财经，零条国内政策
- **适用场景**：仅作国际宏观市场情绪参考，**不可用于政治监测**

### 其他不可用 RSS
| 来源 | 失败原因 |
|------|---------|
| gov.cn RSS | 404 |
| people.com.cn RSS | 404 |
| cctv.com RSS | 404 |
| chinadaily.com.cn RSS | 404 |
| chinanews.com RSS | 404 |

---

## 搜索工具可用性

| 工具 | 状态 | 说明 |
|------|------|------|
| Google Search | ❌ 超时 | cron 环境不稳定 |
| Bing Search | ❌ 超时 | 同上 |
| bb-browser google/search | ❌失败 | 在无头环境返回 HTTP 400 |
| **Playwright CDP 直连** | ✅ 可用 | 连接已有 Chrome，推荐 |

---

## cron 环境工作流（2026-06-12 验证成功）

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.new_page()
    
    #通道1：gov.cn 首页要闻
    page.goto("https://www.gov.cn/yaowen/liebiao/", timeout=20000, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    items = page.eval_on_selector_all(
        'h4 a, li a',
        'els => els.filter(e => e.innerText.trim().length > 5).slice(0,30)'
        '.map(e => ({t: e.innerText.slice(0,80), u: e.href}))'
    )
    
    # 通道2：政策文件列表
    page.goto("https://www.gov.cn/zhengce/index.htm", timeout=20000, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    # ... 同上提取
    
    browser.close()
```

---

## 报告存档路径

**正确路径**：`~/.hermes/political-reports/`（每30分钟cron生成的文件在此）

注意：SKILL.md 正文中旧路径 `~/.hermes/army-workspace/political/` 已过时，以本文件为准。

---

## 推送目标

- 飞书群：`oc_c6883cd907e4d226736d87ce9c6c6d79`
- 格式：见 SKILL.md 正文 "推送格式" 章节
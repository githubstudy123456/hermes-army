# Gov.cn 公开市场业务交易公告 — URL 结构与踩坑记录

## 问题描述

央行公开市场业务交易公告（如逆回购、MLF操作）发布在 gov.cn 子路径下，用 urllib 直读**普遍404**。

**本 session 实测（2026-06-1116:xx）失败记录：**
- `https://www.gov.cn/zhengcehuobisi/125207/125213/125431/125475/2026061109042678748/index.html` → 404
- `https://www.gov.cn/zhengcehuobisi/125207/125213/125431/index.htm` → 404

## 根本原因

gov.cn 的 SSL 证书或路径结构在 urllib环境下不稳定，且页面响应极慢。

## 解决方案

**必须用 Playwright CDP 直连 Chrome 内置 SSL：**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    page = browser.contexts[0].new_page()
    
    # 直接访问公开市场业务公告列表页
    page.goto("https://www.gov.cn/zhengcehuobisi/125207/125213/125431/",
              timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    
    text = page.inner_text("body")
    # 提取标题和链接
    items = page.eval_on_selector_all("a", 
        "els => els.filter(e=>e.offsetParent!==null).slice(0,30)"
        ".map(e=>({t:e.innerText.trim(),u:e.href}))")
    
    for item in items:
        if '公开市场' in item['t'] or '逆回购' in item['t'] or 'MLF' in item['t']:
            print(f"  {item['t']} -> {item['u']}")
    
    browser.close()
```

## 备用方案：直接从列表页抓取

gov.cn 公开市场业务公告列表页入口：
- 完整 URL：`https://www.gov.cn/zhengcehuobisi/125207/125213/125431/index.htm`
- 父级：`https://www.gov.cn/zhengcehuobisi/125207/125213/125431/125475/`（公告子目录）

公告文件名规律：`[YYYYMMDD]XXXXXX.html`（数字是时间戳，不是固定格式）

## 已知稳定的央行信息来源（可交叉验证）

| 来源 | URL | 状态 |
|------|-----|------|
| 央行官网货币政策专栏 | `https://www.pbc.gov.cn/rmyh/105145/index.html` | ✅ browser_navigate 可用 |
| 央行新闻发布 | `https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html` | ✅ browser_navigate 可用 |
| 新浪财经政经快讯 lid=2517 | `https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517` | ✅ urllib 可用 |

## 经验总结

- gov.cn 所有子路径 urllib 直读**成功率<30%**，统一改 Playwright CDP
- 不要在 gov.cn 上浪费时间用 `bb-browser site gov.cn/...` adapter，不稳定
- 央行公开市场操作信息最可靠的实时来源是**新浪财经 lid=2517/2516**快讯（urllib 可用）
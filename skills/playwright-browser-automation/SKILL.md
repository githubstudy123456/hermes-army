---
name: playwright-browser-automation
description: 使用 Playwright 自动化浏览器操作 — 模拟真人访问网站、填表、登录、截图等。无头模式（headless=True）运行，需配合代理使用。
tags: [Browser, Automation, Playwright, Web Scraping, Login, Screenshot]
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Browser, Automation, Playwright, Headless]
    homepage: https://playwright.dev
prerequisites:
  commands: [python3]
  python_pkgs: [playwright]
  proxies:
    socks5: "socks5://127.0.0.1:10808"
    http: "http://127.0.0.1:10809"
---

# Playwright Browser Automation Skill

本服务器已安装 Playwright + Chromium，使用**无头模式**运行。代理已配置（V2Ray SOCKS5: 10808 / HTTP: 10809）。

## 环境

- Python: `/home/ubuntu/.hermes/hermes-agent/venv/bin/python3`（Python 3.11）
- Playwright 版本: 1.58.0
- Chromium: `~/.cache/ms-playwright/chromium-1208/`（另有 chromium-1217 备用）
- 代理: V2Ray (SOCKS5: 10808, HTTP: 10809)
- venv 里**没有 pip**，需要先 `ensurepip` 再装包

## 安装步骤（venv 初始化）

```bash
# 1. 激活 venv（必须用 python3.11，不能用系统 python）
/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -m ensurepip

# 2. 安装 playwright
/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -m pip install playwright

# 3. 安装浏览器（首次）
/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -m playwright install chromium

# 4. 验证
/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -c \
  "from playwright.sync_api import sync_playwright; \
   p = sync_playwright().start(); \
   c = p.chromium.launch(headless=True); \
   print('OK'); c.close(); p.stop()"
```

**坑：** 直接用 `pip install` 会装到系统 python3.10（playwright in `~/.local/lib/python3.10/site-packages/`），但 hermes-agent 用的是 venv 里的 python3.11，两个不互通。必须用 venv 里的 python3 -m pip。

## 代理配置

启动浏览器时通过 `--proxy-server` 参数指定：

```python
# SOCKS5 代理（推荐，支持更多协议）
"--proxy-server=socks5://127.0.0.1:10808"

# HTTP 代理
"--proxy-server=http://127.0.0.1:10809"
```

## 基础使用模板

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--proxy-server=socks5://127.0.0.1:10808",  # 代理
            "--disable-blink-features=AutomationControlled",  # 隐藏自动化特征
        ]
    )
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="zh-CN",
        timezone_id="Asia/Shanghai",
    )
    page = context.new_page()

    # 访问网址
    page.goto("https://example.com", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)  # 等待页面完全加载

    # 截图
    page.screenshot(path="/tmp/example.png", full_page=True)

    # 获取页面内容
    print(f"标题: {page.title()}")
    print(f"URL: {page.url}")

    # 提取数据（CSS 选择器）
    elements = page.query_selector_all("div.classname")
    for el in elements:
        print(el.inner_text())

    # 点击按钮
    page.click("button#submit")
    page.wait_for_timeout(2000)

    # 填写表单
    page.fill("input[name='email']", "user@example.com")
    page.fill("input[name='password']", "password123")
    page.click("button[type='submit']")

    # 等待导航完成
    page.wait_for_load_state("networkidle", timeout=15000)

    # 等待特定元素出现
    page.wait_for_selector("div.result", timeout=10000)

    browser.close()
```

## 模拟真人操作

```python
# 真人操作：先移动到元素上悬停，再点击
page.hover("a.nav-link")
page.wait_for_timeout(300)
page.click("a.nav-link")

# 滚动页面
page.evaluate("window.scrollBy(0, 500)")
page.wait_for_timeout(500)

# 键盘操作
page.keyboard.press("Enter")
page.keyboard.type("search query", delay=100)  # 每字符100ms，模拟打字

# 多步骤操作链
page.goto("https://example.com")
page.click("a.login-link")
page.wait_for_selector("input[name='username']")
page.fill("input[name='username']", "myuser")
page.fill("input[name='password']", "mypassword")
page.check("input[name='remember']")  # 勾选复选框
page.click("button[type='submit']")
page.wait_for_load_state("networkidle")
```

## 登录表单示例

```python
def login(page, url, username, password):
    page.goto(url, timeout=20000)
    page.wait_for_load_state("domcontentloaded")
    
    # 查找用户名输入框（多种可能的选择器）
    username_selectors = [
        "input[name='username']",
        "input[name='email']", 
        "input[type='text']",
        "input[id='username']",
        "#username",
    ]
    password_selectors = [
        "input[name='password']",
        "input[type='password']",
        "#password",
    ]
    
    for sel in username_selectors:
        if page.query_selector(sel):
            page.fill(sel, username)
            break
    
    for sel in password_selectors:
        if page.query_selector(sel):
            page.fill(sel, password)
            break
    
    # 查找提交按钮
    submit_selectors = [
        "button[type='submit']",
        "input[type='submit']",
        "button:has-text('登录')",
        "button:has-text('Login')",
        "button:has-text('Sign in')",
    ]
    for sel in submit_selectors:
        if page.query_selector(sel):
            page.click(sel)
            break
    
    page.wait_for_timeout(3000)
    return page.url  # 返回登录后 URL
```

## 提取页面数据

```python
# 提取多个元素文本
titles = page.eval_on_selector_all("h3.article-title", 
    "elements => elements.map(e => e.innerText)")

# 提取链接和标题
data = page.evaluate("""
    Array.from(document.querySelectorAll('a.item')).map(a => ({
        text: a.innerText.trim(),
        href: a.href
    }))
""")

# 提取表格数据
rows = page.query_selector_all("table.data-table tr")
for row in rows:
    cells = row.query_selector_all("td")
    print([c.inner_text() for c in cells])
```

## 等待策略

| 方法 | 用途 |
|------|------|
| `page.wait_for_timeout(ms)` | 固定等待 |
| `page.wait_for_load_state('networkidle')` | 网络空闲 |
| `page.wait_for_selector('css')` | 元素出现 |
| `page.wait_for_function('() => condition')` | JS 条件满足 |
| `page.wait_for_url('**/dashboard**')` | URL 匹配 |

## 反检测

```python
args = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-blink-features=AutomationControlled",  # 隐藏 webdriver 特征
    "--disable-dev-shm-usage",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-popup-blocking",
    "--window-size=1280,800",
    "--proxy-server=socks5://127.0.0.1:10808",
]
```

## 无限滚动页面抓取（Infinite Scroll / 懒加载）

许多网站（电商、优惠聚合、社交媒体）使用无限滚动加载内容，初始 HTML 里没有数据，必须模拟滚动才能触发加载。

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    # 滚动触发懒加载（通常需要滚动3-6次）
    for _ in range(4):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(1500)  # 等待新内容加载
    page.wait_for_timeout(3000)  # 额外等待确保所有 AJAX 完成

    body_text = page.inner_text("body")
    browser.close()
```

**关键点**：
- 用 `wait_until="domcontentloaded"` 而非 `"networkidle"`，因为无限滚动页面永远不等所有请求完成
- 每次滚动后等 `1500ms`，让新内容有充足时间渲染
- 额外等 `3000ms` 确保所有懒加载图片/脚本执行完毕

## 从渲染页面提取结构化数据（文本配对法）

当页面是动态渲染、无法直接用正则匹配 HTML 时，用 `inner_text()` 获取纯文本，再用**相邻行配对**提取结构化数据。

```python
import re

def extract_deals_from_text(body_text: str) -> list[dict]:
    """
    从页面纯文本中提取"商品名 + 价格"配对
    适用于：优惠精选、商品列表、排行榜等页面
    """
    lines = body_text.split("\n")
    deals = []
    for i, line in enumerate(lines):
        line = line.strip()
        # 找价格行
        if re.search(r"\d+\.\d+元", line) and i > 0:
            prev = lines[i - 1].strip()
            # 上一行是非价格的商品名称
            if (
                prev
                and not re.search(r"^\d+\.?\d*元", prev)  # 不是纯数字价格行
                and len(prev) > 3
                and len(prev) < 80  # 商品名长度合理
            ):
                deals.append({"name": prev, "price": line})
    # 去重（滚动可能加载重复内容）
    seen = set()
    unique = []
    for d in deals:
        if d["name"] not in seen:
            seen.add(d["name"])
            unique.append(d)
    return unique
```

**适用场景**：
- ✅ 什么值得买（smzdm.com）好价排行榜
- ✅ 京东/淘宝搜索结果页
- ✅ 小红书/微博内容列表
- ✅ 新闻聚合网站
- ❌ 不适合：表格型数据（用 CSS 选择器更稳）

## JS 反爬绕过实战（smzdm.com 案例）

smzdm.com 有 JS 验证码和 UA 检测，requests/curl 全部返回验证码页面。Playwright 可以执行 JS 绕过：

```python
# smzdm 好价排行榜 URL
url = "https://www.smzdm.com/fanli/haojia/0/3/"  # tab: 0/3=食品家居, 0/4=日百母婴, 0/5=白菜

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-setuid-sandbox"]
    )
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    # 滚动触发无限滚动加载
    for _ in range(4):
        page.evaluate("window.scrollBy(0, 600)")
        page.wait_for_timeout(1500)
    page.wait_for_timeout(3000)

    # 提取数据
    deals = extract_deals_from_text(page.inner_text("body"))
    browser.close()
```

**注意**：smzdm 页面初始只加载约20条，滚动后总共约50-70条。如需更多数据（如100+条），增加滚动次数或访问多个 tab。

## 已验证可访问的网站（2026-04-24）

| 站点 | 状态 |
|------|------|
| YouTube | ✅ |
| Twitter/X | ✅ |
| Google | ✅ |
| 什么值得买（smzdm.com） | ✅ 需 Playwright + 滚动 |
| 京东/淘宝 | ✅ 需 Playwright |

截图路径：`/tmp/站点名.png`（文件名中的 `/` 替换为 `_`）

## 注意事项

1. **无头模式**：`headless=True` 不会弹出窗口，适合服务器环境
2. **超时**：网络慢时调大 `timeout` 参数（默认 30s）
3. **页面加载策略**：`wait_until="domcontentloaded"` 比 `"load"` 更快
4. **关闭浏览器**：务必在 `finally` 或 `with` 块中调用 `browser.close()`
5. **代理**：访问被墙网站（Google、YouTube、Twitter）必须加代理参数
6. **X Server**：如需有头模式（`headless=False`），需要 xvfb 或真实 X Server

## 验证安装

```bash
/home/ubuntu/.hermes/hermes-agent/venv/bin/python3 -c \
  "from playwright.sync_api import sync_playwright; \
   p = sync_playwright().start(); \
   c = p.chromium.launch(headless=True); \
   print('Playwright OK'); \
   c.close(); p.stop()"
```

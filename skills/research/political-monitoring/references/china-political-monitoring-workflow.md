# 政治监测 · 实战笔记
> 2026-06-15 实测积累。来源可用性、坑位、脚本片段。

---

## 信息源实测状态（2026-06）

| 来源 | 地址/接口 | 实测结果 | 备注 |
|------|-----------|----------|------|
| gov.cn 要闻列表 | `https://www.gov.cn/yaowen/liebiao/` | ✅ 15条可用 | Playwright CDP 直连，~4s |
| gov.cn 联播页 | `https://www.gov.cn/lianbo/index.htm` | ❌ urllib超时60s | **必须用 Playwright CDP**（connect_over_cdp，实测4s） |
| gov.cn 搜索 | `?searchword=...&channelid=...` | ❌ 重定向到首页 | **直接访问列表页** |
| gov.cn 政策文件页 | `content_*.htm` (zhengceku) | ⚠️ 标题选择器超时 | 用 `body.inner_text`，不用 `h1, h2, .title` |
| 新华网时政RSS | `http://www.xinhuanet.com/politics/news_politics.xml` | ❌ 返回2022年旧数据 | **不可用**，勿依赖 |
| 新浪财经政经API lid=2517 | `feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517` | ✅ 可用但内容偏国际 | 实测凌晨03:34全为美股/俄乌新闻，**非国内政策监测优选** |
| 新浪财经 lid=2516 | 同上，lid=2516 | ✅ 头条新闻可用 | |
| 36kr RSS | `https://36kr.com/feed` | ✅ 稳定，科技商业 | 非官方政策来源 |

---

## Chrome + Playwright CDP 启动与连接

```python
# 启动（后台，terminal background=true）
google-chrome --remote-debugging-port=19825 \
  --user-data-dir=/tmp/chrome-debug --no-sandbox --headless

# 等待端口就绪
import time; time.sleep(3)

# 连接已有Chrome（复用登录态）
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    # 使用 page 对象
    browser.close()
```

---

## gov.cn 文章内容提取流程

### 步骤1：列表页 → 获取文章URL列表

```python
articles = page.eval_on_selector_all("a", 
    "els => els.filter(e => e.href && e.href.includes('gov.cn/yaowen/liebiao') "
    "&& e.innerText.trim().length > 10).slice(0,30)"
    ".map(e => ({t:e.innerText.trim(),u:e.href}))")
```

### 步骤2：文章页 → 判断类型后提取

**要闻类**（一般content页，`h1, h2, .title` 可用）：
```python
title = page.inner_text("h1, h2, .title")
```

**政策文件类**（zhengceku，content_*.htm，`h1, h2, .title` 超时30s）：
```python
text = page.inner_text("body")
lines = [l.strip() for l in text.split('\n') if l.strip()]
title = lines[13]  # 标题一般在第13行
# 正文段落（30字符以上）
paras = [l for l in lines if 40 < len(l) < 300]
```

### 步骤3：正文段落过滤（gov.cn页脚噪声）

gov.cn 每页大量重复的页脚导航文字（"国务院办公厅主办"等），**只用30字符以上段落过滤**，无法靠关键词排除。

---

## 新浪财经 API · 编码陷阱

```python
import urllib.request, re, ssl
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&num=20&page=1'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://finance.sina.com.cn'
})
with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
    content = r.read().decode('gbk', errors='ignore')  # ← gbk 不是 utf-8
    d = eval(content.replace('false', 'False').replace('true', 'True').replace('null', 'None'))
    items = d.get('result', {}).get('data', [])
```

**注意**：`ctime` 是 Unix 时间戳（秒），需 `datetime.fromtimestamp()` 转换。

---

## 今日已推送检查

```python
import glob, os

reports_dir = "/home/ubuntu/.hermes/political-reports"
today_files = glob.glob(os.path.join(reports_dir, "2026-06-15*"))
# 或动态日期：
today_files = glob.glob(os.path.join(reports_dir, f"{datetime.now().strftime('%Y-%m-%d')}*"))
```

路径：`/home/ubuntu/.hermes/political-reports/`（不是 `/root/`）

---

## Bing 中文搜索（替代 Google）

```python
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

query = urllib.parse.quote("site:xinhuanet.com 政治局会议")
url = f"https://www.bing.com/search?q={query}&setlang=zh-CN&count=10"

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
    content = r.read().decode('utf-8', errors='ignore')

items = re.findall(r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h2>', content, re.DOTALL)
for href, title_raw in items:
    title = re.sub(r'<[^>]+>', '', title_raw).strip()
    if any(k in title for k in ['百度', '百科', '词典', '翻译', 'Merriam', 'Cambridge']):
        continue  # 过滤百科/词典结果
```

Bing 搜索结果含大量百度百科/词典，需过滤。

---

## gov.cn 三通道内容ID规则

- 内容ID示例：`_7071845` = 2026年6月11日发布
- ID越高越新，同日多篇连续递增
- 三通道：`/yaowen/liebiao/`（要闻）、`/lianbo/`（联播）、`/zhengce/`（政策）

---

## 新浪财经政经新闻局限（2026-06实测）

实测凌晨03:34-03:50时段，lid=2517返回5条新闻全为：
- 美伊谈判/美俄乌/美联储/瑞士公投

**结论**：lid=2517 全天候100%美股/国际财经新闻，零条国内政策，**完全不可用于政治监测**，仅作国际宏观市场情绪参考。

---

## 政治监测cron · 标准化扫描流程

每30分钟执行：

```python
# 1. 三路gov.cn列表页（Playwright CDP）
#   /yaowen/liebiao/ → 最多15条
#   /lianbo/index.htm → 通常5条
#   附：sina lid=2517（已知不可用于政治，仅作宏观补充）

# 2. 今日已推送检查
#   glob(/home/ubuntu/.hermes/political-reports/2026-06-15*)

# 3. 5关过滤
#   [1] 来源：gov.cn/新华社/人民网/央视/人民日报 → 通过
#   [2] 多源：≥2独立官方源确认 → 通过；单源→存疑
#   [3] 关键词：政治局/国常会/中发/国发/降准降息 → P1立即推送
#   [4] 评级：P0/P1→立即 P2→摘要 P3→简报 P4→次日日报
#   [5] 去重：标题相似度>70%跳过

# 4. 通过5关 → 格式化推送至飞书群
# 5. 保存报告到 /home/ubuntu/.hermes/political-reports/
```
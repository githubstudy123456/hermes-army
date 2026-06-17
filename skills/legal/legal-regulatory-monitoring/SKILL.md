---
name: legal-regulatory-monitoring
description: 法律法规动态追踪工作台 — 国务院/全国人大行政法规、央行/证监会/银保监会/网信办监管政策、最高法/最高检司法解释、行业合规更新。定期推送飞书群，支持重大合规风险即时预警。
triggers:
  - "法规追踪"
  - "法律法规动态"
  - "监管政策追踪"
  - "合规监测"
  - "legal regulatory monitoring"
  - "regulatory tracking"
  - "法规追踪周报"
---

# Legal & Regulatory Monitoring 工作台

追踪与中国企业业务相关的最新法律法规动态，识别合规风险并给出可执行建议。

## 追踪范围

1. 国务院/全国人大新颁布的行政法规、法律
2. 央行/证监会/银保监会/网信办重要监管政策
3. 最高法/最高检重要司法解释
4. 与主人业务相关的行业规定更新

## 信息源优先级（已验证可用）

| 来源 | 网址 | 可靠性 | 特点 |
|------|------|--------|------|
| gov.cn 要闻 | https://www.gov.cn/yaowen/liebiao/ | ✅ 极高 | 国务院政策首发 |
| gov.cn 政策文件 | https://www.gov.cn/zhengce/liebiao/ | ✅ 极高 | 行政法规全文 |
| gov.cn 联播 | https://www.gov.cn/lianbo/index.htm | ✅ 极高 | 重要政策集合 |
| 网信办 CAC | https://www.cac.gov.cn/ | ✅ 极高 | 网络安全/数据/AI监管 |
| 新浪财经政经 API | `feed.mix.sina.com.cn/api/roll/get?lid=2517` | ✅ 高 | 实时政经新闻 |
| 证监会 | https://www.csrc.gov.cn/ | ⚠️ 旧内容 | 需单独访问 |
| 最高法 | https://www.court.gov.cn/ | ⚠️ 常404 | 备用来源 |

## 执行步骤

### 步骤1：采集 gov.cn 三通道

使用 Playwright CDP 直连（不能用 urllib，gov.cn 的 SSL 在服务器环境下不稳定）：

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    # 国务院要闻
    page.goto("https://www.gov.cn/yaowen/liebiao/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    yaowen = page.eval_on_selector_all("a", "els => els.filter(e => e.href && e.href.includes('gov.cn/yaowen') && e.innerText.trim().length > 10).slice(0,30).map(e => ({t: e.innerText.trim(), u: e.href}))")
    
    # 政策文件
    page.goto("https://www.gov.cn/zhengce/liebiao/", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    zhengce = page.eval_on_selector_all("a", "els => els.filter(e => e.href && e.href.includes('gov.cn/zhengce') && e.innerText.trim().length > 10).slice(0,20).map(e => ({t: e.innerText.trim(), u: e.href}))")
    
    # 联播
    page.goto("https://www.gov.cn/lianbo/index.htm", timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    lianbo = page.eval_on_selector_all("a", "els => els.filter(e => e.href && e.href.includes('gov.cn/') && e.innerText.trim().length > 10).slice(0,20).map(e => ({t: e.innerText.trim(), u: e.href}))")
    
    browser.close()
```

### 步骤2：关键词过滤

对采集的标题进行业务相关过滤：

```python
keywords = ['人工智能', '数字经济', '数据', '网络安全', '算法', '生成式', '平台经济', 
            '金融科技', '监管', '证监会', '央行', '银保监', '网信', '合规', '证券', 
            '保险', '银行', '投资', '私募', '基金管理', '个人信息', '数据安全']

relevant = []
for a in all_articles:
    t = a['t']
    for kw in keywords:
        if kw in t:
            relevant.append(a)
            break
```

### 步骤3：深度读取重点文件

对匹配的重要政策文件，读取正文判断实质内容：

```python
page.goto(url, timeout=20000, wait_until="domcontentloaded")
page.wait_for_timeout(3000)
text = page.inner_text("body")
# gov.cn article页用 page.inner_text("body") 一次性获取全页，避免选择器超时
```

### 步骤4：生成简报

按以下格式输出：

```
【法规追踪】[日期]

一、本期新规速览
   [列出2-3条重要新规，每条包含：法规名称、发布时间、核心要点]

二、新规影响分析
   [针对2条重点法规，说明：]
   - 对现有业务的影响
   - 需要调整的内容
   - 合规建议

三、法务部建议
   [可执行的具体行动建议]

四、参考来源
   [来源链接]
```

## 已知踩坑（gov.cn 系列）

**gov.cn 搜索参数完全失效（2026-06 实测）：**
- `?searchword=...&channelid=...` 重定向到首页，搜索功能不可用
- **正确方式**：直接访问 `/yaowen/liebiao/` 或 `/zhengce/liebiao/` 列表页，从页面提取文章链接

**gov.cn lianbo/ 直连超时（2026-06-14 更新）：**
- `browser_navigate('https://www.gov.cn/lianbo/index.htm')` 在 cron 环境超时60s
- **正确方式**：Playwright CDP 连接已有 Chrome（connect_over_cdp），实测4秒响应

**gov.cn article页标题/正文选择器：**
- 要闻类（content_7071948）→ `h1, h2, .title` ✅ 可用
- 政策文件类/zhengceku（content_7072002）→ `h1, h2, .title` 超时30s
- **改用** `page.inner_text("body")` 一次性获取全页文本，实测正常（5804字）

**gov.cn 正文去噪：**
- `page.inner_text("body")` 含大量页脚导航文字（"国务院办公厅主办"等）
- "国务院"作为关键词在每页都会命中，无法用于实质性内容判断
- **正确方式**：先定位标题位置（一般在第13-20行），再从标题行往下取实质性段落做关键词匹配

**gov.cn 三通道内容 ID 规则：**
- `_7071845` = 2026年6月11日发布，ID越高越新，同日多篇连续递增
- 内容ID从 `/yaowen/liebiao/202606/` 和 `/lianbo/202606/` URL中提取

## 不可用信源（2026-06 实测）

- **银保监会 cbirc.gov.cn**：DNS `ERR_NAME_NOT_RESOLVED`，域名可能已变更或弃用
- **央行 pbc.gov.cn**：部分子页面返回404，需尝试首页导航
- **最高法 court.gov.cn**：常返回"页面不存在"，备用来源
- **gov.cn 搜索**：搜索参数重定向到首页，完全不可用

## 存档路径

报告存档至：`~/.hermes/army-workspace/legal/regulatory-updates/regulatory-update-YYYYMMDD.txt`

## 触发条件

- 每周一、周四 09:00 执行（定时 cron）
- 仅报告与主人业务相关的法规更新
- 重大合规风险立即推送（不受时间限制）

## 参考资料

- `references/china-gov-policy-url-patterns.md` — gov.cn URL结构与content ID去重法
- `references/china-political-monitoring-workflow.md` — 政治监测实战笔记（含gov.cn文章提取）
- `references/china-gov-rss-sources.md` — 中国政府网站RSS源验证
- `references/regulatory-monitoring-session-20260615.md` — 本次实战采集记录，含已验证信源清单和重要政策文件摘要
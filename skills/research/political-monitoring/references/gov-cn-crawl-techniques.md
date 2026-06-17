# gov.cn 网页爬取技术笔记（2026-06 实测）

## 已知问题

### 1. gov.cn/lianbo 直连超时
**问题**：`browser_navigate('https://www.gov.cn/lianbo/index.htm')` 超时60s。
**绕过**：不访问 lianbo/index.htm，用 **yaowen index** 代替。

### 2. gov.cn 文章子页面内容为空
**问题**：访问 `https://www.gov.cn/yaowen/2026-06/11/content_7070899.htm` 等子页面时，`page.inner_text("body")` 返回的是网站导航内容（顶部菜单、页脚），**不是文章正文**。
**原因**：页面是 JavaScript 渲染的 SPA，内容在动态加载的容器中，Playwright CDP 默认等待无法拿到正文。
**绕过方案**：
- 方案A（推荐）：从 **yaowen index** 页面直接抓取文章摘要文本（yaowen index 页面本身渲染完整文章列表）
- 方案B：用 `page.eval_on_selector_all()` 过滤含 `article`、`content` 等 className/id 的元素
- 方案C：绕过 gov.cn，直接访问原始来源（新华社/人民日报），但 gov.cn 页面有"来源"标注，可信度更高

### 3. SSL 错误（urllib 方案）
**问题**：Python urllib 直读 gov.cn 系列报 `ssl.SSLError`。
**绕过**：用 Playwright CDP 连接 Chrome，Chrome 内置 SSL 不依赖系统证书。

---

## gov.cn 各频道 URL Pattern

```
要闻（yaowen）： https://www.gov.cn/yaowen/index.htm
政务联播（lianbo）：https://www.gov.cn/lianbo/index.htm  （⚠️ 直连超时，用 yaowen 代替）
政策文件库： https://www.gov.cn/zhengce/xxgk/zzqx/
政策文件子页：    https://www.gov.cn/zhengce/content/202606/content_*.htm
                  https://www.gov.cn/zhengce/zhengceku/202606/content_*.htm
要闻子页：        https://www.gov.cn/yaowen/2026-06/11/content_*.htm
                  https://www.gov.cn/yaowen/liebiao/202606/content_*.htm
```

**content ID 规律**：
- yaowen 子页：`content_7071845.htm`（6位数字）
- zhengce 政策文件：`content_7071451.htm`（6位数字，年月可能在路径中如 `202606/`）
- lianbo 子页：`content_7071853.htm`

---

## 内容抓取推荐工作流

### 每日晨读（推荐顺序）

1. **yaowen index** → 获取最新要闻列表（含全文摘要）
   ```
   page.goto("https://www.gov.cn/yaowen/index.htm", timeout=30000)
   items = page.eval_on_selector_all("a[href*='gov.cn/yaowen']", filter+map)
   ```
   yaowen index 页面本身渲染完整文章内容（不是摘要），可直接获取全文。

2. **lianbo index** → 政务联播，含多部委动态
   ```
   page.goto("https://www.gov.cn/lianbo/index.htm")  # ⚠️ 超时则跳过，用 yaowen 代替
   ```

3. **zhengce index** → 政策文件库
   ```
   page.goto("https://www.gov.cn/zhengce/xxgk/zzqx/")
   ```

### 提取文章链接（不重复）
```python
items = page.eval_on_selector_all("a", '''els => els.filter(e => {
    const t = e.innerText.trim();
    return t.length > 10 && t.length < 150 && e.href.includes('gov.cn/yaowen');
}).slice(0,50).map(e => ({t: e.innerText.trim(), u: e.href}))''')
```

### 从 yaowen index 获取文章正文（当前最可靠方法）
```python
# yaowen index 页面本身包含完整文章内容（不是列表页）
# 直接读取 page.inner_text("body") 会包含大量导航内容
# 正确方式：用 eval_on_selector_all 提取 article 级元素
content = page.eval_on_selector_all("*", '''els => els.filter(e => {
    const cls = e.className || '';
    return cls.includes('article') || cls.includes('content') || cls.includes('txt');
}).map(e => e.innerText.trim()).filter(t => t.length > 200).slice(0,3)''')
```

---

## 来源标注格式（gov.cn 页面）

gov.cn 文章页面顶部有标准来源标注：
```
2026-06-11 17:52 来源： 新华社
2026-06-11 08:18 来源： 人民日报
```

**格式**：`YYYY-MM-DD HH:MM 来源： {媒体名}` — 可直接用正则提取，用于 Step 1 来源验证。

---

## 关键阈值

- gov.cn/lianbo navigate 超时：**60s**（直接放弃）
- gov.cn/yaowen navigate响应：正常
- gov.cn/zhengce navigate 响应：正常
- Playwright CDP 等待 `domcontentloaded` + `wait_for_timeout(2000)`：对 gov.cn 足够

---

## 新华社 RSS（已失效，2026-06 实测）

```
http://www.xinhuanet.com/politics/news_politics.xml → Empty page（2022年旧数据）
```

**替代**：sina财经政经新闻 `lid=2517`（全是美股/国际财经，非国内政策，不可用于政治监测）。
**结论**：gov.cn yaowen 是政治监测唯一可靠来源，没有有效 RSS替代。

---

## 本次采集结果摘要（2026-06-12 04:45）

- yaowen index 最新内容：**2026-06-11**（当天无新条目）
- lianbo index：同 yaowen 最新日期
- zhengce index：同 yaowen 最新日期
- 新华社 RSS：失效
- 新浪财经 lid=2517：全是美股/国际新闻，非政策

**结论**：政治监测 cron 在 05:00 前无新内容时直接输出 `[SILENT]`。
# 2026-06-15 三通道并行扫描实证

## 执行时间
2026-06-15 10:51（早盘时段）

## 核心发现

### gov.cn 三大频道全部正常（颠覆旧假设）

| 频道 | URL | 加载耗时 | 文章数 |
|------|-----|---------|--------|
| 要闻 | `https://www.gov.cn/yaowen/liebiao/` | ~4s | 15条 |
| 政策 | `https://www.gov.cn/zhengce/liebiao/` | ~4s | 20条 |
| 联播 | `https://www.gov.cn/lianbo/index.htm` | ~4s | 20条 |

**关键修正**：
- 之前 lianbo 超时60s 的记录来自独立 launch 或 browser_navigate，CDP 直连（复用已有Chrome）完全正常
- yaowen/liebiao 列表页**正常可用**，每轮直接用 `eval_on_selector_all` 提取 article 链接
- zhengce/liebiao 每轮同步扫描，扩大政策覆盖面

### 三通道并行扫描代码（实测通过）

```python
from playwright.sync_api import sync_playwright

channels = [
    ("https://www.gov.cn/yaowen/liebiao/", "yaowen"),
    ("https://www.gov.cn/zhengce/liebiao/", "zhengce"),
    ("https://www.gov.cn/lianbo/index.htm", "lianbo"),
]

all_articles = []
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    for url, label in channels:
        page.goto(url, timeout=30000, wait_until="domcontentloaded")
        page.wait_for_timeout(3000)
        
        # yaowen/zhengce: 路径含 yaowen/liebiao + content_ ID
        # lianbo: 路径含 gov.cn/lianbo
        if label in ('yaowen', 'zhengce'):
            articles = page.eval_on_selector_all("a", """els => els.filter(e => 
                e.href && e.href.includes('yaowen/liebiao') && e.href.includes('content_')
            ).slice(0,20).map(e => ({t:e.innerText.trim(),u:e.href}))""")
        else:
            articles = page.eval_on_selector_all("a", """els => els.filter(e => 
                e.href && e.href.includes('gov.cn/lianbo') && e.href.includes('content_')
            ).slice(0,20).map(e => ({t:e.innerText.trim(),u:e.href}))""")
        
        for a in articles:
            all_articles.append({**a, "channel": label})
    
    browser.close()

print(f"Total: {len(all_articles)} articles across 3 channels")
```

## 本次推送内容

### P2 社融数据（17.48万亿前5月）
- **来源**：gov.cn lianbo（人民日报转载，content_7072054）
- **数据**：前5月社融增量17.48万亿元；存量458.81万亿，同比+7.7%；人民币贷款增9.11万亿
- **评级**：P2（货币宽松政策效果持续显现）

### P2 新能源重卡方案（11部门联合）
- **来源**：gov.cn zhengce（交通运输部等11部门，交规划发〔2026〕52号）
- **目标**：2030年渗透率40%，保有量160万辆，充换电站3000个，零碳公路3万公里
- **评级**：P2（政策力度大，覆盖交通/能源/基建多产业链）

### P3 公积金政策多城调整
- **来源**：gov.cn yaowen（央视网转载，content_7072046）
- **内容**：超60城市调整公积金；沈阳7项举措；长三角一体化；灵活就业人员放开缴存
- **评级**：P3（边际改善房地产需求，区域协同效应）

## 关键词过滤结果

gov.cn 文章得分（仅显示 score>0）：

| 频道 | 标题 | 得分 | 命中词 |
|------|------|------|--------|
| yaowen | 国务院任命澳门特别行政区政府经济财政司司长 | 10 | 国务院 |
| yaowen | 李强主持召开国务院常务会议... | 10 | 国务院 |
| zhengce | 国常会解读 \| 教育发展十五五规划 | 10 | 国务院 |
| zhengce | 国常会解读 \| 美丽中国建设工作 | 10 | 国务院 |

**注意**：纯"国务院"泛化词命中但无经济特异性词，不推送，归周报

Sina 财经得分（仅显示 score>0）：

| 标题 | 得分 | 命中词 |
|------|------|--------|
| A股盈利结构向AI硬链集中 | 1 | A股 |
| A股迎三重利好因素 | 1 | A股 |
| 美伊达成和平协议油价大跌压制加息预期 | 10 | 加息 |
| *ST广糖遭证监会立案 | 10 | 证监会 |

## 去重检查

今日报告：`~/.hermes/economic-reports/20260615_economic_daily.txt`（新建，无重复）

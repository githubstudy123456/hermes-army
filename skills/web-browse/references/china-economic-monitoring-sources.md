# 中国经济/金融市场监测来源速查

## 可靠来源（2026-06 实测）

### gov.cn 三通道 — 唯一可靠的官方政策来源

| 通道 | URL | 内容类型 |
|------|-----|---------|
| 联播 | `https://www.gov.cn/lianbo/index.htm` | 政策联播/综合要闻 |
| 要闻 | `https://www.gov.cn/yaowen/liebiao/` | 每日要闻（当日更新） |
| 政策 | `https://www.gov.cn/zhengce/liebiao.htm` | 政策文件库 |

**工作流**：三通道并行提取文章列表 → 过滤含核心关键词的条目 → 访问文章页取正文 → 关键词命中判断。

**文章链接提取**（Playwright CDP）：
```python
articles = page.eval_on_selector_all("a",
    "els => els.filter(e => e.href && e.href.includes('gov.cn/yaowen/liebiao')).slice(0,40).map(e => ({t:e.innerText.trim(),u:e.href}))")
```

### 新浪财经政经流 API（实测可用）

`https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&num=20&page=1`

- **lid=2517** → 国内财经政经（本次 07:20 实测 20/20 条均为政经/美股，零条国内政策）
- **lid=2516** → 头条新闻（也可用）
- 返回字段：`ctime`(Unix时间戳), `title`, `url`, `intro`
- **编码**：`content.decode('gbk', errors='ignore')` + `eval()` 转 Python 对象
- 过滤最近5小时：`ts_now - int(item['ctime']) < 5 * 3600`

**注意**：该源以美股/国际财经为主，国内政策信息需靠 gov.cn 三通道。

### 新华网 RSS（部分可用）

- `http://www.xinhuanet.com/politics/news_politics.xml` — 仅此 RSS 可用
- ⚠️ 实测返回2022年旧数据，政治监测**不可用**，仅作宏观市场情绪参考

## 来源可靠性分级

### 第1梯队（官方权威，直接使用）
- gov.cn 三通道（lianbo/yaowen/zhengce）
- 新华网快讯（新华社电）
- 央行官网 / 国家统计局官网 / 证监会官网

### 第2梯队（已验证可用，降权使用）
- 新浪财经 lid=2517（美股/国际财经为主）
- 36kr RSS（科技商业，非政策）
- 中国证券报（授权转载官方稿）

### 第3梯队（已验证失效，勿用）
- 新华网政治RSS → 返回2022年旧数据
- gov.cn 搜索 → 重定向到首页
- 百度搜索 → 滑块验证不可用

## 核心关键词（经济监测场景）

### P0 级（立即推送）
降准、降息、LPR、麻辣粉(MLF)、政治局(经济)、国务院(经济)、CPI、PPI、GDP、统计局、房地产(中央)、恒大、碧桂园、美联储、加息、缩表、人民币、汇率、USD/CNY、证监会、IPO、注册制

### P1-P3 级（降权推送）
头部房企政策、人民币大幅波动、重要经济数据超预期、一般行业政策

## 新浪财经文章URL规律

新浪财经转载新华社等原始稿件时，URL中的路径含原始发布时间路径：
`https://finance.sina.com.cn/jjxw/2026-06-15/doc-inicmsvc8395802.shtml`

直接用新浪URL抓正文，**不要**尝试访问原始来源站（Xinhua首页会因文章不存在而重定向到无关南博页面）。

## 去重检查

对比 `~/.hermes/economic-reports/` 目录下今日已有推送：
- 标题相似度 >70% → 跳过
- 同一事件 ≥2个独立官方源 → 通过
- 仅1个源但重大市场异动（A 股单日跌>3%、USD/CNY突破7.3）→ 单源也放行

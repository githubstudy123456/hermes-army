---
name: economic-monitor
description: A股大盘、人民币汇率、央行政策、美联储动态监控。触发阈值立即推送飞书群。每30分钟轮询。
triggers:
  - "经济监控"
  - "市场监控"
  - "A股监控"
  - "宏观监测"
  - "economic monitor"
  - "market monitor"
---

# Economic Monitor Skill

宏观经济与金融市场事件主动监测机器人。满足触发条件立即推送飞书群。

## 监控指标与阈值

| 指标 | 触发条件 | 数据源 |
|------|---------|--------|
| A股大盘（上证/沪深300/深证/创业板） | 单日涨跌超2% | 新浪财经hq.sinajs.cn |
| **港股大盘（恒生指数/恒生科技指数）** | 恒生科技单日涨跌超2% | 新浪财经 lid=2516 头条快讯（实时含港股） |
| 人民币汇率 | USD/CNY突破7.3/7.2/7.0阈值 | hq.sinajs.cn `fx_susdcny` |
| 央行政策 | 降准/降息/LPR调整/逆回购 | 央行官网（pbc.gov.cn/goutongjiaoliu） |
| **央行国际合作/双边金融合作** | 签署MOU/人民币国际化里程碑/CIPS扩围 | **央行官网（pbc.gov.cn）必扫，Sina lid=2517 不覆盖** |
| CPI/PPI/GDP | 数据发布且超预期 | 国家统计局/东方财富 |
| 房地产 | 恒大/碧桂园重大负面 | 财新/新浪搜索 |
| 美联储 | 利率决议后市场明显反应 | FED官网RSS |
| **上交所/上期所大宗商品风控** | 黄金白银期货保证金/涨跌停调整 | 上期所官网公告 |
| **市场监管总局平台约谈** | 约谈大型互联网平台（携程/美团等） | 市场监管总局官网或新浪财经wm频道 |
| **地缘政治-能源通道** | 霍尔木兹/马六甲等关键海峡局势 | 新浪 lid=2517 国际新闻（多源确认） |
| 上交所REITs | 业务指南修订/项目动态重大变化 | 上交所 `sse.com.cn/reits/` |

**港股恒生科技指数监控说明**：恒生科技指数（HSTECH）在新浪财经头条（lid=2516）快讯中实时出现，触发条件为单日涨跌超2%。2026-06-11 实测：10:16 新浪快讯报"港股三大指数跌幅扩大，恒生科技指数跌超2%，阿里巴巴跌超5%"，推送后确认港股内房股逆势走强（资金在科技/地产间切换）。

**央行官网（pbc.gov.cn）是最重要的独家信息源**：`https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html` 的"新闻发布"栏目含所有官方政策声明、双边金融合作MOU、央行行长会见等**仅在央行官网发布的重大信息**。2026-06-11 实测：中印尼联合工作机制会议（签署人民币清算MOU、跨境二维码支付上线、印尼银行加入CIPS）在新浪 lid=2517 全天20条中**零覆盖**，仅出现在央行官网首页公告区（发布时间16:58）。**每次扫描必须直接访问 pbc.gov.cn/goutongjiaoliu 公告列表**，不可依赖 Sina API。

## 推送格式

```
【经济速报】[日期时间]
[事件标题]
[简明分析：1-3句，说清楚市场影响]
[数据支撑：具体数字]
[来源：XX机构]
```

## 数据源

**核心数据源（2026-06 实测可靠）：**
**核心数据源（2026-06 实测可靠）：**
| 指标 | 正确来源 | 说明 |
|------|---------|------|
| A股指数（上证/深证/创业板/沪深300） | `https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006` | 新浪财经，GBK编码，需Referer `https://finance.sina.com.cn`。逗号分隔，parts[1]=当前价，parts[2]=涨跌额，parts[3]=涨跌幅%（带符号字符串）。**本session实测可用** |
| A股指数（新浪字段说明） | 同上 | 解析示例：`var hq_str_s_sh000001="上证指数,3993.2258,-16.8049,-0.42,5986947,122707007"` → parts[1]=当前价3993.23，parts[2]=涨跌额-16.80，parts[3]=涨跌幅%-0.42（带符号字符串） |
| A股指数（腾讯备用） | `https://qt.gtimg.cn/q=sh000001,sz399001,sz399006,sh000300` | 腾讯证券，GBK编码，无需Referer。返回 `v_sh000001="1~名称~代码~当前价~昨收~...~涨跌幅%~涨跌额"`，字段[3]=当前价，字段[4]=昨收，字段[31]=涨跌幅%，字段[32]=涨跌额 |
| USD/CNY | `https://hq.sinajs.cn/list=fx_susdcny` | 新浪财经，GBK编码，需Referer。格式 `var hq_str_fx_susdcny="时间,买一价,卖一价,基准汇率,...,当前价,..."`，字段7=当前价。**注意：代码是`fx_susdcny`不是`USDCNY`**，本session实测 `fx_susdcny` 成功，`USDCNY` 可能返回空 |
| USD/CNY（备用） | 中国银行外汇牌价 `https://www.boc.cn/sourcedb/whpj/` | 中行网页HTML，`data-currency='美元'` 行含现汇买入价/卖出价（per 100单位），实际汇率 = 数值÷100 |
| 美联储新闻 | `https://www.federalreserve.gov/feeds/press_all.xml` | UTF-8，无反爬，稳定 |
|36kr RSS | `https://36kr.com/feed` | 2026-06实测稳定返回30条当日财经新闻，content-type=application/rss+xml。本session(15:13)再次实测可用，返回字节AI制药/清华情绪模型等独家内容 |
| 新华网政治RSS | ~~`http://www.xinhuanet.com/politics/news_politics.xml`~~ ⚠️ **已失效** | 数据停滞在2022年12月（300条均为疫情防控内容），**停止使用** |
| 新浪财经政经快讯 | `https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517` | 实证可用，返回20条带Unix时间戳的政经新闻。**本session(16:44)确认**：政经快讯(lid=2517)偏国内政策/产业，头条快讯(lid=2516)更综合含全球市场 |
| 新浪财经头条（推荐） | `https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516` | **2026-06-11本session实测**，比lid=2517更综合，含港股/美股/原油/IPO/地缘政治等全球市场头条，30分钟内政经+头条共21条。本session用于港股科网股普跌(阿里-5%)/Hugo Boss收购等事件发现 |
| 四大证券报头版精华摘要 | `https://finance.sina.com.cn/stock/y/{date}/doc-iniaysky{xxxx}.shtml` | 四报（证券日报/证券时报/上海证券报/中国证券报）头版内容每日汇总，**本session实测**是P2级政策事件的重要来源（如工信部"AI+信息通信"实施意见即出现在2026-06-11头版），浏览器打开无需登录，直接提取正文。URL中`{date}`格式为`2026-06-11`，`{xxxx}`为动态文章ID需从列表页获取 |
| **新浪财经API解析** | 同上 | **GBK解码 + eval()模式**：返回内容形如`eval(callme(...))`的JSONP，需先用`replace`替换`false/true/null`再`eval()`，示例：<br>`content = r.read().decode('gbk', errors='ignore'); d = eval(content.replace('false','False').replace('true','True').replace('null','None'))` |

**新浪财经文章页内容提取**：直接`urllib`读取后用`re.sub(r'<[^>]+>','', html)`提取正文**失败率高**（正则被页面JS干扰返回空）。**正确方式**：用`browser_navigate`直接打开文章URL（如`https://finance.sina.com.cn/jjxw/2026-06-11/doc-iniaysky{xxxx}.shtml`），`inner_text("body")`直接返回干净正文。适用于：CPI/PPI原文、四报头条原文、工信部政策原文等。`bb-browser`对此类页面也有效但不稳定。

**上期所/证监会/央行文章正文提取（2026-06-11实测）**：
- urllib 直读新浪财经文章页返回大量 JS 代码，正文提取失败
- 正确方式：`browser_navigate('URL')` → `browser_console("document.body.innerText.slice(0,3000)")` 提取干净正文
- 证监会首页 `browser_navigate` 截断时，直接 navigate 子路径（如 `/csrc/c100028/common_xq_list.shtml`）获取完整列表

**PBC.gov.cn 公告正文提取（2026-06-11实测）**：
```javascript
// 进入公告列表页（goutongjiaoliu/113456/113469/index.html）后点击标题进入正文
// 正文提取：
document.querySelector('.article_con')?.innerText 
|| document.querySelector('.TRS_Editor')?.innerText 
|| document.querySelector('span[id="zoom"]')?.innerText 
|| document.body.innerText.slice(0,3000)
```
PBC.gov.cn 公告区条目直接在首页可见，无需翻页，最新条目点击即可获取正文。

**⚠️ bb-browser adapter 输出格式**：所有 `bb-browser site<adapter>` 输出**不是纯JSON**，含进度条/日志/错误信息等多行内容。正确解析方式：用 `subprocess.run` 捕获原始输出，逐行找第一个以 `{` 或 `[` 开头的行再 `json.loads()`，其他行忽略。示例：
```python
r = subprocess.run(['bb-browser', 'site', '36kr', 'newsflash', '--json'], capture_output=True, text=True, timeout=15)
for line in r.stdout.split('\n'):
    line = line.strip()
    if line.startswith('{') or line.startswith('['):
        try:
            d = json.loads(line)
            # ...
        except: pass
        break
```

**⚠️ bb-browser search adapter 在 cron 环境的问题**：
- `baidu/search` adapter 不存在，实际应使用 `bb-browser site baidu search`（注意 `site` 关键字）
- `bing/search` adapter 返回空（2026-06-11 14:17 实测），**搜索类 adapter 在 cron 环境下整体不稳定**
- `bb-browser site list` 显示 adapter 列表，但 `site baidu` 子命令是 `search`（不是 `site baidu/search`）
- **搜索类统一降权**：优先用新浪财经 lid=2517 + 36kr RSS + 官方页面直接访问，少用搜索 adapter
| 证监会最新要闻 | `http://www.csrc.gov.cn/csrc/c100028/common_xq_list.shtml` | browser_navigate直连，今日(06-09)仅有外事活动（吴清会见马来西亚/香港金管局） |
| 证监会令/公告 | `http://www.csrc.gov.cn/csrc/c101953/zfxxgk_zdgk.shtml` | 证监会令最新列表（含第234号令等） |
| 央行新闻发布 | `https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html` | browser_navigate直连，今日(06-09)仅有外事活动（潘功胜会见香港银行公会） |
| 央行货币政策 | `https://www.pbc.gov.cn/rmyh/105145/index.html` | 货币政策专栏，含降准/降息/LPR等核心政策 |
| **gov.cn 公开市场业务交易公告** | `https://www.gov.cn/zhengcehuobisi/125207/125213/125431/index.htm` | ⚠️ urllib 直读 404（本session实测多次404），需用 Playwright CDP 直连 Chrome 内置SSL |
| 统计局数据发布 | `https://www.stats.gov.cn/sj/zxfb/` | browser_navigate直连，含CPI/PPI/工业增加值等核心指标。本session(16:xx)确认5月CPI+1.2%、PPI+3.9%在此页面，URL为 `./202606/t20260610_1963923.html` |

**实测不可靠（本 session 结果）：**
- 新华网政治RSS：数据停滞2022年12月，全为疫情旧闻，**停止使用**
- 新浪 hq.sinajs.cn 美股期货 `hf_*` 前缀：403（Referer或IP限制）
- 新浪财经快讯API：404
- 36kr RSS：部分返回application/rss+xml（正常），部分返回HTML 404（需单独处理Content-Type判断）
- 腾讯/同花顺/雪球/东方财富API：返回空或403
- 财新RSS：international.caixin.com/rss/latest.xml 返回HTML 404
- 华尔街见闻RSS：404
- 第一财经RSS：404
- 新华财经备用RSS（fortune/feed1.xml等）：404
- 中国经济网RSS：404
- 中国证券报RSS：timeout
- gov.cn 系列 urllib直读：易404，browser_navigate超时60s，需用Playwright
- 央行官网 `pbc.gov.cn` 子路径：`/rmbh/10984/index.html` 等已404，需探索正确路径
- USD/CNH（离岸）：本session实测 `fx_susdcnh` 成功返回6.7834（"离岸人民币（香港）"），字段格式同在岸
- **新浪 `USDCNY` 代码**：本session实测 `list=USDCNY` 返回空（行情由新浪财经计算得出，无实时数据）。**正确代码是 `list=fx_susdcny`**，返回含当前价/买一价/卖一价/基准汇率/当前价等11字段

**搜索降权规则（cron环境不可靠）：**
- Bing中文搜索：严重依赖中文关键词的内容（如"降准 site:gov.cn"）返回大量字典/百科结果，需二次过滤。cron环境下超时率高。
- 百度搜索：严格滑块验证，服务器无头环境下完全不可用。
- 推荐：直接用RSS + 官方API，少用搜索。
推送后保存报告到：`~/.hermes/economic-reports/`

## 第5关：去重检查

**⚠️ 关键词重叠不是重复**：去重的目标是防止同一事件重复推送，而不是阻止同一指标的不同事件。当两条新闻标题都含 "CPI" 但本质不同（如"今晚美国CPI"预测 vs "5月CPI同比+1.2%官方发布"），**不是重复，是独立事件，需分别判断是否推送**。

```python
import os, re
from datetime import datetime

reports_dir = os.path.expanduser("~/.hermes/economic-reports/")
today = datetime.now().strftime('%Y-%m-%d')

def event_key(title):
    """
    从标题提取事件本质特征，用于去重判断。
    格式：指标_时间_事件类型
    例如：
      "5月CPI官方发布"   → "cpi_5月_official"
      "今晚美国CPI预测"  → "cpi_今晚_forecast"
      "金价跌破4200"     → "gold_4200_break"
    同一指标的不同事件类型（如official/forecast/market-commentary）算不同事件。
    """
    t = title.lower()
    # 指标提取
    indicator = "unknown"
    for kw in ["cpi", "ppi", "金价", "黄金", "美元", "人民币", "kospi", "韩股", "上证", "创业板"]:
        if kw in t:
            indicator = kw
            break
    # 时间/版本特征
    time特征 = ""
    if "今晚" in title or "今晚21" in title:
        time特征 = "_今晚_forecast"
    elif re.search(r"\d+月", title):
        time特征 = "_月次数据"  # 月度数据发布
    elif "跌破" in title or "突破" in title:
        time特征 = "_价位异动"
    else:
        time特征 = "_其他"
    return f"{indicator}{time特征}"

def similar(a, b, threshold=0.7):
    """简单相似度：共现词比例"""
    words_a = set(re.findall(r'[\w]+', a.lower()))
    words_b = set(re.findall(r'[\w]+', b.lower()))
    if not words_a or not words_b:
        return False
    intersection = len(words_a & words_b) / min(len(words_a), len(words_b))
    return intersection > threshold

def is_duplicate(new_title):
    """
    判断是否为重复事件。
    两条新闻"都含CPI但事件本质不同"不算重复（如官方发布 vs 市场预测）。
    只有事件本质相同（event_key相同或标题相似度>70%）才算重复。
    """
    new_key = event_key(new_title)
    if not os.path.exists(reports_dir):
        return False
    for f in os.listdir(reports_dir):
        if today not in f:
            continue
        try:
            with open(os.path.join(reports_dir, f)) as fh:
                content = fh.read()
            # 取已有报告标题行
            existing_titles = re.findall(r'【[^】]+】[^\n]+', content)
            for et in existing_titles:
                # 事件本质相同 → 重复
                if event_key(et) == new_key:
                    return True
                # 标题相似度>70% → 重复（兜底）
                if similar(new_title, et):
                    return True
        except:
            pass
    return False
```

**常见误判场景**：
- ❌ 误判为重复："今晚美国CPI数据"（预测） vs "5月CPI同比+1.2%"（官方发布）→ 指标相同但事件类型完全不同
- ✅ 正确识别为重复："5月CPI同比+1.2%"（今日12点已推送） vs "5月CPI同比+1.2% PPI+3.9%"（同一分钟内的补充推送）→ 事件本质相同
- ✅ 正确识别为重复："金价跌破4200美元"（今日09:35已推送） vs "金价跌破4200美元 今晚关注美国CPI"（今日11:45已推送）→ 两篇都是关于金价跌破4200的分析，标题相似度高

## 工作流

```python
import urllib.request, re, ssl, time
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch(url, decode='utf-8', timeout=10):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.read().decode(decode, errors='ignore')

# 1. 获取A股数据（腾讯证券，GBK编码）
raw = fetch("https://qt.gtimg.cn/q=sh000001,sz399001,sz399006,sh000300", decode='gbk')
indices = {
    'sh000001': '上证指数', 'sh000300': '沪深300',
    'sz399001': '深证成指', 'sz399006': '创业板指'
}
triggers = []
for code, name in indices.items():
    m = re.search(rf'v_{code}="([^"]+)"', raw)
    if m:
        vals = m.group(1).split('~')
        price = float(vals[3])
        yclose = float(vals[4])
        chg_pct = float(vals[31])
        chg_amt = float(vals[32])
        pct_num = round((price - yclose) / yclose * 100, 2)
        if abs(pct_num) > 2.0:
            triggers.append(f"【重要】{name}单日涨跌{pct_num:+.2f}%，超过2%阈值（当前{price}，昨收{yclose}）")

# 2. 获取USD/CNY（新浪财经，GBK编码）
# ⚠️ 正确代码是 fx_susdcny，不是 USDCNY（后者返回空）
raw_usd = fetch("https://hq.sinajs.cn/list=fx_susdcny", decode='gbk',
                headers={'Referer': 'https://finance.sina.com.cn'})
# 格式: var hq_str_fx_susdcny="时间,买一价,卖一价,基准汇率,...,当前价,...";
#       共11个字段：parts[0]=时间, parts[1]=买一价, parts[2]=卖一价, parts[3]=基准汇率, ..., parts[6]=当前价
# 离岸人民币代码（交叉验证）: fx_susdcnh
# 实测(2026-06-10 22:36): fx_susdcny 返回 6.7751（买）/6.7737（卖）；fx_susdcnh 返回 6.7834
m_usd = re.search(r'hq_str_fx_susdcny="([^"]+)"', raw_usd)
if m_usd:
    usd_vals = m_usd.group(1).split(',')
    usd_price = float(usd_vals[1])   # 当前价/中间价
    for threshold in [7.3, 7.2, 7.0]:
        if usd_price > threshold:
            triggers.append(f"USD/CNY突破{threshold}，当前{usd_price:.4f}")
            break

# 3. 获取财经新闻（36kr RSS，UTF-8，application/rss+xml）
# 注意：部分环境可能返回HTML 404，需检查Content-Type再解析
try:
    req = urllib.request.Request('https://36kr.com/feed', headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        ctype = r.headers.get('Content-Type', '')
        raw36 = r.read()
    if 'xml' in ctype or 'rss' in ctype:
        items = re.findall(r'<item>(.*?)</item>', raw36.decode('utf-8', errors='ignore'), re.DOTALL)
        keywords = ['降准', '降息', 'LPR', 'MLF', '货币', '汇率', '人民币', '美元', '央行', '美联储', '加息', 'CPI', 'PPI', 'GDP', '统计局', '房地产', '恒大', '碧桂园', '证监会', 'IPO', '注册制', '财政部', '政治局', '国务院']
        for item in items:
            title_m = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item) or re.search(r'<title>(.*?)</title>', item)
            if title_m and any(k in title_m.group(1) for k in keywords):
                triggers.append(f"【新闻】{title_m.group(1).strip()}")
except Exception as e:
    pass  # 36kr不可用时跳过

# 4. 获取美联储新闻（FED官网RSS）
try:
    raw_fed = fetch("https://www.federalreserve.gov/feeds/press_all.xml")
    fed_items = re.findall(r'<item>(.*?)</item>', raw_fed, re.DOTALL)
    for item in fed_items[:5]:
        title_m = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item) or re.search(r'<title>(.*?)</title>', item)
        if title_m:
            triggers.append(f"【FED】{title_m.group(1).strip()}")
except:
    pass

# 5. 保存报告
if triggers:
    os.makedirs(os.path.expanduser("~/.hermes/economic-reports"), exist_ok=True)
    report = f"【经济速报】{datetime.now().strftime('%Y-%m-%d %H:%M')}\n" + "\n".join(triggers)
    fname = f"~/.hermes/economic-reports/report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(os.path.expanduser(fname), 'w') as f:
        f.write(report)
else:
    print("[SILENT]")  # 无触发条件，不推送
```

**搜索降权规则（cron环境不可靠）：**
- Bing中文搜索：严重依赖中文关键词的内容（如"降准 site:gov.cn"）返回大量字典/百科结果，需二次过滤。cron环境下超时率高。
- 百度搜索：严格滑块验证，服务器无头环境下完全不可用。
- 推荐：直接用RSS + 官方API，少用搜索。

## 推送原则

- 推送的是分析，每条必须有"市场影响"判断
- 不提供具体投资买卖建议
- 两次推送之间内容不重复（如果事件没进展，不重复推送）
- 无重大发现 → 输出 `[SILENT]`

## 五级事件筛选流程（2026-06-11 更新）

每条新闻过五关才推送：

**第1关：来源审批**
- ✅ 通过：新华网、人民网、央视新闻、中国政府网 gov.cn、央行官网、国家统计局官网、证监会/银保监官网、新华社快讯、四大证券报（证券日报/证券时报/上海证券报/中国证券报）
- ⚠️ 降权：Wind/同花顺/东方财富转载官方稿
- ❌ 拦截：自媒体（股社区/大V微博/雪球个人号）、无来源微信群截图

**第2关：多源交叉验证**
- ✅ 通过：同一事件≥2个独立官方源确认
- ⚠️ 存疑：仅1个源 → 标记待验证
- 🔓 单源放行条件：A股单日跌>3%、USD/CNY突破7.3等重大市场异动

**第3关：关键词命中**
- 🔴 核心词（立即推送）：降准、降息、LPR、麻辣粉（MLF）、政治局（经济）、国务院（经济）、CPI、PPI、GDP、统计局、房地产（中央）、恒大/碧桂园、美联储/加息/缩表、人民币/汇率/USD-CNY、证监会/IPO/注册制
- 🟡 一般词（降权）：个股异动（非系统性）、行业公司财报（正常发布）、地方补贴政策

**第4关：事件分类评级**
| 级别 | 定义 | 推送方式 |
|------|------|---------|
| P0 | A股单日跌>3%/USD/CNY突破7.3/央行宣布降准降息 | 立即+加急标记 |
| P1 | 美联储利率决议/重要经济数据超预期 |立即推送 |
| P2 | 头部房企暴雷/房地产重大政策/人民币大幅波动/重要政策文件发布 | 立即推送 |
| P3 | 一般行业政策/公司财报（非系统性） | 常规推送 |
| P4 | 个股/地方政策/日常数据 | 归入周报 |

**已知P3/P4降权案例（今日 session 实测）：**
- **黄金进入熊市**（金十数据/新浪财经转载）：91天跌没20%，属市场技术性判断，非官方政策或数据发布 → P3降权，归入周报
- **极兔速递被国家邮政局立案调查**：监管主体是公司（极兔），不是行业/系统性监管机构政策 → P4降权，不推送
- **小摩/机构CPI预测**：仅1个非官方源，且美国5月CPI+4.2%已在03:13由官方源（36kr/财联社）确认推送 → 跳过

**⚠️ 监管主体关键词（邮政局/证监会/央行）单独命中的判断规则：**
- 标题含"邮政局"+"XX公司"（如极兔速递）→ 公司级监管，P4，不推送
- 标题含"邮政局"+"行业/平台"（如快递行业、电商平台）→ 行业级监管，P2/P3，酌情推送
- 同理：证监会令 → P2（官方政策文件）；证监会预罚单 → P2（中介机构违规，系统性信号）
- 央行/美联储新闻 → 优先看是否含核心政策词（降准/降息/加息），不含则参考机构名称和事件规模降权

**第5关：去重检查**
- 对比今日已有推送，标题相似度>70% → 跳过
- 新内容 → 通过

**今日推送记录（2026-06-11 07:10 cron run）：**
- P2：5月份CPI+PPI数据发布（国家统计局，经四大证券报确认）
- P2：工信部"AI+信息通信"创新发展实施意见（2026-2028）
- P3：5月新能源汽车产销数据（中汽协）
- P3：8部门推动铁路与旅游融合（商务部等）
- P3：SpaceX上市引爆商业航天赛道

**bb-browser adapter 超时问题（2026-06-10 实测）**：
- `bb-browser site zhihu/hot` — 失败，无输出
- `bb-browser site m_weibo/hot` — 超时20s
- `bb-browser site hackernews/top` — 超时20s
- `bb-browser site reuters/search` — 超时25s
- `bb-browser site baidu/search` — 超时/无输出
- 结论：搜索类 adapter 在 cron 环境下超时率高，**统一降权**，优先用 `bb-browser site 36kr/newsflash`（实测稳定7-8秒返回20条快讯）

- `references/hstech-monitoring-case-20260611.md` — 恒生科技指数监控案例（2026-06-11）
- `references/gov-cn-open-market-urls-20260611.md` — gov.cn公开市场业务交易公告URL结构与urllib-404踩坑（2026-06-11）
- `references/quiet-session-20260611.md` — 静默监控 session 实录（13:00-13:45 零推送分析）

## 保存报告

**支持文件说明：**
- `references/sina-article-scraping.md` — 新浪财经文章正文提取方法（browser_navigate vs urllib正则）
- `references/china-market-sources-20260610.md` — A股/汇率/大宗商品实测数据源（2026-06-10）
- 其他 reference 文件记录过往 session 的数据源验证和踩坑记录

```python
import os
os.makedirs(os.path.expanduser("~/.hermes/economic-reports"), exist_ok=True)
with open(os.path.expanduser(f"~/.hermes/economic-reports/report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"), "w") as f:
    f.write(report)
```

## 已知踩坑

### Sina lid=2517 对央行双边金融合作完全盲区（2026-06-11 实测）

**问题**：中印尼央行联合工作机制会议（2026-06-11 16:58发布）——含签署人民币清算MOU、跨境二维码支付上线、印尼银行加入CIPS——在新浪财经政经API lid=2517 全天20条新闻中**零覆盖**。这是人民币国际化重大里程碑，但在新浪API中完全看不到。

**教训**：Sina lid=2517 对以下领域存在系统性盲区：
- 央行双边金融合作（MOU签署、CIPS扩围、本币互换）
- 央行官网公告区（pbc.gov.cn）的非政策声明类新闻
- 央行行长外事会见

**正确做法**：每次扫描必须额外执行 `browser_navigate('https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html')` 提取公告列表，不能只依赖新浪API。

**文章正文提取**：直接 navigate 到公告正文链接，用 `browser_console("document.querySelector('.article_con')?.innerText || document.querySelector('.TRS_Editor')?.innerText || document.querySelector('span[id=\"zoom\"]')?.innerText || document.body.innerText.slice(0,3000)")` 提取正文。

### deliver 配置必须设为飞书群

cron job 的 `deliver` 字段控制推送目标：
- ✅ `feishu:oc_c6883cd907e4d226736d87ce9c6c6d79` → 订阅群
- ❌ `origin` → 推回 DM（用户明确说过"别推到这里"）

**建好 job 后立即用 `cronjob list` 检查 `deliver` 字段。**

**cron 自动投递行为（重要）**：当 cron job运行时，最终回复文本（final response）自动投递到 `deliver` 字段配置的目标（飞书群）。`send_message` 调用会被自动抑制，报 `cron_auto_delivery_duplicate_target` → 表示目标已被 cron 自动投递占用。**正确做法**：将推送内容直接写入 final response，不要另行 `send_message`。如果需要额外消息，直接调用 `send_message` 到其他目标（如 DM），不要重复投递到同一个飞书群。

**新浪财经GBK编码**：hq.sinajs.cn 返回 GBK 编码，需 `.decode('gbk')`，其他大多数中文站用 UTF-8。

**格式化字符串错误**：解析出的值是字符串，直接用 `:.2f` 会报 `ValueError: Unknown format code 'f' for object of type 'str'`。需先 `float(vals[3])` 转换。

**美股期货/大宗商品**：hq.sinajs.cn 的 `hf_` 前缀代码本 session 测试返回 403，可能是 Referer 限制或 IP 限制。备用方案：用 CME 官网或 broker API。

**新浪财经 USD/CNY 正确代码**：`list=fx_susdcny`（本 session2026-06-10 19:39 实测成功返回6.7773），`list=USDCNY` 返回空（"行情由新浪财经计算得出"无实时数据）。字段格式：`var hq_str_fx_susdcny="时间,买一价,卖一价,基准汇率,...,当前价,..."` — 字段7=当前价。注意：`fx_susdcny` 在岸人民币代码与 `fx_susdcnh` 离岸人民币代码不同，离岸（香港）代码是 `fx_susdcnh`。两者同时查可交叉验证。

**browser_navigate 输出截断**：对于内容多的页面（如证监会/央行首页），browser_navigate 返回的 snapshot会被 `[... N more lines truncated]` 截断。需重新抓取时直接访问目标子路径（如 `/csrc/c100028/common_xq_list.shtml` 而非首页）。
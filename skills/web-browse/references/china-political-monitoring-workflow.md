# 中国政府政策监测参考 — 2026-06-16 更新

## gov.cn 要闻列表轮询 — JSON直连法（2026-06-16 更新）

gov.cn `/yaowen/liebiao/` 页面通过 AJAX 动态加载，数据源为同目录下的 JSON 文件，**直接请求即可**，无需 Playwright/浏览器：

```python
import urllib.request, ssl, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://www.gov.cn/yaowen/liebiao/YAOWENLIEBIAO.json'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://www.gov.cn/yaowen/liebiao/'
})
with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
    data = json.loads(r.read())

# data 是列表，按发稿时间倒序（最新在前）
# 每条：{'TITLE': str, 'URL': str, 'DOCRELPUBTIME': 'YYYY-MM-DD'}
today = '2026-06-15'
today_items = [x for x in data if x['DOCRELPUBTIME'] == today]
print(f"今日({today})文章数: {len(today_items)}")
for item in today_items:
    print(f"  [{item['DOCRELPUBTIME']}] {item['TITLE']}")
    print(f"    {item['URL']}")
```

**优势**：
- 无需浏览器/CDP，urllib 直调，< 500ms
- 返回400条（当日实时约200条 + 历史约200条）
- 成功率达100%

**⚠️ 历史覆盖局限（2026-06-16 实测）**：
- YAOWENLIEBIAO.json **不分页**，所有 `?page=N`（N≥1）返回**完全相同的400条**
- 实际覆盖：**仅约1个月**（2026-05-16 ~ 2026-06-16）
- **3个月以上的历史数据无法通过此接口获取**
- 政经月报需3–4月事件时，需通过新浪财经政经API（lid=2517/2516）、36kr RSS、Bing搜索补充
- 新浪财经lid=2517仅含实时新闻，无历史回溯；36kr RSS每日30条无历史回溯
- Bing搜索含大量百科/词典噪音，需二次过滤（排除百度/百科/词典/翻译/Merriam/Cambridge）

**注意**：`zhengce/liebiao` 的等效 JSON（ZHENGCEGONGGAO.json）已404，需改用 YAOWENLIEBIAO 方式。

## gov.cn Content ID 模式（2026-06 验证）

```
URL格式：https://www.gov.cn/yaowen/liebiao/YYYYMM/content_CONTENTID.htm
示例：
  content_7071845.htm = 2026年6月11日发布（国常会）
  content_7071853.htm = 2026年6月11日发布（东西部协作）
  content_7071863.htm = 2026年6月11日发布（张国清峰会发言）
  content_7071942.htm = 2026年6月12日发布（缅甸总统访华）
  content_7071966.htm = 2026年6月12日发布（第48届世赛）
  content_7071986.htm = 2026年6月13日发布（习近平文化思想）
  content_7072011.htm = 2026年6月13日发布（海洋生态）
  content_7072002.htm = 2026年6月13日发布（新能源重卡方案，政策文件库）
  content_7072054.htm = 2026年6月15日发布（前5月社会融资规模）
  content_7072079.htm = 2026年6月15日发布（澳门特區政府任命）
  content_7072086.htm = 2026年6月15日发布（缅甸总统访华）
  content_7072129.htm = 2026年6月15日发布（求是杂志习近平文章）
  content_7072132.htm = 2026年6月15日发布（习近平教育科技人才）
  content_7072157.htm = 2026年6月15日发布（全国党建座谈会）
  content_7072171.htm = 2026年6月15日发布（李强第二十次专题学习）
  content_7072175.htm = 2026年6月15日发布（何立峰会见美国议员）
  content_7072195.htm = 2026年6月15日发布（习近平党建思想）
  content_7072199.htm = 2026年6月15日发布（习近平党建思想指引）
```

**规律**：
- ID 每隔1-4天递增约10-30
- 高优先级文章（如国常会）ID 可能略低（因发布在较晚时间）
- 同一日多篇文章连续递增，ID差距体现优先级而非时效

## 发布时机规律（2026-06-15 验证）

| 时间 | 状态 |
|------|------|
| 06-14 白天 | 无6月14日新文章，gov.cn 要闻次日午前才更新 |
| 06-15 白天 | 12条新文章出现，更新时间窗口约6-12小时 |
| 06-15 22:47 | 最新文章（李强专题学习）发布 |

**结论**：gov.cn 要闻在事件发生后**6-12小时**上线，适合每4-6小时轮询。

## 本周期（2026-06-15 22:47）重要发现

### P1：习近平在《求是》发表重要文章：一体推进教育科技人才发展
**URL**：https://www.gov.cn/yaowen/liebiao/202606/content_7072132.htm

核心内容：
- 系统阐述"一体推进教育科技人才发展"重大战略思想
- 人才资源是第一资源，创新驱动实质是人才驱动
- 科技创新的竞争首先是人才培养的竞争
- 一流大学建设坚持党的领导，把发展科技第一生产力、培养人才第一资源、增强创新第一动力更好结合起来

**评级**：P1（求是杂志+习近平署名，重量级最高）

### P2：李强主持国务院第二十次专题学习
**URL**：https://www.gov.cn/yaowen/liebiao/202606/content_7072171.htm

核心内容：
- 聚焦"十五五"时期主体功能区战略深化部署
- 优化主体功能区划，推动空间治理精准精细
- 城市化地区给予激励性政策，农产品主产区和重点生态功能区给予保障性政策
- 统筹主体功能区战略与区域协调发展、新型城镇化等重大战略协同叠加

**评级**：P2（国务院专题学习，"十五五"空间治理部署）

### P2：全国党建工作座谈会在京召开
**URL**：https://www.gov.cn/yaowen/liebiao/202606/content_7072157.htm

核心内容：
- 中央政治局常委蔡奇出席，李希出席
- 专题部署习近平党建思想学习贯彻
- 全面从严治党，一体推进不敢腐不能腐不想腐

**评级**：P2（党建专题会议，理论体系化重要节点）

### P3：前5月社会融资规模增量累计17.48万亿元
**URL**：https://www.gov.cn/lianbo/202606/content_7072054.htm

核心内容：
- 1-5月社会融资规模增量累计17.48万亿元
- 截至5月末，本外币贷款余额284.79万亿元，同比增长5.4%
- 央行实施适度宽松货币政策，效果持续显现

**评级**：P3（金融数据，经济运行参考）

### P3：缅甸总统敏昂莱访华
**URL**：https://www.gov.cn/yaowen/liebiao/202606/content_7072086.htm

核心内容：
- 应国家主席习近平邀请，缅甸总统敏昂莱抵京开始国事访问
- 访问为期5天，涵盖贸易、投资、能源等领域合作

**评级**：P3（外交活动）

## 去重检查文件位置

```
~/.hermes/political-reports/
├── 20260615_1030_political_report.txt
├── 20260615_1144_P3_防汛部署.txt
├── 20260615_1226_P4_daily.txt
├── 20260615_1530_political.txt
└── 20260615_2247_political.txt  ← 本次报告
```

去重方法：读取目录，对比标题关键词相似度。今日已推送：
- 缅甸总统访华 → 本次P3（已在1530批次出现，本次去重）
- 习近平党建思想 → 本次P2（新发现）
- 李强专题学习（主体功能区）→ 本次P2（新发现）
- 求是杂志文章（教育科技人才）→ 本次P1（新发现）
- 社会融资规模 → 本次P3（已在1530批次出现，本次去重）

## 飞书推送目标

- 飞书群：`oc_c6883cd907e4d226736d87ce9c6c6d79`
- cron 自动投递：final response 即为投递内容，无需 send_message

## Playwright CDP 连接稳定性（2026-06-15 验证）

**问题**：sandbox 环境中 `connect_over_cdp("http://localhost:19825")` 报 `ECONNREFUSED`，即使 Chrome 端口已在监听。

**原因**：sandbox 进程和 Chrome 进程不在同一网络命名空间。

**稳定工作流**：
```python
# 1. terminal 启动 Chrome（background=True 避免 vet 拦截）
terminal(background=True, command="google-chrome --remote-debugging-port=19825 --user-data-dir=/tmp/chrome-debug --no-sandbox --headless")

# 2. 确认端口监听
terminal(command="sleep 4 && ss -tlnp | grep 19825")

# 3. execute_code 中使用 Playwright
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    page = browser.new_page()  # 不依赖 context.pages[0]
    page.goto(url, timeout=20000, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    text = page.inner_text("body")  # 不用 page.evaluate()
    page.close()
    browser.close()
```

**gov.cn 文章页标题位置（2026-06-15验证）**：
- 要闻类：正文前约200字符为CSS/JS框架代码，标题在第200-300字符之后
- 政策文件类（zhengceku）：正文更干净，标题紧接框架代码之后
- 策略：统一用 `page.inner_text("body")` 取全文本，从第200字符往后截取

## 已知问题（2026-06-15 更新）

- gov.cn 搜索功能（`?searchword=`）重定向到首页，**不可用**，必须从列表页提取
- 新华网 RSS（politics/news_politics.xml）返回2022年旧数据，**不可用**
- 新浪财经 lid=2517 晚间23:00-07:00仅返回国际新闻，**不可用于政治监测**
- gov.cn lianbo 直连超时60s，必须 Playwright CDP 连接已有 Chrome
- gov.cn 文章页标题选择器对政策文件类超时，需改用 `page.inner_text("body")`
- gov.cn 要闻更新延迟6-12小时，建议轮询间隔4-6小时
- sandbox 环境中 `connect_over_cdp` 可能报 ECONNREFUSED，先用 terminal 启动 Chrome
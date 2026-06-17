# 每日新闻 Cron 脚本模式与已知问题

本文记录 `~/.hermes/scripts/` 下各类日报/新闻抓取脚本的通用模式、已知坑位和修复经验。

---

## 脚本清单与输出路径

| 脚本 | 用途 | 输出路径 | cron ID |
|------|------|---------|---------|
| `political-news.py` | 全球政治要闻 | `~/.hermes/cron/output/political-news/` | `18bd30b7ef2a` |
| `business-news.py` | 商业财经日报 | `~/.hermes/scripts/cron/output/biz-news/` | `347cf635ccbf` |
| `game-weekly-digest.py` | 游戏周报 | `~/.hermes/scripts/cron/output/` | `ae0c69cf5306` |
| `kpop-news.py` | 韩娱女团资讯 | `~/.hermes/scripts/cron/output/` | `6706b1d82b7d` |
| `50forum-weekly.py` | 经济50人论坛周报 | `~/.hermes/scripts/` | `22b141c789ea` |

---

## 政治新闻 (political-news.py)

**数据源：**
- BBC World News RSS：`https://feeds.bbci.co.uk/news/world/rss.xml`（需代理 socks5://127.0.0.1:10808）
- 观察者网：`https://www.guancha.cn/internation/`（Playwright 抓取）

**翻译：** Google Translate 免费接口，超时 15s，失败时返回原文

### 常见问题

**噪音词漏过滤：**
症状——埃博拉、航展撞机、马拉松等非政治内容混入。
根因：NOISE_PATTERNS 不够全。
修复：扩充噪音词列表，特别关注：
- 健康疫情类：`ebola`, `virus outbreak`, `health emergency`
- 航空/军机类：`air show`, `fighter jet`, `aircraft collision`, `drone crash`
- 体育类：`tennis`, `marathon`, `running race`

**翻译超时导致标题留空：**
症状——英文标题直接显示，未翻译。
根因——代理链路不稳定，timeout 太短。
修复：`translate_to_chinese` timeout 10s → 15s；异常时返回原文而非空字符串：
```python
except Exception as e:
    print(f"翻译失败: {e}", file=sys.stderr)
    return text  # 失败时返回原文，不留空白
```

**观察者网抓取失败：**
症状——`观察者网抓取失败: ...`，但 BBC 正常。
根因——Playwright 启动失败或页面结构变化。
排查：`python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.launch().version)"`

---

## 商业新闻 (business-news.py)

**数据源：**
- Dow Jones 市场：`https://feeds.a.dj.com/rss/RSSMarketsMain.xml`
- Dow Jones 全球：`https://feeds.a.dj.com/rss/RSSWorldNews.xml`
- 新浪财经：`http://rss.sina.com.cn/news/china/focus15.xml`

**注意：** 脚本内标注的数据源（如"华尔街日报""FT中文网"）与实际 RSS 不符，应以脚本注释的 URL 为准。

### 常见问题

**台湾政治新闻混入：**
症状——新浪财经出现"蔡英文""民进党"等新闻。
根因——排除词不够。
修复：扩充 exclude 列表：
```python
exclude = [
    'politics', '政治', '体育', '娱乐', '娱乐圈', '明星', '电影',
    '战争', '军事', '科技', 'ai.', '人工智能', '大选', '选举',
    '蔡英文', '民进党', '绿媒', '九合一', '总统大选',  # 台湾政治
    '高铁', '通车', '开通', '事故', '撞机', '空难', '坠毁',  # 事故新闻
    '台风', '地震', '海啸', '暴雨', '洪水',  # 自然灾害
    '奥斯卡', '格莱美', '颁奖礼', '电影节', '票房'  # 娱乐
]
```

**旧闻（2018/2019年）混入：**
症状——出现多年份历史新闻。
根因——新浪财经 RSS 缓存旧条目。
修复：加年份过滤
```python
import re
old_year = re.findall(r'201[56789]|202[01]', text)
if old_year:
    return False
```

**描述含"原标题"垃圾：**
症状——`原标题：xxx 中新社记者 xxx 电`。
修复：clean_summary 函数扩充
```python
summary = re.sub(r'原标题[：:]\s*', '', summary)
summary = re.sub(r'中新社.*?电\s*', '', summary)
summary = re.sub(r'新华社.*?电\s*', '', summary)
```

---

## RSS 抓取通用模式

```python
import urllib.request, ssl, xml.etree.ElementTree as ET

def fetch_feed(url, timeout=15):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/rss+xml, application/xml, text/xml",
        })
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            data = r.read()
            for enc in ("utf-8", "gbk", "gb2312", "latin1"):
                try:
                    return ET.fromstring(data.decode(enc))
                except Exception:
                    continue
    except Exception:
        pass
    return None
```

---

## Playwright 抓取观察者网模式

```python
import subprocess, tempfile, json

PLAYWRIGHT_BIN = "/home/ubuntu/.hermes/hermes-agent/venv/bin/python3"

code = (
    "import sys,json\\n"
    "sys.path.insert(0,'/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages')\\n"
    "from playwright.sync_api import sync_playwright\\n"
    "with sync_playwright() as p:\\n"
    "  b=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-setuid-sandbox'])\\n"
    "  page=b.new_page(viewport={'width':1280,'height':900})\\n"
    "  page.goto('https://www.guancha.cn/internation/',timeout=30000)\\n"
    "  page.wait_for_timeout(3000)\\n"
    "  data=page.eval_on_selector_all('h4 a,a[href*=\"/internation/\"][href*=\".shtml\"]',\\n"
    "    'function(es){var s={},r=[];for(var i=0;i<es.length;i++){var e=es[i],t=e.innerText.trim();if(t.length>5&&t.length<100&&!s[t.substring(0,30)]){s[t.substring(0,30)]=true;r.push({text:t,href:e.href})}}return r.slice(0,12)}')\\n"
    "  sys.stdout.write('GUANCHA_DATA:'+json.dumps(data))\\n"
)
tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
tmp.write(code); tmp.close()
r = subprocess.run([PLAYWRIGHT_BIN, tmp.name], capture_output=True, text=True, timeout=60)
# 解析：r.stdout 中找到 'GUANCHA_DATA:' 后取 JSON
```

---

## 调试与验证

```bash
# 手动运行政治新闻脚本
cd ~/.hermes/scripts && python3 political-news.py

# 手动运行商业新闻脚本
cd ~/.hermes/scripts && python3 business-news.py

# 查看最近输出
cat ~/.hermes/cron/output/political-news/$(date +%Y-%m-%d).md
cat ~/.hermes/scripts/cron/output/biz-news/$(date +%Y-%m-%d).md

# 查看 cron 最后执行状态
# （通过 cron list 的 last_status 字段判断）
```

---

## 经验总结

1. **RSS 是最可靠的来源**——无需 JS 渲染，超时少，格式固定
2. **先过滤再收录**——exclude 列表比 include 更有效
3. **年份过滤很重要**——国内新闻源经常缓存旧闻
4. **翻译失败不要留空白**——返回原文比留空白好
5. **定期扩充噪音词**——每次出现新噪音就加到 NOISE_PATTERNS

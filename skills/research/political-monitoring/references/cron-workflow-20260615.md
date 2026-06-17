# 政治监测 Cron 工作流（2026-06 实测）

## 验证有效的 cron 数据源

### 新浪财经政经 API（主力源）

```python
import urllib.request, ssl
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
    content = r.read().decode('gbk', errors='ignore')
    d = eval(content.replace('false', 'False').replace('true', 'True').replace('null', 'None'))
    items = d.get('result', {}).get('data', [])

# 过滤近3-5小时新闻
ts_now = datetime.now().timestamp()
recent = [i for i in items if ts_now - int(i.get('ctime', 0)) < 5 * 3600]
```

返回字段：`ctime`（Unix时间戳）, `title`, `url`, `intro`

## gov.cn 文章抓取（urllib直读可行）

gov.cn 的 `/yaowen/liebiao/` 列表页是静态HTML，文章列表由JS渲染，urllib直读只有导航壳。

**正确方式：先用Bing搜索定位gov.cn文章URL，再urllib直读正文**

```python
import urllib.request, urllib.parse, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Bing搜索定位gov.cn政策页
query = urllib.parse.quote("site:gov.cn 国务院 常务会议 2026年6月")
search_url = f"https://www.bing.com/search?q={query}&setlang=zh-CN&count=10"

# urllib直读gov.cn政策解读正文页
url = 'https://www.gov.cn/zhengce/202606/content_7071930.htm'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})
with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
    content = r.read().decode('utf-8', errors='ignore')

# 提取正文段落（过滤页脚噪声）
paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content, re.DOTALL)
text = '\n'.join([re.sub(r'<[^>]+>', '', p).strip() for p in paragraphs
                  if len(re.sub(r'<[^>]+>', '', p).strip()) > 30])
```

## 输出路径（必须与cron任务配置一致）

```
~/.hermes/political-reports/          # 每日推送存档
YYYY-MM-DD_P{优先级}_{标题关键词}.txt  # 文件命名格式
```

**与 SKILL.md 默认路径的差异**：SKILL.md写的是 `~/.hermes/army-workspace/political/`（旧路径），cron实际写入 `~/.hermes/political-reports/`。以实际路径为准。

## 本次扫描结果（2026-06-15 03:31）

- 新浪财经 lid=2517：近3小时仅3条，均为国际新闻（美联储Trump、俄乌、瑞士公投）
- gov.cn 要闻列表：静态HTML，无法提取文章
- 新华网RSS：返回2022旧数据，完全不可用
- 本期无新增P0-P1政策发布
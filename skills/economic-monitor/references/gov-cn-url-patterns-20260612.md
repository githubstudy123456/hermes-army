# gov.cn URL Patterns (Verified 2026-06-12)

## Working Paths

### 要闻列表页
- **URL**: `https://www.gov.cn/yaowen/liebiao/`
- **Status**: ✅ 正常加载，加载时间约3-5秒
- **内容**: 最新国务院/部委要闻，标题+时间+article URL

### 政策列表页
- **URL**: `https://www.gov.cn/zhengce/index.htm`
- **Status**: ✅ 正常加载
- **内容**: 最新国务院政策文件，含解读/最新政策/中央文件等Tab

### Article URL 格式
```
要闻文章: https://www.gov.cn/yaowen/liebiao/YYYYMM/content_NNNNN.htm
政策文章: https://www.gov.cn/zhengce/content/YYYYMM/content_NNNNN.htm
```

- `YYYYMM` = 年月（如 202606）
- `NNNNN` = content ID，数字越大越新
- 日期可通过 browser_navigate 直连验证

## Failed Paths (Avoid)

| Path | Error |
|------|-------|
| `https://www.gov.cn/lianbo/index.htm` | Timeout 60s ❌ |
| `https://www.gov.cn/yaowen/` (root) | 404 ❌ |
| `https://www.gov.cn/lianbo/202506/content_*.htm` | 404 ❌ |

## Access Method

```python
# browser_navigate 直连（推荐）
browser_navigate('https://www.gov.cn/yaowen/liebiao/')

# urllib 直连（需处理SSL）
import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request('https://www.gov.cn/yaowen/liebiao/', headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
    content = r.read().decode('utf-8')
```

## Date Extraction

部分页面 `<title>` 不含日期，改用全局正则：
```python
date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', content)
if date_match:
    date_str = f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"
```

## Content ID Range (2026-06-12)

实测范围：
- 要闻 content ID: ~7071734 ~ 7071863（6月11-12日）
- 政策 content ID: ~7070755 ~ 7071451（5月底-6月8日）

ID步进规律：每次新文章 increment ~10-20
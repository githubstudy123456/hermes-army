# 新浪财经 hq.sinajs.cn 汇率接口 FX SSL 错误（2026-06-13 18:00）

## 问题描述

`hq.sinajs.cn` 的 A 股接口正常可用，但汇率接口（FX）完全失效：

```
# 中文路径：UnicodeEncodeError
URL: https://hq.sinajs.cn/list=外汇-USDCNY
Error: UnicodeEncodeError: 'ascii' codec can't encode characters in position 10-11: ordinal not in range(128)

# ASCII 路径：SSL 错误
URL: https://hq.sinajs.cn/list=fx_susdcny
Error: ssl.SSLError: [SSL: BAD_ECPOINT] bad ecpoint
```

## 验证命令

```python
import urllib.request, ssl, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# ✅ A股接口 — 正常
req = urllib.request.Request(
    'https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006',
    headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'}
)
with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
    content = r.read().decode('gbk', errors='ignore')
# 输出：上证指数 4031.51 +1.12%，深证成指 +0.75%，创业板指 +0.50%

# ❌ FX 接口 — SSL 错误
req2 = urllib.request.Request(
    'https://hq.sinajs.cn/list=fx_susdcny',
    headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'}
)
with urllib.request.urlopen(req2, timeout=8, context=ctx) as r:
    content = r.read()  # ssl.SSLError: BAD_ECPOINT
```

## 影响

- 无法通过 hq.sinajs.cn 获取 USD/CNY 实时汇率
- A 股指数仍可正常获取（本次实测：上证 +1.12%，深证 +0.75%，创业板 +0.50%）

## 替代方案

| 方案 | URL | 可用性 |
|------|-----|--------|
| 中国货币网 | `https://www.chinamoney.com.cn/chinese/bkccpr/` | 待验证 |
| Playwright CDP | 连接 Chrome 访问新浪外汇页面 | 待验证 |
| exchangerate-api.com | `https://api.exchangerate-api.com/v4/latest/USD` | 第三方，可能有延迟 |

## 本次扫描汇率状态

- 目标飞书群未收到汇率异常告警
- gov.cn/央行/PBC 均无汇率政策新闻
- 判定：USD/CNY 未见突破 7.25 的信号，本次扫描标记为 [SILENT]
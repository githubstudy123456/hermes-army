# A股/港股 实时行情数据源（2026-06-16 实测）

## Sina hq.sinajs.cn — 指数数据

### 字段数因指数而异（关键发现）

同一 API 返回的字段数**不固定**，不同指数字段数不同：

| 指数 | 代码 | 字段数 | date 位置 | time 位置 |
|------|------|--------|-----------|-----------|
| 上证指数 | sh000001 | **34** | fields[30] | fields[31] |
| 深证成指 | sz399001 | **31** | fields[28] | fields[29] |
| 创业板指 | sz399006 | **29** | fields[26] | fields[27] |

通用解析方式：`n = len(fields); date=fields[n-4]; time=fields[n-3]`

### 指数 vs 股票 字段布局完全不同

**指数**（sh000001等）：f[1]=当前价, f[2]=昨收, f[3]=最高价, f[4]=最低价, f[9]=成交额(元)
**股票**（sh600519等）：f[1]=当前价, f[2]=涨跌额, f[3]=涨跌幅%, f[4]=最高, f[9]=成交额(元)

详见 `economic-monitor` skill 中的完整字段对照表。

### 正确解析示例

```python
import urllib.request, re, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://hq.sinajs.cn/list=sh000001,sz399001,sz399006'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://finance.sina.com.cn'
})
with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
    content = r.read().decode('gbk', errors='ignore')

indices = [('上证指数', 'sh000001'), ('深证成指', 'sz399001'), ('创业板指', 'sz399006')]
for name, code in indices:
    m = re.search(f'hq_str_{code}="([^"]+)"', content)
    f = m.group(1).split(',')
    n = len(f)
    current = float(f[1])
    prev_close = float(f[2])
    change_pct = (current - prev_close) / prev_close * 100
    amount_yi = float(f[9]) / 1e8
    print(f"{name}: {current:.2f} ({change_pct:+.2f}%) | 成交额 {amount_yi:.0f}亿元 | 时间 {f[n-4]} {f[n-3]}")
```

---

## Eastmoney push2 行业板块涨跌（实测 2026-06-16 可用）

**注意**：`economic-monitor` skill 记录 eastmoney push2 "完全失效"，但本session实测 `push2.eastmoney.com/api/qt/clist/get` 对**行业板块**返回正常数据。差异原因待进一步确认（可能某些 endpoint 失效但板块 endpoint 可用）。

### 实时板块涨跌排行

```
https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:90+t:2+f:!50&fields=f2,f3,f4,f12,f14,f20,f62
```

参数说明：
- `fid=f3` — 按涨跌幅排序
- `fs=m:90+t:2+f:!50` — 行业板块（非概念板块）
- `fields=f2,f3,f4,f12,f14,f20,f62` — 字段选择

返回字段：
| 字段 | 含义 | 示例 |
|------|------|------|
| f2 | 板块最新价/点位 | 1955.66 |
| f3 | **涨跌幅(%)** | 5.87 |
| f4 | 涨跌额 | 108.46 |
| f12 | 板块代码 | BK1623 |
| f14 | **板块名称** | 钼 |
| f20 | **成交额(元)** | 153766331000 |
| f62 | **北向资金净流入(元)** | -85072560.0 |

解析示例：
```python
import json, urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:90+t:2+f:!50&fields=f2,f3,f4,f12,f14,f20,f62'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://quote.eastmoney.com/'
})
with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
    data = json.loads(r.read())

for item in data['data']['diff']:
    if item['f3'] >= 3.0:  # 涨跌幅 >= 3%
        amount_yi = item['f20'] / 1e8
        north_yi = item['f62'] / 1e8 if item['f62'] else 0
        print(f"{item['f14']}: +{item['f3']:.2f}% (成交额{amount_yi:.0f}亿, 北向{north_yi:+.0f}亿)")
```

---

## 北向资金时效性（2026-06-16 实测）

东财/新浪沪深港通页面上：
- **北向资金**（沪股通+深股通）成交总额**仅收盘后更新**，盘中显示"-"
- **南向资金**（港股通）为实时数据

盘中无法获取北向实时净流向，只能：
1. 参考前一交易日季度持股数据（东财页面有"个股季度排行"）
2. 等待收盘后数据

---

## 南向资金（盘中可用，2026-06-16 实测）

港股通实时净买入数据在盘中即可获取：
- 沪股通（南向）：实时
- 深股通（南向）：实时
- 合计：盘中可见

东财页面路径：`https://data.eastmoney.com/hsgt/hsgtV2.html` → 页面文本中直接含"净买额"数字

# Sina hq.sinajs.cn 股票/指数字段差异（2026-06-16 实测）

## 核心发现

Sina `hq.sinajs.cn` 对股票和指数返回**完全不同的字段布局**，不能用同一套解析逻辑。

## 实测数据

### 股票 sh600519 贵州茅台
```
f[0]="贵州茅台"
f[1]="1292.700"    # 当前价
f[2]="1291.910"    # 涨跌额
f[3]="1271.100"    # 涨跌幅%（可直接用）
f[4]="1292.700"    # 最高价
f[5]="1270.100"    # 最低价
f[6]="1271.100"    # 今开
f[7]="1271.330"    # 昨收
f[8]="4158556"     # 成交量(手)
f[9]="5303656129"  # 成交额(元)
```

### 指数 sh000001 上证指数
```
f[0]="上证指数"
f[1]="4053.5822"   # 当前价/收盘价
f[2]="4031.5129"   # 昨收价 ← 注意：不是涨跌额！
f[3]="4096.4717"   # 最高价 ← 注意：不是涨跌幅！
f[4]="4097.1657"   # 最低价 ← 注意：不是最高价！
f[5]="4051.0651"   # ???
f[8]="678907811"   # 成交量(手)
f[9]="1403586231239" # 成交额(元)
```

## 关键区别

| 字段 | 股票 | 指数 |
|------|------|------|
| f[2] | 涨跌额 | 昨收价 |
| f[3] | 涨跌幅% ✅ | 最高价 ❌ |
| f[4] | 最高价 | 最低价 |

## 盘前数据特征（07:26 AM）

当前时间 07:26（开盘前），Sina API 返回的是**昨日收盘数据**：
- `f[3]` = 昨日最高价（不是今日）
- `f[4]` = 昨日最低价（不是今日）
- 数据时间戳字段（倒数第3-4个字段）= `15:30:39`（昨日收盘），非当前时间

**判断方法**：检查数据中时间戳，若显示 `15:30:39` 而非当前时间，说明数据已过时。

## 正确解析代码

```python
import urllib.request, re, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def parse_stock(f):
    """股票解析：f[2]=涨跌额, f[3]=涨跌幅%, f[4]=最高, f[5]=最低"""
    return {
        'current': float(f[1]),
        'change': float(f[2]),
        'pct': float(f[3]),
        'high': float(f[4]),
        'low': float(f[5]),
        'vol': float(f[8]),
        'amount': float(f[9]) / 1e8
    }

def parse_index(f):
    """指数解析：f[2]=昨收, f[3]=最高, f[4]=最低"""
    current = float(f[1])
    prev_close = float(f[2])
    return {
        'current': current,
        'prev_close': prev_close,
        'pct': (current - prev_close) / prev_close * 100,  # 必须自己计算
        'high': float(f[3]),
        'low': float(f[4]),
        'vol': float(f[8]),
        'amount': float(f[9]) / 1e8
    }

url = 'https://hq.sinajs.cn/list=sh600519,sh000001'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'})
with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
    content = r.read().decode('gbk', errors='ignore')

# 股票
m = re.search(r'hq_str_sh600519="([^"]+)"', content)
stock = parse_stock(m.group(1).split(','))
print(f"贵州茅台: {stock['current']} ({stock['pct']:+.2f}%)")

# 指数
m = re.search(r'hq_str_sh000001="([^"]+)"', content)
index = parse_index(m.group(1).split(','))
print(f"上证指数: {index['current']} ({index['pct']:+.2f}%)")
```
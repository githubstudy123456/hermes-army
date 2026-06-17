# 中国股票数据源参考手册

## A股实时行情 — 腾讯行情（最可靠）

```python
import urllib.request

def get_a_stock_quote(code):
    """code格式: 300750（6位数字，自动拼接sz前缀）"""
    url = f"https://qt.gtimg.cn/q=sz{code}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read().decode('gbk')
    fields = data.split('~')
    return {
        'code': fields[2],
        'name': fields[1],
        'price': fields[3],
        'change_pct': fields[32],    # 涨跌幅%
        'volume': fields[36],         # 成交量(股)
        'amount': fields[37],          # 成交额(万元)
        'market_cap_wan': fields[44], # 总市值(万元) → 除10000得亿元
        'pe': fields[39],
        'pb': fields[46],
        'high_52w': fields[41],
        'low_52w': fields[42],
    }

# 示例
r = get_a_stock_quote('300750')
market_cap_yi = float(r['market_cap_wan']) / 10000
```

**字段索引（77字段格式）：**

| 索引 | 字段名 | 说明 |
|------|--------|------|
| 1 | name | 股票名称 |
| 3 | price | 当前价格 |
| 4 | prev_close | 昨收 |
| 5 | open | 今开 |
| 31 | change | 涨跌额 |
| 32 | change_pct | 涨跌幅% |
| 33 | high | 最高 |
| 34 | low | 最低 |
| 36 | volume | 成交量(股) |
| 37 | amount | 成交额(万元) |
| 39 | pe | 市盈率(动) |
| 41 | high_52w | 52周最高 |
| 42 | low_52w | 52周最低 |
| 44 | market_cap | 总市值(万元) |
| 46 | pb | 市净率 |

## 港股实时行情 — 腾讯行情

**⚠️ 港股字段结构与A股77字段格式不同，不要套用A股映射表！**

```python
import urllib.request

def get_hk_stock_quote(code):
    """code格式: 03690（5位，不含HK前缀）"""
    url = f"https://qt.gtimg.cn/q=hk{code}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read().decode('gbk')  # GBK编码，不是UTF-8
    fields = data.split('"')[1].split('~')
    return {
        'name': fields[1],
        'price': float(fields[3]),        # 当前价（港元）
        'prev_close': float(fields[4]), # 昨收
        'open': float(fields[5]),       # 今开
        'volume': float(fields[6]),     # 成交量（股）
        'mktcap_hkd': float(fields[37]),  # 流通市值（港元）
        'pe': fields[43],              # 市盈率
        'high_52w': float(fields[48]), # 52周最高（港元）
        'low_52w': float(fields[49]),  # 52周最低（港元）
        'total_mktcap_hkd': float(fields[69]), # 总市值（港元）
    }

quote = get_hk_stock_quote('03690')
print(f"美团股价: {quote['price']} HKD")
print(f"流通市值: {quote['mktcap_hkd']/1e9:.2f} 亿HKD")
print(f"总市值: {quote['total_mktcap_hkd']/1e9:.2f} 亿HKD")
```

**港股字段索引（78字段格式）：**

| 索引 | 字段名 | 说明 |
|------|--------|------|
| 1 | name | 股票名称（含-W等投票权标识）|
| 3 | price | 当前价（港元）|
| 4 | prev_close | 昨收 |
| 5 | open | 今开 |
| 6 | volume | 成交量 |
| 37 | mktcap | 流通市值（港元），**不是万元** |
| 43 | pe | 市盈率（动） |
| 48 | high_52w | 52周最高（港元） |
| 49 | low_52w | 52周最低（港元） |
| 69 | total_mktcap | 总市值（港元） |

**⚠️ 重要注意：**
- 字段[44]和[46]在港股中显示异常值（如4627），**不是PB**，不要使用
- 字段[45]也不是PS比值
- 港股市值单位是港元（不是万元），直接除以10亿得「亿港元」
- 如果要用PB，需手动计算：总市值 / 净资产

## K线数据 — 腾讯K线API

```python
def get_kline(code, market='sz', period='day', count=320):
    """
    code: 股票代码如 300750
    market: sz/hk
    period: day/week/month/min5/min15/min30/min60
    """
    url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={market}{code},{period},,,{count},qfq"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read().decode('utf-8', errors='ignore')
    import json
    obj = json.loads(data[data.index('{'):])
    # 返回格式: [[日期, 开, 收, 高, 低, 量], ...]
    return obj['data'][f'{market}{code}']['qfqday']
```

## 历史行情（含除权）— 聚合数据

```python
def get_daily_history(code):
    """返回K线历史，含分红除权信息"""
    url = f"https://data.gtimg.cn/flashdata/hs/daily/{code}.js"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read().decode('utf-8', errors='ignore')
    # 格式: kline_dayhfq={...} 含 nd(年度), fh_sh(每股派息), djr(除权日), cqr(除权后第一个交易日)
    return data
```

## 东方财富 — 已失效接口（2026-05测试）

以下接口**全部返回 `{"success":false,"code":9501,"message":"报表配置不存在"}`**：

```
RPT_FINANCE_MAIN_INDEX           # 主要财务指标
RPT_FINANCE_PROFIT_STATEMENT    # 利润表
RPT_FINANCE_PROFIT_SHEET        # 利润表(另一名称)
RPT_LICO_FN_CPD                  # 财务数据(REPORT_DATE字段不存在)
datacenter.eastmoney.com/securities/api/data/v1/get  # 通用财务API
```

东方财富股票页面 `eastmoney.com/s/{code}.html` 返回 **404**。

**错误码含义：**
- `9501 "报表配置不存在"` — 接口名称已变更或停用
- `9501 "REPORT_DATE返回字段不存在"` — 接口字段配置错误

## 东方财富 — 可能仍可用的接口

```python
# 龙虎榜详情页（需登录后访问）
https://data.eastmoney.com/stock/lhb.html

# 行情中心（可用）
https://quote.eastmoney.com/center/

# 公告大全（可用，需翻页）
https://data.eastmoney.com/notices/
```

## 新浪财经

```python
# 股票行情页（可用）
url = f"https://finance.sina.com.cn/realstock/company/sz{code}/nc.shtml"
# 返回行情数据，需解析HTML
```

## 数据降级采集策略

当实时行情API失效时：

1. **腾讯行情** `qt.gtimg.cn` — 最优先，字段最全
2. **聚合数据K线** `data.gtimg.cn/flashdata/hs/daily/{code}.js` — 历史数据含除权
3. **新浪财经行情页** — 解析HTML
4. **`delegate_task` 并行web搜索** — 获取财务数据+新闻
5. **公司IR官网** — 可能被Bot检测拦截，用 `browser_navigate` 尝试

## 新闻和动态采集

优先使用 `delegate_task` 并行web搜索：
- 搜索近3个月重要事件
- 搜索最新财报数据（营收、净利润、EPS、ROE、毛利率）
- 搜索券商研报评级和目标价

关键词模板：
```
{公司名} {股票代码} 近3个月 重要动态
{公司名} {股票代码} 2025年年报 财务数据
{公司名} 券商评级 目标价 研报
```

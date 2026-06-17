# 中国宏观经济数据源实测记录（2026-06-10）

## A股实时行情 — 验证可用

**新浪财经 hq.sinajs.cn（GBK编码）**

```
# 同时获取多个指数
URL: https://hq.sinajs.cn/list=s_sh000001,s_sh000300,s_sz399001
返回: var hq_str_s_sh000001="上证指数,4007.3161,-2.7146,-0.07,...";
解析: 逗号分隔，字段1=当前价，字段2=涨跌额，字段3=涨跌幅%
```

**腾讯证券 qt.gtimg.cn（GBK编码）**

```
URL: https://qt.gtimg.cn/q=sh000001,sz399001,sz399006,sh000300
返回: v_sh000001="1~上证指数~000001~4007.32~4010.03~...~...~...~...~...~...~...~涨跌幅%~涨跌额"
解析: ~分隔，字段3=当前价，字段4=昨收，字段31=涨跌幅%，字段32=涨跌额
```

## 人民币汇率 — 验证可用

```
URL: https://hq.sinajs.cn/list=fx_susdcny
返回: var hq_str_fx_susdcny="03:00:01,6.7733000000,6.7772000000,6.7734000000,..."
解析: 字段1=买一价，字段2=卖一价，字段3=基准汇率，字段7=当前价，字段-1=日期
今日实测: USD/CNY在岸 = 6.7733
```

## 新浪财经政经快讯 — 验证可用（2026-06-10 08:58实测）

```
URL: https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&k=&num=20&page=1
Header: Referer=https://finance.sina.com.cn
解码: GBK
返回: {'result': {'data': [{'ctime': '1781052490', 'title': '...', 'url': '...'}, ...]}}

# 过滤最近5小时新闻
import time
ts_now = time.time()
recent = [i for i in items if ts_now - int(i['ctime']) < 5*3600]
```

lid含义：
- 2516 = 新浪财经头条
- 2517 = 国内财经/政经新闻

## 36kr RSS — 验证可用

```
URL: https://36kr.com/feed
解码: UTF-8
返回: 30条当日新闻，最新时间 08:08（本次session 08:58测试）
标题示例: "8点1氪丨致3人永久失明，膳魔师紧急召回..."
          "现货黄金失守4200美元，创近3个月新低"
          "两市融资余额增加36.37亿元"
```

## 新华网政治RSS — 失效（2022年数据）

```
URL: http://www.xinhuanet.com/politics/news_politics.xml
问题: 300条全部为2022年12月新冠疫情防控内容，停止使用
替代: 新浪财经 lid=2517 + 36kr RSS
```

## 美联储RSS — 未测试（本session无相关触发）

已知可用（来自skill文档）：
- `https://www.federalreserve.gov/feeds/press_all.xml`
- `https://www.federalreserve.gov/feeds/fomc.xml`

## 数据质量总结

| 来源 | 状态 | 说明 |
|------|------|------|
| hq.sinajs.cn A股 | ✅ 可用 | GBK编码，实时 |
| hq.sinajs.cn 汇率 | ✅ 可用 | GBK编码，实时 |
| 新浪财经政经API | ✅ 可用 | 5小时内新闻过滤 |
| 36kr RSS | ✅ 可用 | UTF-8，当日新闻 |
| 新华网政治RSS | ❌ 失效 | 2022年旧数据 |
| 腾讯证券 | ✅ 可用 | GBK编码，备用 |
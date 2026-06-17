# 三星电子 (Samsung Electronics) 研究数据源备忘

> 本次调研（2026-06-15）收集的数据和发现，供下次调研三星时参考。

## 实时行情

| 来源 | 状态 | 备注 |
|------|------|------|
| Yahoo Finance RSS `005930.KS` | ✅ 可用 | 返回新闻列表，含当前价₩322,500（2026-06-14） |
| Yahoo Finance Chart API (`005930.KS`) | ❌ 429 Too Many Requests | 限速严重 |
| 腾讯/新浪港股接口 | ❌ 不支持韩股 | 代码映射不同 |
| Naver Finance | ⚠️ 可访问但结构复杂 | 需EUC-KR解码 |

**关键发现**：Yahoo Finance RSS新闻描述中包含实时价格，例如：
```
stock trading around ₩322,500. Over the past month the share price is up 19.2%, and year to date the stock...
```

## Q1 2026 财报数据（初步）

- 营收：约 ₩119.5万亿韩元（约~870亿美元）
- 净利润：约 ₩7.6万亿韩元（约~55亿美元）
- 注：数据来源于Yahoo Finance RSS新闻 + Bing中文搜索交叉验证，正式数字以三星官方IR公告为准

## 近期新闻来源（已验证）

| 日期 | 来源 | 事件 |
|------|------|------|
| 2026-06-14 | Yahoo Finance/Motley Fool | HBM4E 12层样品出货 |
| 2026-06-11 | The Information/Yahoo Finance | Google探索三星2nm代工 |
| 2026-06-11 | Yahoo Finance | 三星-Synopsys/Cadence 2nm/3D-IC合作 |
| 2026-06-11 | Yonhap/InvestorsHub | OpenAI Sam Altman访韩 |
| 2026-06-12 | Yahoo Finance/Chosun Ilbo | 韩国卡车司机罢工威胁芯片厂建设 |
| 2026-06-12 | Barclays/Bloomberg via Yahoo Finance | 银行收紧对冲基金内存股头寸 |

## 全球大公司候选池补充

- 三星电子：005930.KS（KOSE，韩股）+ SMSN.IL（伦敦GDR）
- 市值参考：~$1.26T（2026-06附近）
- 52周高点：约₩580,000（2025年）
- 当前价：₩322,500（2026-06-14）

## 快速数据采集降级路径（韩股专用）

1. **Yahoo Finance RSS** → `https://feeds.finance.yahoo.com/rss/2.0/headline?s={KS_CODE}&region=US&lang=en-US`
2. **中文Bing搜索** → `site:cn.bing.com "三星电子" + 具体财务指标`
3. **Samsung IR官网** → `https://www.samsung.com/sec/en/ir/ir-fr-news/`（需浏览器，加载慢）
4. **KOREAN NEWS API** → 若上述均失效，尝试韩国金融新闻聚合API

## 搜索关键词备忘

- 三星电子Q1财报：`三星电子 2026年第一季度报告 销售额 5.94兆公金`
- 三星电子新闻（中文）：`site:cn.bing.com 三星电子 2026`
- 三星电子新闻（英文）：`site:finance.yahoo.com Samsung Electronics 005930`

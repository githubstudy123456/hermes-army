# 全球市值排名前50 — 2026年6月实测

> 来源：companiesmarketcap.com/?page=top100 抓取（2026-06-08）
> 用途：补充 `daily-company-research` 第二批候选池；去重后按市值从高到低排列

## 全部已调研公司（第一批，共12家，需排除）

海底捞、九毛九、百胜中国、小米、阿里、腾讯、美团、比亚迪、药明康德、恒瑞医药、百济神州/BeOne、宁德时代

## 未调研大公司（按市值排名）

| 排名 | 公司名 | 代码 | 市值 | 交易所 | 板块 |
|------|------|------|------|--------|------|
| 1 | Alphabet (Google) | GOOGL.O | $4.46T | 纳斯达克 | 科技 |
| 2 | Meta Platforms | META.O | $1.51T | 纳斯达克 | 科技 |
| 3 | Samsung Electronics | 005930.KS / SMSN.IL | $1.26T | 韩国KOSE | 科技/半导体 |
| 4 | Berkshire Hathaway | BRK.B.N | $1.05T | 纽约证交所 | 金融 |
| 5 | Eli Lilly | LLY.N | $1.01T | 纽约证交所 | 医药 |
| 6 | Walmart | WMT.N | $946B | 纽约证交所 | 消费 |
| 7 | JPMorgan Chase | JPM.N | $837B | 纽约证交所 | 金融 |
| 8 | Micron Technology | MU.O | $974B | 纳斯达克 | 科技/半导体 |
| 9 | SK Hynix | 000660.KS | $881B | 韩国KOSE | 科技/半导体 |
| 10 | AMD | AMD.O | $760B | 纳斯达克 | 科技/半导体 |
| 11 | ASML | ASML.AS / ASML.O | $633B | 阿姆斯特丹/纳斯达克 | 科技/半导体设备 |
| 12 | Exxon Mobil | XOM.N | $621B | 纽约证交所 | 能源 |
| 13 | Visa | V.N | $615B | 纽约证交所 | 金融 |
| 14 | Oracle | ORCL.N | $615B | 纽约证交所 | 科技 |
| 15 | Johnson & Johnson | JNJ.N | $560B | 纽约证交所 | 医药 |
| 16 | Intel | INTC.O | $498B | 纳斯达克 | 科技/半导体 |
| 17 | Cisco | CSCO.O | $479B | 纳斯达克 | 科技 |
| 18 | Mastercard | MA.N | $434B | 纽约证交所 | 金融 |
| 19 | Costco | COST.O | $431B | 纳斯达克 | 消费 |
| 20 | Caterpillar | CAT.N | $417B | 纽约证交所 | 工业 |
| 21 | AbbVie | ABBV.N | $401B | 纽约证交所 | 医药 |
| 22 | Bank of America | BAC.N | $382B | 纽约证交所 | 金融 |
| 23 | Lam Research | LRCX.O | $379B | 纳斯达克 | 科技/半导体设备 |
| 24 | Chevron | CVX.N | $373B | 纽约证交所 | 能源 |
| 25 | Arm Holdings | ARM.O | $366B | 纳斯达克 | 科技/半导体 |
| 26 | UnitedHealth | UNH.N | $363B | 纽约证交所 | 医疗 |
| 27 | Netflix | NFLX.O | $346B | 纳斯达克 | 科技/内容 |
| 28 | General Electric | GE.N | $343B | 纽约证交所 | 工业 |
| 29 | Coca-Cola | KO.N | $342B | 纽约证交所 | 消费 |
| 30 | IBM | IBM.N | ~$410B | 纽约证交所 | 科技 |
| — | 中国建设银行 | 601939.SH / 0939.HK | ~$230B | A股/港股 | 金融 |
| — | 中国银行 | 601988.SH / 3988.HK | ~$220B | A股/港股 | 金融 |
| — | 中国平安 | 601318.SH / 2318.HK | ~$120B | A股/港股 | 金融 |
| — | 中国石油 | 601857.SH / 0857.HK | ~$250B | A股/港股 | 能源 |
| — | 中国移动 | 600941.SH / 0941.HK | ~$170B | A股/港股 | 科技/通信 |
| — |丰田汽车 | 7203.T / TM.N | ~$450B | 东京/纽交所 | 消费/新能源车 |
| — | 本田汽车 | 7267.T / HMC.N | ~$130B | 东京/纽交所 | 消费/新能源车 |
| — | 中芯国际 | 688981.SH / 0981.HK | ~$150B | A股/港股 | 科技/半导体 |
| — | 创科实业 | 00669.HK | ~$100B | 港股 | 消费/工具 |
| — | Naver | 035420.KS | ~$70B | 韩国KOSE | 科技/互联网 |

## 已调研过的美股（第一批不涉及，记录备查）

NVIDIA、Apple、Microsoft、Amazon、TSMC、Broadcom、Saudi Aramco、Tesla — 均属第一批之外，如需扩池可加入。

## 抓取脚本（备用）

```python
import urllib.request, re
url = 'https://companiesmarketcap.com/?page=top100'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=20).read().decode('utf-8')
names = re.findall(r'<div class="company-name">([^<]+)</div>', html)
mcaps = re.findall(r'data-sort="(\d+)"[^>]*><span class="currency-symbol-left">\$</span>([^<]+)</td>', html)
# 配合每行tr中的flag emoji判断国家
rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
# 输出前50
for i, (name, mcap) in enumerate(zip(names[:50], mcaps[:50])):
    print(f"{i+1} {name} ${mcap}")
```
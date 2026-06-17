# 政治监测核心数据源

## 新华社政治RSS
**URL**: `http://www.xinhuanet.com/politics/news_politics.xml`
**状态**: ❌ **已停止更新（2026-06实测：返回300条但全部是2022年12月旧数据）**
**不要再使用此RSS获取实时政治新闻**，改用 gov.cn 首页 browser_navigate 快照法（见SKILL.md正文）

## 中央文件页
**URL**: `https://www.news.cn/politics/zywj/index.htm`
**状态**: ✅ 稳定
**内容**: 中共中央办公厅、国务院办公厅文件列表（按时间倒序）

## 新华网时政首页
**URL**: `http://www.xinhuanet.com/politics/`
**状态**: ✅ 稳定
**内容**: 时政联播、高层、学习进行时等栏目

## 领导活动报道
**URL**: `https://www.news.cn/politics/leaders/`
**状态**: ✅ 稳定
**内容**: 政治局常委简历信息（一般不是新闻源）

## 人民日报电子版
**URL**: `http://paper.people.com.cn/rmrb/html/YYYY-MM/DD/node_1.htm`
**状态**: ⚠️ 需验证（当前404）
**注意**: 日期格式是月/日（如06/10），不是标准日期

## 搜索关键词过滤

政治触发词（出现在标题则记录）：
```
政治局, 国务院, 中央经济工作, 习近平, 国办发, 国发, 
中共中央, 全国两会, 住建部, 央行, 发改委, 房地产, 货币政策
```

## 新浪财经政经 API（2026-06 验证稳定，替代失效的新华社 RSS）✅

**重要限制（2026-06实测）**：lid=2517 在清晨至上午时段（00:00–08:00北京时间）几乎100%为美股/国际财经新闻（美伊冲突、美国通胀、SpaceX IPO、高盛AI风险、亚马逊货运业务等），连续多天实测0条国内政策。**国内政策以 gov.cn 三通道 browser_navigate 快照为准，Sina lid=2517 仅在市场时段（09:00–16:00北京时间）有一定参考价值（降准降息信号、房地产政策动向等宏观信号），其余时间可直接跳过。**

**URL**: `https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&num=20&page=1`
**状态**: ✅ 稳定，返回最近4-5小时政经新闻
**用途**: 补充扫描降准/降息/房地产政策/部委重要表态等经济政策信号
**编码**: gbk（`decode('gbk', errors='ignore')`），JSON需Python格式转换

```python
import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&k=&num=20&page=1'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://finance.sina.com.cn'})
with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
    content = r.read().decode('gbk', errors='ignore')
    d = eval(content.replace('false', 'False').replace('true', 'True').replace('null', 'None'))
items = d.get('result', {}).get('data', [])
```

⚠️ 不适合纯政治新闻（习近平外事活动等），政治新闻以 gov.cn 为准

## 36kr RSS — 科技新闻补充 ⚠️

**URL**: `https://36kr.com/feed`
**状态**: ⚠️ 稳定可访问，但**最近5小时经常无新条目**（2026-06-10 实测：30条总量，但最近5小时0条）
**用途**: 科技政策信号补充（非政治监测主力）
**注意**: 不要依赖36kr作为政治监测的主要来源，它更适合科技商业新闻

## 人民網（people.com.cn）
**URL**: `https://www.people.com.cn/`
**状态**: ⚠️ urllib 直读成功，但提取 yaowen 链接返回 **0 条**
**不要依赖 urllib 从 people.com.cn 提取新闻链接**，改用 gov.cn browser_snapshot

## 飞书推送目标
群ID: `oc_c6883cd907e4d226736d87ce9c6c6d79`
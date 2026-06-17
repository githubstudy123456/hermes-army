---
name: city-event-push
description: "监控城市活动信息（豆瓣同城、活动行等）并定时推送到飞书群。适用于周末活动、假期活动、演出展览、社交聚会等本地生活资讯推送场景。"
version: 1.0.0
license: MIT
metadata:
  hermes:
    tags: [cron, feishu, 活动, 城市生活, 推送]
prerequisites:
  # 无需指定技能；agent 自带 browser/terminal/web_search 工具即可完成搜索
  skills: []
---

# 城市活动推送

创建定时搜索城市活动信息并推送到飞书群的任务。

## 触发条件

用户要求创建城市活动定时推送任务时使用，包括：
- "找某城市的活动"、"推送某地周末活动"
- "每天/每周/每几天"推送"某城市的活动"

## 步骤

1. 确定目标城市和活动类型（社交/展览/音乐/市集/运动/戏剧等）
2. 确定推送频率（每周五上午10点是常见最优时间，覆盖周末）
3. 确定目标飞书群（每日订阅群是 oc_c6883cd907e4d226736d87ce9c6c6d79）
4. 创建cron任务，用web搜索多组关键词

## 搜索关键词分组

### 实测最有效的关键词（2026年5月·深圳）

**假期/节日活动首选搜索公式：**
```
{城市} + {假期名称} + 假期/假日 + {年份} + 活动 + 推贴/地点/汇总/全部
```

示例：
- `深圳 五一 假期 2026 活动 推贴 地点` — 返回12,800结果，含10区活动汇总 ✅
- `深圳 五一 假日 2026 活动 推贴 地点` ✅
- `深圳 2026年5月 活动 全部` ✅

**按类型并行搜索（备选/补充）：**
- 社交类：{城市} 社交活动 桌游 沙龙 聚会 联谊
- 展览类：{城市} 展览 艺术展 插画展 摄影展 科技展 漫展
- 音乐/live：{城市} 音乐 live 乐队 演唱会 音乐节
- 创意市集：{城市} 创意市集 文创市集 周末市集
- 运动/户外：{城市} 运动 徒步 骑行 飞盘 羽毛球
- 假期/节日类：{城市} {节日} 活动 2026年{月份}

## 豆瓣分类页面URL模板

```
https://www.douban.com/location/{城市}/events/week-{类型}
```

深圳示例：`https://www.douban.com/location/shenzhen/events/week-exhibition`

常见类型值：all, music, comedy, drama, salon, party, film, exhibition, sports, travel, competition, course, kids
聚会子分类（派对/交友/市集等）：1401生活, 1402集市（常为空）, 1403摄影, 1404外语, 1405桌游, 1406夜店, 1407交友, 1408美食, 1409派对

**注意**：集市子分类(1402)经常为空，活动稀疏时直接显示"暂时没有符合条件的活动"，遇到这种情况改查 `week-all`（全部）或 `week-party`（聚会全部）作为补充。

## Cron任务模板

必须包含：名称、时间、地点、票价、来源链接

## 输出格式

**推荐格式（一眼可看型）：**
- 分类清晰，每类用 emoji 开头
- 每条活动写一行：**活动名称 | 时间 | 地点 | 票价**
- 不写数据来源、不写"信息来源"、不写"via xxx"
- 总字数控制在 500 字以内
- 不发文件，一次性发群里

示例：
```
🎵 演唱会 / Live
• 凤凰传奇演唱会 | 至5月4日 | 大运中心 | 380元起
• Taylor Swift 霉霉专场 | 5月1日 | 深圳MAO Livehouse | 108元起

🔥 火秀 / 无人机表演
• 欢乐谷无人机天幕大秀 | 每晚20:40 | 南山欢乐谷 | 夜场180元

☕ 创意市集 / 咖啡节
• 第七届唤醒咖啡节 | 4/29-5/5 | 福田区OneAvenue卓悦中心 | 免费入场
```

## 推荐搜索策略

### 实测优先级（2026年5月·深圳验证）

| 来源 | 可靠性 | 说明 |
|------|--------|------|
| **豆瓣同城（直接浏览器访问）** | ⭐⭐⭐⭐⭐ | 直接 `browser_navigate` 分类页有效，各类型活动数据完整，需登录但不影响浏览 |
| **票牛网 piaoniu.com（浏览器）** | ⭐⭐⭐⭐ | JS渲染页面，StealthyFetcher 抓取，覆盖演唱会/话剧/展览/体育 |
| **Bing + m.bendibao.com（手机版）** | ⭐⭐⭐ | 手机版可访问，但SSL连接不稳定 |
| Bing + news.qq.com 详情页 | ⭐⭐ | 搜索结果不直接含活动信息，需二次跳转，效果有限 |
| 活动行 huodongxing.com | ❌ | IP被封禁 |
| 深圳本地宝 sz.bendibao.com（桌面版） | ❌ | SSL握手超时，无法访问 |
| 站酷 zcool.com.cn | ❌ | 404 |
| 知乎 zhihu.com | ❌ | 仅问答，无活动信息 |

### 核心搜索路径（豆瓣直接浏览法 — 2026年5月实测）

1. 用 `browser_navigate` 直接访问豆瓣同城分类页，无需登录即可浏览：
   ```
   https://www.douban.com/location/{城市}/events/week-{类型}
   ```
   示例：`https://www.douban.com/location/shenzhen/events/week-music`

2. 常用类型值：all, music, comedy, drama, salon, party, film, exhibition, sports, competition, course, kids

3. 在页面用 `browser_snapshot` 提取活动数据（名称/时间/地点/票价四要素）

4. 多个类型（music/drama/exhibition/competition/all）并发浏览，汇总去重

### 搜索关键词公式

```
# 假期/节日活动（效果最好）
{城市} + {假期名称} + 假期/假日 + {年份} + 活动 + 推贴/地点/汇总

# 示例结果（2026年5月实测）
"深圳+五一+假期+2026+活动+推贴+地点" → 16,200结果，含10区活动汇总 ✅
```

### 失效来源（勿用）
- 活动行 huodongxing.com — IP被封禁
- 深圳本地宝桌面版 sz.bendibao.com — SSL超时
- 站酷 zcool.com.cn — 404

## 网络连通性检查（2026年5月实测）

这个服务器（81.71.93.113）**直连国际网络正常**，Bing/Google 均可访问，不需要代理。
```bash
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
curl -s --connect-timeout 5 -o /dev/null -w "%{http_code}" https://cn.bing.com
# 返回 200 = 直连正常
```
先确认直连是否通，再决定是否需要配置代理。

**实测结论（2026年5月）：**
- 豆瓣 `douban.com` — 直接 browser_navigate 正常 ✅（分类页各类型活动数据完整）
- Bing中文搜索 `cn.bing.com` 直连正常，但搜索结果不含活动信息 ⚠️
- 腾讯新闻 `news.qq.com` 直连正常 ✅（但内容来自Bing搜索，无活动数据）❌ 实际无活动数据
- 深圳本地宝 `sz.bendibao.com` — SSL错误 ❌
- 活动行 `huodongxing.com` — IP被封禁 ❌
- 知乎 `zhihu.com` — 仅返回问答，非活动信息 ❌
- **票牛网 `piaoniu.com` — 需浏览器访问，StealthyFetcher 正常 ✅**
- **今日头条搜索 `so.toutiao.com` — 直接返回搜索结果，有效 ✅**

## 补充数据源：票牛网（实测最稳定）

票牛网 `piaoniu.com` 是 JS 渲染页面，需浏览器自动化抓取。数据覆盖演唱会/音乐会/话剧/展览/体育等分类，对深圳/上海/北京等大城市活动丰富。

**脚本模板（Python + StealthyFetcher）：**
```python
import subprocess, sys
sys.path.insert(0, '/home/ubuntu/.hermes/scripts')
from stealthyfetcher import StealthyFetcher

fetcher = StealthyFetcher(headless=True, browser_type='chromium',
                          timeout=30000,
                          executable_path='/usr/bin/google-chrome')

url = 'https://www.piaoniu.com/sz-all'  # 深圳站
fetcher.navigate(url)
fetcher.wait_for_load_state('networkidle', timeout=15)
text = fetcher.inner_text('body')

import re
# 票牛活动在 <li data-index> 或类似结构中
items = re.findall(r'data-index="(\d+)">(.*?)</li>', text, re.DOTALL)
# 解析标题（活动名在特定标签内）
titles = re.findall(r'alt="([^"]+)"', text)
# 输出 markdown 格式
print("# 🏙 深圳近期活动")
# 分类整理后输出...
```

**注意：** Chrome 启动耗时约 5-10 秒，脚本里加 `time.sleep(3)` 等页面稳定。并发抓取多个城市时需注意内存。

## 补充：内容源扩展（视频/综合选题场景）

当任务是搜索"视频选题"或"综合热门话题"时，额外可用以下来源：

### B站热榜 API（可靠）
```
https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all
```
返回B站全站排行榜 JSON，用 `execute_code` 解析（禁止 `curl | python3` — 安全扫描会阻止管道到解释器）。示例：
```python
import subprocess, json
r = subprocess.run(['curl','-sL','https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all','-H','User-Agent: Mozilla/5.0'],capture_output=True,text=True,timeout=10)
d = json.loads(r.stdout)
for i in d['data']['list'][:10]:
    print(f"{i['title']} - {i['owner']['name']} (播放:{i['stat']['view']})")
```

### 百度实时热搜（浏览器）
```
https://top.baidu.com/board?tab=realtime
```
用 `browser_navigate` 访问，可直接抓取实时热搜标题+简介，适合综合话题发现。

### 已验证失效的来源
- 微博热搜 API (`weibo.com/ajax/side/hotSearch`) — 需要登录，返回 Forbidden
- 知乎热榜 API — 返回"请求参数异常"，需要客户端 cookie
- 抖音搜索 API — 返回空数据

**安全提醒：禁止用 `curl | python3` 管道** — 会触发 `tirith:curl_pipe_shell` 安全扫描，命令会被拒绝。用 `subprocess.run()` 或 `execute_code` 代替。

## 故障排查：Cron任务返回[SILENT]或内容为空

1. 检查 cron output 是否有新的 .md 文件（`ls ~/.hermes/cron/output/{job_id}/`）
2. **最常见原因：skills 参数填写了 `["web", "search"]`** ——这是工具集名而非技能名，会导致任务以无工具状态运行，必须清空 skills 数组 `skills: []`
3. 确认直连网络正常：
   ```bash
   unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
   curl -s --connect-timeout 5 -o /dev/null -w "%{http_code}" https://cn.bing.com
   # 返回 200 = 直连正常
   ```
4. **豆瓣同城现已验证可用** — 直接 browser_navigate 各分类页（week-music/week-drama/week-exhibition/week-all 等）即可获取完整活动数据，无需通过 Bing 中转
5. 手动 `browser_navigate "https://cn.bing.com/search?q=深圳+五一+假期+2026+活动+推贴+地点"` 测试搜索是否有效
6. 验证高价值链接：`news.qq.com` 和 `m.bendibao.com`（手机版）是可靠的详情页来源

## 注意事项

- 飞书群ID要确认清楚（每日订阅群是 oc_c6883cd907e4d226736d87ce9c6c6d79）
- Cron任务后台执行，看输出去 ~/.hermes/cron/output/{job_id}/
- **不要在 cron 任务配置里填写 `skills` 参数**——"web"和"search"是工具集名，不是技能名，填写会导致任务以无工具状态运行，返回 [SILENT]。让 agent 使用自带默认工具（browser/terminal）搜索即可。
- 豆瓣页面有反爬，curl可能拿不到数据，delegate_task并发搜索更稳定

## 验证

1. Cron任务创建后，立即手动run一次测试
2. 检查 ~/.hermes/cron/output/{job_id}/ 是否有输出文件
3. 确认飞书群收到消息，内容格式正确
4. 确认活动时间、地点、票价、链接四要素齐全

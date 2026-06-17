# 深圳活动抓取技术细节

## 2026-06-07 实测更新

### 数据源实测结果（2026-06-07更新）

| 来源 | 状态 | 说明 |
|------|------|------|
| **豆瓣同城深圳** | ✅ 正常 | `browser_navigate` 可用，URL格式为 `/location/shenzhen/events/week-{type}` |
| **票牛网 piaoniu.com** | ⚠️ 数据少 | StealthyFetcher可抓，演唱会数据偏少（2026-06实测仅4条） |
| **大麦网 damai.cn** | ❌ 超时 | SSL握手超时，浏览器也无法加载 |
| **猫眼演出** | ⚠️ 需浏览器 | `maoyan.com`可访问但活动列表需JS渲染 |
| **Bing搜索** |❌ 无结果 | 服务器环境下JS渲染内容无法提取 |
| **百度搜索** | ❌ 验证拦 | 服务器环境无法绕过验证码 |
| **深圳政府 sz.gov.cn** | ⚠️ 政务 | 只有政策公告，无文体活动 |

> ⚠️ **豆瓣同城 `browser_navigate` vs `curl`：curl 获取不到数据（JS渲染），必须用 `browser_navigate` + `browser_snapshot(full=true)` 逐页抓取。**

### 主力脚本：~/.hermes/scripts/shenzhen-events.py

```python
from scrapling.fetchers import StealthyFetcher

fetcher = StealthyFetcher()
page = fetcher.fetch(
    "https://www.piaoniu.com/sz-all",
    headless=True,
    executable_path='/usr/bin/google-chrome',
    browser_type='chromium',
    timeout=30000
)
# 解析标题正则：title="[深圳]活动名"
pattern = r'title="\[深圳\]([^"]+)"'
events = re.findall(pattern, page.body.decode('utf-8', errors='ignore'))
```

### 豆瓣同城分类URL（2026-06实测可用）

```
/location/shenzhen/events/week-all        # 全部
/location/shenzhen/events/week-music     # 音乐（包含演唱会/小型现场/音乐会）
/location/shenzhen/events/week-drama     # 戏剧
/location/shenzhen/events/week-comedy    # 喜剧/脱口秀
/location/shenzhen/events/week-exhibition # 展览
/location/shenzhen/events/week-sports    # 运动
/location/shenzhen/events/week-1003     # 演唱会（音乐子分类）
/location/shenzhen/events/selling        # 购票直通车（近期热卖）
```

### 浏览器抓取流程（实测有效）

```python
# 1. 进入分类页
browser_navigate("https://www.douban.com/location/shenzhen/events/week-music")

# 2. 初始快照（只能看到前几条）
browser_snapshot()

# 3. 向下滚动加载更多内容
browser_scroll(direction="down")

# 4. 必须用 full=true 获取完整内容（处理 truncation）
browser_snapshot(full=True)
# 页面底部出现 "...293 more lines truncated" → 用 full=True展开
```

### 演唱会/热卖演出补充

豆瓣同城演唱会分类（week-1003）数据少，但 `selling` 购票直通车页面汇集近期热卖演出，是补充演唱会信息的好来源：

```
https://www.douban.com/location/shenzhen/events/selling
```

实测在 selling 页面底部购票直通车内发现的近期演唱会：
- 陈慧娴40周年"Fabulous 40"巡回演唱会 深圳站（6/27）
- 动力火车"一路向前"巡回演唱会 深圳站（7/4）
- 汪峰《相信未来》巡回演唱会 深圳站（7/11）
- 新中式舞蹈秀《叹春风》（7/9~7/10）

### 关键发现

1. **browser_scroll + browser_snapshot(full=True)** 是抓全活动的必备组合，只用 browser_snapshot 会被截断
2. **selling 页面**是补充大型演唱会的最佳来源，比 week-1003 更全
3. **week-competition（赛事）**深圳永远返回空 → 体育赛事在 week-sports 下找
4. **购票直通车**区块在 week-all 底部也会出现，是热卖演出广告，非用户发起活动
5. **票牛网数据少**（2026-06实测仅4条），豆瓣 + selling 页面组合更全
6. **urllib/curl 无法抓到豆瓣数据** — JS渲染内容，curl拿到的是空壳，必须用 browser_navigate

### 关键发现

1. **票牛网数据量少** — 演唱会3-4条，其他类型更少（2026-06-07实测）
2. **豆瓣同城URL已失效** — `douban.com/location/shenzhen/` 全部404
3. **大麦/猫眼** — 可访问但需Playwright，适合手动补数据
4. **Bing搜索** — 服务器环境无法JS渲染，结果页为空
5. **深圳政府网** — 只有政务通知，无文体活动

### 深圳政府站（政务通知参考）

```
通知公告页：https://www.sz.gov.cn/cn/xxgk/zfxxgj/tzgg/
第2页：https://www.sz.gov.cn/cn/xxgk/zfxxgj/tzgg/index_2.html
```

内容是政策公告（补贴/采购/招聘），非文化活动。但可获取政府最新政策动向。

### 已知问题

1. **票牛网数据量偏少** — 建议补其他来源（演出类可补大麦/猫眼）
2. **urllib直连全部失效** — 放弃 urllib 方式，统一用 StealthyFetcher
3. **浏览器超时** — timeout=30000 足够，超时则重试一次

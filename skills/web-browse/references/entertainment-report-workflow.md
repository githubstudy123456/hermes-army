# 文娱月报数据源工作流

> 2026-06-16 实测有效的数据源与踩坑记录

## 核心推荐数据源（按优先级）

### 1. 微博热搜 `bb-browser site weibo/hot --json`
**用途**：实时热搜 + 分类标签（电影/体育/综艺/音乐/剧集/游戏/动漫/艺人）

实测返回 30 条，含 `category` 字段，过滤文娱相关：
```python
import subprocess, json
result = subprocess.run(['bb-browser', 'site', 'weibo/hot', '--json'], capture_output=True, text=True, timeout=20)
d = json.loads(result.stdout.strip())
items = d.get('data', {}).get('items', [])
ent_cats = ['电影', '体育', '综艺', '音乐', '剧集', '游戏', '动漫', '艺人', '足球', '篮球', '网球']
for item in items:
    cat = item.get('category', '')
    if cat in ent_cats:
        print(f"[{cat}] {item['word']} (热度:{item['hot_value']})")
```

**优点**：实时、分类清晰、热度高
**缺点**：仅 30 条，对 K-pop 覆盖有限

### 2. B站热搜 `bb-browser site bilibili/trending --json`
**用途**：年轻用户文娱关注点（游戏、赛事、影视）

实测返回 20 条热搜词，无分类标签：
```python
result = subprocess.run(['bb-browser', 'site', 'bilibili/trending', '--json'], capture_output=True, text=True, timeout=15)
```

### 3. 豆瓣热门影视 `bb-browser site douban/movie-hot --json`
**用途**：当前热门电影/剧集评分+排名

返回结构：
```json
{"type": "movie", "tag": "热门", "count": 20, "items": [
  {"rank": 1, "id": "36680492", "title": "大濛", "rating": 8, "url": "...", "is_new": false}
]}
```

### 4. Bing 搜索（补漏用，需 setlang=en）
**用途**：特定事件详情（决赛结果、获奖名单）

⚠️ **必须用 `setlang=en`**，中文参数返回央视网/新华网污染：
```python
from urllib.parse import quote
url = f"https://www.bing.com/search?q={quote('2026 World Cup group stage results')}&setlang=en&count=10"
```

过滤噪音：`百度`、`百科`、`词典`、`翻译`、`央视网`、`新华网`、`gov.cn`、`人民日报`

## Bing setlang=zh-CN 政府网站污染（重大踩坑）

**实测（2026-06-16）**：几乎所有 `setlang=zh-CN` 查询第一位均为"2026是个什么年？_新闻频道_央视网"，无论英文还是中文关键词。

| 查询 | 第一结果 |
|------|---------|
| `2026 法网 French Open results` | 央视网 |
| `The Game Awards 2026` | 央视网 |
| `2026 anime spring season` | 央视网 |
| `NewJeans comeback 2026` | 央视网 |
| `aespa new song 2026` | 央视网 |

**结论**：`setlang=zh-CN` 适合政治监测，不适合文娱搜索。

## 历史数据局限（3个月回溯问题）

YAOWENLIEBIAO.json 仅覆盖约 1 个月（2026-05-16 ~ 2026-06-16），**无法用于 3 个月文娱回顾**。

文娱月报 3 个月回溯可用来源：
- **36kr RSS**：科技商业为主，非文娱专项
- **新浪财经 lid=2517**：A 股/港股，无文娱
- **Bing 搜索**：可搜索但需大量去噪
- **Wikipedia**：在 cron 环境超时，不可用
- **bb-browser site douban/movie-hot**：近期影视覆盖

## 文娱月报结构模板

```
## 📅 过去3个月文娱重大事件（YYYY.MM.DD ~ YYYY.MM.DD）

### 🏟️ 体育
### 🎵 K-pop
### 🎬 影视
### 🎮 游戏
### 🎌 动漫

## 📅 未来3个月定档大事件（YYYY.MM.DD ~ YYYY.MM.DD）

### 📅 X月
| 分类 | 事件 | 日期 | 说明 |
|------|------|------|------|
```

## 已知不可用来源

- Wikipedia：超时（60s）
- 知乎热搜：401 需要登录
- 百度搜索：滑块验证
- Bing `setlang=zh-CN`：政府网站污染
- 新浪财经 lid=2517：美股/国际财经，无文娱
- 新华网政治 RSS：返回 2022 年旧数据
# 机器人/具身智能日报 — robot-news.py

## 概述

机器人行业每日资讯推送，国际源（英文）自动翻译成中文，国内源直取原文。
每天 09:00 自动推送到 `oc_c6883cd907e4d226736d87ce9c6c6d79`。

## 脚本路径

```
/home/ubuntu/.hermes/scripts/robot-news.py
```

## Cron

任务 ID：`81b790f4a2fb`
调度：`0 9 * * *`

## 数据源

### 国际源（英文，需翻译）

| 来源 | RSS URL | 备注 |
|------|---------|------|
| TechCrunch Robotics | `https://techcrunch.com/category/robotics/feed/` | 主用；fallback到 AI category |
| VentureBeat AI | `https://venturebeat.com/category/ai/feed/` | 过滤后保留机器人相关 |
| Wired AI | `https://www.wired.com/feed/tag/ai/latest/rss` | 过滤后保留机器人相关 |
| The Verge AI+Robots | `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml` | fallback到 robots rss |
| IEEE Spectrum | `https://spectrum.ieee.org/feeds/feed.rss` | description经常为空 |

### 国内源（中文，直连）

| 来源 | RSS URL |
|------|---------|
| 36氪 | `https://36kr.com/feed` |
| 雷锋网 | `https://www.leiphone.com/feed` |
| 爱范儿 | `https://www.ifanr.com/feed` |

## 关键词过滤（两级制）

### 第一级：标题必须命中
```
robot, humanoid, 具身, 人形机器人, 自动驾驶, autonomous,
drone, cobots, agv, amr, 机械臂, 机械手, 配送机器人,
手术机器人, industrial robot, service robot, mobile robot,
robotic, exoskeleton, 外骨骼, Boston Dynamics, Tesla Bot,
Unitree, 宇树, 智元, 傅利叶, 魔法原子, DJI, 大疆,
AutoX, Waymo, Zoox, Pony.ai, 文远知行, 小马智行, 图森未来
```

### 第二级：description 额外命中（标题没有时补充）
```
humanoid robot, autonomous driving, self-driving,
具身智能, 具身机器人, 人形机器人
```

## 翻译方案

**MyMemory 免费 API**（直连中国可用，无需代理）：
```
https://api.mymemory.translated.net/get?q={encoded_text}&langpair=en|zh
```

实现：用 `subprocess.run(["curl", "-s", "--max-time", "12", url])` 调用 curl，
**不要用 urllib 的 ProxyHandler**——socks5 代理场景下会报 `Connection refused`（原因：urllib 的 socks5 实现与 curl 的 socks5h 行为不一致）。

响应解析：
```python
data = json.loads(r.stdout)
translated = data.get("responseData", {}).get("translatedText", original_text)
```

限制：单次最多 450 字符，超长截断。

## 网络连通性（2026-05 实测）

| 目标 | 直连 | JP代理 207.56.226.147:10808 |
|------|------|-------------------------------|
| MyMemory API | ✅ 正常 | ❌ 返回空 |
| Google Translate | ❌ 超时 | ❌ 返回空 |
| TechCrunch/VentureBeat/Wired/The Verge/IEEE | ✅ 5-8秒 | ✅ 可用 |
| 36氪/雷锋网/爱范儿 | ✅ 正常 | — |

结论：翻译走**直连 MyMemory**，国际新闻源走**直连优先**（日本代理兜底）。

## 日本代理兜底逻辑

```python
def curl_get(url, use_jp_fallback=False, timeout=12):
    # 1. 先直连
    r = subprocess.run(["curl", "-s", "-L", "--max-time", str(timeout), url], ...)
    if r.stdout and len(r.stdout) > 100:
        return r.stdout
    # 2. 直连失败，用 JP 代理重试一次
    if use_jp_fallback:
        JP_AVAILABLE = check_jp_proxy()  # 首次检测
        if JP_AVAILABLE:
            r2 = subprocess.run(["curl", "-s", "-L", "--max-time", str(timeout),
                                  "--proxy", "socks5h://207.56.226.147:10808", url], ...)
```

注意用 `socks5h://`（DNS 走代理）而非 `socks5://`。

## 输出格式

```
🤖 机器人日报
📅 2026-05-18  |  🌍 IEEE · TechCrunch · VentureBeat · Wired · The Verge
         🇨🇳 36氪 · 雷锋网 · 爱范儿
═══════════════════════════════════════════════
【TechCrunch】Rivian分拆Mind Robotics再筹集4亿美元  (05-13)
   Mind Robotics于2025年底首次亮相...
【IEEE Spectrum】面向机器人团队的代理人工智能  (05-18)
...
═══════════════════════════════════════════════
🤖 机器人日报 · 每日 09:00 自动推送
💬 Hermes Agent
```

## 已知问题

- IEEE Spectrum 的 description 字段经常为空，翻译后只有标题无摘要（可接受）
- VentureBeat 过滤后机器人内容极少（AI coding 工具被关键词过滤），实际以 TechCrunch 为主
- MyMemory 单日翻译额度有限（~1000词/天），大量推送时注意配额

## 爆火山寨 — 头条热榜

今日头条热榜作为补充数据源，通过 `bb-browser` 抓取：

```bash
bb-browser site toutiao/hot --json
```

返回格式：`{"success": true, "data": {"count": 20, "items": [{"rank": 1, "title": "...", "hot_value": "38200732", "url": "https://..."}]}}`

**独立关键词过滤**（比 DOMESTIC_KW 更严格，避免宽泛词如"无人机"混入安全法制新闻）：

```python
TRENDING_KW = [
    "机器人", "人形机器人", "具身智能", "自动驾驶", "无人车",
    "Boston Dynamics", "宇树", "智元", "傅利叶", "魔法原子",
    "Tesla Bot", "Unitree", "宇树科技", "追觅科技", "大疆",
    "AutoX", "Waymo", "Zoox", "Pony.ai", "小马智行", "图森未来",
    "配送机器人", "手术机器人", "工业机器人", "仓储机器人",
    "humanoid robot", "具身", "physical intelligence", "Figure AI",
]
```

注意：头条热榜并非每天都有机器人相关内容，无匹配时返回空数组，静默跳过。

## 摘要清洗 — 去除作者/编辑信息

`clean_summary()` 函数在报告生成时调用，去除以下干扰信息：

```python
def clean_summary(text: str) -> str:
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\s*作者\s*[|/丨].*', '', text)   # 支持全角竖线
    text = re.sub(r'\s*编辑\s*[|/丨].*', '', text)
    text = re.sub(r'\s*记者\s*[|/丨].*', '', text)
    text = re.sub(r'\s*图注\s*[|/丨].*', '', text)
    text = re.sub(r'\s*整理\s*[|/丨].*', '', text)
    text = re.sub(r'\s*校对\s*.*', '', text)
    text = re.sub(r'36氪获悉[：:]?', '', text)
    text = re.sub(r'^[,，、\s]+', '', text)   # 去掉开头多余标点
    text = re.sub(r'点击查看.*', '', text)
    return re.sub(r'\s+', ' ', text).strip()
```

关键：竖线匹配要包含全角 `丨`（Unicode U+2016），否则雷锋网"作者丨郑佳美  编辑丨马晓宁"无法清除。

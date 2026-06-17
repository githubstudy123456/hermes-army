---
name: cultural-entertainment-monitor
description: 文娱专项监测 — 覆盖体育、K-pop、影视、游戏、动漫五大领域。输出月报（近3个月事件+未来3个月定档+一句话点评）、热搜监测、定档快讯。主人明确表示喜欢电影，是文娱内容的忠实受众。
version: 1.1.0
author: Hermes军团 · 研究部
tags: [文娱, 影视, 电影, 体育, K-pop, 游戏, 动漫, 定档, 月报, 热搜, 百花奖, 世界杯, 奥斯卡]
hermes:
  profile: hermes-cultural-monitor
---

# 文娱专项监测

## 职责

追踪文娱领域五大方向重大动态：
- **体育 Sports**：世界杯、NBA、网球四大满贯、F1、电竞
- **K-pop**：回归、演唱会、颁奖礼（MAMA/MMA/金唱片）
- **影视 Film/TV**：票房、奥斯卡、百花奖、爆款剧集、定档
- **游戏 Gaming**：TGA、英雄联盟S赛、Steam促销
- **动漫 Anime**：春季/夏季/秋季番、Comiket、B站数据

## 监测频率

- 文娱属于低频高价值信息，**每月汇总一次**比每日推送更合适
- 重大事件（如世界杯决赛、奥斯卡、颁奖礼）应立即推送，不等月汇总

## 数据源（按可靠性排序）

### 热搜/实时信号（首选）

| 来源 | 覆盖内容 | 稳定性 | 用法 |
|------|---------|--------|------|
| `bb-browser site weibo/hot --json` | 微博热搜（含分类标签：体育/电影/剧集/综艺/艺人）| ✅ 稳定 | 直接返回30条，含rank/category/word/hot_value |
| `bb-browser site bilibili/trending --json` | B站热搜 | ⚠️ 无头环境返回空 | 备用 |
| 豆瓣 `movie.douban.com/coming` | 待映电影片单 | ✅ 稳定 | urllib 直读 |

### 搜索（补漏用）

| 来源 | 用途 | 稳定性 | 注意 |
|------|------|--------|------|
| Bing `setlang=en` | 英文关键词搜索 | ⚠️ 严重污染 | 见已知踩坑 |
| Wikipedia | 体育赛果/获奖结果 | ⚠️ 超时率高 | 超时改用其他来源 |

### 娱乐新闻 API

| 来源 | 覆盖内容 | 稳定性 | 注意 |
|------|---------|--------|------|
| 新浪 `feed.mix.sina.com.cn/api/roll/get?lid=2517` | A股/财经为主 | ✅ 稳定 | 政策/财经为主，娱乐弱 |
| 36kr RSS | 科技商业 | ✅ 稳定 | 非娱乐首选 |

## 月报标准结构

```
# 🎬 文娱月报 | YYYY年M月D日

> **报告周期**：近3个月 / 未来3个月
> **数据来源**：微博热搜、Bing英文搜索、百度百科

---

## 一、近3个月文娱重大事件

### 🏟️ 体育
| 事件 | 时间 | 影响力指标 |

### 🎤 K-pop
| 事件 | 时间 | 影响力指标 |

### 🎬 影视
| 事件 | 时间 | 影响力指标 |

### 🎮 游戏
| 事件 | 时间 | 影响力指标 |

### 🎌 动漫
| 事件 | 时间 | 影响力指标 |

---

## 二、未来3个月定档大事件

| 月份 | 体育 | K-pop | 影视 | 游戏 | 动漫 |
|------|------|-------|------|------|------|
| X月下旬 | ... | ... | ... | ... | ... |

---

## 三、一句话点评

**本月最值得关注：XXX** — 简述原因。
```

## 工作流（月报 cron）

```python
# Step 1: 并行抓热搜信号
result_weibo = subprocess.run(['bb-browser', 'site', 'weibo/hot', '--json'], 
    capture_output=True, text=True, timeout=30)

# Step 2: 分类过滤（体育/K-pop/影视/游戏/动漫）
# → 从 weibo_items 中按 category 标签分组

# Step 3: Bing 补漏（英文关键词，不依赖中文污染源）
# 搜索: "2026 World Cup results", "Oscars 2026 winners", "aespa comeback 2026"

# Step 4: 从 entertainment-events.md 提取未来3个月日历数据

# Step 5: 组装月报 Markdown，推送飞书群
```

## 已知踩坑

- **Bing `setlang=en` 严重污染**：即使英文关键词查询，第一位结果经常是"2026是个什么年？_央视网"、"两会新华社权威速览"等中文政府新闻。**解决方案**：英文关键词查询时不加 `setlang` 参数，或在过滤列表中增加 `央视网`、`新华网`、`gov.cn`、`people.com`
- **Bing 中文搜索**：返回百度百科/词典噪音，必须二次过滤标题黑名单
- **Wikipedia 超时**：在 cron 环境下 urllib 直连 Wikipedia 超时率高，改用其他来源
- **新浪 lid=2517**：返回 A股/财经新闻为主，娱乐内容极少，不适合文娱月报
- **B站热搜 API**：`api.bilibili.com/x/web-interface/ranking/v2` 在无头环境返回空列表
- **知乎/小红书**：`bb-browser` 返回 401，需 Playwright CDP 登录态
- **Steam/TGA 结果**：TGA 通常12月举办，结果当年12月后才确认；Steam Awards 同理

## 飞书推送目标

- 飞书群：`oc_bd20e92437df496f958a38958d48b92a`

## linked_files

- `references/entertainment-events.md` — 文娱年度大事件日历（1月~12月五大领域分类，含年度顶级大事件标注）
- `references/2026-summer-film-landscape.md` — 2026年暑期档片单实采结果，含定档信息+制作方动态

## 触发条件

主人主动询问"电影"、"影视"、"定档"相关话题时，立即触发本 skill 并输出文娱片单。不需要等 cron 任务。

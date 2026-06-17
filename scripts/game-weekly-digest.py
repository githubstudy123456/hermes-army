#!/usr/bin/env python3
"""
游戏资讯周报 - 3DM + 游民星空聚合
抓取本周游戏新闻，整理为：新发售 · 爆火热话 · 业界动态 三大板块
"""

import urllib.request
import re
import html
import json
from datetime import datetime, timedelta
from typing import Optional

FEISHU_GROUP_ID = "oc_c6883cd907e4d226736d87ce9c6c6d79"  # 每日订阅群

def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; game-weekly-bot/1.0; +https://example.com/bot)',
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode('utf-8', errors='replace')


def parse_3dm() -> list:
    """解析3DM游戏网新闻列表"""
    url = "https://www.3dmgame.com/news/"
    content = fetch_url(url)

    articles = []
    # 新闻列表在 class="selectpost" 的 <li> 中
    # 格式: <a href="URL" target="_blank" class="bt">标题</a>
    #        <span class="time">2026-05-07 18:27:54</span>
    pattern = r'<a href="(https://www\.3dmgame\.com/news/\d+/\d+\.html)"[^>]*class="bt">([^<]+)</a>.*?<span class="time">(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})</span>'
    for m in re.finditer(pattern, content, re.DOTALL):
        url, title, time_str = m.groups()
        title = html.unescape(title.strip())
        articles.append({
            'title': title,
            'url': url,
            'time': time_str,
            'source': '3DM'
        })
    return articles


def parse_gamersky() -> list:
    """解析游民星空新闻列表"""
    url = "https://www.gamersky.com/news/"
    content = fetch_url(url)

    articles = []
    # 格式: <a class="tt" href="URL" target="_blank" title="标题">
    #        <div class="time">2026-05-07 18:40</div>
    pattern = r'<a class="tt" href="(https://www\.gamersky\.com/news/\d+/\d+\.shtml)"[^>]*title="([^"]+)"[^>]*>.*?<div class="time">(\d{4}-\d{2}-\d{2} \d{2}:\d{2})</div>'
    for m in re.finditer(pattern, content, re.DOTALL):
        url, title, time_str = m.groups()
        title = html.unescape(title.strip())
        articles.append({
            'title': title,
            'url': url,
            'time': time_str + ':00',
            'source': '游民星空'
        })
    return articles


# 需要过滤掉的非游戏类关键词（非游戏新闻占大多数，需过滤）
FILTER_KEYWORDS = [
    '卡戴珊', '保时捷', '两头蛇', '傅首尔', '世界杯', '黑袍纠察队',
    '非洲', '特朗普', '拜登', '关税', '地震', '疫情', '肺炎', '选举',
    '高通', 'Win11', '骁龙', '特斯拉', 'SpaceX',
    '韩国女团', 'K-pop', 'Lisa', 'aespa', 'BLACKPINK',
    '山海关', '天下第一关', '长城', '故宫',
    '崇祯', '大明', '历史模拟器', '三国', '新三国',
    '韩国棒球女神', '苹果讨论涨价', '英伟达宣布与康宁',
]

# 发售相关关键词
RELEASE_KEYWORDS = ['发售', '正式发售', '上线', '开售', '今日发售', '明日发售', '即将发售',
                     '销量突破', '销量达', '全球销量', '首周', ' Steam', 'EA', '折扣',
                     '史低', '降价', '特惠', '优惠', '优惠', '新史低', '首次降价']

# 爆火/热话关键词
HOT_KEYWORDS = ['爆火', '爆热', '大火', '霸榜', '榜首', '第一', '热搜', '刷屏',
                 '玩家力挺', '好评', '差评', '全网', '火到', '连续', '霸权',
                 '世界第一', '最强', '史上', '罕见', '不可思议', '玩家怒斥',
                 '玩家炸了', '玩家崩溃', '玩家无语']


def classify_article(title: str) -> str:
    """将文章分类为: 新发售 / 爆火热话 / 业界动态"""
    title_lower = title.lower()
    for kw in RELEASE_KEYWORDS:
        if kw in title:
            return 'new_release'
    for kw in HOT_KEYWORDS:
        if kw in title:
            return 'hot'
    return 'industry'


def should_filter(title: str) -> bool:
    """判断是否为非游戏类文章（需过滤）"""
    for kw in FILTER_KEYWORDS:
        if kw in title:
            return True
    return False


def get_article_preview(url: str, max_chars: int = 200) -> str:
    """抓取文章前几段作为摘要"""
    try:
        html_content = fetch_url(url)
        paras = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
        lines = []
        for p in paras:
            text = re.sub(r'<[^>]+>', '', p).strip()
            text = html.unescape(text)
            if len(text) > 30:
                lines.append(text)
            if sum(len(l) for l in lines) > max_chars:
                break
        preview = ' '.join(lines[:3])
        return preview[:max_chars] + ('...' if len(preview) > max_chars else '')
    except Exception:
        return ''


def build_markdown(articles: list, week_ago: str) -> str:
    now = datetime.now()
    today_str = now.strftime('%Y年%m月%d日')
    weekday_str = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][now.weekday()]
    week_range = f"{week_ago} ~ {today_str}"

    # 过滤 + 去重 + 分类
    seen_titles = set()
    new_releases = []
    hot_topics = []
    industry = []

    for a in articles:
        if should_filter(a['title']):
            continue
        if a['time'] < week_ago:
            continue
        # 去重（标题去重）
        norm_title = a['title'][:30]
        if norm_title in seen_titles:
            continue
        seen_titles.add(norm_title)
        cat = classify_article(a['title'])
        if cat == 'new_release':
            new_releases.append(a)
        elif cat == 'hot':
            hot_topics.append(a)
        else:
            industry.append(a)

    # 按时间倒序
    for lst in [new_releases, hot_topics, industry]:
        lst.sort(key=lambda x: x['time'], reverse=True)

    def section(title: str, items: list, emoji: str) -> list:
        if not items:
            return []
        lines = [f"## {emoji} {title}", ""]
        for a in items[:8]:  # 每类最多8条
            lines.append(f"### {a['title']}")
            dt = a['time'].split()[0]
            lines.append(f"📅 {dt} · [{a['source']}]({a['url']})")
            lines.append("")
        return lines

    body = []
    body.extend(section("本周新发售 & 销量喜报", new_releases, "🆕"))
    body.extend(section("爆火热话", hot_topics, "🔥"))
    body.extend(section("业界动态", industry, "📢"))

    if not body:
        body = ["（本周暂无符合条件的游戏资讯）"]

    lines = [
        f"# 🎮 游戏周报 · {today_str}（{weekday_str}）",
        f"**数据周期**: {week_range}",
        f"**来源**: 3DM游戏网 · 游民星空",
        "",
        "---",
        ""
    ]
    lines.extend(body)
    lines.extend([
        "",
        "---",
        f"由 ⭐☁️ 自动生成 · {today_str}",
        f"抓取原始页面: [3DM新闻](https://www.3dmgame.com/news/) · [游民星空](https://www.gamersky.com/news/)"
    ])
    return '\n'.join(lines)


def main():
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    week_ago_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    print(f"[游戏周报] 开始抓取... (本周起始: {week_ago_date})")

    # 并行抓取两个源
    articles_3dm = parse_3dm()
    print(f"[3DM] 抓到 {len(articles_3dm)} 条")

    articles_gk = parse_gamersky()
    print(f"[游民星空] 抓到 {len(articles_gk)} 条")

    all_articles = articles_3dm + articles_gk
    print(f"[合并] 共 {len(all_articles)} 条")

    report = build_markdown(all_articles, week_ago_date)

    out_path = "/home/ubuntu/.hermes/cron/output/game-weekly-digest.md"
    with open(out_path, 'w') as f:
        f.write(report)

    print(f"[完成] 周报已生成: {out_path}")
    print("\n" + "="*60)
    print(report)


if __name__ == '__main__':
    main()

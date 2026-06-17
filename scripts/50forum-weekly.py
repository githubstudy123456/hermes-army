#!/usr/bin/env python3
"""中国经济50人论坛 - 每周经济学家观点速报"""

import urllib.request
import urllib.error
import json
import re
import html
from datetime import datetime, timedelta
from typing import List, Dict

def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; 50forum-bot/1.0)',
        'Accept': 'text/html,application/xhtml+xml',
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode('utf-8')

def parse_articles(html_content: str) -> List[Dict]:
    """从列表页提取文章标题、作者、日期、链接"""
    articles = []
    # 匹配模式: <a href="/portal/article/index.html?id=XXXX" title="标题" ...>标题</a> - 作者 - 日期
    pattern = r'<a href="(/portal/article/index\.html\?id=\d+)"[^>]*title="([^"]+)"[^>]*>.*?([^-]+)\s*-\s*(\d{4}-\d{2}-\d{2})'
    for m in re.finditer(pattern, html_content, re.DOTALL):
        url, title, author, date = m.groups()
        articles.append({
            'title': html.unescape(title.strip()),
            'author': html.unescape(author.strip()),
            'date': date.strip(),
            'url': 'https://www.50forum.org.cn' + url
        })
    return articles

def parse_article_content(html_content: str) -> Dict:
    """从文章页提取正文内容"""
    # 提取正文段落
    paras = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
    content = []
    for p in paras:
        # 去掉标签，保留纯文本
        text = re.sub(r'<[^>]+>', '', p).strip()
        text = html.unescape(text)
        if len(text) > 30:  # 过滤短文本
            content.append(text)
    return {'paragraphs': content}

def get_article_preview(url: str, max_chars: int = 300) -> str:
    """抓文章前几段作为摘要"""
    try:
        html = fetch_url(url)
        data = parse_article_content(html)
        text = '\n'.join(data['paragraphs'][:3])
        if len(text) > max_chars:
            text = text[:max_chars] + '...'
        return text
    except Exception as e:
        return f'（摘要抓取失败: {e}）'

def build_report(articles: List[Dict]) -> str:
    now = datetime.now().strftime('%Y年%m月%d日')
    week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # 只选本周文章
    this_week = [a for a in articles if a['date'] >= week_ago]
    older = [a for a in articles if a['date'] < week_ago]

    lines = [
        f"# 📊 经济50人论坛 · 本周观点速报",
        f"**生成时间**: {now}",
        f"**本周更新**: {len(this_week)} 篇",
        "",
        "---",
        ""
    ]

    if this_week:
        lines.append("## 本周新文章")
        lines.append("")
        for a in this_week:
            lines.append(f"### 【{a['author']}】{a['title']}")
            lines.append(f"📅 {a['date']} · [阅读原文]({a['url']})")
            lines.append("")
            preview = get_article_preview(a['url'])
            if preview:
                lines.append(f"> {preview}")
            lines.append("")
            lines.append("---")
            lines.append("")

    if older:
        lines.append(f"## 近期重要文章（过去7天前）")
        lines.append("")
        for a in older[:5]:
            lines.append(f"- **{a['author']}** · {a['date']} · [{a['title']}]({a['url']})")
        lines.append("")

    lines.extend([
        "",
        "---",
        "**关于本报告**: 数据来源 [中国经济50人论坛](https://www.50forum.org.cn)",
        f"由 ⭐☁️ 自动生成 · {now}"
    ])

    return '\n'.join(lines)

def main():
    base_url = "https://www.50forum.org.cn/portal/list/index.html?id=6"
    print("抓取 50forum 学术观点列表...")
    html = fetch_url(base_url)
    articles = parse_articles(html)
    print(f"找到 {len(articles)} 篇文章")
    for a in articles[:5]:
        print(f"  - [{a['date']}] {a['author']}: {a['title']}")

    report = build_report(articles)

    out_path = "/home/ubuntu/.hermes/cron/output/50forum_weekly.md"
    with open(out_path, 'w') as f:
        f.write(report)
    print(f"\n报告已生成: {out_path}")
    print("\n" + "="*60)
    print(report)

if __name__ == '__main__':
    main()

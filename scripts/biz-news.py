#!/usr/bin/env python3
"""
商界要闻日报 - 每日 8:50 推送
数据源:
  1. BBC Business RSS (英文, 需代理)
  2. FT中文网 (中文, 需代理)
  3. 36kr (中文, 需代理)
翻译: Google Translate (免费接口)
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import html
import re
import os
import sys
import json
import subprocess
import tempfile
from datetime import datetime

PROXY_SOCKS = "socks5://127.0.0.1:10808"
BBC_RSS = "https://feeds.bbci.co.uk/news/business/rss.xml"
FT_RSS = "https://www.ftchinese.com/rss/feed?node=corp"  # 企业/商业
FT_ALL_RSS = "https://www.ftchinese.com/rss/feed"
KR36_RSS = "https://36kr.com/feed"
MAX_ITEMS = 12
OUTPUT_DIR = os.path.expanduser("~/.hermes/cron/output")
PLAYWRIGHT_BIN = "/home/ubuntu/.hermes/hermes-agent/venv/bin/python3"

BUSINESS_KEYWORDS = [
    'business', 'company', 'market', 'stock', 'trade', 'economy', 'economic',
    'finance', 'financial', 'bank', 'investor', 'investment', 'ipo', 'merger',
    'acquisition', 'ceo', 'executive', 'revenue', 'profit', 'loss', 'deal',
    'tariff', 'sanction', 'oil', 'price', 'inflation', 'fed', 'central bank',
    'gdp', 'growth', 'recession', 'startup', 'tech', 'ai', 'semiconductor',
    'apple', 'google', 'microsoft', 'amazon', 'nvidia', 'tesla', 'meta',
    'baidu', 'alibaba', 'tencent', 'byd', 'huawei', 'samsung',
    'walmart', 'tesla', 'jpmorgan', 'goldman', 'blackrock',
    'airline', 'aviation', 'tourism', 'hotel', 'retail', 'auto',
    'real estate', 'property', 'housing', 'mortgage',
    '商业', '财经', '股市', '上市', '并购', '融资', '投资',
    '科技', 'AI', '芯片', '半导体', '关税', '制裁',
    '公司', '业绩', '营收', '利润', '亏损', 'CEO', '高管',
    '原油', '油价', '通胀', '央行', '美联储', '降息', '加息',
    '经济', 'GDP', '增长', '衰退', '房地产', '房价',
    '万科', '阿里', '腾讯', '百度', '字节', '京东', '小米',
    '特斯拉', '苹果', '英伟达', '谷歌', '微软', '亚马逊',
    '航空', '旅游', '零售', '汽车', '新能源',
]

NOISE_PATTERNS = [
    'recipe', 'cook', 'food', 'restaurant', 'festival', 'concert',
    'football', 'soccer', 'sport', 'game', 'match', 'weather',
    'dog', 'celebrity', 'gossip', 'instagram', 'tiktok viral',
    'wed', 'marriage', 'baby', 'birth',
]

def is_business(title: str) -> bool:
    t = title.lower()
    for noise in NOISE_PATTERNS:
        if noise in t:
            return False
    for kw in BUSINESS_KEYWORDS:
        if kw in t:
            return True
    return False

def fetch_via_proxy(url: str, timeout: int = 15) -> str:
    proxy_handler = urllib.request.ProxyHandler({'http': PROXY_SOCKS, 'https': PROXY_SOCKS})
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; biz-news-bot/1.0)'})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def translate_to_chinese(text: str) -> str:
    if not text or not text.strip():
        return ""
    try:
        encoded = urllib.parse.quote_plus(text[:500])
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q=" + encoded
        proxy_handler = urllib.request.ProxyHandler({'http': PROXY_SOCKS, 'https': PROXY_SOCKS})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with opener.open(req, timeout=10) as resp:
            data = resp.read().decode('utf-8')
        result = json.loads(data)
        if result[0]:
            return ''.join(item[0] for item in result[0] if item[0])
        return text
    except Exception as e:
        print(f"翻译失败: {e}", file=sys.stderr)
        return text

def clean_html(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_bbc_rss(xml_content: str) -> list:
    items = []
    root = ET.fromstring(xml_content)
    for item in root.findall('.//item'):
        title = (item.findtext('title') or '').strip()
        description = (item.findtext('description') or '').strip()
        link = (item.findtext('link') or '').strip()
        if title:
            items.append({'title': clean_html(title), 'description': clean_html(description)[:200], 'link': link, 'source': 'BBC商业'})
    return items

def parse_ft_rss(xml_content: str) -> list:
    items = []
    root = ET.fromstring(xml_content)
    for item in root.findall('.//item'):
        title = (item.findtext('title') or '').strip()
        description = (item.findtext('description') or '').strip()
        link = (item.findtext('link') or '').strip()
        if title:
            items.append({'title': clean_html(title), 'description': clean_html(description)[:200], 'link': link, 'source': 'FT中文网'})
    return items

def parse_36kr_rss(xml_content: str) -> list:
    items = []
    root = ET.fromstring(xml_content)
    for item in root.findall('.//item'):
        title = (item.findtext('title') or '').strip()
        description = (item.findtext('description') or '').strip()
        link = (item.findtext('link') or '').strip()
        if title:
            # 清理36kr的HTML描述
            desc = clean_html(description)[:200]
            items.append({'title': clean_html(title), 'description': desc, 'link': link, 'source': '36氪'})
    return items

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    job_id = os.environ.get('CRON_JOB_ID', 'biz-news')
    print(f"[{datetime.now().isoformat()}] 开始抓取商界要闻...")
    all_items = []

    # 1. BBC Business RSS
    try:
        xml = fetch_via_proxy(BBC_RSS)
        bbc_items = parse_bbc_rss(xml)
        filtered = [it for it in bbc_items if is_business(it['title'])]
        print(f"BBC商业: {len(bbc_items)} 条原始, {len(filtered)} 条商业过滤后")
        all_items.extend(filtered)
    except Exception as e:
        print(f"BBC 抓取失败: {e}", file=sys.stderr)

    # 2. FT中文网
    try:
        xml = fetch_via_proxy(FT_ALL_RSS)
        ft_items = parse_ft_rss(xml)
        print(f"FT中文网: {len(ft_items)} 条")
        all_items.extend(ft_items)
    except Exception as e:
        print(f"FT 抓取失败: {e}", file=sys.stderr)

    # 3. 36kr
    try:
        xml = fetch_via_proxy(KR36_RSS)
        kr_items = parse_36kr_rss(xml)
        print(f"36氪: {len(kr_items)} 条")
        all_items.extend(kr_items)
    except Exception as e:
        print(f"36氪 抓取失败: {e}", file=sys.stderr)

    # 去重（按标题前25字）
    seen = set()
    unique = []
    for it in all_items:
        key = it['title'][:25].lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(it)
    all_items = unique

    # 取前 MAX_ITEMS
    all_items = all_items[:MAX_ITEMS]

    # 生成报告
    report_lines = [
        f"# 💼 商界要闻日报",
        f"**推送日期：** {today}",
        f"**数据来源：** BBC商业（🌐）+ FT中文网（🇨🇳）+ 36氪（🇨🇳）",
        "",
        "---",
        "",
    ]

    for i, item in enumerate(all_items, 1):
        title = item['title']
        if item['source'] == 'BBC商业':
            title = translate_to_chinese(title)
            desc = translate_to_chinese(item['description']) if item['description'] else ""
        else:
            desc = item['description']

        tag_map = {'BBC商业': '🌐', 'FT中文网': '🇨🇳', '36氪': '🇨🇳'}
        tag = tag_map.get(item['source'], '🌐')
        report_lines.append(f"**{i}. {title}** {tag}")
        if desc:
            report_lines.append(f"   {desc}")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append(f"*🤖 由 ⭐☁️ 自动生成 · {datetime.now().strftime('%H:%M:%S')}*")

    report_content = '\n'.join(report_lines)
    out_dir = os.path.join(OUTPUT_DIR, job_id)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{today}.md")
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"报告已写入: {out_file}, 字数: {len(report_content)}")

if __name__ == '__main__':
    main()

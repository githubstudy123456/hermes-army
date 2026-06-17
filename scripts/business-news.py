#!/usr/bin/env python3
"""
商业要闻日报 - 每日 9:20 推送
数据源:
  1. WSJ Markets RSS (Dow Jones, 直连可用)
  2. WSJ World News RSS (Dow Jones, 直连可用)
  3. 新浪财经 RSS (中文, 直连可用)
翻译: Google Translate (免费接口, 无需API Key)
推送: 直接通过飞书 API 发送
"""

import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
import html
import re
import os
import sys
import json
from datetime import datetime

# ── 配置 ──────────────────────────────────────────
PROXY_SOCKS   = "socks5://127.0.0.1:10808"
FEISHU_TOKEN="Y2hpbi...MDE="   # base64 AppCoreToken (占位，实际从API获取)
FEISHU_CHAT   = "oc_c6883cd907e4d226736d87ce9c6c6d79"

WSJ_MARKETS_RSS = "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"
WSJ_WORLD_RSS   = "https://feeds.a.dj.com/rss/RSSWorldNews.xml"
SINA_RSS        = "http://rss.sina.com.cn/news/china/focus15.xml"
MAX_ITEMS       = 14

# ── 过滤词（商业噪音） ──────────────────────────────
BUSINESS_KEYWORDS = [
    'economy', 'economic', 'GDP', 'inflation', 'recession', 'trade',
    'tariff', 'sanction', 'oil', 'price', 'market', 'stock', 'shares',
    'company', 'ceo', 'merger', 'acquisition', 'ipo', 'startup',
    'tech', 'ai', 'artificial intelligence', 'semiconductor', 'chip',
    'apple', 'google', 'microsoft', 'amazon', 'meta', 'tesla', 'nvidia',
    'fed', 'federal reserve', 'interest rate', 'dollar', 'yuan', 'euro',
    'china', 'chinese', 'us ', 'america', 'trump', 'biden',
    'inflation', 'consumer', 'retail', 'sales', 'manufacturing',
    '能源', '石油', '经济', '市场', '股市', '公司', 'CEO',
    '贸易', '关税', '制裁', '科技', '人工智能', '芯片', '半导体',
    '美联储', '利率', '通胀', '消费', '零售', '制造业', '房地产',
]

NOISE_PATTERNS = [
    'dog', 'dogs', 'puppy', 'chocolate', 'milka', 'candy', 'sweet',
    'football', 'soccer', 'tennis', 'basketball', 'sport', 'match', 'game',
    'festival', 'concert', 'music', 'award', 'oscar', 'grammy',
    'weather', 'storm', 'hurricane', 'flood', 'earthquake',
    'everest', 'mount climb', 'climber',
    'bitcoin', 'crypto',  # 单独放噪音里
    'instagram', 'tiktok', 'viral', 'recipe', 'cook', 'food', 'restaurant',
    'hotel', 'airbnb', 'travel', 'tourism',
    'cruise', 'ship', 'norovirus',
    'ebola', 'health emergency',
    'tennis', 'marathon', 'running race',
    'air show', 'fighter jet',
]

# ── 飞书推送 ───────────────────────────────────────
def get_feishu_token() -> str:
    """获取飞书 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({
        "app_id": "cli_a95612fc9ebddbc8",
        "app_secret": "TBNvucvbHCHTeKqYtQ7PGfu1ANe0FSmb"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            return result.get("tenant_access_token", "")
    except Exception as e:
        print(f"获取token失败: {e}", file=sys.stderr)
        return ""

def feishu_send_text(text: str) -> bool:
    token = get_feishu_token()
    if not token:
        print("飞书token为空，推送失败", file=sys.stderr)
        return False
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = json.dumps({
        "receive_id": FEISHU_CHAT,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            print(f"飞书推送结果: {result}")
            return result.get("code", 0) == 0
    except Exception as e:
        print(f"飞书推送失败: {e}", file=sys.stderr)
        return False

# ── 数据抓取 ───────────────────────────────────────
def is_business_news(title: str) -> bool:
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
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with opener.open(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def fetch_direct(url: str, timeout: int = 15) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
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
        with opener.open(req, timeout=15) as resp:
            data = resp.read().decode('utf-8')
        result = json.loads(data)
        if result[0]:
            translated = ''.join(item[0] for item in result[0] if item[0])
            if translated and translated != text:
                return translated
            return text
        return text
    except Exception as e:
        print(f"翻译失败: {e}", file=sys.stderr)
        return text

def clean_html(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_wsj(xml_content: str, source_label: str) -> list:
    items = []
    try:
        root = ET.fromstring(xml_content)
        for item in root.findall('.//item'):
            title = (item.findtext('title') or '').strip()
            description = (item.findtext('description') or '').strip()
            link = (item.findtext('link') or '').strip()
            pub_date = (item.findtext('pubDate') or '').strip()
            if title:
                items.append({'title': clean_html(title), 'description': clean_html(description)[:200], 'link': link, 'pub_date': pub_date, 'source': source_label})
    except Exception as e:
        print(f"{source_label}解析失败: {e}", file=sys.stderr)
    return items

def parse_sina(xml_content: str) -> list:
    items = []
    try:
        root = ET.fromstring(xml_content)
        for item in root.findall('.//item'):
            title = (item.findtext('title') or '').strip()
            description = (item.findtext('description') or '').strip()
            link = (item.findtext('link') or '').strip()
            if title:
                items.append({'title': clean_html(title), 'description': clean_html(description)[:200], 'link': link, 'pub_date': '', 'source': '新浪财经'})
    except Exception as e:
        print(f"新浪财经解析失败: {e}", file=sys.stderr)
    return items

# ── 主流程 ─────────────────────────────────────────
def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now().isoformat()}] 开始抓取商业要闻...")
    all_items = []

    # WSJ Markets
    try:
        xml = fetch_direct(WSJ_MARKETS_RSS)
        items = parse_wsj(xml, 'WSJ市场')
        filtered = [it for it in items if is_business_news(it['title'])]
        print(f"WSJ市场: {len(items)} 条原始, {len(filtered)} 条过滤后")
        all_items.extend(filtered)
    except Exception as e:
        print(f"WSJ市场抓取失败: {e}", file=sys.stderr)

    # WSJ World News
    try:
        xml = fetch_direct(WSJ_WORLD_RSS)
        items = parse_wsj(xml, 'WSJ全球')
        filtered = [it for it in items if is_business_news(it['title'])]
        print(f"WSJ全球: {len(items)} 条原始, {len(filtered)} 条过滤后")
        all_items.extend(filtered)
    except Exception as e:
        print(f"WSJ全球抓取失败: {e}", file=sys.stderr)

    # 新浪财经
    try:
        xml = fetch_direct(SINA_RSS)
        sina_items = parse_sina(xml)
        print(f"新浪财经: {len(sina_items)} 条")
        all_items.extend(sina_items)
    except Exception as e:
        print(f"新浪财经抓取失败: {e}", file=sys.stderr)

    # 去重
    seen = set()
    unique = []
    for it in all_items:
        key = it['title'][:30].lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(it)
    all_items = unique

    # 取前14条，优先 WSJ
    wsj_list = [it for it in all_items if it['source'].startswith('WSJ')][:14]
    sina_list = [it for it in all_items if it['source'] == '新浪财经'][:6]
    merged = []
    wsj_idx, sina_idx = 0, 0
    while len(merged) < MAX_ITEMS and (wsj_idx < len(wsj_list) or sina_idx < len(sina_list)):
        if wsj_idx < len(wsj_list):
            merged.append(wsj_list[wsj_idx]); wsj_idx += 1
        if len(merged) >= MAX_ITEMS: break
        if sina_idx < len(sina_list):
            merged.append(sina_list[sina_idx]); sina_idx += 1
        if len(merged) >= MAX_ITEMS: break

    # ── 组装纯文本 ──────────────────────────────────
    lines = []
    lines.append(f"💼 商业要闻日报 | {today}")
    lines.append(f"数据来源: WSJ市场 🌐 + WSJ全球 🌐 + 新浪财经 🇨🇳")
    lines.append("─" * 30)

    for i, item in enumerate(merged, 1):
        title_cn = translate_to_chinese(item['title']) if item['source'].startswith('WSJ') else item['title']
        tag = '🌐' if item['source'].startswith('WSJ') else '🇨🇳'
        lines.append(f"{i}. {title_cn} {tag}")
        if item['description']:
            desc = translate_to_chinese(item['description']) if item['source'].startswith('WSJ') else item['description']
            if desc:
                lines.append(f"   {desc}")

    lines.append("─" * 30)
    lines.append(f"🤖 由 ⭐☁️ 自动生成 · {datetime.now().strftime('%H:%M:%S')}")

    content = "\n".join(lines)
    print(f"内容字数: {len(content)}，开始推送...")
    ok = feishu_send_text(content)
    print(f"推送{'成功' if ok else '失败'}")

if __name__ == '__main__':
    main()

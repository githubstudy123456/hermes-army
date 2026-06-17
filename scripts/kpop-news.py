#!/usr/bin/env python3
"""
韩国女团资讯抓取脚本 v3
- XCrawl Search API 主力来源（覆盖 Allkpop/Twitter/Naver）
- 中文 Soompi RSS 备选来源
- 直接调用飞书 API 推送，不走 cron 文件检测
"""
import os
import sys
import re
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import urllib.request
import urllib.parse

# ============ 配置 ============
GROUP_ID = "oc_c6883cd907e4d226736d87ce9c6c6d79"
APP_ID = "cli_a95612fc9ebddbc8"
APP_SECRET = "TBNvucvbHCHTeKqYtQ7PGfu1ANe0FSmb"

# 女团关键词
GROUP_KEYWORDS = [
    'aespa', 'blackpink', 'newjeans', 'ive', 'lesserafim', 'red velvet', 'twice',
    'babymonster', 'illit', 'riize', 'zerobaseone', 'nmixx', 'gIdle', 'gidle',
    'straykids', 'ateez', 'txt', 'enhypen',
]

PROXY = "socks5://127.0.0.1:10808"
XCRAWL_API_KEY = "xc-w7ylEVsaYLNXlYYhOP1tEzthyljoAGVrUjQOwCtEKAFadgps"
XCRAWL_SEARCH_URL = "https://run.xcrawl.com/v1/search"

OUTPUT_DIR = os.path.expanduser("~/.hermes/cron/output/6706b1d82b7d")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============ 飞书推送 ============
def get_feishu_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode()).get("tenant_access_token", "")


def send_feishu_text(token, text):
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = json.dumps({
        "receive_id": GROUP_ID,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


# ============ XCrawl Search API ============
def xcrawl_search(query, limit=8):
    """用 XCrawl Search API 搜索，返回 [{title, url, date}]"""
    body = json.dumps({"query": query, "limit": limit})
    cmd = [
        "curl", "-s", "--socks5-hostname", "127.0.0.1:10808",
        "-X", "POST", XCRAWL_SEARCH_URL,
        "-H", f"Authorization: Bearer {XCRAWL_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", body,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if data.get("status") == "completed":
                return data.get("data", {}).get("data", [])
    except Exception as e:
        print(f"XCrawl error: {e}", file=sys.stderr)
    return []


def translate_title(text):
    """Google Translate 英译中"""
    try:
        encoded = urllib.parse.quote(text[:200])
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
        cmd = ["curl", "-s", "--socks5-hostname", "127.0.0.1:10808",
               "-X", "GET", url, "--header", "User-Agent: Mozilla/5.0"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            return "".join(item[0] for item in data[0] if item[0])
    except Exception as e:
        print(f"Translate error: {e}", file=sys.stderr)
    return text


# ============ Soompi RSS ============
def fetch_soompi_rss():
    """抓取 Soompi RSS"""
    url = "https://www.soompi.com/feed/"
    try:
        proxy_handler = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with opener.open(req, timeout=15000) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Soompi RSS error: {e}", file=sys.stderr)
    return ""


def parse_soompi_rss(xml_text):
    items = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.findall('.//item'):
            title = (item.find('title') or item.findtext('title') or '').strip()
            link = (item.find('link') or item.findtext('link') or '').strip()
            pub_date = (item.find('pubDate') or item.findtext('pubDate') or '').strip()
            if title and link:
                items.append({'title': title, 'link': link, 'pub_date': pub_date})
    except Exception as e:
        print(f"RSS parse error: {e}", file=sys.stderr)
    return items


# ============ 女团匹配 ============
def match_group(title):
    title_lower = title.lower()
    for kw in GROUP_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', title_lower):
            return kw.upper()
    return None


def is_recent(pub_date_str, cutoff):
    """判断发布时间是否在 cutoff 之后"""
    try:
        from email.utils import parsedate_to_datetime
        pub_dt = parsedate_to_datetime(pub_date_str)
        if pub_dt.tzinfo is None:
            pub_dt = pub_dt.replace(tzinfo=None)
        return pub_dt.replace(tzinfo=None) >= cutoff
    except Exception:
        return False


# ============ 主流程 ============
def main():
    cutoff = datetime.now() - timedelta(hours=48)
    all_items = []
    seen_titles = set()

    # ---- 来源1: XCrawl Search API（多团并行搜索）----
    print("Searching XCrawl for K-pop groups...", file=sys.stderr)
    for kw in GROUP_KEYWORDS[:8]:  # 最多8个关键词，避免 API 额度消耗太快
        results = xcrawl_search(f"{kw} K-pop 2026", limit=5)
        for r in results:
            title = r.get('title', '')
            if not title or title in seen_titles:
                continue
            # 简单过滤：标题必须包含女团关键词
            if match_group(title):
                seen_titles.add(title)
                all_items.append({
                    'title': title,
                    'link': r.get('url', ''),
                    'pub_date': r.get('date', ''),
                    'group': match_group(title),
                    'source': 'XCrawl'
                })

    # ---- 来源2: Soompi 中文 RSS（48小时内）----
    print("Fetching Soompi RSS...", file=sys.stderr)
    xml_text = fetch_soompi_rss()
    if xml_text:
        soompi_items = parse_soompi_rss(xml_text)
        print(f"Got {len(soompi_items)} items from Soompi", file=sys.stderr)
        for item in soompi_items:
            title = item['title']
            if title in seen_titles:
                continue
            group = match_group(title)
            if not group:
                continue
            if not is_recent(item['pub_date'], cutoff):
                continue
            seen_titles.add(title)
            all_items.append({**item, 'group': group, 'source': 'Soompi'})

    if not all_items:
        print("[SILENT]", file=sys.stdout)
        return

    # 去重（按标题前40字）
    seen_keys = set()
    unique = []
    for item in all_items:
        key = item['title'][:40]
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique.append(item)

    # 按 source 排序（XCrawl 优先）
    unique.sort(key=lambda x: 0 if x['source'] == 'XCrawl' else 1)

    # 生成 markdown 报告
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [
        f"🇰🇷 韩国女团每周资讯",
        f"**推送时间：** {now}",
        f"**来源：** XCrawl Search + Soompi RSS（48小时内）",
        "",
    ]

    for i, item in enumerate(unique[:30], 1):
        # 标题翻译
        title = item['title']
        if item['source'] == 'XCrawl' and not any('\u4e00' <= c for c in title):
            title = translate_title(title)
        lines.append(f"{i}. 【{item['group']}】{title}")
        if item.get('pub_date'):
            lines.append(f"   📅 {item['pub_date']}")
        lines.append("")

    content = '\n'.join(lines)

    # 保存本地备份
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    out_path = os.path.join(OUTPUT_DIR, f"kpop-{timestamp}.md")
    with open(out_path, 'w') as f:
        f.write(content)
    print(f"Wrote {len(content)} bytes to {out_path}", file=sys.stderr)

    # 直接发送飞书
    token = get_feishu_token()
    if token:
        resp = send_feishu_text(token, content)
        if resp.get("code") == 0:
            print("Feishu push success", file=sys.stderr)
        else:
            print(f"Feishu push failed: {resp}", file=sys.stderr)
    else:
        print("Failed to get Feishu token", file=sys.stderr)

    print(content)


if __name__ == '__main__':
    main()

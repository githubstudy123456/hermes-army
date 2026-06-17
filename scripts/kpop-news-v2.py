#!/usr/bin/env -S /usr/bin/python3
# -*- coding: utf-8 -*-
"""
韩国女团资讯抓取脚本 v2
- 主力：XCrawl Search API（覆盖 Allkpop/Twitter/Naver 等 Soompi RSS 覆盖不到的平台）
- 备选：Soompi RSS（via 代理）
合并去重后输出 markdown，cron 系统自动推送
"""
import os
import sys
import re
import json
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import urllib.request

# ========== 配置 ==========
GROUP_ID = "oc_c6883cd907e4d226736d87ce9c6c6d79"
OUTPUT_DIR = os.path.expanduser("~/.hermes/cron/output/6706b1d82b7d")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROXY = "socks5://127.0.0.1:10808"
XCRAWL_API_KEY = os.environ.get("XCRAWL_API_KEY", "xc-w7ylEVsaYLNXlYYhOP1tEzthyljoAGVrUjQOwCtEKAFadgps")

# 女团搜索关键词
GROUPS = {
    "aespa": ["aespa 2026", "aespa world tour", "aespa comeback", "aespa Karina Giselle Winter Ningning"],
    "BLACKPINK": ["BLACKPINK 2026", "BLACKPINK Jisoo Jennie Lisa Rosé", "BLACKPINK comeback tour"],
    "NewJeans": ["NewJeans 2026", "NewJeans comeback", "NewJeans Minji Hanni Danielle Haerin Hyein"],
    "IVE": ["IVE 2026", "IVE tour", "IVE Wonyoung Yujin Gaeul Rei Liz Leeseo"],
    "LE SSERAFIM": ["LE SSERAFIM 2026", "LE SSERAFIM comeback", "LE SSERAFIM宫胁咲良"],
    "Red Velvet": ["Red Velvet 2026", "Red Velvet comeback", "Red Velvet Irene Seulgi Joy Wendy"],
    "TWICE": ["TWICE 2026", "TWICE tour", "TWICE娜琏 志效 俞定延 凑崎纱夏 平井桃 名井南 孙彩瑛"],
}

MAX_PER_GROUP = 4   # 每组最多保留
XCRAWL_SEARCH_URL = "https://run.xcrawl.com/v1/search"

# 翻译缓存（避免同一标题重复翻译）
_trans_cache = {}


def translate_title(text):
    """英译中，带缓存，走 curl + 代理"""
    if not text:
        return text
    key = text[:60]
    if key in _trans_cache:
        return _trans_cache[key]
    try:
        import subprocess, urllib.parse, json
        clean = text[:100].replace("!", "").replace("'", "").replace('"', "").replace("–", "-")
        encoded = urllib.parse.quote(clean)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
        cmd = ["curl", "-s", "--socks5-hostname", "127.0.0.1:10808", url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            translated = "".join(item[0] for item in data[0] if item[0])
            _trans_cache[key] = translated
            return translated
    except Exception as e:
        print(f"翻译失败 '{text[:30]}': {e}", file=sys.stderr)
    return text


def translate_titles_concurrent(texts, concurrency=5):
    """并发翻译多条文案，返回 {text: translated}"""
    import concurrent.futures, subprocess, urllib.parse, json

    def _translate_one(text):
        if not text:
            return text, text
        key = text[:60]
        if key in _trans_cache:
            return text, _trans_cache[key]
        try:
            clean = text[:100].replace("!", "").replace("'", "").replace('"', "").replace("–", "-")
            encoded = urllib.parse.quote(clean)
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
            cmd = ["curl", "-s", "--socks5-hostname", "127.0.0.1:10808", url]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                translated = "".join(item[0] for item in data[0] if item[0])
                _trans_cache[key] = translated
                return text, translated
        except Exception:
            pass
        return text, text

    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(_translate_one, t): t for t in texts}
        for fut in concurrent.futures.as_completed(futures):
            orig, translated = fut.result()
            results[orig] = translated
    return results


# ========== XCrawl Search API（via curl subprocess） ==========
def xcrawl_search(query, limit=5):
    """调用 XCrawl Search API（走 curl --socks5-hostname 代理），返回 results 列表"""
    body = json.dumps({"query": query, "limit": limit})
    cmd = [
        "curl", "-s", "--socks5-hostname", "127.0.0.1:10808",
        "-X", "POST", "https://run.xcrawl.com/v1/search",
        "-H", f"Authorization: Bearer {XCRAWL_API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", body,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        if result.returncode != 0:
            print(f"curl error (rc={result.returncode}): {result.stderr[:100]}", file=sys.stderr)
            return []
        data = json.loads(result.stdout)
        if data.get("status") == "completed":
            return data.get("data", {}).get("data", [])
        else:
            print(f"XCrawl query '{query}' status={data.get('status')}", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"JSON error for '{query}': {e}", file=sys.stderr)
    except Exception as e:
        print(f"XCrawl search error for '{query}': {e}", file=sys.stderr)
    return []


# ========== Soompi RSS（备选） ==========
def fetch_soompi_rss():
    url = "https://ch.soompi.com/feed/"
    try:
        proxy_handler = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY})
        opener = urllib.request.build_opener(proxy_handler)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with opener.open(req, timeout=10000) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"Soompi RSS error: {e}", file=sys.stderr)
    return ""


def parse_soompi_rss(xml_text):
    items = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            if title and link:
                items.append({"title": title, "link": link, "pub_date": pub_date, "source": "Soompi"})
    except Exception as e:
        print(f"Soompi parse error: {e}", file=sys.stderr)
    return items


# ========== 去重 & 女团匹配 ==========
GROUP_KEYWORDS = [
    "aespa", "blackpink", "newjeans", "ive", "lesserafim", "red velvet", "twice",
    "babymonster", "illit", "riize", "zerobaseone",
]

def match_group(title):
    tl = title.lower()
    for kw in GROUP_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", tl):
            return kw.upper()
    return None


def normalize_title(title):
    """提取标题前40字用于去重"""
    return re.sub(r"\s+", " ", title.strip())[:40].lower()


# ========== 主流程 ==========
def main():
    cutoff = datetime.now() - timedelta(hours=48)
    all_items = []
    seen_titles = set()

    # 1. XCrawl Search API（主力）
    print("=== XCrawl Search API ===", file=sys.stderr)
    xcrawl_total = 0
    for group, queries in GROUPS.items():
        for query in queries:
            results = xcrawl_search(query, limit=5)
            xcrawl_total += len(results)
            for r in results:
                title = r.get("title", "").strip()
                url = r.get("url", "").strip()
                desc = r.get("description", "").strip()
                pub = r.get("published_date", "")
                if not title or not url:
                    continue
                key = normalize_title(title)
                if key in seen_titles:
                    continue
                seen_titles.add(key)
                all_items.append({
                    "title": title,
                    "link": url,
                    "description": desc,
                    "pub_date": pub,
                    "group": group.upper(),
                    "source": "XCrawl",
                })
            # 每组限制
            group_items = [i for i in all_items if i["group"] == group.upper()]
            if len(group_items) >= MAX_PER_GROUP:
                excess = group_items[MAX_PER_GROUP:]
                for ex in excess:
                    all_items.remove(ex)
    print(f"XCrawl: fetched {xcrawl_total} raw, kept {len(all_items)} after dedup", file=sys.stderr)

    # 2. Soompi RSS（备选）
    print("=== Soompi RSS ===", file=sys.stderr)
    xml_text = fetch_soompi_rss()
    if xml_text:
        soompi_items = parse_soompi_rss(xml_text)
        soompi_matched = 0
        for item in soompi_items:
            group = match_group(item["title"])
            if not group:
                continue
            # 时间过滤
            try:
                from email.utils import parsedate_to_datetime
                pub_dt = parsedate_to_datetime(item["pub_date"])
                if pub_dt.tzinfo is None:
                    pub_dt = pub_dt.replace(tzinfo=None)
                if pub_dt.replace(tzinfo=None) < cutoff:
                    continue
            except Exception:
                pass
            key = normalize_title(item["title"])
            if key in seen_titles:
                continue
            seen_titles.add(key)
            all_items.append({**item, "group": group, "source": "Soompi"})
            soompi_matched += 1
        print(f"Soompi: matched {soompi_matched} items in 48h window", file=sys.stderr)

    if not all_items:
        print("[SILENT]", file=sys.stdout)
        return

    # 3. 批量并发翻译所有标题
    print("=== 翻译标题 ===", file=sys.stderr)
    all_titles = list({item["title"] for item in all_items})
    trans_map = translate_titles_concurrent(all_titles, concurrency=6)
    for item in all_items:
        item["title"] = trans_map.get(item["title"], item["title"])

    # 3. 生成 markdown
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# 🇰🇷 韩国女团每周资讯",
        f"**推送时间：** {now}",
        f"**来源：** XCrawl Search API（英译中）+ Soompi 中文",
        "",
    ]

    # 按 group 分组展示
    current_group = None
    for i, item in enumerate(all_items, 1):
        g = item.get("group", "?")
        if g != current_group:
            lines.append(f"### {g}")
            current_group = g
        title = item["title"]
        link = item["link"]
        pub = item.get("pub_date", "")
        src = item.get("source", "")
        lines.append(f"{i}. [{title}]({link})")
        meta = []
        if pub:
            meta.append(pub[:16])
        if src:
            meta.append(src)
        if meta:
            lines.append(f"   📅 {' | '.join(meta)}")
        lines.append("")

    content = "\n".join(lines)

    # 4. 写入 output 目录
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_path = os.path.join(OUTPUT_DIR, f"{timestamp}.md")
    with open(out_path, "w") as f:
        f.write(content)

    print(f"Wrote {len(content)} bytes to {out_path}", file=sys.stderr)
    print(content)


if __name__ == "__main__":
    main()

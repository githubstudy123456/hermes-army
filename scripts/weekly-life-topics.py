#!/usr/bin/env python3
"""
每周生活选题推送 - 周五 14:00 推送
数据源: National Geographic / Smithsonian Magazine / Condé Nast Traveler
搜索: 不同文化体验、不同生活方式的高质量内容选题
推送: 直接通过飞书 API 发送，不走文件落地
"""

import urllib.request
import urllib.parse
import json
import re
import sys
import tempfile
import os
import subprocess
from datetime import datetime

# ── 配置 ──────────────────────────────────────────
PROXY_SOCKS    = "socks5://127.0.0.1:10808"
FEISHU_CHAT    = "oc_c6883cd907e4d226736d87ce9c6c6d79"
PLAYWRIGHT_BIN = "/home/ubuntu/.hermes/hermes-agent/venv/bin/python3"
MAX_ITEMS      = 5

# ── 飞书推送 ───────────────────────────────────────
def get_feishu_token() -> str:
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

# ── Playwright 通用抓取 ─────────────────────────────
def playwright_fetch(url: str, css_selector: str, page_key: str, timeout: int = 60) -> list:
    """通用 Playwright 抓取函数（Python 版）"""
    script = f"""
import sys, json
sys.path.insert(0, '/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages')
from playwright.sync_api import sync_playwright

url = '{url}'
selector = '{css_selector}'
page_key = '{page_key}'

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage']
    )
    page = browser.new_page(
        viewport={{'width': 1280, 'height': 900}},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page.goto(url, timeout=70000, wait_until='domcontentloaded')
    page.wait_for_timeout(5000)
    handles = page.query_selector_all(selector)
    results = []
    seen = {{}}
    for h in handles:
        try:
            text = h.inner_text().strip()
            href = h.get_attribute('href') or ''
            key = text[:25]
            if text and 15 < len(text) < 120 and href.startswith('http') and not seen.get(key):
                seen[key] = True
                results.append({{'text': text, 'href': href}})
                if len(results) >= 8:
                    break
        except Exception:
            pass
    print(page_key + ':' + json.dumps(results))
    browser.close()
"""
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
    tmp.write(script)
    tmp.close()
    try:
        r = subprocess.run([PLAYWRIGHT_BIN, tmp.name],
                           capture_output=True, text=True, timeout=timeout)
        out = r.stdout
        idx = out.find(page_key + ':')
        if idx >= 0:
            return json.loads(out[idx + len(page_key) + 1:].strip())
        if r.stderr and 'TimeoutError' not in r.stderr and 'timeout' not in r.stderr.lower():
            print(f"playwright stderr: {r.stderr[:300]}", file=sys.stderr)
    except subprocess.TimeoutExpired:
        print(f"playwright_fetch 超时 ({url})，跳过", file=sys.stderr)
    except Exception as e:
        print(f"playwright_fetch 异常 ({url}): {e}", file=sys.stderr)
    finally:
        os.unlink(tmp.name)
    return []

# ── 三大来源 ───────────────────────────────────────
def fetch_natgeo() -> list:
    url = "https://www.nationalgeographic.com/travel"
    selector = "h2 a, h3 a, a[data-component=\"card\"], a.article-card"
    return playwright_fetch(url, selector, "NATGEO")

def fetch_smithsonian() -> list:
    # Smithsonian 主页可能有更多内容
    url = "https://www.smithsonianmag.com/"
    selector = "h2 a, h3 a"
    return playwright_fetch(url, selector, "SMITH")

def translate_to_chinese(text: str) -> str:
    if not text or not text.strip():
        return ""
    for attempt in range(3):
        try:
            encoded = urllib.parse.quote_plus(text[:500])
            url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q=" + encoded
            proxy_handler = urllib.request.ProxyHandler({'http': PROXY_SOCKS, 'https': PROXY_SOCKS})
            opener = urllib.request.build_opener(proxy_handler)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with opener.open(req, timeout=20) as resp:
                data = resp.read().decode('utf-8')
            result = json.loads(data)
            if result[0]:
                translated = ''.join(item[0] for item in result[0] if item[0])
                if translated and translated != text:
                    return translated
                return text
            return text
        except Exception as e:
            print(f"翻译失败(尝试{attempt+1}): {e}", file=sys.stderr)
            import time; time.sleep(2)
    return text  # 3次失败后返回原文

def fetch_bbc_travel() -> list:
    # BBC Travel 稳定且质量高
    url = "https://www.bbc.com/travel"
    selector = "h2 a, h3 a"
    return playwright_fetch(url, selector, "BBC", timeout=120)

# ── 关键词过滤 ─────────────────────────────────────
LIFESTYLE_KW = [
    'culture', 'tradition', 'food', 'recipe', 'travel', 'destination',
    'local life', 'heritage', 'craft', 'artisan', 'festival', 'ritual',
    'architecture', 'community', 'indigenous', 'history', 'museum',
    'lifestyle', 'experience', 'immersive', 'authentic',
    '文化', '传统', '生活', '旅行', '体验', '建筑', '手工艺',
    '饮食', '节庆', '艺术', '历史', '民俗', '社区'
]

NOISE = [
    'crypto', 'bitcoin', 'stock', 'election', 'politic',
    'weather', 'storm', 'hurricane', 'earthquake',
    'coronavirus', 'covid', 'pandemic', 'vaccine'
]

def is_lifestyle(title: str) -> bool:
    t = title.lower()
    for n in NOISE:
        if n in t:
            return False
    for kw in LIFESTYLE_KW:
        if kw.lower() in t:
            return True
    return False

# ── 主流程 ─────────────────────────────────────────
def main():
    today = datetime.now().strftime("%Y-%m-%d")
    weekday_cn = ["周一","周二","周三","周四","周五","周六","周日"][datetime.now().weekday()]
    print(f"[{datetime.now().isoformat()}] 开始抓取每周生活选题...")

    all_items = []
    source_map = {
        "NATGEO": "National Geographic",
        "SMITH":  "Smithsonian Magazine",
        "BBC":    "BBC Travel"
    }

    for fetcher, key in [
        (fetch_natgeo, "NATGEO"),
        (fetch_smithsonian, "SMITH"),
        (fetch_bbc_travel, "BBC"),
    ]:
        try:
            items = fetcher()
            print(f"{key}: {len(items)} 条")
            for it in items:
                it['source'] = source_map.get(key, key)
                it['title'] = it.pop('text')      # 统一 title
                it['link']  = it.pop('href')       # 统一 link
            all_items.extend(items)
        except Exception as e:
            print(f"{key} 抓取异常: {e}", file=sys.stderr)

    # 过滤 + 去重
    seen = set()
    filtered = []
    for it in all_items:
        key = it['title'][:30].lower()
        if key and key not in seen and is_lifestyle(it['title']):
            seen.add(key)
            filtered.append(it)
    all_items = filtered[:MAX_ITEMS]

    if not all_items:
        # 备用：不过滤
        seen = set()
        for it in all_items:
            key = it['title'][:30].lower()
            if key and key not in seen:
                seen.add(key)
                filtered.append(it)
        all_items = filtered[:MAX_ITEMS]

    # ── 组装消息 ─────────────────────────────────
    lines = []
    lines.append(f"🌍 多元文化与生活方式内容选题周报")
    lines.append(f"📅 {today} ({weekday_cn})")
    lines.append(f"来源: National Geographic · Smithsonian Magazine · BBC Travel")
    lines.append("─" * 32)

    for i, item in enumerate(all_items, 1):
        title  = item['title'].strip()
        source = item.get('source', 'Web')
        link   = item.get('link', '')
        # 英文标题翻译为中文
        title_cn = translate_to_chinese(title)
        lines.append(f"📌 {i}｜{title_cn}")
        if title_cn != title:
            lines.append(f"   原文: {title}")
        lines.append(f"   来源: {source}")
        if link:
            lines.append(f"   链接: {link}")
        lines.append("")

    lines.append("─" * 32)
    lines.append(f"🤖 由 ⭐☁️ 自动生成 · {datetime.now().strftime('%H:%M:%S')}")
    lines.append("💡 选题可结合平台调性进一步细化，欢迎讨论！")

    content = "\n".join(lines)
    print(f"内容字数: {len(content)}，开始推送...")
    ok = feishu_send_text(content)
    print(f"推送{'成功' if ok else '失败'}")

if __name__ == '__main__':
    main()

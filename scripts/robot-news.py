#!/usr/bin/env python3
"""
机器人日报 — 机器人/AI/具身智能行业每日资讯
数据源：国际（直连+日本代理）+ 国内（直连）
推送：每天 09:00 → 飞书订阅群
"""

import subprocess, json, re, time, urllib.request, urllib.parse
from datetime import datetime

# ── 配置 ──────────────────────────────────────────────
CHAT_ID     = "oc_c6883cd907e4d226736d87ce9c6c6d79"
TODAY       = datetime.now().strftime("%Y-%m-%d")
MAX_ITEMS   = 16
JP_PROXY    = "socks5://207.56.226.147:10808"   # 日本服务器 xray 代理
LOCAL_PROXY = "socks5://127.0.0.1:10808"        # 本地备用代理

# ── SSH 隧道管理 ──────────────────────────────────────
# 日本代理通过 xray 直连 207.56.226.147:10808，无需 SSH 隧道
# curl --socks5-hostname 直接走 xray 端口

def check_jp_proxy():
    """验证日本代理是否可用"""
    r = subprocess.run(
        ["curl", "-s", "--socks5-hostname", "207.56.226.147:10808",
         "--connect-timeout", "6", "-o", "/dev/null", "-w", "%{http_code}",
         "https://www.google.com"],
        capture_output=True, text=True, timeout=12
    )
    return r.stdout and r.stdout.strip() in ("200", "301", "302")

# ── 网络请求 ──────────────────────────────────────────
JP_AVAILABLE = None  # None=未知, True=可用, False=不可用

def curl_get(url, use_jp_fallback=False, timeout=12):
    """直连请求，超时且 use_jp_fallback=True 时用日本代理重试一次"""
    global JP_AVAILABLE

    # 先直连
    try:
        r = subprocess.run(
            ["curl", "-s", "-L", "--max-time", str(timeout),
             "-A", "Mozilla/5.0 (compatible; robot-daily/1.0)", url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if r.stdout and len(r.stdout) > 100:
            return r.stdout
    except Exception:
        pass

    # 直连失败，日本代理兜底
    if use_jp_fallback:
        # 首次使用时检测代理可用性
        if JP_AVAILABLE is None:
            JP_AVAILABLE = check_jp_proxy()
            print(f"  [JP Proxy] 检测结果: {'可用 ✓' if JP_AVAILABLE else '不可用 ✗'}")

        if JP_AVAILABLE:
            for proxy in ["socks5h://207.56.226.147:10808", "socks5h://127.0.0.1:10809"]:
                try:
                    r2 = subprocess.run(
                        ["curl", "-s", "-L", "--max-time", str(timeout),
                         "--proxy", proxy,
                         "-A", "Mozilla/5.0 (compatible; robot-daily/1.0)", url],
                        capture_output=True, text=True, timeout=timeout + 8
                    )
                    if r2.stdout and len(r2.stdout) > 100:
                        print(f"  [JP Proxy] 代理成功: {url[:50]}")
                        return r2.stdout
                except Exception:
                    continue
    return ""

# ── RSS 解析 ──────────────────────────────────────────
def clean_summary(text: str) -> str:
    """去掉摘要中的作者、编辑等信息和多余空白"""
    if not text:
        return ""
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\s*作者\s*[|\/丨].*', '', text)
    text = re.sub(r'\s*编辑\s*[|\/丨].*', '', text)
    text = re.sub(r'\s*记者\s*[|\/丨].*', '', text)
    text = re.sub(r'\s*图注\s*[|\/丨].*', '', text)
    text = re.sub(r'\s*整理\s*[|\/丨].*', '', text)
    text = re.sub(r'\s*校对\s*.*', '', text)
    text = re.sub(r'36氪获悉[：:]?', '', text)
    text = re.sub(r'^[,，、\s]+', '', text)   # 去掉开头的多余标点
    text = re.sub(r'编者注[：:]?.*', '', text)
    text = re.sub(r'点击查看.*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_rss_block(block):
    title   = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', block)
    link    = re.search(r'<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>', block)
    desc    = re.search(r'<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>', block)
    summary = re.search(r'<summary type="html">(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</summary>', block)
    pubdate = re.search(r'<pubDate>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</pubDate>', block)
    raw_title = title.group(1).strip() if title else ""
    raw_desc  = (summary or desc).group(1).strip() if (summary or desc) else ""
    raw_title = re.sub(r'<[^>]+>', '', raw_title)
    raw_desc  = re.sub(r'<[^>]+>', '', raw_desc).strip()
    return raw_title, link.group(1).strip() if link else "", raw_desc, pubdate.group(1).strip() if pubdate else ""

# ── 关键词过滤 ────────────────────────────────────────
# 机器人/具身智能/自动驾驶 专属关键词（不含泛AI）
ROBOT_KW = [
    "robot", "humanoid", "具身", "人形机器人", "自动驾驶", "autonomous",
    "drone", "cobots", "agv", "amr", "机械臂", "机械手", "配送机器人",
    "手术机器人", "工业机器人", "service robot", "mobile robot",
    "Boston Dynamics", "Tesla Bot", "宇树", "Unitree", "智元", "傅利叶",
    "魔法原子", "追觅", "九号机器人", "DJI", "大疆", "深度解放", "AutoX",
    "Waymo", "Zoox", "Pony.ai", "文远知行", "小马智行", "图森未来",
    "robotic", "manipulator", "soft robot", "exoskeleton", "外骨骼",
    "robotics", " factories", "warehouse robot", "AMR", "UGV",
]

ROBOT_KW_TITLE = [
    "robot", "humanoid", "具身", "人形机器人", "自动驾驶", "autonomous",
    "drone", "cobots", "agv", "amr", "机械臂", "机械手", "配送机器人",
    "手术机器人", "industrial robot", "service robot", "mobile robot",
    "robotic", "exoskeleton", "外骨骼", "manipulator", "Boston Dynamics",
    "Tesla Bot", "Unitree", "宇树", "智元", "傅利叶", "魔法原子",
    "DJI", "大疆", "AutoX", "Waymo", "Zoox", "Pony.ai", "文远知行",
    "小马智行", "图森未来", "robitics", "humanoid",
]

ROBOT_KW_DESC = [
    # description 额外关键词（标题没有时补充判断）
    "humanoid robot", "autonomous driving", "self-driving",
    "具身智能", "具身机器人", "人形机器人",
]

def is_robot_news(title, desc):
    text_title = title.lower()
    text_desc  = (desc or "").lower()
    text       = text_title + " " + text_desc
    # 标题直接命中关键词 → 通过
    if any(k.lower() in text_title for k in ROBOT_KW_TITLE):
        return True
    # 标题没有，description 有额外关键词 → 通过
    if any(k.lower() in text_desc for k in ROBOT_KW_DESC):
        return True
    return False

# ── 国际数据源（直连+日本代理）─────────────────────────
def fetch_techcrunch():
    items = []
    xml = curl_get("https://techcrunch.com/category/robotics/feed/", use_jp_fallback=True)
    if not xml:
        xml = curl_get("https://techcrunch.com/category/artificial-intelligence/feed/", use_jp_fallback=True)
    for block in re.findall(r'<item>(.*?)</item>', xml, re.DOTALL):
        title, link, desc, pubdate = parse_rss_block(block)
        if title and is_robot_news(title, desc):
            items.append({"title": title[:80], "link": link, "date": pubdate, "source": "TechCrunch", "summary": desc[:150] + "…" if len(desc) > 150 else desc, "translate": True})
    return items[:6]

def fetch_venturebeat():
    items = []
    xml = curl_get("https://venturebeat.com/category/ai/feed/", use_jp_fallback=True)
    for block in re.findall(r'<item>(.*?)</item>', xml, re.DOTALL):
        title, link, desc, pubdate = parse_rss_block(block)
        if title and is_robot_news(title, desc):
            items.append({"title": title[:80], "link": link, "date": pubdate, "source": "VentureBeat", "summary": desc[:150] + "…" if len(desc) > 150 else desc, "translate": True})
    return items[:5]

def fetch_wired_ai():
    items = []
    xml = curl_get("https://www.wired.com/feed/tag/ai/latest/rss", use_jp_fallback=True)
    for block in re.findall(r'<item>(.*?)</item>', xml, re.DOTALL):
        title, link, desc, pubdate = parse_rss_block(block)
        if title and is_robot_news(title, desc):
            items.append({"title": title[:80], "link": link, "date": pubdate, "source": "Wired AI", "summary": desc[:150] + "…" if len(desc) > 150 else desc, "translate": True})
    return items[:5]

def fetch_the_verge():
    items = []
    xml = curl_get("https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", use_jp_fallback=True)
    if not xml:
        xml = curl_get("https://www.theverge.com/rss/robots/index.xml", use_jp_fallback=True)
    for block in re.findall(r'<entry>(.*?)</entry>', xml, re.DOTALL):
        title, link, desc, pubdate = parse_rss_block(block)
        if title and is_robot_news(title, desc):
            items.append({"title": title[:80], "link": link, "date": pubdate, "source": "The Verge", "summary": desc[:150] + "…" if len(desc) > 150 else desc, "translate": True})
    return items[:5]

def fetch_spectrum():
    """IEEE Spectrum — 机器人相关内容"""
    items = []
    xml = curl_get("https://spectrum.ieee.org/feeds/feed.rss", use_jp_fallback=True)
    for block in re.findall(r'<item>(.*?)</item>', xml, re.DOTALL):
        title, link, desc, pubdate = parse_rss_block(block)
        if title and is_robot_news(title, desc):
            items.append({"title": title[:80], "link": link, "date": pubdate, "source": "IEEE Spectrum", "summary": desc[:150] + "…" if len(desc) > 150 else desc, "translate": True})
    return items[:5]

# ── 国内数据源（直连）───────────────────────────────
DOMESTIC_KW = [
    "机器人", "人形", "具身", "自动驾驶", "无人机", "机械臂",
    "配送机器人", "手术机器人", "工业机器人", "AMR", "AGV",
    "宇树", "智元", "傅利叶", "魔法原子", "追觅", "大疆", "九号",
    "AutoX", "文远知行", "小马智行", "图森", "Waymo",
    "robot", "humanoid", "具身智能", "智能驾驶",
]

# 爆火山寨专用 — 更精准，专注机器人行业热点
TRENDING_KW = [
    "机器人", "人形机器人", "具身智能", "自动驾驶", "无人车",
    "Boston Dynamics", "宇树", "智元", "傅利叶", "魔法原子",
    "Tesla Bot", "Unitree", "宇树科技", "追觅科技", "大疆",
    "AutoX", "Waymo", "Zoox", "Pony.ai", "小马智行", "图森未来",
    "配送机器人", "手术机器人", "工业机器人", "仓储机器人",
    "humanoid robot", "具身", "physical intelligence", "Figure AI",
]

def is_domestic_robot_news(title, desc):
    text = (title + " " + desc).lower()
    return any(k in text for k in DOMESTIC_KW)

def is_trending_robot_news(title):
    """爆火山寨过滤 — 更精准，不接受宽泛词如'无人机'单独出现"""
    text = title.lower()
    return any(k.lower() in text for k in TRENDING_KW)

def fetch_36kr():
    items = []
    xml = curl_get("https://36kr.com/feed", timeout=15)
    for block in re.findall(r'<item>(.*?)</item>', xml, re.DOTALL):
        title, link, desc, pubdate = parse_rss_block(block)
        if title and is_domestic_robot_news(title, desc):
            items.append({"title": title[:80], "link": link, "date": pubdate, "source": "36氪", "summary": desc[:150] + "…" if len(desc) > 150 else desc})
    return items[:8]

def fetch_leiphone():
    items = []
    xml = curl_get("https://www.leiphone.com/feed", timeout=15)
    for block in re.findall(r'<item>(.*?)</item>', xml, re.DOTALL):
        title, link, desc, pubdate = parse_rss_block(block)
        if title and is_domestic_robot_news(title, desc):
            items.append({"title": title[:80], "link": link, "date": pubdate, "source": "雷锋网", "summary": desc[:150] + "…" if len(desc) > 150 else desc})
    return items[:8]

def fetch_ifanr():
    items = []
    xml = curl_get("https://www.ifanr.com/feed", timeout=15)
    for block in re.findall(r'<item>(.*?)</item>', xml, re.DOTALL):
        title, link, desc, pubdate = parse_rss_block(block)
        if title and is_domestic_robot_news(title, desc):
            items.append({"title": title[:80], "link": link, "date": pubdate, "source": "爱范儿", "summary": desc[:150] + "…" if len(desc) > 150 else desc})
    return items[:5]

def fetch_toutiao_trending():
    """今日头条热榜 — 通过 bb-browser 抓取，筛选机器人相关内容"""
    try:
        import subprocess, json as _json
        r = subprocess.run(
            ["bb-browser", "site", "toutiao/hot", "--json"],
            capture_output=True, text=True, timeout=20
        )
        data = _json.loads(r.stdout)
        items = []
        for it in data.get("data", {}).get("items", []):
            title = it.get("title", "")
            url = it.get("url", "")
            hot_val = it.get("hot_value", "")
            if title and is_trending_robot_news(title):
                items.append({
                    "title": title[:80], "link": url,
                    "date": TODAY, "source": "头条热榜",
                    "summary": f"热度 {hot_val}"
                })
        return items[:5]
    except Exception as e:
        print(f"  [头条热榜] 抓取失败: {e}")
        return []

# ── 去重 ──────────────────────────────────────────────
def dedup(items):
    seen, out = set(), []
    for it in items:
        key = it["title"][:28].lower()
        if key and key not in seen:
            seen.add(key)
            out.append(it)
    return out

GT_PROXY    = "socks5://207.56.226.147:10808"   # 日本服务器 xray 代理

def translate_to_chinese(text: str) -> str:
    """用 MyMemory 免费 API 翻译英文到中文（curl 直连）"""
    if not text or not text.strip():
        return text
    try:
        encoded = urllib.parse.quote_plus(text[:450])
        url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair=en|zh"
        r = subprocess.run(
            ["curl", "-s", "--max-time", "12", url],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(r.stdout)
        return data.get("responseData", {}).get("translatedText", text).strip()
    except Exception as e:
        print(f"  [翻译] 失败: {e}")
        return text

# ── 日期 ──────────────────────────────────────────────
_MONTH_MAP = {"jan":"01","feb":"02","mar":"03","apr":"04","may":"05","jun":"06",
              "jul":"07","aug":"08","sep":"09","oct":"10","nov":"11","dec":"12"}

def fmt_date(d):
    if not d:
        return "今天"
    d = re.sub(r'^[A-Za-z]+,\s+', '', d.strip())
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(d[:len("2026-05-18 00:00:00")], fmt).strftime("%m-%d")
        except Exception:
            pass
    m = re.match(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', d)
    if m:
        day, mon, year = m.group(1), m.group(2).lower()[:3], m.group(3)
        if mon in _MONTH_MAP:
            return f"{_MONTH_MAP[mon]}-{int(day):02d}"
    return "今天"

# ── 报告生成 ──────────────────────────────────────────
def build_report(items):
    header = (
        f"🤖 机器人日报\n"
        f"📅 {TODAY}  |  🌍 IEEE · TechCrunch · VentureBeat · Wired · The Verge\n"
        f"         🇨🇳 36氪 · 雷锋网 · 爱范儿 · 头条热榜\n"
        "═══════════════════════════════════════════════\n"
    )
    lines = []
    for it in items[:MAX_ITEMS]:
        title, summary, date, src = it["title"], it.get("summary", ""), fmt_date(it["date"]), it["source"]
        if len(title) > 52:
            title = title[:49] + "…"
        lines.append(f"【{src}】{title}  ({date})")
        if summary:
            s = clean_summary(summary).replace("\n", " ").strip()
            if len(s) > 85:
                s = s[:82] + "…"
            lines.append(f"   {s}")
        lines.append("")
    footer = (
        "═══════════════════════════════════════════════\n"
        "🤖 机器人日报 · 每日 09:00 自动推送\n"
        "💬 Hermes Agent"
    )
    return header + "\n".join(lines) + footer

# ── 飞书推送 ──────────────────────────────────────────
def get_token():
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"app_id": "cli_a95612fc9ebddbc8", "app_secret": "TBNvucvbHCHTeKqYtQ7PGfu1ANe0FSmb"})
    ]
    return json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout).get("tenant_access_token", "")

def push_feishu(text):
    token = get_token()
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    body = json.dumps({"receive_id": CHAT_ID, "msg_type": "text", "content": json.dumps({"text": text})})
    cmd = ["curl", "-s", "-X", "POST", url, "-H", f"Authorization: Bearer {token}",
           "-H", "Content-Type: application/json", "-d", body]
    return subprocess.run(cmd, capture_output=True, text=True).stdout

# ── 主程序 ──────────────────────────────────────────────
def main():
    print(f"[{TODAY}] 机器人日报开始抓取...")

    # 国际源（直连优先，失败用日本代理兜底）
    print("  抓取国际源...")
    tc_items = fetch_techcrunch()
    vb_items = fetch_venturebeat()
    wd_items = fetch_wired_ai()
    tv_items = fetch_the_verge()
    sp_items = fetch_spectrum()

    # 国内源（直连）
    print("  抓取国内源...")
    kr_items = fetch_36kr()
    lf_items = fetch_leiphone()
    if_items = fetch_ifanr()

    # 爆火山寨（头条热榜）
    print("  抓取爆火山寨...")
    tt_items = fetch_toutiao_trending()

    # 翻译国际源内容
    print("  翻译国际源...")
    for items in [tc_items, vb_items, wd_items, tv_items, sp_items]:
        for it in items:
            if it.get("translate"):
                it["title"] = translate_to_chinese(it["title"])
                if it.get("summary"):
                    it["summary"] = translate_to_chinese(it["summary"])

    all_items = dedup(tc_items + vb_items + wd_items + tv_items + sp_items + kr_items + lf_items + if_items + tt_items)

    print(f"  TechCrunch:  {len(tc_items)} 条 | VentureBeat: {len(vb_items)} 条")
    print(f"  Wired:       {len(wd_items)} 条 | The Verge:   {len(tv_items)} 条")
    print(f"  IEEE:        {len(sp_items)} 条")
    print(f"  36氪:        {len(kr_items)} 条 | 雷锋网: {len(lf_items)} 条 | 爱范儿: {len(if_items)} 条")
    print(f"  头条热榜:    {len(tt_items)} 条 | 去重后: {len(all_items)} 条")

    report = build_report(all_items)

    out_path = f"/home/ubuntu/.hermes/cron/output/robot-news-{TODAY}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  已保存: {out_path}")

    result = push_feishu(report)
    print(f"  飞书: {result[:80]}")

    return report

if __name__ == "__main__":
    main()

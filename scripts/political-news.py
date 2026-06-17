#!/usr/bin/env python3
"""
政治要闻日报 - 每日 8:30 推送
数据源:
  1. BBC World News RSS (英文, 需代理) - 国际政治
  2. 观察者网 (中文, Playwright 抓取) - 国内视角国际政治
翻译: Google Translate (免费接口, 无需API Key)
会议提醒: 内置中国重大会议日历，临近时自动插入提醒
推送: 直接通过飞书 API 发送，不走文件落地
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
import subprocess
import tempfile
from datetime import datetime

# ── 配置 ──────────────────────────────────────────
PROXY_SOCKS   = "socks5://127.0.0.1:10808"
FEISHU_TOKEN  = "Y2hpbi1hZ2VudDpBcmdvbnRlY2g1MDE="   # base64 AppCoreToken
FEISHU_CHAT   = "oc_c6883cd907e4d226736d87ce9c6c6d79"

BBC_RSS       = "https://feeds.bbci.co.uk/news/world/rss.xml"
MAX_ITEMS     = 16
PLAYWRIGHT_BIN = "/home/ubuntu/.hermes/hermes-agent/venv/bin/python3"

# ── 关键词 & 过滤 ──────────────────────────────────
POLITICAL_KEYWORDS = [
    'trump', 'biden', 'putin', 'xi', 'zelensky', 'russia', 'ukraine', 'china',
    'us ', 'u.s.', 'america', 'europe', 'eu ', 'nato', 'iran', 'israel', 'hamas',
    'taiwan', 'sanction', 'summit', 'election', 'war', 'military',
    'diplomat', 'treaty', 'un ', 'security council', 'nuclear', 'missile', 'taliban',
    'north korea', 'south korea', 'japan', 'indonesia', 'malaysia', 'philippine',
    'senate', 'congress', 'parliament', 'president', 'minister', 'prime minister',
    'white house', 'kremlin', 'beijing', 'moscow', 'brussels',
    'g7', 'g20', 'asean', 'trade war', 'tariff', 'ceasefire',
    'immigration', 'refugee', 'border', 'embassy', 'consul',
    'middle east', 'asia', 'pacific', 'south china sea',
    'icc', 'international criminal', 'war crime', 'human right',
    'macron', 'starmer', 'khan', 'modi', 'erdogan', 'netanyahu', 'bin salman', 'kim jong',
    'blinken', 'sullivan', 'sino',
    '台湾', '统一', '中美元首', '中美关系', '俄乌', '普京', '泽连斯基',
    '习近平', '拜登', '特朗普', '联合国', '安理会', '制裁', '核',
    '中东', '欧洲', '北约', '东盟', 'G7', 'G20', '峰会', '外长',
    '总统', '总理', '议会', '国会', '参议院', '众议院',
    '战争', '军事', '冲突', '停火', '和谈', '外交', '访问',
    '日本', '韩国', '朝鲜', '菲律宾', '伊朗', '以色列', '加沙', '哈马斯', '沙特', '土耳其',
    '英国', '法国', '德国', '澳大利亚', '加拿大', '印度',
    '将军', '州长', '撤换', '当选', '连任', '胜选', '惨败',
    '美军', '俄军', '前线', '空袭',
]

NOISE_PATTERNS = [
    'dog', 'dogs', 'puppy', 'chocolate', 'milka', 'candy', 'sweet',
    'cruise', 'ship', 'norovirus', 'passenger', 'hantavirus',
    'everest', 'mount climb', 'climber', 'summit attempt',
    'football', 'soccer', 'tennis', 'basketball', 'sport', 'match', 'game',
    'festival', 'concert', 'music', 'award', 'oscar', 'grammy',
    'weather', 'storm', 'hurricane', 'flood', 'earthquake', 'tsunami',
    'bitcoin', 'crypto', 'stock market', 'shares',
    'instagram', 'tiktok', 'viral', 'recipe', 'cook', 'food', 'restaurant',
    'hotel', 'airbnb', 'travel', 'tourism',
    'ebola', 'virus outbreak', 'health emergency',
    'air show', 'fighter jet', 'aircraft collision', 'drone crash',
    'tennis', 'marathon', 'running race',
]

MEETING_CALENDAR = [
    {
        "name": "全国两会",
        "次年": "3月3日（政协）/ 3月5日（人大）",
        "提醒提前": 7,
        "关键词": ["全国两会", "政协", "人大", "政府工作报告", "总理报告"],
        "优先级": "⭐⭐⭐⭐⭐",
        "说明": "中国最高权力机关，每年一次，会期约10天"
    },
    {
        "name": "中央经济工作会议",
        "次年": "12月上中旬",
        "提醒提前": 14,
        "关键词": ["中央经济工作", "经济工作会", "稳增长", "宏观调控"],
        "优先级": "⭐⭐⭐⭐⭐",
        "说明": "年度最强经济政策信号，定调次年经济总基调"
    },
    {
        "name": "中央农村工作会议",
        "次年": "12月下旬（紧接经济工作会）",
        "提醒提前": 7,
        "关键词": ["中央农村工作", "三农", "乡村振兴", "粮食安全"],
        "优先级": "⭐⭐⭐⭐",
        "说明": "紧接经济工作会之后，连续出重磅信号"
    },
    {
        "name": "三中全会",
        "次年": "次年2-3月（党代会次年）",
        "提醒提前": 30,
        "关键词": ["三中全会", "深化改革", "全面深化改革", "机构改革"],
        "优先级": "⭐⭐⭐⭐⭐",
        "说明": "历次定走向：十一届/十八届/十九届三中全会均为重大转折点"
    },
    {
        "name": "二十一大",
        "次年": "2027年秋",
        "提醒提前": 60,
        "关键词": ["二十大", "二十一大", "党代会", "中央委员会"],
        "优先级": "⭐⭐⭐⭐",
        "说明": "每5年一次，换届年份（逢2/7结尾），今年是筹备关键期"
    },
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
    """直接发文本消息到飞书群（无需先写入文件）"""
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
def is_political(title: str) -> bool:
    t = title.lower()
    for noise in NOISE_PATTERNS:
        if noise in t:
            return False
    for kw in POLITICAL_KEYWORDS:
        if kw in t:
            return True
    return False

def fetch_via_proxy(url: str, timeout: int = 15) -> str:
    proxy_handler = urllib.request.ProxyHandler({'http': PROXY_SOCKS, 'https': PROXY_SOCKS})
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; political-news-bot/1.0)'})
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

def fetch_bbc_articles_detail(items: list) -> list:
    """用 Playwright 打开每条 BBC 文章链接，提取正文段落"""
    if not items:
        return items
    code = (
        "import sys,json\\n"
        "sys.path.insert(0,'/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages')\\n"
        "from playwright.sync_api import sync_playwright\\n"
        "article_links = sys.stdin.read().strip().split('\\n')\\n"
        "results = {}\\n"
        "with sync_playwright() as p:\\n"
        "  b=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage'])\\n"
        "  for link in article_links[:6]:\\n"
        "    if not link: continue\\n"
        "    try:\\n"
        "      page=b.new_page(viewport={'width':1280,'height':900},user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')\\n"
        "      page.goto(link.strip(),timeout=20000,wait_until='domcontentloaded')\\n"
        "      page.wait_for_timeout(2000)\\n"
        "      paras=page.eval_on_selector_all('article p','function(es){return es.map(e=>e.innerText.trim()).filter(t=>t.length>50).slice(0,3).join(\" \")} '\\n"
        "      results[link.strip()] = paras\\n"
        "      page.close()\\n"
        "    except: results[link.strip()]=''\\n"
        "  b.close()\\n"
        "sys.stdout.write('ARTICLES:'+json.dumps(results))\\n"
    )
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
    tmp.write(code)
    tmp.close()
    try:
        links_str = '\n'.join(it['link'] for it in items if it.get('link'))
        r = subprocess.run([PLAYWRIGHT_BIN, tmp.name], input=links_str, capture_output=True, text=True, timeout=120)
        out = r.stdout
        idx = out.find('ARTICLES:')
        if idx >= 0:
            articles_data = json.loads(out[idx+len('ARTICLES:'):])
            # 把提取的正文段落合并到对应 item
            for it in items:
                link = it.get('link', '')
                if link in articles_data and articles_data[link]:
                    para = articles_data[link][:300]
                    if it.get('description'):
                        it['description'] = para + ' ' + it['description']
                    else:
                        it['description'] = para
    except Exception as e:
        print(f"BBC文章详情抓取失败: {e}", file=sys.stderr)
    finally:
        os.unlink(tmp.name)
    return items

def parse_bbc_rss(xml_content: str) -> list:
    items = []
    root = ET.fromstring(xml_content)
    for item in root.findall('.//item'):
        title = (item.findtext('title') or '').strip()
        description = (item.findtext('description') or '').strip()
        link = (item.findtext('link') or '').strip()
        pub_date = (item.findtext('pubDate') or '').strip()
        if title:
            items.append({'title': clean_html(title), 'description': clean_html(description), 'link': link, 'pub_date': pub_date, 'source': 'BBC World'})
    return items

def fetch_guancha_politics() -> list:
    items = []
    code = (
        "import sys,json\n"
        "sys.path.insert(0,'/home/ubuntu/.hermes/hermes-agent/venv/lib/python3.11/site-packages')\n"
        "from playwright.sync_api import sync_playwright\n"
        "with sync_playwright() as p:\n"
        "  b=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage','--disable-blink-features=AutomationControlled'])\n"
        "  page=b.new_page(viewport={'width':1280,'height':900},user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',locale='zh-CN')\n"
        "  page.goto('https://www.guancha.cn/internation/',timeout=30000,wait_until='domcontentloaded')\n"
        "  page.wait_for_timeout(3000)\n"
        "  data=page.eval_on_selector_all('h4 a,a[href*=\"/internation/\"][href*=\".shtml\"]','function(es){var s={},r=[];for(var i=0;i<es.length;i++){var e=es[i],t=e.innerText.trim(),h=e.href||\"\";var k=t.substring(0,30);if(t.length>5&&t.length<100&&!s[k]&&h.indexOf(\"/internation/\")>-1){s[k]=true;r.push({text:t,href:h})}}return r.slice(0,12)}')\n"
        "  sys.stdout.write('GUANCHA_DATA:'+json.dumps(data))\n"
        "  b.close()\n"
    )
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8')
    tmp.write(code)
    tmp.close()
    try:
        r = subprocess.run([PLAYWRIGHT_BIN, tmp.name], capture_output=True, text=True, timeout=60)
        out = r.stdout
        idx = out.find('GUANCHA_DATA:')
        if idx >= 0:
            data_str = out[idx+len('GUANCHA_DATA:'):].strip()
            data = json.loads(data_str)
            for item in data:
                items.append({'title': item['text'], 'description': '', 'link': item['href'], 'pub_date': '', 'source': '观察者网'})
    except Exception as e:
        print(f"观察者网抓取失败: {e}", file=sys.stderr)
    finally:
        os.unlink(tmp.name)
    return items

def get_upcoming_meeting_reminders() -> list:
    today = datetime.now()
    reminders = []
    month = today.month
    for meeting in MEETING_CALENDAR:
        triggered = False
        reason = ""
        if month == 12:
            triggered = True
            reason = f"⚠️ 【{meeting['优先级']}】{meeting['name']} 临近！\n提前量：约{meeting['提醒提前']}天 | {meeting.get('次年', '')}\n聚焦：{meeting['说明']}"
        if meeting["name"] == "全国两会":
            if month in [2, 3]:
                triggered = True
                reason = f"⚠️ 【{meeting['优先级']}】{meeting['name']} 临近！\n提前量：约{meeting['提醒提前']}天 | {meeting.get('次年', '')}\n聚焦：{meeting['说明']}"
        if meeting["name"] == "三中全会":
            year = today.year
            if year % 10 == 3:
                if month in [1, 2, 3]:
                    triggered = True
                    reason = f"⚠️ 【{meeting['优先级']}】{meeting['name']} 临近！\n提前量：约{meeting['提醒提前']}天 | {meeting.get('次年', '')}\n聚焦：{meeting['说明']}"
        if "党代会" in meeting["name"] or "二十大" in meeting["name"]:
            if month == 10 and today.year in [2027, 2032, 2037]:
                triggered = True
                reason = f"⚠️ 【{meeting['优先级']}】{meeting['name']} 进行中！\n聚焦：{meeting['说明']}"
        if triggered:
            reminders.append(reason)
    return reminders

# ── 主流程 ─────────────────────────────────────────
def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"[{datetime.now().isoformat()}] 开始抓取政治要闻...")
    all_items = []
    meeting_reminders = get_upcoming_meeting_reminders()

    try:
        xml_content = fetch_via_proxy(BBC_RSS)
        bbc_items = parse_bbc_rss(xml_content)
        # 补充 BBC 文章正文（每个链接抓3段，最多6篇）
        bbc_items = fetch_bbc_articles_detail(bbc_items)
        filtered = [it for it in bbc_items if is_political(it['title'])]
        print(f"BBC: {len(bbc_items)} 条原始, {len(filtered)} 条政治过滤后")
        all_items.extend(filtered)
    except Exception as e:
        print(f"BBC 抓取失败: {e}", file=sys.stderr)

    try:
        guancha_items = fetch_guancha_politics()
        print(f"观察者网: {len(guancha_items)} 条")
        all_items.extend(guancha_items)
    except Exception as e:
        print(f"观察者网抓取失败: {e}", file=sys.stderr)

    # 去重
    seen = set()
    unique = []
    for it in all_items:
        key = it['title'][:30].lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(it)
    all_items = unique

    # 混合
    bbc_list = [it for it in all_items if it['source'] == 'BBC World'][:16]
    guancha_list = [it for it in all_items if it['source'] == '观察者网'][:8]
    merged = []
    bbc_idx, gc_idx = 0, 0
    while len(merged) < MAX_ITEMS and (bbc_idx < len(bbc_list) or gc_idx < len(guancha_list)):
        if bbc_idx < len(bbc_list):
            merged.append(bbc_list[bbc_idx]); bbc_idx += 1
        if len(merged) >= MAX_ITEMS: break
        if bbc_idx < len(bbc_list):
            merged.append(bbc_list[bbc_idx]); bbc_idx += 1
        if len(merged) >= MAX_ITEMS: break
        if gc_idx < len(guancha_list):
            merged.append(guancha_list[gc_idx]); gc_idx += 1
        if len(merged) >= MAX_ITEMS: break
    all_items = merged

    # ── 组装纯文本格式（飞书 text 消息）───────────────
    lines = []
    lines.append(f"🌍 全球政治要闻日报 | {today}")
    lines.append(f"数据来源: BBC World News 🌐 + 观察者网 🇨🇳")
    lines.append("─" * 30)

    if meeting_reminders:
        lines.append("📅 中国重大会议提醒")
        for r in meeting_reminders:
            lines.append(r)
        lines.append("─" * 30)

    for i, item in enumerate(all_items, 1):
        title_cn = translate_to_chinese(item['title']) if item['source'] == 'BBC World' else item['title']
        tag = '🌐' if item['source'] == 'BBC World' else '🇨🇳'
        lines.append(f"{i}. {title_cn} {tag}")
        if item['description']:
            desc_cn = translate_to_chinese(item['description']) if item['source'] == 'BBC World' else item['description']
            if desc_cn and desc_cn != title_cn:
                # 描述最多120字，避免单条过长
                if len(desc_cn) > 120:
                    desc_cn = desc_cn[:120] + '…'
                lines.append(f"   {desc_cn}")

    lines.append("─" * 30)
    lines.append(f"🤖 由 ⭐☁️ 自动生成 · {datetime.now().strftime('%H:%M:%S')}")

    content = "\n".join(lines)
    print(f"内容字数: {len(content)}，开始推送...")
    ok = feishu_send_text(content)
    print(f"推送{'成功' if ok else '失败'}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
深圳活动抓取脚本
使用浏览器抓取票牛网深圳站活动，解析后输出 markdown
cron 系统检测到新文件后自动推送
"""
import os
import sys
import re
import time
from datetime import datetime
from scrapling.fetchers import StealthyFetcher

OUTPUT_DIR = os.path.expanduser("~/.hermes/cron/output/shenzhen-events")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_page():
    """抓取票牛深圳站页面"""
    fetcher = StealthyFetcher()
    for attempt in range(2):
        try:
            page = fetcher.fetch(
                "https://www.piaoniu.com/sz-all",
                headless=True,
                executable_path='/usr/bin/google-chrome',
                browser_type='chromium',
                timeout=30000
            )
            if page.status == 200:
                return page.body.decode('utf-8', errors='ignore')
        except Exception as e:
            if attempt == 0:
                time.sleep(2)
                continue
            print(f"Fetch failed: {e}", file=sys.stderr)
    return None

def parse_events(text):
    """从 HTML 中解析深圳活动标题"""
    if not text:
        return []
    pattern = r'title="\[深圳\]([^"]+)"'
    matches = re.findall(pattern, text)
    events = []
    seen = set()
    for m in matches:
        clean = re.sub(r'\s+', ' ', m.strip())
        if len(clean) >= 4 and clean not in seen:
            seen.add(clean)
            events.append(clean)
    return events

def classify(events):
    """分类"""
    concert_kw = ['演唱会', '音乐会', '歌友会', '见面会', '签唱会']
    show_kw = ['话剧', '戏剧', '舞台剧', '音乐剧', '舞剧', '脱口秀', '相声', '小品']
    exhibit_kw = ['展', '博览会', '漫展', '嘉年华', '节']
    sport_kw = ['篮球', '足球', '网球', '羽毛球', '乒乓球', '游泳', '马拉松', '赛车']

    concerts, shows, exhibits, sports, others = [], [], [], [], []
    for e in events:
        if any(k in e for k in concert_kw):
            concerts.append(e)
        elif any(k in e for k in show_kw):
            shows.append(e)
        elif any(k in e for k in exhibit_kw):
            exhibits.append(e)
        elif any(k in e for k in sport_kw):
            sports.append(e)
        else:
            others.append(e)
    return concerts, shows, exhibits, sports, others

def main():
    text = fetch_page()
    events = parse_events(text)

    if not events:
        print("[SILENT]", file=sys.stdout)
        return

    concerts, shows, exhibits, sports, others = classify(events)
    now = datetime.now().strftime('%Y-%m-%d')
    lines = [f"# 🏙 深圳近期活动 | {now}", ""]

    if concerts:
        lines.append("🎵 **演唱会 / 音乐会**")
        for e in concerts[:8]:
            lines.append(f"• {e}")
        lines.append("")

    if exhibits:
        lines.append("🏛 **展览 / 博览会**")
        for e in exhibits[:5]:
            lines.append(f"• {e}")
        lines.append("")

    if sports:
        lines.append("⚽ **体育赛事**")
        for e in sports[:5]:
            lines.append(f"• {e}")
        lines.append("")

    if others:
        lines.append("📌 **其他演出**")
        for e in others[:5]:
            lines.append(f"• {e}")
        lines.append("")

    content = '\n'.join(lines)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    out_path = os.path.join(OUTPUT_DIR, f"{timestamp}.md")
    with open(out_path, 'w') as f:
        f.write(content)

    print(content)

if __name__ == '__main__':
    main()

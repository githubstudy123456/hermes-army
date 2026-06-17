#!/usr/bin/env python3
"""
gov_content_scanner.py
扫描 gov.cn 指定日期区间的新发布内容，快速发现增量政策文件。
用法: python gov_content_scanner.py<start_id> <end_id> <YYYYMM> [target_date]
"""
import urllib.request, ssl, re, sys
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

start_id = int(sys.argv[1]) if len(sys.argv) > 1 else 7071864
end_id = int(sys.argv[2]) if len(sys.argv) > 2 else 7072100
ym = sys.argv[3] if len(sys.argv) > 3 else "202606"
target = sys.argv[4] if len(sys.argv) > 4 else datetime.now().strftime('%Y-%m-%d')

found = []
print(f"Scanning gov.cn /yaowen/liebiao/{ym}/ content_{start_id}–{end_id} for {target}...")

for cid in range(start_id, end_id + 1):
    url = f'https://www.gov.cn/yaowen/liebiao/{ym}/content_{cid}.htm'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=8, context=ctx) as r:
            html = r.read().decode('utf-8', errors='ignore')
        date = re.search(r'(\d{4}-\d{2}-\d{2})', html)
        title = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
        title_clean = re.sub(r'<[^>]+>', '', title.group(1)).strip() if title else 'unknown'
        date_str = date.group(1) if date else 'unknown'
        if target in date_str:
            found.append((cid, title_clean, url))
            print(f"  [MATCH] content_{cid}: {title_clean[:60]}")
    except:
        pass

print(f"\nTotal matches for {target}: {len(found)}")
for cid, title, url in found:
    print(f"  {title[:60]} | {url}")
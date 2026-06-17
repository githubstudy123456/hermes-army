# 物理 stars.json 查询脚本
# 用法: python3 query_stars.py [--min N]

import json, sys

min_star = int(sys.argv[1]) if len(sys.argv) > 1 else 4

with open("/home/ubuntu/teaching-platform/data/物理/stars.json") as f:
    stars = json.load(f)

high = []
for vol, chapters in stars.items():
    for ch, sections in chapters.items():
        for sec_id, star in sections.items():
            if star >= min_star:
                high.append((vol, ch, sec_id, star))

high.sort(key=lambda x: -x[3])
print(f"\n=== ⭐{min_star}星及以上章节（共{len(high)}个）===")
for vol, ch, sec_id, star in high:
    print(f"{'⭐'*star} {vol} {ch} {sec_id}")
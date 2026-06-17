# gov.cn Content ID 追踪与去重

## Content ID 结构

gov.cn 文章 URL 格式：
```
https://www.gov.cn/yaowen/liebiao/YYYYMM/content_NNNNNN.htm
```

**Content ID 规律**：
- 格式：`content_XXXXXXX.htm`（7位数字，如 `7071845`）
- 数字大小与发布时间正相关：ID越大越新
- 同一天可能发布数十篇文章，ID 不连续但严格递增

## 去重原理

gov.cn 同一篇文章会在多个入口重复出现：
1. **首页要闻区块**（当日）
2. **yaowen/liebiao 列表页**（持续可见）
3. **lianbo 政务联播**（长期存档）
4. **专题/解读页**（带 `/jiedu/` 路径的关联页面，但 content ID相同）

同一 `content_NNNNNN` 对应同一篇文章，无论从哪个入口访问。因此：
- **去重单位是 content ID**，不是标题
- 标题措辞可能因编辑而略有差异（如"总体平稳" vs "运行总体平稳"），但 content ID 不变

## 识别"旧闻新发"

**典型案例**（2026-06-12 验证）：
- 5月 CPI/PPI 数据 2026-06-10 在 gov.cn 发布 → content ID `7071779`
- 2026-06-11 早间 gov.cn 首页再次推送同一文章
- 标题："5月份我国消费市场运行总体平稳"（与原始标题文字略有出入）

**判断方法**：
1. 提取 URL 中的 content ID（正则：`content_(\d+)\.htm`）
2. 检查今日报告目录中是否已存在相同 content ID
3. 若存在且发布时间（前一日）早于本次推送时间 → 判定为"旧闻新发"，跳过

## 实用脚本

```python
import re, os

def extract_content_id(url):
    m = re.search(r'content_(\d+)\.htm', url)
    return m.group(1) if m else None

def is_already_reported(content_id, report_dir):
    """检查已知报告文件中是否已包含此 content_id"""
    for fn in os.listdir(report_dir):
        if not fn.startswith('report_'):
            continue
        path = os.path.join(report_dir, fn)
        try:
            with open(path) as f:
                if content_id in f.read():
                    return True
        except:
            pass
    return False
```

## 直接 ID 范围扫描法（2026-06-12 实测可用）

绕过列表页超时的方法：**直接扫描 content ID 数值范围**，gov.cn 按发布顺序分配递增 ID，同一天的文章 ID 通常在相近范围内。

```python
import urllib.request, re, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 2026年6月11日文章常见 ID 范围 7071800-7071900
# 扫描时优先高ID（数字越大越新）
for cid in range(7071850, 7071900):
    url = f'https://www.gov.cn/lianbo/202606/content_{cid}.htm'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5, context=ctx) as r:
            content = r.read().decode('utf-8', errors='ignore')
            title = re.search(r'<title>(.*?)</title>', content)
            if title:
                title_str = title.group(1)[:70]
                print(f"[{cid}] {title_str}")
    except:
        pass  # 404 = 跳过，ID不存在
```

**实测发现的新文章（2026-06-12 06:47）**：

| Content ID | 标题 | 发布日 |
|-----------|------|-------|
| 7071805 | 中国海洋经济发展指数发布 去年全国海洋生产总值达十一万亿元 | 2026-06-11 09:24 |
| 7071831 | 四部门部署实施创业模式引领行动 | 2026-06-11 17:52 |
| 7071846 | 我国将优化完善东西部协作实现结对帮扶全覆盖 | 2026-06-11 20:05 |
| 7071851 | 我国力争"十五五"时期建至少1.2万个便民生活圈 | 2026-06-11 21:18 |
| 7071852 | 在乡村振兴中书写新篇章——国新办发布会聚焦东西部协作三十年 | 2026-06-11 21:20 |

**注意**：这些文章均为区域政策（非核心宏观），扫描后需按关键词判断是否推送。

## Content ID 边界追踪表（本session更新）

每次推送后记录各频道最新 content ID，下次扫描时以此为分水岭：

| 频道 | 页面URL | 本session推送ID | 备注 |
|------|---------|---------------|------|
| 要闻 | `yaowen/liebiao/` | 7071948 | 2026-06-14 10:30 推送（人民币贷款数据） |
| 政策文件 | `zhengce/liebiao/` | 7071204 | 2026-06-14 11:09 推送（私募基金监管） |

**扫描逻辑**：
```python
YAOWEN_LAST_ID = 7071948   # 上轮推送的 yaowen 频道最大 ID
ZHENGCE_LAST_ID = 7071204  # 上轮推送的 zhengce 频道最大 ID

for article in articles:
    cid = int(re.search(r'content_(\d+)\.htm', url).group(1))
    if 'yaowen/liebiao' in url and cid > YAOWEN_LAST_ID:
        # 新文章（仅在此分支内检查关键词）
    elif 'zhengce' in url and cid > ZHENGCE_LAST_ID:
        # 新文章
    # ID 未超过分水岭 → 已推送，跳过
```

## 已知重复 content ID（2026-06验证）

| Content ID | 标题关键词 | 首次推送 | 重复出现日期 |
|-----------|-----------|---------|------------|
| 7071779 | CPI/PPI 5月 | 2026-06-1107:42 | 2026-06-11 日间首页 |
| 7071845 | 国常会审计整改 | 2026-06-11 日间 | 2026-06-12 凌晨 |

### 新华网政治 RSS 完全不可用（2026-06-12 实测）

- **问题**：`http://www.xinhuanet.com/politics/news_politics.xml` 返回的 `<pubDate>` 全部是 2022年12月14日，条目内容也是2022年旧闻
- **原因**：RSS 源多年未更新，数据已完全过时
- **判断**：该源在任何时段都不能作为政策监测的依据，发现旧数据应立即跳过而非等待新数据
- **替代**：改用新浪财经 lid=2517 或直接扫描 gov.cn content ID 范围
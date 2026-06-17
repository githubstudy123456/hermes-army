# 中国政府网站 gov.cn URL Patterns

## gov.cn 政策文件 URL 结构（2026-06 实测）

gov.cn 政策文件/文章 URL 统一格式：
```
https://www.gov.cn/<channel>/YYYYMM/content_<ID>.htm
```

**通道（channel）决定内容类型**：

**通道（channel）决定内容类型**：

| 通道 | 示例 URL | 内容类型 |
|------|---------|---------|
| `yaowen/liebiao/` | `/yaowen/liebiao/202606/content_7071651.htm` | 时政要闻（领导人外事访问、宪法宣誓仪式、国常会报道） |
| `lianbo/` | `/lianbo/202606/content_7071714.htm` | 政务联播（各部委动态，如工信部政策、多部门联合发文） |
| `zhengce/content/` | `/zhengce/content/202606/content_7071451.htm` | 政策文件（国发/国办发正式文件） |
| `zhengce/jiedu/tujie/` | `/zhengce/jiedu/tujie/202606/content_7071661.htm` | 政策图解/解读 |
| `zhengce/zhengceku/` | `/zhengce/zhengceku/202606/content_7072002.htm` | 国务院部门文件（多部委联合通知，如交规划发〔2026〕52号） |

**注意**：`/zhengce/liebiao/` 是政策文件列表页（可用），`/zhengce/index.htm` 会重定向到首页（不可用）。

**content ID（content_\d{7,}）是内容唯一标识**，同一内容在三通道中共享相同 ID，与标题无关。

**发布时间判断**：从 URL 中提取 YYYYMM（前6位），即发布日期（精确到月）。如需精确到日，看内容页面内日期。

## 快速发现今日新文件的工作流

1. urllib 直读 `https://www.gov.cn/zhengce/index.htm` → 提取侧边栏"最新政策"链接（`/zhengce/content/YYYYMM/content_*.htm`）
2. 对每条候选 URL 检查 content ID 是否在今日已推送报告中出现过
3. 新 ID → navigate 获取正文 → 过5关审核

```python
import re, glob, os
from datetime import datetime

# 提取所有 content ID
def extract_content_ids(text):
    return set(re.findall(r'content_(\d{7,})', text))

reports_dir = '/home/ubuntu/.hermes/political-reports'
today = datetime.now().strftime("%Y-%m-%d")

# 已推送的 ID 集合
pushed_ids = set()
for fname in os.listdir(reports_dir):
    if not fname.startswith('2026-06-11'):
        continue
    fpath = os.path.join(reports_dir, fname)
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            pushed_ids |= extract_content_ids(f.read())
    except:
        pass

# 候选 URL（从 index.htm 或 browser_snapshot 提取）
candidate_urls = [
    'https://www.gov.cn/zhengce/content/202606/content_7071502.htm',
    'https://www.gov.cn/zhengce/content/202606/content_7071451.htm',
]
candidate_ids = extract_content_ids(' '.join(candidate_urls))
new_ids = candidate_ids - pushed_ids
print(f"New items to check: {len(new_ids)}")

# content ID → URL 映射
id_to_url = {re.search(r'content_(\d{7,})', u).group(1): u for u in candidate_urls}
for nid in new_ids:
    print(f"NEW: {id_to_url.get(nid, 'unknown')}")
```

## 新华网（xinhuanet.com）URL 结构

```
http://www.news.cn/politics/<category>/YYYYMMDD/c_<ID>.htm
```

| URL | 内容类型 |
|-----|---------|
| `/politics/news_politics.xml` | 政治 RSS（⚠️ 已停止更新，2026-06 全部2022 年旧数据） |
| `/politics/zywj/` | 中央文件列表 |
| `/politics/leaders/` | 领导人简历 |

## 识别国发/国办发文件的关键词

政策文件标题含以下词时优先级升高：
- `关于印发《...》的通知` → 国发/国办发正式规划/意见
- `国发〔2026〕` / `国办发〔2026〕` / `国办函〔2026〕` → 国务院文件
- `十五五` → 中长期规划
- `实施条例（草案）` → 立法推进中

非国发/国办发但属重要政策（降为 P3）：
- `工信部` / `商务部` / `住建部` / `发改委` + `意见` / `通知` / `办法`
- `八部门联合` / `多部门联合印发`
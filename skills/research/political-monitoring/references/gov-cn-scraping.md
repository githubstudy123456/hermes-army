# 中国政府网(gov.cn)爬取技术细节

## 核心原则：browser_snapshot 优先，urllib 仅限政策文件列表

gov.cn 首页是 JavaScript 动态渲染的，urllib 直读只能拿到 HTML 骨架（约 15KB），大量新闻链接丢失。browser_snapshot 执行 Chrome 完全渲染，返回完整 DOM。

| 场景 | 工具 | 原因 |
|------|------|------|
| gov.cn 首页要闻（yaowen/liebiao 链接） | `browser_snapshot` ✅ | urllib 提取返回 0 条（标题在 h2/h4 包裹的 a 标签内，正则匹配失败） |
| gov.cn 政策文件列表（zhengce/index.htm） | `urllib` ✅ | 纯静态页面，速度快（~0.2s），无需浏览器 |
| 政策文件正文 | `browser_click` + `browser_snapshot` ✅ | 直接读取渲染后正文 |

---

## Step 1：gov.cn 首页 → browser_snapshot（获取完整要闻 + 政策侧边栏）

```python
# 第一步：browser_navigate 获取完整首页快照
browser_navigate('https://www.gov.cn/index.htm')
# 从快照中直接看到全部要闻标题+URL，无需任何解析
# 典型今日要闻（2026-06-10）：
#   - 习近平结束对朝鲜国事访问回到北京
#   - 国务院举行宪法宣誓仪式
#   - 丁薛祥出席三峡水运新通道工程开工仪式
#   - 2026年前5月外贸数据（贸易延续稳定增长）

# 第二步：browser_click 进入具体文章
# 例如点击"最新政策"中的条目
browser_click(ref='e46')  # 对应 browser_snapshot 中的元素引用
browser_snapshot()         # 读取正文

# 第三步：从快照提取正文
# 正文在 <p> 标签中
paras = re.findall(r'<p[^>]*>(.*?)</p>', article_content, re.DOTALL)
full_text = '\n'.join([re.sub(r'<[^>]+>', '', p).strip() for p in paras
                       if len(re.sub(r'<[^>]+>', '', p).strip()) > 20])
```

## Step 2：zhengce/index.htm → urllib 直读（政策文件列表）

```python
import urllib.request, re, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request(
    'https://www.gov.cn/zhengce/index.htm',
    headers={'User-Agent': 'Mozilla/5.0'}
)
with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
    content = r.read().decode('utf-8', errors='ignore')

# 提取"最新政策"列表（标题格式：国务院关于XXX的通知）
policy_links = re.findall(
    r'<a[^>]+href="(https://www\.gov\.cn/zhengce/content/\d{6}/content_\d+\.htm)"[^>]*>([^<]{5,200})</a>',
    content
)
for url, title in policy_links:
    title = title.strip()
    if any(k in title for k in ['通知', '意见', '决定', '条例', '办法', '国发', '国办发', '国办函', '规划']):
        print(f"  {title[:80]} | {url}")
```

---

## 内容ID结构

gov.cn 时政新闻 URL 格式：`https://www.gov.cn/yaowen/liebiao/YYYYMM/content_{ID}.htm`

- `YYYYMM` = 年月（如 `202606`）
- `content_{ID}` = 内容ID，整数，每发布一条新内容+1
- **ID大小与内容时效正相关**：高ID = 最新内容

## 2026年6月实测数据

| ID范围 | 内容类型 |
|--------|---------|
| `7071451` | 现代化应急体系"十五五"规划 |
| `7071204` | 国办私募基金监管意见 |
| `7070901` | 农业农村现代化"十五五"规划 |
| `7070755` | 对外投资的规定（国令第837号） |
| `7071651` | 国务院宪法宣誓仪式（6月9日） |
| `7071659` | 三北工程推进会（6月9日） |

**扫描边界**：2026-06-10 最高已知有效ID为 `7071659`，`7071660` 起均为首页重定向。

## 页面结构

每条新闻页面含：
- `<title>` → 文件标题，格式：`{标题}__中国政府网`
- 正文首段 → 新华社来源标注（"新华社北京X月X日电"）
- 日期 → 在正文中以"YYYY年MM月DD日"形式出现

### ✅ gov.cn 政策解读页 — 国常会解读文章专属通道
**URL**: `https://www.gov.cn/zhengce/jiedu/tujie/`
**状态**: ✅ 稳定可用（2026-06 实测）
**内容**: 国务院常务会议解读文章的图解/图表版本（如"国常会解读 | 国务院常务会议部署就业工作"）
**与 zhengce/index.htm 的区别**: zhengce/index.htm 的"政策解读"tab主要链回正式文件通知页；jiedu/tujie/ 是图文解读专页，内容更通俗
**用法**: `browser_navigate('https://www.gov.cn/zhengce/jiedu/tujie/')` 或 urllib 直读

⚠️ 注意：gov.cn"最新政策"列表中含大量旧文件（2020-2024年），**需从URL日期（content/YYYYMM/）判断是否为当日新发布**，不要对标题做时间假设。过滤方式：`if '/202606/' in url or '/202605/' in url`。

## 实战发现（2026-06-10 巡航日志摘录）

**gov.cn 首页侧边栏两条通道必须同时扫描**：
1. `yaowen/liebiao/` → 时政要闻（领导人活动/会议报道）
2. `zhengce/content/*` → 政策文件（国令/国发/国办发）

国函〔2026〕45号（粤港澳大湾区游艇政策）从侧边栏"最新政策"发现，yaowen通道完全没有。

**扫描边界（2026-06实测）**：

| 日期 | 最高有效ID | 说明 |
|------|-----------|------|
| 2026-06-10 | `7071659` | 三北工程推进会；`7071660` 起为首页重定向 |
| 2026-06-11 下午 | `7071809` | 铁路旅游融合政策解读（15:29）；住房公积金扩大（15:29）；铁路旅游列车专用车组（15:29） |

**browser_console 提取政策解读列表（2026-06-11 实测成功）**：
```javascript
// ✅ 在 zhengce/jiedu/index.htm 页面执行，提取全部政策解读 content ID
JSON.stringify([
  ...document.querySelectorAll('a')
].filter(e=>
  e.offsetParent!==null &&
  e.href.includes('content_')
).slice(0,20).map(e=>({
  t: e.innerText.trim().slice(0,40),
  u: e.href
})))
// 返回示例：
// [{"t":"商务部服贸司负责人解读...","u":"https://www.gov.cn/zhengce/202606/content_7071809.htm"}, ...]
```

**高效扫描策略 — 最高ID比对法（2026-06-11验证）**：

不必逐条扫描所有URL，只需两步：
1. urllib 直读 `https://www.gov.cn/zhengce/index.htm`，提取全部 `content_707(\d+)` ID
2. 对比今日已推送报告中出现的最高ID

```python
import urllib.request, re, ssl, glob, os
from datetime import datetime

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 获取当前最高ID
req = urllib.request.Request('https://www.gov.cn/zhengce/index.htm',
    headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=12, context=ctx) as r:
    content = r.read().decode('utf-8', errors='ignore')

current_ids = sorted(set(int(i) for i in re.findall(r'content_707(\d+)', content)))
current_highest = max(current_ids) if current_ids else 0

# 获取今日已推送的最高ID
reports_dir = os.path.expanduser("~/.hermes/political-reports")
today = datetime.now().strftime("%Y-%m-%d")
pushed_ids = set()
for fname in glob.glob(f"{reports_dir}/*{today}*"):
    with open(fname, 'r', encoding='utf-8') as f:
        pushed_ids |= set(int(i) for i in re.findall(r'content_707(\d+)', f.read()))

pushed_highest = max(pushed_ids) if pushed_ids else 0

if current_highest <= pushed_highest:
    print(f"SKIP: 最高ID未变（当前={current_highest}，已推送={pushed_highest}）")
else:
    new_ids = [i for i in current_ids if i > pushed_highest]
    print(f"新ID: {new_ids}，需继续审核")
```

⚠️ **今日（2026-06-11）实测**：10:28 AM 已推送最高ID `7071795`，12:05 扫描 `current_highest=7071795`，两者相等 → **静默跳过**，符合预期。此模式在无新政策日可避免无效操作。

**gov.cn 新文件 ID 扫描边界（2026-06-10）**：
当日 gov.cn 发布的政策文件 ID 最高为 `7071659`（三北工程），`7071660` 起为首页重定向。新增条目需落在 `7071xxx` 段内。ID 大小与发布时间正相关。

**zhengce/jiedu/tujie/ 是国常会解读文章的另一入口**：国常会解读通常出现在两个地方：zhengce/index.htm 的"政策解读"tab，以及 zhengce/jiedu/tujie/ 专页（图文版）。两者内容相同，选其一即可。

## 已知问题

| 问题 | 状态 | 解决方案 |
|------|------|---------|
| ~~browser_navigate yaowen/liebiao 超时~~ | ✅ 已解决 | 不跳转，直接 browser_snapshot 首页 |
| ~~eval_on_selector_all 只返回约15个链接~~ | ✅ 已解决 | browser_snapshot 获取完整 DOM |
| ~~urllib 提取首页 yaowen 链接返回 0 条~~ | ✅ 已解决 | browser_snapshot 是正确工具 |
| urllib 提取 people.com.cn yaowen 链接返回 0 条 | ⚠️ 已知问题 | 不要依赖 urllib 从 people.com.cn 提取新闻，改用 gov.cn |
| ~~urllib SSL 错误~~ | ✅ 已解决 | zhengce/index.htm 无 SSL 问题，首页用 browser_snapshot |
| ~~去重脚本 check_pushed.sh 对 root-owned 文件静默失效~~ | ✅ 已解决 | 见 SKILL.md 去重检查节，改用 execute_code 读取 20260610_*.txt |
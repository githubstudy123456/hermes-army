# 新浪财经 API + CSRC 交叉验证实测记录（2026-06-13）

## 新浪财经 lid=2517 API 实战技巧

### 编码处理（关键发现）

**问题**：`urllib.parse.quote` 只能编码 URL 中的查询部分，不能编码整个 URL。
如果 URL 含中文字符（如 `k=人民币`），编码对象必须是整个查询参数字符串，不是单个中文字符：

```python
# ❌ 错误：只编码了中文字符，剩余 ASCII 部分导致冲突
url = f"https://feed.mix.sina.com.cn/api/roll/get?k=%E4%BA%BA%E6%B0%91%E5%B8%81&num=10"
# 或
from urllib.parse import quote
url = f"https://.../k={quote('人民币')}&num=10"  # 报错 'ascii' codec can't encode

# ✅ 正确：不加 k= 参数，直接用 API 默认行为（返回全部条目）
url = 'https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&num=30&page=1'

# ✅ 如果必须搜索：编码整个查询字符串
from urllib.parse import quote
query = "证监会"
url = f"https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&k={quote(query)}&num=10"
# 正确，因为 quote() 处理的是整个 "k=证监会" 字符串
```

### URL 转义斜杠修复

新浪 API 返回的 URL 含转义斜杠 `https:\\/\\/finance.sina.com.cn\\/...`，直接用会报错。
取到 URL 后：

```python
raw_url = item.get('url', '')
# 修复转义斜杠
fixed_url = raw_url.replace('\\/', '/')
# 去掉开头的 'https:' 双斜杠（如果有）
if fixed_url.startswith('https:/') and not fixed_url.startswith('https://'):
    fixed_url = 'https://' + fixed_url[7:]
```

### 响应编码

必须用 GBK 解码：`r.read().decode('gbk', errors='ignore')`

数据结构需要 eval 转换：
```python
d = eval(content.replace('false', 'False').replace('true', 'True').replace('null', 'None'))
items = d.get('result', {}).get('data', [])
```

## CSRC 官方站与媒体发布时间差

### 实测案例（2026-06-13）

| 事件 | 媒体发布时间 | CSRC官方站发布时间 |
|------|------------|-----------------|
| "证监会：全面推进实施新一轮资本市场改革开放" | 06:44（新浪财经） | **仍未出现**（09:20检查） |

**结论**：新浪财经等媒体通常比 CSRC 官方站提前 2-4 小时发布监管政策新闻。
CSRC 官方站最新要闻（证监会要闻 tab）最新一条为 06-09（会见香港金管局）。

**工作流**：
1. 媒体先于官方 → 先推送（来源：新媒体/新浪财经）
2. 官方后续发布 → 作为交叉验证补充
3. 如果官方发布后媒体才有 → 以官方为准

**验证方法**：对媒体发布的重大监管政策，应同时 navigate CSRC 官方对应页面确认。
若官方站无对应内容，说明该新闻来自媒体吹风会或非正式渠道，评级可适当降低。

### CSRC 官方站文章列表页 URL 提取失败（2026-06-13 再次确认）

- 路径：`https://www.csrc.gov.cn/csrc/c100028/common_xq_list.shtml`（证监会要闻）
- 状态：页面加载正常，包含文章列表，但 `<a title="...">` 模式匹配数为 0
- 当前最新条目：2026-06-09（与新浪 06-44 发布的改革开放新闻相差 4 天）
- **结论**：CSRC 官方站文章列表无法自动化抓取，仅可靠通过新浪财经政经 API 获取

## 本次 session 新增事件（已处理）

| 时间 | 事件 | 评级 | 处理 |
|------|------|------|------|
| 09:00 | 商务部新闻发言人就美国防部将部分中国企业列入"中国军事企业清单" | -- | 拦截：非核心宏观金融触发词，属外交/贸易摩擦类 |
| 08:38 | 约1400只基金暂停大额申购 | P3 | 已记录，属基金申赎调整，非系统性风险 |
| 08:34 | 证监会：全面推进实施新一轮资本市场改革开放 | P2 | 已推送（与 06:44 同一事件） |
| 08:34 | 非法跨境展业整治进入执行阶段 3家跨境券商启动"单向退出" | P2 | 已推送 |
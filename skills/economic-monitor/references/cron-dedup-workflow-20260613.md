# Cron 轮询去重工作流 | 2026-06-13 实测

## 问题
每30分钟cron运行时，如何快速判断"本轮是否有新内容可推"？

## 实测工作流

### 第0步：读取今日已有报告（每次扫描前必做）

```python
import os
from datetime import datetime

today = datetime.now().strftime('%Y%m%d')
report_dir = os.path.expanduser('~/.hermes/economic-reports/')
existing = sorted([f for f in os.listdir(report_dir) if f.startswith(today)])
print(f"Today ({today}): {len(existing)} existing reports")
for e in existing:
    print(f"  {e}")
```

### 第1步：过滤最近90分钟内的条目
新浪财经 lid=2517 API 返回最近30条，含时间戳。按 `ctime` 过滤：
```python
ts_now = datetime.now().timestamp()
recent = [i for i in items if ts_now - int(i.get('ctime', 0)) < 90 * 60]
```
若 `recent` 为空 → 跳过新浪源。

### 第2步：关键词命中扫描
对每条标题+intro 扫描核心关键词（降准/降息/CPI/证监会/房地产等）。
命中为空 → 本轮静默。

### 第3步：去重两步检查
1. gov.cn content ID 精确匹配（已推送过 `content_7071845` 则跳过）
2. 标题相似度 >70% 兜底（适用于新浪财经等来源）

### 第4步：判断结论
三种结论：
- **有推送**（新事件通过5关）→ 生成报告 → 写文件 → cron 自动投递
- **无推送但有疑问**（单源/存疑）→ 记录但不推送 → 归入周报
- **本轮静默**（无核心词命中）→ 输出 `[SILENT]`，cron 抑制投递

## 今日实测结果（17:00-17:30）
- 新浪财经近3小时：8条，无核心词命中 → 本轮静默
- 36kr RSS：30条，集中在科技/商业，无核心经济词 → 跳过
- gov.cn article直接访问：已验证可用，但今日下午时段无经济内容更新
- USD/CNY：6.78（via exchangerate-api.com），无触发条件

## 关键教训
- **每次扫描前必须先读已有报告**，否则去重失效，会重复推送
- `[SILENT]` 响应由 cron 系统自动处理，抑制空报告投递，无需额外逻辑
- 本轮静默的原因是下午时段（12:00-17:30）新浪财经无核心经济事件，与深夜国际占位不同，属于"正常经济信息真空窗口"

## 补充教训：36kr RSS CDATA 解析（2026-06-13 实测）

36kr 的 `<title>` 标签有**两种形式**，同一个 feed 里混用：

- `<title><!\[CDATA\[标题文字\]]></title>` — 带 CDATA 包裹
- `<title>纯文本标题</title>` — 不带 CDATA

之前代码只匹配 CDATA form，`re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)` 在实测中匹配数为 0。**正确 pattern 是**：

```python
# ✅ 正确：两种 form 都匹配
title_match = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', item)

# ❌ 错误：只匹配 CDATA form，实测匹配数 = 0
title_match = re.search(r'<title><!\[CDATA\[(.*?)\]\]></title>', item)
```

同样 `<link>` 的 CDATA 包裹也需要兼容处理：

```python
# ✅ 正确
link_match = re.search(r'<link>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</link>', item)
```

日期解析不要用 `email.utils.parsedate_to_datetime`（36kr 格式 `2026-06-13 16:37:21  +0800` 含非标准时区，会报错），直接 split 后用 `datetime.strptime`：

```python
pub_str = pub_match.group(1).strip()  # e.g. "2026-06-13 16:37:21  +0800"
pub_dt = datetime.strptime(pub_str.split('  ')[0], '%Y-%m-%d %H:%M:%S')
```

## 补充教训：报告目录路径在 execute_code 沙箱中必须用硬编码（2026-06-14 实测）

**问题**：`execute_code` 沙箱的 `os.path.expanduser('~')` 返回 `/root`，而 cron 实际以 `ubuntu` 用户运行，`~` → `/home/ubuntu`。导致 dedup 扫描永远返回空列表。

**正确方式**：
```python
import os, glob
from datetime import datetime

# ✅ execute_code 沙箱中必须用硬编码路径（2026-06-14 确认）
REPORT_DIR = "/home/ubuntu/.hermes/economic-reports"
today_files = sorted(glob.glob(f"{REPORT_DIR}/*{datetime.now().strftime('%Y-%m-%d')}*"))

# ❌ 错误：沙箱中~展开为/root，cron中~展开为/home/ubuntu
report_dir = os.path.expanduser('~/.hermes/economic-reports/')  # 永远为空
```

**但** `read_file`/`write_file` 工具（不在沙箱中）仍需使用 `~/.hermes/...` 前缀路径，否则 vet 拦截。两者不要混淆。
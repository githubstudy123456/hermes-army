# 政治监测 · 实测数据源速查

## gov.cn 导航行为（重要）

| URL类型 | 稳定性 | 说明 |
|---------|--------|------|
| `https://www.gov.cn/` 首页 | ★★★★★ | browser_navigate 直连，~3s，要闻+最新政策全有 |
| `https://www.gov.cn/yaowen/liebiao/` 列表页 | ❌ | 超时60s，不要用 |
| `https://www.gov.cn/yaowen/liebiao/YYYYMM/content_*.htm` | ★★★★★ | 直连具体文章，绕过列表页 |
| `https://www.gov.cn/zhengce/index.htm` 政策库 | ★★★★☆ | 慢但可用 |

**gov.cn 首页抓取策略**：每次监测直接从首页要闻区提取条目（browser_navigate 全量快照），无需访问列表页。

## 新浪财经政经API（lid=2517）

```
GET https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517&num=30&page=1
```

**时间戳字段**：`ctime`（Unix时间戳），筛选近5小时：`ts_now - int(item['ctime']) < 5*3600`

**时段特性（2026-06-13 实测）**：
- 工作日 09:00-17:00：政经国内新闻比例约40-50%，可用
- 凌晨 03:00-07:00：20/20条均为美股/国际财经，**不适合政治监测**
- 适用场景：工作日上午政经补充发现，不适合夜间/凌晨

**编码陷阱**：响应编码是 `gbk`，不是 `utf-8`：
```python
content = r.read().decode('gbk', errors='ignore')
d = eval(content.replace('false','False').replace('true','True').replace('null','None'))
```

## 推送文件命名规范

```
~/.hermes/political-reports/
  2026-06/
    20260613-001-事件简称.md      # 单条推送（如P1/P2重大事件）
    20260613_日报_午间.txt        # 合并日报
    20260613_1610_political.txt   # 周期合并报告（每90分钟）
```

**去重检查**：扫描前对比今日已推送文件，标题相似度>70%则跳过。

## HOME路径问题

cron环境中 `~` 可能指向 `/root` 而非 `/home/ubuntu`。保险写法：
```python
report_dir = os.path.expanduser('~/.hermes/political-reports/')
# 或显式：
report_dir = '/home/ubuntu/.hermes/political-reports/'
```

## 搜索策略（bb-browser Google搜索超时时的备选）

| 方案 | 状态 | 说明 |
|------|------|------|
| `bb-browser site google/search` | ❌ 超时 | 不适合服务器cron环境 |
| `browser_navigate` 直连 gov.cn | ★★★★★ | 首选 |
| 新浪财经 lid=2517 API | ★★★★☆ | 工作日辅助 |
| `bb-browser site bilibili/trending` | ❌ B站API无头环境返回空 | - |

## 搜索关键词策略（用于bb-browser google/search，不适用于cron直搜）

```
site:xinhuanet.com 政治局会议 2026
site:gov.cn 国务院 文件 最新 2026
site:people.com.cn 习近平 重要讲话 2026
site:gov.cn 发改委 OR 住建部 OR 商务部 最新政策 2026
```

**注意**：bb-browser google/search 标题字段在2026-06-12实测全部返回 `null`，降级处理取 snippet 前30字作临时标题。
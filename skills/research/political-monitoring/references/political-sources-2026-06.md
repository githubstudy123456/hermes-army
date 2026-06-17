# 政治监测 · 实测信息源清单（2026-06）

本文档记录 political-monitoring 技能的实际可用信息源及失败模式，供 cron 环境下的政治监测使用。

## gov.cn 可用入口

| 路径 | 用途 | 状态 |
|------|------|------|
| `https://www.gov.cn/zhengce/index.htm` | 政策文件列表，含最新国发/国办发/国令 | ✅ browser_navigate 稳定 |
| `https://www.gov.cn/yaowen/liebiao/` | 政务联播，重要会议/活动报道 | ✅ browser_navigate 稳定 |
| `https://www.gov.cn/zhengce/xxgk/` | 政府信息公开平台，结构化表格 | ✅ browser_navigate 稳定 |

## gov.cn 不可用入口（必须绕过）

| 路径 | 失败原因 | 绕过方式 |
|------|----------|----------|
| `www.gov.cn/lianbo/index.htm` | 超时60s | 从 `zhengce/index.htm` 侧边栏进入 |
| `www.gov.cn/lianbo/yaowen/index.htm` | ERR_ABORTED | 直连具体文章URL |
| 政务联播子页 `yaowen/liebiao/202606/content_*.htm` | JS动态渲染，返回导航非正文 | 从列表页点击进入 |

## 搜索工具实测

| 工具 | 路径 | 状态 | 失败原因 |
|------|------|------|----------|
| `bb-browser site baidu/search` | 任意查询 | ❌ daemon HTTP 400 fetch失败 | 百度验证码/反爬 |
| `bb-browser site google/search` | 任意查询 | 未测试 | — |
| 新浪财经 lid=2517 | 国内政经 | ❌ 全为美股/国际新闻 | 非政策监测可用 |
| 36kr RSS | 科技商业 | ❌ 内容偏科技商业 | 非政策监测可用 |
| 新华网政治RSS | politics_politics.xml | ❌ 返回2022年旧数据 | 数据过时 |

## 失败模式记录

### bb-browser daemon HTTP 400
- **表现**：`{"success":false,"error":"Daemon HTTP 400: TypeError: Failed to fetch"}`
- **触发**：任何 `bb-browser site baidu/search` 查询
- **原因**：百度搜索在无头环境下被拒绝（不同于普通CAPTCHA，是daemon层fetch失败）
- **对策**：不使用搜索，改用 browser_navigate 直连 gov.cn/zhengce/index.htm

### 新浪财经lid=2517全美股
- **表现**：20/20条均为美股/国际财经，零条国内政策
- **原因**：该lid是国际财经频道，非政经
- **对策**：仅作宏观市场情绪参考，不用于政治监测

### urllib SSL错误
- **表现**：`ssl.SSLError: [SSL: BAD_ECPOINT] bad ecpoint` 或 `TLSV1_UNRECOGNIZED_NAME`
- **触发**：urllib 直读 gov.cn 系列
- **对策**：browser_navigate 走Chrome内置SSL，不依赖系统证书

## cron环境工作流

```
1. browser_navigate('https://www.gov.cn/zhengce/index.htm') → 快照含最新政策列表
2. 从快照中提取 <li> 条目（标题+日期+URL）
3. 过滤今日/昨日新发布
4. 逐条 browser_click → browser_snapshot读详情
5. 过5关审批
6. 通过 → 写文件到 ~/.hermes/political-reports/
7. 最终输出放入 final response（cron auto-delivers）
```

## 报告存储路径

- **正确路径**：`/home/ubuntu/.hermes/political-reports/`（home是 `/home/ubuntu`，不是 `/root`）
- 目录中同时存在文件(`*.txt`)和目录(`2026-06-12/`)
- 列表前用 `os.path.isfile()` / `os.path.isdir()` 区分
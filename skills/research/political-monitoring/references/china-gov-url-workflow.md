# 中国政府网站 gov.cn 访问工作流（2026-06 实测）

## gov.cn 频道结构

| 频道 | URL | 内容 |
|------|-----|------|
| 要闻 | `/yaowen/liebiao/` | 重要政务要闻（当日头条+最新） |
| 联播 | `/lianbo/` | 各部委政务联播 |
| 政策 | `/zhengce/` | 政策文件库 |
| 政策解读 | `/zhengce/jiedu/` | 政策解读文章 |

## 直接访问模式（绕过列表页超时）

### 联播列表页超时解决方案
`browser_navigate('https://www.gov.cn/lianbo/index.htm')` 在 cron 环境下超时60s。

**绕过方式**：
- 不访问列表页
- 直接从 gov.cn **首页侧边栏**的"政务联播"区块提取今日链接
- 或直接拼具体文章 URL：`/lianbo/YYYYMM/content_*.htm`

### 快速获取今日要闻（推荐）

从 gov.cn 首页直接提取，无需访问列表页：
```
https://www.gov.cn/yaowen/liebiao/YYYYMM/content_XXXXXXXX.htm
```

文章内容页通常稳定，响应快。

## 新浪财经 lid=2517 实测结论（2026-06）

- `lid=2517` → 100%美股/国际金融新闻，零条国内政策，**不可用于政治监测**
- `lid=2516` → 同样是美股/国际头条
- 该 API 仅作宏观经济市场情绪参考

## 政策文章页内容抓取

政策文章页（如 `/yaowen/liebiao/content_*.htm`）内容完整，包含：
- 发布时间+来源（新华社/人民日报等）
- 完整正文段落
- 领导讲话原文

适合直接 `browser_navigate` → 提取 `<p>` 段落文本。

## 已知踩坑

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| `/lianbo/index.htm` 超时60s | 列表页含大量动态内容 | 跳过，直接访问文章页 |
| urllib 访问 gov.cn SSL错误 | 系统证书不兼容中文站点SSL | 换用 browser_navigate（走Chrome内置SSL） |
| 新浪财经 lid=2517 返回美股 | 该lid是国际财经专用 | 政治监测不用该API |

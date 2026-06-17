# 中国政府网站 gov.cn 可靠访问模式

## 2026-06 实测结论

### 不可用（超时/失败）

| URL | 原因 |
|-----|------|
| `www.gov.cn/lianbo/index.htm` | urllib: 302重定向循环；browser_navigate: 超时60s |
| `www.gov.cn/yaowen/index.htm` | 同上，超时60s |
| `www.gov.cn/lianbo/` 列表页任意形式 | 同上 |

### 可用（实测）

| URL | 方式 | 说明 |
|-----|------|------|
| `www.gov.cn/zhengce/zhengceku/gwywj/index.htm` | browser_navigate ✅ | 国务院政策文件库，JS渲染，browser_navigate获取完整列表 |
| `www.gov.cn/lianbo/YYYYMM/content_XXXXXXXX.htm` | browser_navigate ✅ | 直接文章页，不过列表 |
| `www.news.cn/politics/leaders/` | urllib ✅ | 中央领导机构页面 |
| `www.news.cn/politics/YYYYMMDD/xxxxx/c.html` | urllib ✅ | 新华网文章直连 |

### gov.cn 文章页 URL 结构

```
# 政务联播文章页
https://www.gov.cn/lianbo/202506/content_5321000.htm
#    └─ YYYYMM ─┘└─ content_数字.htm

# 政策文件库文章页
https://www.gov.cn/zhengce/zhengceku/202606/content_7071452.htm
#    └─ YYYYMM ─┘└─ content_数字.htm
```

content ID 是递增数字，无规律，不能枚举。

### 政策文件库（gwywj）页面结构

browser_navigate 渲染后内容：
- 每条记录是 `h4` + `span` 组合
- `h4` 内含 `a` 链接，文字是文件标题
- `span` 文字是日期 `YYYY-MM-DD`
- 日期最近的是2026-06-10（下次更新时可见最新）

urllib直读拿到的原始HTML不含JS渲染内容，只能提取到一个最新日期（2026-06-10），**不可用于实时监测**。

### 绕过列表页的工作流

1. 直接访问 `www.gov.cn/zhengce/zhengceku/gwywj/index.htm`（browser_navigate）
2. 解析渲染后页面中的 `h4` + `span` 组合获取所有文件标题+日期
3. 对比今日日期过滤最新发布
4. 点击具体文章URL获取正文

### 搜索不靠谱

Bing/Google 搜索gov.cn政策在cron环境超时。直接用browser_navigate访问政策库页面更稳定。

### 新华网文章页直连模式

已知文章页URL格式（从本次搜索结果）：
```
https://www.news.cn/politics/leaders/20250829/e4a2c7e258bb4eb797ea3e2daf25298b/c.html
```

从gov.cn列表页提取的链接可能是相对路径，需拼接完整URL。
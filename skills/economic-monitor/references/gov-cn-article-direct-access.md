# gov.cn Article Direct Access Pattern

**验证日期**：2026-06-13
**适用场景**：绕过失效的gov.cn列表页URL提取，直接获取政策文件/国常会/要闻正文

## 核心发现

gov.cn 列表页（yaowen/liebiao）的URL提取已失效（正则匹配不到新ID），但**直接 navigate 具体 article URL 完全正常**，3-5秒加载完整正文。

## URL格式

| 类型 | URL格式 |
|------|---------|
| 要闻/国常会 | `https://www.gov.cn/yaowen/liebiao/202606/content_7071845.htm` |
| 政策文件 | `https://www.gov.cn/zhengce/content/202606/content_7071451.htm` |
| 政务联播 | `https://www.gov.cn/lianbo/202606/content_7071831.htm` |

**路径规律**：`/yaowen/liebiao/` = 要闻；`/zhengce/` = 政策；`/lianbo/` = 政务联播

## 工作流

```
1. browser_navigate('https://www.gov.cn/') 
   → 从snapshot heading+link提取当日要闻列表

2. 过滤关键词命中的条目
   → 获得 article URL

3. browser_navigate('https://www.gov.cn/yaowen/liebiao/202606/content_7071845.htm')
   → 直接加载完整正文（李强主持国常会实测3-5秒）

4. 从snapshot/text提取：
   - 日期：re.search(r'<strong>(.*?)<\/strong>', text) 或读取首段
   - 新华社电头：正文首行"新华社北京X月X日电"
   - 全文内容：paragraph/text节点
```

## 已知可用 article URL（2026-06-13）

- `content_7071845` — 李强主持召开国务院常务会议（2026-06-11，20:02发布）
- `content_7071450` — 住建部："十五五"建设改造城市地下管网约77万公里

## 正文提取示例

```python
# 国常会文章正文结构
snapshot = browser_navigate('https://www.gov.cn/yaowen/liebiao/202606/content_7071845.htm')

# 提取日期（首段meta行）
date_match = re.search(r'(\d{4}-\d{2}-\d{2})', snapshot['text'][:200])

# 提取新华社电头+正文
# 页面结构：
# - title: "李强主持召开国务院常务会议..."
# - date: 2026-06-11 20:02
# - source: 新华社
# - body: 多个 <paragraph> 节点含正文内容
```

## 失效列表页对比

| 页面 | 状态 | 原因 |
|------|------|------|
| `https://www.gov.cn/lianbo/index.htm` | ❌ 超时60s | 页面不存在/重定向 |
| `https://www.gov.cn/yaowen/liebiao/` | ⚠️ 可加载但URL提取失效 | 页面含ancient IDs (5748xxx)，无新文章URL |
| `https://www.gov.cn/yaowen/liebiao/202606/content_7071845.htm` | ✅ 直接访问正常 | article页面独立可访问 |
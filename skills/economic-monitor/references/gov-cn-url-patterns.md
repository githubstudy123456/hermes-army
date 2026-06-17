# gov.cn 政务要闻 URL 格式与访问模式

## 已验证可用的 URL 结构

### 政务要闻列表页（推荐入口）
```
https://www.gov.cn/yaowen/liebiao/
```
- 加载时间：约3-5秒
- 内容：当日全部政务要闻，按发稿时间排序
- **不是** lianbo/index.htm（那个60s超时）

### 具体文章页
```
https://www.gov.cn/yaowen/liebiao/YYYYMM/content_NNNNN.htm
```
- 日期编码在路径中（如 `202606` 表示2026年6月）
- 内容 ID 是序列号，无明显规律
- 例：`https://www.gov.cn/yaowen/liebiao/202606/content_7071845.htm`

### 政策文件列表页
```
https://www.gov.cn/zhengce/index.htm
```
- 最新政策标签页：`https://www.gov.cn/zhengce/zuixin/`
- 政策解读：`https://www.gov.cn/zhengce/jiedu/`

## 不可用 URL（实测超时/404）

| URL | 问题 | 替代方案 |
|-----|------|---------|
| `https://www.gov.cn/lianbo/index.htm` | 超时60s | 用 yaowen/liebiao |
| `https://www.gov.cn/youce/list.htm?catalogCode=10401` | 404 | gov.cn yaowen |
| `https://www.gov.cn/lianbo/yaowen.htm` | 404 | gov.cn yaowen |

## 从首页快照导航到具体文章（2026-06-12实测）

gov.cn 首页（`https://www.gov.cn/`）的 `browser_snapshot` 返回的列表项含 article ref（如 `ref=e32`），直接用 `browser_click(ref)` 可打开对应文章，再 `browser_snapshot` 获取正文内容。

**工作流示例：**
```python
# 1. 获取首页快照
browser_navigate("https://www.gov.cn/")
browser_snapshot()  # 返回 ref=e32 等可点击元素

# 2. 点击要闻条目（ref=e32 = "李强主持召开国务院常务会议..."）
browser_click("e32")

# 3. 获取文章正文
browser_snapshot()  # 完整正文，含新华社电头+全文段落
```

**注意**：`browser_click` 后页面URL不一定变（可能是JS路由），但 `browser_snapshot` 可获取渲染后的完整正文。

## 已知内容特征（2026-06-11验证）

- gov.cn 要闻页无直接"经济政策"标签，需人工浏览标题判断
- 国务院常务会议内容通常在20:00-21:00发布（新华社同步）
- 教育/环保十五五规划属于常规政策，不含降准降息等核心宏观关键词
- CPI/PPI数据发布后 gov.cn 会有专题页面（如"5月居民消费价格指数总体平稳"）
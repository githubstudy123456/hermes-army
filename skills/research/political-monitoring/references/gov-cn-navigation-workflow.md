# gov.cn 导航工作流（2026-06 实测）

## 核心原则
**永远直接 nav 文章页，不要访问列表页。**

gov.cn 的列表页（lianbo/index.htm、yaowen/liebiao/）在 cron 环境下超时 60s，但从首页侧边栏点入具体文章 URL 则秒开。

## URL 模式

```
# 文章详情页（直接 nav，稳定）
https://www.gov.cn/yaowen/liebiao/YYYYMM/content_XXXXXX.htm

# 内容ID提取：链接中的 7071845 就是去重用的 content_id
https://www.gov.cn/yaowen/liebiao/202606/content_7071845.htm
                                                    ^^^^^^^^

# 政务联播列表（⚠️ 超时，不要直接访问）
https://www.gov.cn/lianbo/

# 政策文件库（✅ 稳定）
https://www.gov.cn/zhengce/index.htm
```

## 今日扫描工作流（2026-06-13 实测有效）

```python
# 1. browser_navigate 打开 gov.cn 首页（稳定）
browser_navigate("https://www.gov.cn/")

# 2. 从 snapshot 的要闻/政务联播/最新政策 区块中提取文章 URL
#    每条要闻的 URL 格式: /yaowen/liebiao/202606/content_7071845.htm
#    直接拼 https://www.gov.cn + 该路径 nav

# 3. 对每个 content_id 与今日已推送列表对比，决定是否推送
already_pushed = [7071845, 7071619, ...]  # 已知 content_id 列表
new_articles = [art for art in articles if art['id'] not in already_pushed]

# 4. 推送新文章并写入 ~/.hermes/political-reports/
```

## 内容ID 去重法

gov.cn 文章 URL 中的 `content_7071845.htm` → ID = `7071845`（六位十进制）

已推送文章 ID 列表（2026-06-13 部分）：
```
7071845 - 国常会（教育/美丽中国/审计整改）
7071619 - 习近平出席金正恩欢送仪式
7071438 - 教育部百日冲刺就业行动
7071450 - 城市地下管网77万公里
7071504 - 三峡水运新通道开工
7071965 - 小麦收获过八成
7071967 - 失能老人照护体系
7071984 - 机电产品出口占比
7071986 - 文化遗产保护（人民日报）
7071808 - 谌贻琴出席国际劳工大会
7071863 - 张国清出席全球趋同促增长峰会
7071451 - 现代化应急体系十五五规划
7071204 - 私募投资基金监管54号
7070901 - 农业农村现代化十四五规划
7070755 - 对外投资规定
```

## 已知踩坑

| 场景 | 错误做法 | 正确做法 |
|------|---------|---------|
| 访问要闻列表 | nav `lianbo/index.htm` 超时60s | nav 首页，从侧边栏点入 |
| 政务联播列表 | nav `/lianbo/` 超时 | 从首页政务联播区块点入 |
| 获取所有文章 | 依赖列表页 | browser_snapshot 首页，从结果中提取所有文章URL |
| 标题提取失效 | bb-browser google/search 标题=null | 改用 gov.cn browser_navigate 直读文章页 |

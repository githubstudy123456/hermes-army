# 法规追踪实战笔记（2026-06-15）

## 本次采集结果汇总

### 成功采集的信源
- gov.cn 要闻列表：https://www.gov.cn/yaowen/liebiao/ — 20条/页，含政策解读
- gov.cn 政策文件：https://www.gov.cn/zhengce/liebiao/ — 行政法规全文
- gov.cn 联播页：https://www.gov.cn/lianbo/index.htm — 重要新闻集合
- 网信办 CAC 首页：https://www.cac.gov.cn/ — 政策首发
- 新浪财经政经 API（lid=2517）— 实时政经新闻，凌晨可用

### 失败/不可用信源
- 银保监会 cbirc.gov.cn — DNS `ERR_NAME_NOT_RESOLVED`
- 央行 pbc.gov.cn/ — 部分 404，需尝试 http://www.pbc.gov.cn/ 备用
- 最高法 court.gov.cn — 大量子页面 404
- gov.cn 搜索 — 参数重定向完全失效
- Bing 搜索 — 返回大量百度百科/词典结果，需二次过滤

## 重要政策文件（2026-06-15 采集）

1. **国办函〔2026〕54号** — 私募投资基金监管指导意见（2026-06-05发布）
   - https://www.gov.cn/zhengce/content/202606/content_7071204.htm
   - 关键禁用行为：借贷、"名股实债"、通道化
   - 重要机制："吹哨人"制度、强制托管

2. **国发〔2026〕15号** — 现代化应急体系建设"十五五"规划（2026-06-08发布）
   - https://www.gov.cn/zhengce/content/202606/content_7071451.htm
   - 非直接相关但含数据安全条款

3. **网信办** — 金融信息服务数据分类分级指南（2026-06）
   - https://www.cac.gov.cn/ — 首页显示
   - 金融信息服务机构数据分类分级管理

4. **网信办** — 中国个人信息保护报告（2025年）
   - https://www.cac.gov.cn/ — 首页显示

## 简报格式模板

```
【法规追踪】YYYY年MM月DD日（周X）

一、本期新规速览
   [列出2-3条，每条含：法规名称、发布时间、核心要点]

二、新规影响分析
   [针对2条重点，说明：]
   - 对现有业务的影响
   - 需要调整的内容
   - 合规建议

三、法务部建议
   [可执行的具体行动建议，标记优先级]

四、参考来源
   [来源链接，每条一行]
```

## 存档路径

`~/.hermes/army-workspace/legal/regulatory-updates/regulatory-update-YYYYMMDD.txt`
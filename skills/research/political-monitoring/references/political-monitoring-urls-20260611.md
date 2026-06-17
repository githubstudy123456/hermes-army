# 政治监测 · gov.cn 要闻页验证（2026-06-11）

## 验证结果

| URL | 状态 | 说明 |
|-----|------|------|
| `https://www.gov.cn/lianbo/index.htm` | ❌ 超时60s | 政务联播首页不可访问 |
| `https://www.gov.cn/zhengce/index.htm` | ✅ 可用 | 政策文件列表页 |
| `https://www.gov.cn/zhengce/zuixin/` | ✅ 可用 | **最新政策**（按发稿时间排序，推荐入口） |
| `https://www.gov.cn/zhengce/xxgk/` | ✅ 可用 | 政府信息公开平台（政策文件完整列表，含发文字号） |
| `https://www.gov.cn/yaowen/liebiao/` | ✅ 可用 | **要闻列表页**（实时更新，推荐轮询入口） |
| `https://www.gov.cn/yaowen/liebiao/202606/content_7071845.htm` | ✅ 可用 | 国务院常务会议（2026-06-11）原文 |

## 最佳轮询路径（本session验证）

```
gov.cn 要闻列表 → https://www.gov.cn/yaowen/liebiao/
gov.cn 最新政策 → https://www.gov.cn/zhengce/zuixin/
gov.cn 政策文件库 → https://www.gov.cn/zhengce/xxgk/
```

## gov.cn 页面结构观察

### 要闻列表页（yaowen/liebiao）
- 每行格式：heading + 来源日期 + URL（`/yaowen/liebiao/YYYYMM/content_*.htm`）
- 内容：领导人活动、重要会议新闻稿、政策文件要闻
- 排序：按发稿时间倒序，最新在最前
- **今日（2026-06-11）最新条目**：
  - `content_7071855` — 工程机械数据（经济）
  - `content_7071854` — 朝鲜媒体评价习近平访朝
  - `content_7071853` — 东西部协作30年
  - `content_7071845` — **国务院常务会议（教育/美丽中国十五五/道交法修订）** ← P1
  - `content_7071837` — 《习近平外交文选》出版发行 ← P2
  - `content_7071826` — 张国清出席峰会（P4）
  - `content_7071808` — 谌贻琴出席国际劳工大会（P4）
  - `content_7071795` — 八部门铁路旅游融合（P3，已推）
  - `content_7071789` — 工信部AI+信息通信（P3，已推）
  - `content_7071714` — 人形机器人具身智能专项行动（P3，已推）

### 最新政策页（zhengce/zuixin）
- 格式：`国务院/国办 关于 XXX 的通知/意见`
- 日期：成文日期（早于发布日期）
- 今日最新（2026-06-11扫表）：
  - 国发〔2026〕15号 — 现代化应急体系建设"十五五"规划（2026-06-08）
  - 国办发 — 私募投资基金监管指导意见（2026-06-05）
  - 国发〔2026〕14号 — 加快农业农村现代化"十五五"规划（2026-06-02）

## 踩坑记录

1. **gov.cn/lianbo/ 超时**：不可用，换用 `yaowen/liebiao/`
2. **browser_navigate gov.cn 超时**：60s超时限制，需多试或换用政策列表页
3. **内容ID命名规律**：`content_YYYYMMDD_nnnn.htm`，发布日期可从URL推断
4. **同一事件多篇报道**：如习近平访朝同日出现5条不同角度报道 → 去重后合并为1条P2推送

## 去重检查实战（本session）

今日要闻中习近平访朝系列（5条）：
- 朝鲜媒体高度评价 / 中朝关系纪实 / 国际社会评价 / 弘扬优良传统 / 守护蔚蓝向海图强
- → 均指向同一事件，合并为P2外交事件推送1条

已推送报告（2026-06-11-2215_political.txt）已覆盖全系列，无需重复推送。
---
name: shenzhen-events-research
description: 深圳同城娱乐活动调研 — 豆瓣/猫眼多分类抓取，过滤今天/明天/本周，输出结构化活动列表
triggers:
  - 深圳 近期 活动
  - 深圳 周末 活动
  - 深圳 有什么 玩的
  - 深圳 演出 展览
---

# 深圳同城活动调研

## 来源优先级
1. **豆瓣同城深圳**（JS渲染，必须用浏览器工具）
2. **猫眼演出**（大型演出/演唱会）
3. ~~深圳政府网~~（只有政务公告，不是娱乐来源）

## 豆瓣分类URL（browser_navigate）
| 分类 | URL |
|------|-----|
| 全部 | `/location/shenzhen/events/week-all` |
| 音乐 | `/location/shenzhen/events/week-music` |
| 演唱会 | `/location/shenzhen/events/week-1003` |
| 戏剧 | `/location/shenzhen/events/week-drama` |
| 喜剧/脱口秀 | `/location/shenzhen/events/week-comedy` |
| 展览 | `/location/shenzhen/events/week-exhibition` |
| 运动 | `/location/shenzhen/events/week-sports` |
| 聚会/社交 | `/location/shenzhen/events/week-party` |
| 课程/体验 | `/location/shenzhen/events/week-course` |
| 电影 | `/location/shenzhen/events/week-film` |
| 赛事 | `/location/shenzhen/events/week-competition` |
| 亲子 | `/location/shenzhen/events/week-kids` |

## 输出格式
按**今天 / 明天 / 本周**三档分类，每条：
`名称 | 时间 | 地点 | 费用`

费用标注：¥数字 / 免费（突出）/ "280元起"保留"起"字

## 陷阱
- curl 拿不到豆瓣数据（JS渲染）→ 必须 `browser_navigate`
- 政府网不是娱乐来源
- 豆瓣购票直通车道具有延迟，优先采信主列表
- 部分活动多日连续，日期格式"xx月xx日 ~ xx月xx日"
- **免费观影/福利活动多为抽奖制**：进入活动详情页后，必须检查「名单公布」时间。如果今天是公布日期之后，活动已结束，**不要推荐给用户**
- **检查活动状态**：打开活动页后，关注"报名参加"按钮状态 + 活动须知里的「名单公布：X月X日」/ 「中奖才可以参加」等字样，如果已过公布日期则跳过

## 工作流
1. `browser_navigate` 打开分类页
2. `browser_snapshot` 提取活动
3. 滚动 + 再 snapshot 补全（豆瓣只渲染可见区域）
4. 按日期过滤，汇总输出

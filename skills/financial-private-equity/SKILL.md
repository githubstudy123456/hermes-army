---
name: financial-private-equity
description: 私募股权投资工作台 — 覆盖项目筛选、尽职调查、IC Memo 起草、组合报告四大模块，支持 PE 投资全生命周期。
version: 0.1
owner: hermes-finance
tags: [private-equity, screening, diligence, ic-memo, portfolio-report, deal-sourcing, investment]
created: 2026-06-15
trigger: 当主人要求"项目筛选"、"尽职调查"、"IC Memo"、"组合报告"、"PE"时自动激活
---

# Financial Private Equity · 私募股权投资工作台

## 核心定位

统一的私募股权投资工作台，覆盖项目筛选、尽职调查、IC Memo 起草、组合报告四大模块，支持 PE 投资全生命周期（从 deal sourcing 到投后管理）。

---

## 模块菜单

| 模块 | Skill 章节 | 适用触发词 |
|------|-----------|-----------|
| 项目筛选 | [§项目筛选](#项目筛选) | `筛选项目`、`deal sourcing`、`项目初筛`、`投资机会筛选` |
| 尽职调查 | [§尽职调查](#尽职调查) | `尽职调查`、`尽调`、`due diligence`、`DD清单` |
| IC Memo 起草 | [§IC Memo 起草](#ic-memo-起草) | `IC Memo`、`投资委员会`、`投委会报告` |
| 组合报告 | [§组合报告](#组合报告) | `组合报告`、`portfolio report`、`被投企业报告` |

---

## 项目筛选

### 触发条件
- 用户输入包含 deal sourcing / screening / 项目筛选 / 投资机会 / pipeline
- 分析师请求对目标公司进行快速初判
- PE 团队例行 pipeline review

### 执行步骤
**Step 1 · 收集项目基本信息（web）**
- 通过公开来源（PitchBook、Crunchbase、新闻、官网）获取标的：
  - 公司名称、成立时间、总部所在
  - 所处行业与细分赛道
  - 商业模式（产品/服务、变现方式）
  - 创始团队背景与过往经历
  - 融资历史（轮次、估值、领投方）

**Step 2 · 行业与竞争格局分析（web）**
1. 目标行业市场规模（TAM）及增速（5年CAGR）
2. 行业竞争格局：头部玩家、市场份额、集中度
3. 标的公司的差异化壁垒（技术/品牌/网络效应/监管资质）
4. 政策环境：是否受监管、补贴、限制

**Step 3 · 财务指标初筛（web + terminal）**
1. 获取可获得的财务数据（营收、增速、毛利率、EBITDA）
2. 计算关键指标：营收 CAGR、Gross Margin / EBITDA Margin、烧钱速度、ARR
3. 对标行业 Comps（EV/Revenue、EV/EBITDA、P/S）
4. 使用 `terminal` 执行 Python 脚本快速计算评分

**Step 4 · 估值水平评估（web）**
1. 最近一轮估值 vs. 行业平均估值倍数
2. 本轮融资预期估值区间
3. 估值是否在基金策略覆盖范围（Size Check）

**Step 5 · 筛选评分卡输出**
| 维度 | 权重 | 评分(1-5) | 说明 |
|---|---|---|---|
| 行业赛道 | 20% | | TAM、CAGR、格局 |
| 商业模式 | 15% | | 可规模化、壁垒 |
| 团队背景 | 15% | | 过往业绩、行业资源 |
| 财务表现 | 20% | | 增速、利润率 |
| 估值合理性 | 15% | | vs. Comps |
| 基金策略匹配 | 15% | | 规模、阶段、关注点 |

**加权总分** = Σ(评分 × 权重)，输出是否建议进入尽调

### Pitfalls
1. 数据来源不权威：仅依赖新闻稿或公司官网
2. 行业判断主观：未量化赛道规模
3. 财务数据残缺：早期项目无公开财报，使用估算数据时未标注不确定性
4. 估值倍数滥用：用 ARR 倍数套用到非订阅模式公司
5. 忽略基金策略匹配：好项目不一定适合本基金

### Verification
- [ ] 行业数据来源标注
- [ ] 财务数字有据可查
- [ ] 估值倍数与行业 Comps 一致
- [ ] 评分卡逻辑自洽
- [ ] 结论与数据匹配

---

## 尽职调查

### 触发条件
- 用户输入包含 due diligence / 尽职调查 / 尽调 / DD checklist
- 项目通过初筛，需要正式进入尽调阶段
- IC 会议前需要完整尽调材料

### 执行步骤
**Step 1 · 确认尽调范围与时间表**
1. 确认基金类型（Buyout / Growth / Venture）及投资策略
2. 确定尽调时间表（通常 4–12 周）和关键节点（IC deadline）
3. 确认标的公司提供的数据室（Virtual Data Room）访问权限
4. 组建尽调团队（业务/财务/法律/技术各负责人）

**Step 2 · 业务尽调（Business DD）**
- 市场与竞争：TAM / SAM / SOM 分析、客户画像、客户留存率与 concentration risk
- 商业模式：收入结构、单位经济模型（Unit Economics）
- 成长性：历史增速驱动因素、未来增长假设及敏感性

**Step 3 · 财务尽调（Financial DD）**
- 历史财务数据：过去 3–5 年三张表、Adjusted EBITDA、收入确认政策
- 盈利质量：收现比（CFS/NI）、DSO、ITO、DPO
- 估值模型支持：LBO 模型输入数据核实

**Step 4 · 法律尽调（Legal DD）**
- 公司治理：股权结构、Vesting Schedule、董事会构成
- 合同合规：重大合同审查、知识产权、监管合规资质
- 诉讼与或有负债：正在进行的诉讼、潜在诉讼风险

**Step 5 · 运营与技术尽调（Operational & Tech DD）**
- 运营体系：核心业务流程、关键供应商依赖度
- 技术尽调：技术架构与护城河、数据安全与隐私合规

**Step 6 · 尽调清单追踪与报告输出**
使用 `terminal` 生成 Markdown 尽调追踪表：
| 模块 | 尽调事项 | 负责方 | 状态 | 完成度 |
|---|---|---|---|---|
| 业务 DD | TAM 分析 | @Analyst A | 已完成 | 100% |

### Pitfalls
1. 尽调时间不足：压缩尽调周期导致关键问题未深入挖掘
2. 依赖公司提供数据：未独立核实
3. 忽略尾部风险：小概率事件未纳入分析
4. 财务尽调不深入：仅看 EBITDA，忽略现金流质量
5. 法律尽调流于形式：未仔细审查股东协议中的保护性条款

### Verification
- [ ] 业务 DD 数据来源标注
- [ ] 财务数据与审计报告一致
- [ ] 法律文件清单完整
- [ ] 尽调完成度 ≥ 80% 方可提交 IC Memo

---

## IC Memo 起草

### 触发条件
- 用户要求起草投资委员会（IC）备忘录
- 项目尽调完成后需要提交 IC 决策

### 执行步骤
**Step 1 · 收集 IC 材料**
- 项目筛选评分卡 + 尽调报告 + 财务模型
- 确认基金策略匹配性
- 确认交易结构（股权/债权/估值区间）

**Step 2 · 提炼投资亮点与风险**
- 投资亮点（≥3 条，每条附数据支撑）
- 主要风险因素（≥3 条，含风险缓解措施）
- 团队评估（背景、过往业绩）

**Step 3 · 财务摘要**
- 关键假设（收入增速、利润率、WACC）
- 估值区间（DCF 区间、Comps 区间）
- IRR 预测（基础/乐观/悲观）
- 退出路径分析

**Step 4 · IC Memo 结构生成**
```
1. Executive Summary
2. Investment Highlights
3. Risk Factors & Mitigants
4. Team Assessment
5. Financial Summary & Valuation
6. Investment Recommendation
7. Appendix
```

**Step 5 · 输出**
- 生成 Word/PowerPoint 格式
- 标注"STRICTLY CONFIDENTIAL — FOR IC DISCUSSION ONLY"

### Pitfalls
1. 亮点与风险不匹配数据
2. IRR 假设过于乐观
3. 缺乏退出路径分析
4. 格式不符合 IC 标准模板

### Verification
- [ ] 所有数据有来源标注
- [ ] IRR 敏感性分析覆盖关键假设
- [ ] 退出路径有具体分析
- [ ] 文档标注"CONFIDENTIAL — FOR IC DISCUSSION ONLY"

---

## 组合报告

### 触发条件
- 用户要求生成被投企业组合报告
- 季度/年度 LP 报告场景
- 投后管理定期 review

### 执行步骤
**Step 1 · 收集组合数据**
- 被投企业财务数据（季报/年报）
- 运营数据（用户数/GMV/ARR 等）
- 估值数据（最新一轮估值/净资产）
- 重大事项（融资/高管变动/监管）

**Step 2 · 财务分析**
- 各被投企业收入/EBITDA/净亏损
- 组合加权平均收入增速
- 组合整体 IRR（已投项目）
- 净资产/账面价值分析

**Step 3 · 运营分析**
- 关键运营指标汇总
- 里程碑达成情况
- 与预算/预测对比

**Step 4 · 生成组合报告**
```
# Portfolio Report · [年份]Q[X]

【组合概览】
- 被投企业数量：X
- 总投资成本：X万元
- 最新净资产（NAV）：X万元
- 组合 IRR：X%

【各被投企业情况】
| 企业 | 行业 | 投资成本 | 净资产 | IRR | 关键指标 |

【重大事项】
1. [企业名称]：[事项描述]

【下季度关注事项】
1. ...
```

### Pitfalls
1. 数据截止日期不一致
2. IRR 计算忽略资金时点
3. 缺少与上期对比
4. 敏感数据未脱敏

### Verification
- [ ] 数据截止日期一致
- [ ] IRR 计算基于实际资金时点
- [ ] 包含与上期环比
- [ ] LP 敏感数据已脱敏
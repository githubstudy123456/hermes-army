# hermes-financial · 金融部

> 来源：[github.com/anthropics/financial-services](https://github.com/anthropics/financial-services)  
> Stars: 20.8k · 官方模板版本

## 部门定位

金融部（Financial Services Division），专注投资银行、股票研究、私募股权、财富管理场景，辅助分析师完成模型、备忘录、研报、对账工作流。所有输出需人工复核，不构成投资建议。

---

## 7个垂直领域（Vertical Plugins）

### equity-research · 股票研究
- 财报笔记提取与整理
- 首发覆盖（Initiation）报告draft
- Model update 追踪
- 投资主题（Thesis）追踪与验证

### financial-analysis · 财务分析
- Comps 分析（三张表横向对比）
- DCF、LBO 模型搭建
- Excel 审计与 QC 检查
- Pitch deck 财务数据校验

### investment-banking · 投资银行
- CIM（Confidential Information Memorandum）draft
- Teaser 制作
- Buyer list / Seller list 梳理
- Merger model + deal tracker
- 竞标流程管理

### private-equity · 私募股权
- Deal sourcing & screening
- 尽职调查（Due Diligence）支持
- IC Memo（投资委员会备忘录）draft
- Portfolio 监控与 reporting

### wealth-management · 财富管理
- 客户账户定期 review
- 财务计划（Financial Plan）制定
- Rebalancing 建议
- Tax-Loss Harvesting（税务亏损抵减）

### fund-admin · 基金管理
- GL（总账）对账与差异溯源
- Break tracing（账目差异追踪）
- NAV tie-out（净值对齐）
- 月结/年结支持

### operations · 运营
- KYC 文档解析与合规筛查
- AML/KYC 规则引擎
- 客户尽职调查（CDD）流程

---

## 11个专职 Agent

| Agent | 用途 | 领域归属 |
|---|---|---|
| **pitch-agent** | 路演材料：Comps + Precedents + LBO → branded pitch deck | investment-banking |
| **market-researcher** | 行业研究、竞争格局、comps、idea 短名单 | equity-research |
| **earnings-reviewer** | 财报 + 建模更新 + 笔记草稿 | equity-research / financial-analysis |
| **model-builder** | DCF、LBO、三张表、comps，输出 live Excel | financial-analysis |
| **valuation-reviewer** | GP package 估值、LP 报告审查 | private-equity / fund-admin |
| **kyc-screener** | 开户文档解析 + KYC/AML 规则引擎 | operations |
| **gl-reconciler** | 找账目差异、溯源、分发审批 | fund-admin |
| **month-end-closer** | 应计、roll-forward、差异分析 | fund-admin |
| **statement-auditor** | LP 报表审计 | fund-admin |
| **meeting-prep-agent** | 客户会前 briefing pack 准备 | wealth-management |
| **dataroom-watcher** | 虚拟数据室监控与动态更新 | private-equity / corporate |

---

## Skills（按领域划分）

### equity-research
- `earnings-analysis` · 财报关键数据提取
- `model-update` · 模型更新流程
- `thesis-tracker` · 投资主题追踪
- `initiation-draft` · 首发报告draft

### financial-analysis
- `comps-analysis` · 可比公司三张表
- `dcf-model` · DCF模型搭建
- `lbo-model` · LBO模型搭建
- `excel-audit` · Excel勾稽关系审计

### investment-banking
- `cim-draft` · CIM起草
- `teaser-builder` · Teaser制作
- `merger-model` · Merger model
- `deal-tracker` · 交易进度管理

### private-equity
- `screening` · 项目筛选
- `diligence-checklist` · 尽调清单
- `ic-memo` · 投资委员会备忘录
- `portfolio-report` · Portfolio监控报告

### wealth-management
- `client-review` · 客户账户review
- `rebalancing` · 组合再平衡
- `tax-loss-harvest` · 税务亏损抵减
- `financial-plan` · 财务计划制定

### fund-admin
- `gl-recon` · 总账对账
- `break-trace` · 差异溯源
- `nav-tieout` · 净值对齐
- `month-end-close` · 月结流程

### operations
- `kyc-screening` · KYC合规筛查
- `aml-check` · 反洗钱核查
- `cdd-process` · 客户尽职调查

---

## 数据接口（MCP Connectors）

已集成（按需启用）：
- Daloopa、Morningstar、S&P Capital IQ、FactSet、Moody's
- MT Newswires、Aiera、LSEG、PitchBook
- Chronograph、Egnyte

---

## 推送目标

- 紧急风控预警 → 订阅群 `oc_c6883cd907e4d226736d87ce9c6c6d79`
- 每日市场简报 → 主人 DM
- 持仓标的重大事件 → 即时推送
- 每周组合复盘 → 周报

---

## 禁止事项

- 不提供具体买卖点位
- 不承诺投资收益
- 不传播内幕消息
- 不代客理财
- 所有建议标注"仅供参考，不构成投资建议"
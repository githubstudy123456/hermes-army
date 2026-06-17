# Anthropic Claude for Financial Services

**来源**：[github.com/anthropics/financial-services](https://github.com/anthropics/financial-services)
**Stars**：20.8k
**状态**：待处理
**添加时间**：2026-05-12

---

## 项目定位

Anthropic 官方出品的金融服务业 AI Agent 系统，面向投行、PE、Equity Research、财富管理场景，辅助分析师draft工作产物（模型、备忘录、研报、对账），所有输出需人工复核。

---

## 核心模块

### Agent（9个）

| Agent | 用途 |
|---|---|
| Pitch Agent | Comps + precedents + LBO → branded pitch deck |
| Meeting Prep Agent | 客户会前briefing pack |
| Market Researcher | 行业研究、竞争格局、comps、idea短名单 |
| Earnings Reviewer | 财报 + 建模更新 + 笔记草稿 |
| Model Builder | DCF、LBO、三张表、comps，live Excel |
| Valuation Reviewer | GP package估值、LP报告 |
| GL Reconciler | 找账目差异、溯源、分发审批 |
| Month-End Closer | 应计、roll-forward、差异分析 |
| Statement Auditor | LP报表审计 |
| KYC Screener | 开户文档解析 + 规则引擎 |

### 垂直插件包

- **financial-analysis**（核心）：comps、DCF、LBO、三张表、Excel审计、deck QC
- **investment-banking**：CIM、teaser、buyer list、merger model、deal tracker
- **equity-research**：财报笔记、initiation、model update、thesis追踪
- **private-equity**：sourcing、screening、diligence、IC memo、portfolio监控
- **wealth-management**：客户review、财务计划、rebalancing、TLH
- **fund-admin**：GL recon、break tracing、NAV tie-out
- **operations**：KYC文档解析

### 数据接口（11个MCP Connector）

Daloopa、Morningstar、S&P Capital IQ、FactSet、Moody's、MT Newswires、Aiera、LSEG、PitchBook、Chronograph、Egnyte

### 部署方式

1. **Claude Cowork 插件**：网页直接装，无需服务器
2. **Claude Managed Agents API**：自建编排层，调用 `/v1/agents`

---

## 技术细节

- **文件结构**：纯 Markdown + JSON，无构建步骤
- **Skills**：按领域垂直划分，agent 打包时同步一份
- **Connectors**：MCP（Model Context Protocol）标准，配置 `.mcp.json`
- **命令**：`/comps`、`/dcf`、`/lbo`、`/earnings`、`/ic-memo` 等

---

## 部署前提

- [ ] Anthropic API Key（ANTHROPIC_API_KEY）
- [ ] `claude` CLI（Node.js 环境）
- [ ] 如用 Managed Agent：自建编排层（orchestrate.py）

---

## 潜在用途

- [ ] 拆出 DCF/LBO 模型 skill 单独使用
- [ ] 拆出 GL Recon 工作流
- [ ] 财富管理场景的 client review agent
- [ ] PE deal sourcing & screening agent

---

## 备注

> Nothing in this repository constitutes investment, legal, tax, or accounting advice. All outputs require human review before use.

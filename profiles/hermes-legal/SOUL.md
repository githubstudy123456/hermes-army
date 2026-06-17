# hermes-legal · 法律部

> 来源：[github.com/anthropics/claude-for-legal](https://github.com/anthropics/claude-for-legal)  
> Stars: 7.9k · 官方模板版本

## 部门定位

法律部（Legal Division），面向企业内部法务、隐私合规、知识产权、诉讼支持、监管合规等场景，辅助律师完成合同审查、文件起草、合规监控、研究检索等工作流。所有输出为草稿，需律师审核确认，不构成法律结论。

---

## 9个垂直领域（Practice Areas）

### corporate-legal · 公司法务
- 董事会会议记录
- Closing checklist（交割清单）
- Entity compliance（实体合规）
-  Written consent 起草
- Deal team summary
- Integration management（整合管理）
- Material contract schedule（重大合同清单）
- 尽职调查（Due Diligence）问题提取

### commercial-legal · 商事合同
- Vendor agreement review（供应商合同审查）
- NDA triage（保密协议分类）
- SaaS MSA review（SaaS主协议审查）
- Renewal tracker（续约追踪）
- Escalation flagger（升级路由）
- Stakeholder summary（业务侧摘要）
- Amendment history（合同变更追溯）
- Matter workspace（案件工作区）

### employment-legal · 劳动法务
- 员工假期/请假追踪（leave-tracker）
- 劳动合同合规性审查
- 竞业限制条款评估
- 保密义务与发明归属
- 入离职流程合规

### ip-legal · 知识产权
- IP renewal watcher（商标/专利续展监控）
- 著作权登记与管理
- 商标侵权监测
- 专利布局分析
- 开源许可合规

### litigation-legal · 诉讼支持
- Docket watcher（诉讼日程监控）
- 诉状/答辩状 draft
- 证据组织与管理
- 诉讼时效追踪
- 判决执行跟踪

### privacy-legal · 隐私合规
- Privacy policy（隐私政策）审查
- Cookie 政策
- 数据处理协议（DPA）审查
- GDPR/中国PIPL合规
- 数据泄露响应流程

### product-legal · 产品法务
- Launch watcher（产品上市合规审查）
- Terms of Service（用户协议）
- 平台规则与治理机制
- 用户生成内容（UGC）合规
- 儿童保护政策

### regulatory-legal · 监管合规
- Regulatory change monitor（监管动态监控）
- 行业监管报告合规性审查
- 执法动态追踪
- 合规培训与咨询

### ai-governance-legal · AI治理法务
- AI产品合规评估
- 算法备案与公示
- AI伦理审查
- 生成式AI合规（深度合成、算法推荐等）

---

## 各领域专职 Agent

| Agent | 用途 | 领域归属 |
|---|---|---|
| **renewal-watcher** | 续约监控（90天内到期合同清单） | commercial-legal |
| **deal-debrief** | 合同签署后偏差记录（帮助完善 playbook） | commercial-legal |
| **playbook-monitor** | 合同偏差达到阈值时提议更新 playbook | commercial-legal |
| **dataroom-watcher** | 虚拟数据室动态监控 | corporate-legal |
| **leave-tracker** | 员工假期余额与请假流程追踪 | employment-legal |
| **ip-renewal-watcher** | 商标/专利到期续展提醒 | ip-legal |
| **docket-watcher** | 诉讼日程节点监控 | litigation-legal |
| **launch-watcher** | 产品上市前合规checklist | product-legal |
| **reg-change-monitor** | 监管政策变动即时推送 | regulatory-legal |

---

## Skills（按领域划分）

### corporate-legal
- `ai-tool-handoff` · AI工具与法务工作流对接
- `board-minutes` · 董事会会议记录
- `closing-checklist` · 交割清单
- `cold-start-interview` · 新业务/客户接入访谈
- `deal-team-summary` · 交易团队摘要
- `diligence-issue-extraction` · 尽调问题提取
- `entity-compliance` · 实体合规管理
- `integration-management` · 整合期管理
- `material-contract-schedule` · 重大合同清单
- `matter-workspace` · 案件工作区
- `tabular-review` · 表格化审查
- `written-consent` · 书面同意书起草

### commercial-legal
- `cold-start-interview` · 团队playbook初始化
- `vendor-agreement-review` · 供应商合同审查
- `nda-review` · 保密协议快速分类（GREEN/YELLOW/RED）
- `saas-msa-review` · SaaS主协议审查
- `renewal-tracker` · 续约追踪
- `escalation-flagger` · 升级路由
- `stakeholder-summary` · 业务侧摘要
- `amendment-history` · 合同变更追溯
- `matter-workspace` · 案件工作区

### employment-legal
- `leave-tracker` · 假期追踪与合规
- `employment-contract-review` · 劳动合同审查
- `non-compete-assessment` · 竞业限制评估
- `ip-assignment` · 发明归属确认

### ip-legal
- `ip-renewal-watcher` · 知识产权续展监控
- `trademark-watch` · 商标侵权监测
- `open-source-compliance` · 开源许可合规

### litigation-legal
- `docket-watcher` · 诉讼日程监控
- `pleading-draft` · 诉状/答辩状起草
- `evidence-org` · 证据组织管理

### privacy-legal
- `privacy-policy-review` · 隐私政策审查
- `cookie-policy` · Cookie政策
- `dpa-review` · 数据处理协议审查
- `breach-response` · 数据泄露响应

### product-legal
- `launch-watcher` · 产品上市合规审查
- `tos-review` · 用户协议审查
- `ugc-compliance` · 用户生成内容合规

### regulatory-legal
- `reg-change-monitor` · 监管动态监控
- `reg-report-review` · 监管报告合规性审查

### ai-governance-legal
- `ai-product-assessment` · AI产品合规评估
- `algorithm-filing` · 算法备案
- `genai-compliance` · 生成式AI合规审查

---

## 部署说明

**Cold Start 流程**（commercial-legal 专属）：
1. `/legal:cold-start-interview` 启动团队playbook初始化
2. 提供 5-10 份近期签署的合同作为参考样本
3. 系统生成 `CLAUDE.md`，记录团队偏好和立场
4. 之后所有 skill 读取该文件，输出自动对齐团队风格

**权限与行为准则**：
-  consequential actions（发送、归档、执行）需明确确认才执行
-  引用来源标注 `[verify]`，需人工核实
-  律师-委托人特权标记保守，防止意外 waived

---

## 推送目标

- 重大合同到期/续约提醒 → 订阅群 `oc_c6883cd907e4d226736d87ce9c6c6d79`
- 监管政策重大变动 → 即时推送主人
- 知识产权到期预警 → 提前30天推送
- 诉讼日程重要节点 → 提前7天推送

---

## 禁止事项

- 不出具正式法律意见书
- 不承诺诉讼/仲裁结果
- 不代替律师做出判断
- 所有输出标注"草稿，需律师审核确认"
- 不传播当事人隐私信息
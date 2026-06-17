---
name: legal-risks
description: 合同风险深度分析（条款打分 + 财务影响估算）
trigger: 用户发来合同文本或文件，要求分析风险/审合同/看合同有没有坑
owner: lobster-legal
version: 0.1
---

# 合同风险分析

## 触发条件

- 用户发来合同文本（粘贴或文件）
- 用户说"帮我看看这个合同有没有坑"
- 用户说"审一下这份合同"

## 工作流程

### Step 1：判断合同类型

| 类型 | 识别信号 |
|------|---------|
| SaaS/软件许可 | subscription/SLA/uptime/license |
| 服务合同 | services/deliverables/scope of work |
| 劳动合同 | employee/salary/benefits/at-will |
| NDA | confidential/non-disclosure/receiving party |
| 租赁合同 | landlord/tenant/premises/rent |
| 销售合同 | buyer/seller/purchase price/warranty |
| 投资协议 | investor/equity/convertible/SAFE |

### Step 2：逐条风险评分

每个条款 1-10 分：

- **1-3**：低风险，标准条款
- **4-6**：中等风险，需要关注
- **7-10**：高风险，需要修改

### Step 3：重点排查

- 无上限赔偿条款
- 自动续约陷阱（短取消窗口）
- 宽泛的保密信息定义
- 单方面修改权
- 隐性费用/涨价机制
- 不合理的竞业限制
- 知识产权归属过于宽泛
- 第三方嵌入风险（通过引用纳入其他文件）

### Step 4：财务影响估算

对于高风险条款，估算潜在损失：
- 违约赔偿规模
- 律师费
- 机会成本

## 输出格式

```
⚠️ 合同风险评估报告

合同类型：xxxxx
对方当事人：xxxxx
合同期限：xxxxx

【安全评分】X/10

【高风险条款】（7分以上）
1. [条款位置] — 风险：xxxxx | 建议修改：xxxxx
2. ...

【中等风险条款】（4-6分）
1. ...

【标准条款】（略）

【财务影响估算】
- 最大风险敞口：xxxxx
- 建议风险准备金：xxxxx

【综合建议】
- 必须修改：xxxxx
- 建议谈判：xxxxx
- 可接受：xxxxx
```

## 注意

- 评分要有具体理由，不可只给分数
- 财务估算需说明假设条件
- 涉及主观判断时说明"法律上没有统一标准"
- 如果合同文本过短或不完整，先要求补充完整再出具正式报告
# Hermès 军团架构（2026-06-17 确立）

## 核心理念

- **CEO（commander）只做四件事**：拆解任务、派发部门、跟踪进度、汇总汇报
- **先广后细原则**：执行层充分表达 → 高管专业判断 → 过滤深化 → 汇总汇报
- **具体执行交给下属**，CEO 不做具体产出

## 完整架构图

```
commander（CEO）— 只做：拆解任务、派发部门、跟踪进度、汇总汇报
├── COO  → hermes-content / hermes-marketing / hermes-pm / hermes-qa
├── CFO  → hermes-financial
├── CIO  → hermes-collector / hermes-data-science / hermes-ai-lab
├── CLO  → hermes-legal（仅法律合规，政经研究归研究部）
└── CTO  → hermes-architect / hermes-fullstack / hermes-dev-frontend / hermes-dev-backend / hermes-dev-3d / hermes-test / hermes-devops / hermes-security
```

## 高管职责边界

| 高管 | 下属 | 职责边界 |
|------|------|---------|
| COO | content/marketing/pm/qa | 日常运营/项目管理/质量保证 |
| CFO | financial | 财务分析/资本运作（**不含法律合规**） |
| CIO | collector/data-science/ai-lab | 信息战略/数据采集/AI研发 |
| CLO | legal | 法律合规/合同审查/算法备案（**仅法律，不做政经研究**） |
| CTO | 8个技术部门 | 技术战略/架构/开发/测试/运维/安全 |

## 先广后细工作流（所有高管通用）

**第一阶段（广）：收集所有输出**
1. 复述确认：用自己的话复述任务目标和交付标准
2. 拆解派发：给下属下达**具体可执行指令**（含明确交付物、格式、截止标准）
3. 等回报：不做预判，让每个 agent 充分输出
4. 汇总合并：收集所有产出，不删减，全部汇总

**第二阶段（细）：过滤与深化**
5. 专业判断：按下属专业领域过滤噪声、识别重点
6. 补充深化：对重要结论追问细节，让对应下属补充
7. 整合输出：形成有主次的完整产出，汇报 commander

> 原则：先让执行层充分表达，高管再做判断和过滤。

## Profile 创建检查清单

新建 hermes-xxx 时必须完成：
1. `SOUL.md` — 角色定义、专长、边界（**必须写明"不做XX"防止越界**）
2. `config.yaml` — name / description / approval / toolsets
3. toolsets 根据部门类型配置（不是通用堆砌）：

| 部门类型 | toolsets |
|---------|---------|
| 研究类 | terminal file browser web |
| 技术支撑 | terminal file browser web delegation cronjob |
| 内容/生活 | terminal file browser vision |
| 信息采集 | terminal file browser web |
| 高管 | terminal file browser web session_search |

## CLO vs 研究部 边界

- **CLO/legal**：法律合规、合同审查、AI监管合规、算法备案
- **研究部**：政治/经济/市场/生活/战略/产业研究

两者互不重叠。CLO 不做政经研究，研究部不做法律合规。

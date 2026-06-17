# DAG Workflow YAML Schema（Agency Orchestrator 兼容）

> Reverse-engineered from `jnMetaCode/agency-orchestrator` v1.x. 理解这个 schema 才能正确编写和调试 workflows。

## 顶层结构

```yaml
name: "工作流中文名"
description: "一句话描述触发条件和行为"

# 全局设置
concurrency: 5          # 最大并行节点数（可选，默认无限制）
inputs:                 # 入口变量定义（可选）
  - name: variable_name
    description: "描述"
    required: true|false
    default: "默认值"

steps:
  - id: node_id         # 唯一标识，snake_case
    role: profile名      # 调用的 profile（如 hermes-cto）
    task: |             # 任务描述，支持 {{variable}} 插值
      ...
    output: output_var  # 输出变量名，供下游消费
    depends_on: [node_id, ...]   # 前置依赖节点
    depends_on_mode: all_completed|any_completed  # 汇聚模式
    condition: "{{context_var}} contains 关键词"   # 条件触发
    priority: critical|high|normal|low  # 优先级（可选）
    secretary: hermes-xxx-secretary    # 秘书审核（可选）
    output_mode: append|replace       # 输出追加或替换（可选）

metadata:              # 元信息（可选，不影响执行）
  version: "1.0"
  author: Hermès Corp
  created: "2026-06-17"
  tags: [...]
```

## 节点类型

### 入口节点（无 `depends_on`）
```yaml
- id: commander_analyze
  role: commander
  task: |
    你是 Hermès CEO...
  output: commander_decision
  required_context:
    - request        # 声明需要哪些输入变量
```

### 部门执行节点（条件触发）
```yaml
- id: coo_dept
  role: hermes-coo
  task: |
    {{commander_decision}}
    {{request}}
  output: coo_report
  depends_on: [commander_analyze]
  condition: "{{commander_decision}} contains COO"
  secretary: hermes-coo-secretary
```

### 汇聚节点（等待所有分支完成）
```yaml
- id: commander_final
  role: commander
  task: |
    {% if coo_report %}COO报告：{{coo_report}}{% endif %}
    {% if cto_report %}CTO报告：{{cto_report}}{% endif %}
  depends_on: [coo_dept, cto_dept, ...]
  depends_on_mode: all_completed   # 全部完成才触发
  output: final_decision
```

## 条件触发（Conditional Edge）

```yaml
condition: "{{variable}} contains STRING"    # 包含关键词
condition: "{{variable}} not contains STRING"  # 不包含
condition: "{{variable}} matches REGEX"      # 正则匹配
condition: "{{variable}} == VALUE"           # 等于
```

**condition 写在节点上，而不是边上**。Engine 评估条件为 true 才激活该节点。

### 多条件组合
```yaml
condition: "{{incident_classification}} contains 后端故障 or {{incident_classification}} contains P0"
```

## 变量注入（Context Injection）

上游 `output` 自动成为下游可引用的变量：

```yaml
# 节点 A
- id: triage
  role: hermes-cto
  output: incident_classification   # 输出这个变量

# 节点 B（引用 A 的输出）
- id: backend_emergency
  role: hermes-cto
  task: |
    分类结果：{{incident_classification}}   # 直接插值使用
  depends_on: [triage]
  condition: "{{incident_classification}} contains 后端故障"
```

## 模板语法（Jinja2）

```yaml
# 条件输出
{% if coo_report %}
**COO 报告：**{{coo_report}}
{% endif %}

# 默认值
{{optional_var|default("未涉及该部门")}}
```

## DAG 执行顺序

Engine 按以下规则自动排序：
1. 无依赖的节点并行启动（`concurrency` 限制内）
2. 依赖节点全部 `depends_on_mode` 完成后，触发下游
3. `condition` 为 false 的节点跳过，不占并发槽位

## 实际 DAG 示例（故障响应）

```yaml
steps:
  - id: triage          # 无依赖，最先跑
    role: hermes-cto
    output: classification

  - id: backend_analysis   # 依赖 triage，triage 完就跑
    depends_on: [triage]
    condition: "{{classification}} contains 后端故障"
    output: backend_result

  - id: frontend_analysis  # 与 backend_analysis 并行
    depends_on: [triage]
    condition: "{{classification}} contains 前端故障"
    output: frontend_result

  - id: postmortem         # 依赖两个分析节点，都完才跑
    depends_on: [backend_analysis, frontend_analysis]
    depends_on_mode: all_completed
    output: postmortem
```

**执行图：**
```
triage ──┬──→ backend_analysis ──┐
         └──→ frontend_analysis ─┴──→ postmortem
```

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `depends_by` | 拼写错误 | 正确写法是 `depends_on` |
| 节点未激活 | condition 永远为 false | 检查变量名和关键词是否匹配 |
| 汇聚节点未触发 | depends_on_mode=all_completed 但有分支跳过 | 有分支时应改用 `any_completed` 或确保所有分支都执行 |
| 变量未定义 | output 变量名拼写错误 | 检查上游 output 和下游引用是否一致 |

---
name: software-development-methodology
description: 软件开发方法论全集 — 任务闭环 SOP + 系统化调试 + 快速验证实验 + Python 调试工具
version: 0.1
owner: lobster
tags: [software-development, methodology, debugging, task-management, python, experiments, sop]
created: 2026-05-31
trigger: 主人进行复杂开发任务、需要调试、需要进行实验验证时激活
---

# 软件开发方法论

> **本技能已吸收以下窄化技能的核心内容：**
> - `task-closure-sop` → 附录A：任务闭环 SOP
> - `systematic-debugging` → 正文：系统化调试流程（4阶段法）
> - `python-debugpy` → 附录B：Python 调试工具
> - `spike` → 附录C：快速验证实验

> **保留在此分类中的独立技能：**
> - `frontend-dev-patterns` — 前端开发模式（React/TypeScript/Next.js 专项）
> - `systematic-debugging` 中直接保留了 task-closure-sop 的完整内容（不再单独归档 task-closure-sop）

---

# 系统化调试（4阶段法）

## 核心原则

> **NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST**
> 随机修复浪费时间并引入新 bug。快速补丁掩盖潜在问题。
> **在找到根本原因之前，不允许提出修复方案。**

## 何时使用

适用于任何技术问题：
- 测试失败
- 生产环境 bug
- 异常行为
- 性能问题
- 构建失败
- 集成问题

**特别要用于：**
- 时间紧迫时（紧急情况更容易猜）
- "就一个快速修复"看起来很明显时
- 已经尝试了多种修复时
- 之前的修复没有奏效时

---

## 阶段1：根本原因调查

**在尝试任何修复之前：**

### 1. 仔细阅读错误信息
- 不要跳过错误或警告
- 错误通常包含精确的解决方案
- 完整阅读堆栈跟踪
- 记录行号、文件路径、错误码

### 2. 稳定复现
- 能可靠地触发吗？
- 确切步骤是什么？
- 每次都发生吗？
- 如果无法复现 → 收集更多数据，不要猜测

### 3. 检查最近变更
- 什么变更可能导致这个问题？
- Git diff、最近提交
- 新依赖、配置变更

### 4. 多组件系统证据收集

**在系统有多个组件时（API → service → database）：**
- 在每个组件边界添加诊断日志
- 记录进入组件的数据
- 记录离开组件的数据
- 验证环境/配置传播
- 检查每层状态

### 5. 追踪数据流

**当错误在调用栈深处时：**
- 坏值从哪里起源？
- 什么调用了这个函数并传入了坏值？
- 一直追踪到找到源头
- 在源头修复，不要在症状处修复

### 阶段1完成检查清单
- [ ] 错误信息完全阅读并理解
- [ ] 问题能稳定复现
- [ ] 最近变更已识别和审查
- [ ] 证据已收集（日志、状态、数据流）
- [ ] 问题已隔离到特定组件/代码
- [ ] 已形成根本原因假设
- **停止：** 在完成阶段1之前不要进入阶段2

### Build-First 发现模式

某些错误只在 `npm run build`（Turbopack/Next.js）时出现，不在 dev 模式或类型检查时出现：

- 嵌套路由中错误的相对导入路径（`'../../../../lib/stripe'` 但写成 `'../../../lib/stripe'`）
- 复杂嵌套查询结果中的 TypeScript 类型不匹配
- 扩展联合类型后缺少变体（如在 `ModelKind` 添加 `'spring-oscillator' | 'wave-equation' | 'optics-demo'` — `tsc --noEmit` 通过但 `App.tsx` 的 `modelLabelMap` 缺少条目，导致构建错误）
- **useMemo 变量顺序 TDZ 错误：`ReferenceError: Cannot access 'X' before initialization`** — 在 Next.js 16 + Turbopack 中，在同一函数组件中后面声明的 `useMemo`/`useCallback` 引用的变量，即使在另一个 hook 内部引用，也可能在 `tsc --noEmit` 通过但在运行时失败。**修复：** 将计算派生状态的 `useMemo`/`useCallback` 声明移到 `useState` 声明之后、首次引用之前。

**实践：** 创建或修改 Next.js 路由文件后，始终运行 `npm run build` 再手动测试 — 它能捕获运行时不会显示直到路由被调用时的导入解析和类型错误。

**当构建超时（>120s）时：** 回退到 `npx tsc --noEmit` 做快速类型验证，然后手动运行构建确认。

---

## 阶段2：模式分析

**在修复之前找到模式：**

### 1. 找到工作的例子
- 在同一代码库中找到类似的正常工作的代码
- 什么能工作是类似的但有问题的？

### 2. 与参考实现对比
- 如果是实现某个模式，阅读参考实现**完整内容**
- 不要略读 — 完整阅读每一行
- 在应用之前完全理解模式

### 3. 识别差异
- 工作和损坏之间有什么不同？
- 列出每一个差异，无论多小
- 不要假设"那不重要"

---

## 阶段3：假设与测试

**科学方法：**

### 1. 形成单一假设
- 清晰陈述："我认为 X 是根本原因，因为 Y"
- 写下来
- 要具体，不要模糊

### 2. 最小化测试
- 做**最小的可能改变**来测试假设
- 一次只改一个变量
- 不要同时修复多个东西

### 3. 验证后再继续
- 成功了吗？→ 阶段4
- 没成功？→ 形成**新的**假设
- **不要在顶上加更多修复**

---

## 阶段4：实施

**修复根本原因，不是症状：**

### 1. 创建失败的测试用例
- 最简单的复现
- 如果可能，自动化测试
- 必须在修复前有测试

### 2. 实施单一修复
- 解决已识别的根本原因
- 一次一个改变
- 不要有"既然在这里"的改进

### 3. 验证修复
```bash
pytest tests/test_module.py::test_regression -v
pytest tests/ -q
```

### 4. 如果修复不奏效 — 三次规则
- **停止。** 数一下：你尝试了多少次修复？
- 如果 < 3：回到阶段1，用新信息重新分析
- **如果 ≥ 3：停止并质疑架构（见下）**
- 不经架构讨论不要再尝试修复 #4

### 5. 如果3+次修复失败：质疑架构

**表明架构问题的模式：**
- 每次修复都在不同地方揭示新的共享状态/耦合
- 修复需要"大规模重构"才能实施
- 每次修复在其他地方产生新症状

**停止并质疑基础：**
- 这个模式根本上是合理的吗？
- 我们是"纯粹因为惯性而坚持"吗？
- 架构重构 vs 继续修复症状？

---

## 附录A：任务闭环 SOP（task-closure-sop）

### 触发条件
当任务满足以下任一条件时，强制执行本 SOP：
- 任务需要 3 步以上操作
- 任务有明确交付物（文件/代码/报告）
- 任务结果需要用户确认

### 七步闭环流程

#### Step 1 — 目标确认
```
[ ] 用 clarify 确认：最终交付物是什么？
[ ] 确认成功标准：什么样算完成？
[ ] 确认截止时间（如果有）
```

#### Step 2 — 规划步骤
```
[ ] 把任务拆解成 N 个有序步骤（不超过7步）
[ ] 识别每步的检查点（checklist item）
[ ] 预估每步的工具和耗时
[ ] 如果步骤 > 7，拆分或委托子任务
```
**主人偏好：** 一次只处理一个阻塞项，不允许提前并行启动多个方向。收到任务后先列出所有阻塞项 → 问主人按什么顺序处理 → 按指定顺序一个个解决。**例外**：明确说"可以同时做"的才能并行。

#### Step 3 — 执行 + 检查点
每执行一步后：
```
[ ] 对照检查点确认该步完成
[ ] 记录关键发现（toolong → 写到临时文件）
[ ] 如果检查点失败 → 记录原因 → 重试或调整
```

#### Step 4 — 验证输出
```
[ ] 交付物存在且非空
[ ] 格式正确（文件类型、内容结构）
[ ] 自查：如果我是用户，会满意这个结果吗？
[ ] 如果不满意 → 回退到 Step 2 重新规划
```

#### Step 5 — 异常处理（最多3次重试）
- 第1次失败：记录原因 → 调整策略（换工具/换方法）→ 重试
- 第2次失败：记录原因 → 尝试完全不同路径 → 重试
- 第3次失败：停止重试 → 汇报：任务卡在哪里 + 已尝试的方法 + 建议方案 → 升级给用户决策

#### Step 6 — 结果汇报
```
📋 任务状态：✅ 完成 / ⚠️ 部分完成 / ❌ 失败
📦 交付物：[文件路径或内容摘要]
📝 执行摘要：[N] 步，[X] 次重试，[Y] 个检查点通过
💡 备注：[如果有的话]
```

#### Step 7 — 交接确认
```
[ ] 用户确认收到 / 满意
[ ] 如果需要后续行动 → 创建 cronjob 或记录到 MEMO
[ ] 更新当天日记（当天日记文件追加记录）
```

---

## 附录B：Python 调试工具（python-debugpy）

### pdb REPL（内置，无需安装）

```python
import pdb; pdb.set_trace()
```

常用 pdb 命令：
- `n` (next) — 执行下一行
- `s` (step into) — 进入函数
- `c` (continue) — 继续到下一个断点
- `p variable_name` — 打印变量
- `l` (list) — 查看当前代码上下文
- `w` (where) — 当前调用栈

### debugpy（远程 DAP 调试）

适合 VSCode/IDEA 远程调试：

```python
import debugpy
debugpy.listen(("0.0.0.0", 5678))  # 在断点前调用
```

launch.json（VSCode）：
```json
{
  "name": "Python: Remote Attach",
  "type": "python",
  "request": "attach",
  "host": "<服务器IP>",
  "port": 5678
}
```

### 常见 Python 崩溃排查

| 错误 | 排查方向 |
|------|----------|
| `AttributeError: 'NoneType'...` | 对象未初始化或函数返回 None |
| `IndexError: list index out of range` | 索引越界，边界检查缺失 |
| `KeyError` | 字典键不存在，用 `.get()` 或 `setdefault()` |
| `ImportError` | 模块路径问题，确认 `sys.path` |
| `MemoryError` | 大数据处理，检查是否一次性加载太大文件 |
| `RecursionError` | 递归没有出口，增加递归深度或改用循环 |

---

## 附录C：快速验证实验（spike）

### 目的

在正式构建之前，快速验证一个想法是否可行。适用于：
- 技术可行性不确定
- 需要在两种方案之间选择
- 不知道某个库/框架能否做到

### 原则

1. **有时间限制**：最多 2 小时，不出结果就放弃
2. **最小化**：只写验证核心想法的最少代码
3. **记录结果**：包括失败的结果（这个路径不行）
4. **立即丢弃**：验证完就删，不要留到正式代码库

### 输出模板

```
【Spike 结果】[想法描述]
日期：[日期]
用时：[X] 小时

结论：✅ 可行 / ❌ 不可行

发现：
1. [什么可行/不可行]
2. [关键细节]

如果可行，下一步：
- [具体下一步行动]
```

---

## 附录D：Flask 特定调试模式

> 适用于 Flask API 开发、Flask + SSH 多组件调用、Flask + Japan 服务器等跨服务架构。

### D.1 `app.run()` 是阻塞陷阱

**症状**：`/api/xxx` 路由注册正确，`test_client()` 测试通过，但外网 curl 访问返回 404，且 Flask 日志显示 `"GET /api/xxx HTTP/1.1" 404`。

**根因**：`app.run()` 是同步阻塞调用。如果 `if __name__ == '__main__': app.run(...)` 写在代码底部，在它之前的路由函数确实会被注册并可访问——但如果 Japan/远程路由写在 `app.run()` 之后（因为开发时先写了 `app.run()`，后来在上面追加路由），这些后加的路由在运行时不会被注册到真实 server。

**另一层陷阱**：Flask `test_client()` 在同一进程内加载所有路由（包括 `if __name__` 之后的），但实际 `python3 app.py` 启动的进程只执行 `app.run()` 之后的代码。

**排查顺序**：
1. 确认端口上跑的是哪个进程：`ss -tlnp | grep 5001`
2. 确认进程加载的是哪个文件：`cat /proc/<pid>/cmdline`
3. 确认文件行数：路由是否写在 `if __name__` 之前
4. 用 Python `urllib` 而非 curl 测试真实端口
5. 用 `curl http://localhost:5001/api/subjects` 验证基础路由是否正常

**修复**：把所有 `@app.route` 写在 `if __name__` 之前，或把 `if __name__` 移到最后。

### D.2 subprocess shell=False 对路径空格/中文截断

**症状**：命令在 terminal 直接跑成功，但通过 `subprocess.run([...], shell=False)` 失败，报 `FileNotFoundError` 或路径被截断到第一个空格。

**根因**：`shell=False` 时，列表元素按 whitespace 分割（空格、制表符、换行）。路径含空格（如 `第1课时  长度的单位和测量.pptx`）被切分成多个参数。

**解法**：用 base64 编码路径，传给 Japan 服务器的脚本解码：
```python
import base64
full_path = f"/data/baidu-library/files/{clean_path}"  # clean_path 含空格
encoded_path = base64.b64encode(full_path.encode('utf-8')).decode('ascii')
cmd = ["/usr/bin/ssh", "-i", "/home/ubuntu/.ssh/japan", "-o", "StrictHostKeyChecking=no",
       "root@207.56.226.147", "python3", "/tmp/hermes/parse_pptx_b64.py", encoded_path]
result = subprocess.run(cmd, shell=False, capture_output=True, text=True, timeout=60)
```

### D.3 curl vs Python urllib URL 编码行为差异

**症状**：Python `urllib.request.urlopen(url)` 返回 200 并正确 JSON，但 `curl url` 返回 404 或 400。

**根因**：HTTP 客户端对 `%20`（空格编码）和非 ASCII 字符的 URL 编码实现不一致。Python `urllib.parse.quote()` 和 JavaScript `encodeURIComponent()` 行为接近（都 encode 空格为 `%20`），但 curl 在某些 shell 环境下会二次 decode。

**验证方法**：始终用 Python urllib 测试 API，不依赖 curl 结果：
```python
import urllib.request, urllib.parse
path = '第1课时  长度的单位和测量.pptx'  # 含空格
url = 'http://localhost:5001/api/japan/pptx?path=' + urllib.parse.quote(path)
resp = urllib.request.urlopen(url, timeout=65)
data = json.loads(resp.read())
```

### D.4 跨服务器 SSH 架构调试流程

**架构**：`本地 Flask (:5001) → SSH → Japan (远端执行 Python 脚本)`

**调试三层分离**：
1. **Layer 1 - 本地 Flask 路由**：先确认 `/api/japan/pptx` 收到请求，返回非 404。用 `curl http://localhost:5001/api/japan/pptx?path=test` 或 Python urllib 验证。
2. **Layer 2 - SSH 连接**：直接 SSH 测试连接稳定性：`ssh -i ~/.ssh/japan root@207.56.226.147 'echo ok'`。注意 SSH 端口 22 有时被临时阻断（Connection refused），重试即可。
3. **Layer 3 - 远端脚本**：直接 SSH 执行脚本验证：`ssh ... 'python3 /tmp/hermes/parse_pptx_b64.py <b64path>'`。不经过 Flask。

**分层验证日志格式**：
```
Layer1: curl http://localhost:5001/api/xxx → HTTP xxx
Layer2: ssh -i ~/.ssh/japan root@207.56.226.147 'echo ok' → exit:0
Layer3: ssh ... 'python3 /tmp/hermes/parse_pptx_b64.py <b64>' → N页JSON
```

**每次只动一个变量**：修 SSH 脚本 → Layer3 验证 → 通过后 → Layer2 验证 → 通过后 → Layer1 验证。

---

## 附录E：前端开发模式（Frontend Dev Patterns）

> 来源：`frontend-dev-patterns` — 本节已吸收其核心内容，原技能归档

### 核心原则

- **Never disable `strict: true`** — TypeScript 严格模式错误是真实 bug
- **组件定义顺序**：`useState` → `useEffect` → `useMemo/useCallback` → 事件处理函数 → `return JSX`。所有派生状态计算放首次引用之前。
- **禁止"统一格式强迫症"**：没有模型的章节不加多余按钮，UI是内容的容器不是框架

### React + TypeScript 常见模式

#### 动态 Import 与 strict null

```typescript
let THREE: typeof import('three') | null = null
const init = async () => {
  THREE = await import('three')
  const mesh = new THREE!.Mesh(geometry, material) // 断言在调用点
}
```

#### forwardRef + 泛型 Props

```typescript
export const MyWrapper = forwardRef<MyRef, MyProps>(
  function MyWrapper({ prop1, prop2 }, ref) {
    useImperativeHandle(ref, () => ({
      method1: () => { ... },
      getValue: () => value,
    }), [value])
    return <div>{prop1}</div>
  }
)
```

#### 外部控制 vs 内部 State 同步

```typescript
function Player({ initialStep = 0, onStepChange }: PlayerProps) {
  const [step, setStep] = useState(initialStep)
  useEffect(() => { setStep(initialStep) }, [initialStep])
  const goToStep = (s: number) => {
    setStep(s); onStepChange?.(s)
  }
}
```

### Next.js 关键坑

| 错误 | 修复 |
|------|------|
| `Cannot find name 'ComponentName'` | 缺少 import — 检查所有引用 |
| `'THREE' is possibly null` | `!` 断言在调用点，非赋值点 |
| 静态预渲染 TDZ | `force-dynamic` 或 `useMemo` 声明顺序移到首次引用前 |
| 嵌套路由导入深度 | `../../../../lib/` 逐级回退 |

**Webhooks 必须显式关闭静态优化：**
```typescript
export const dynamic = 'force-dynamic'
```

**Supabase Service Role vs Anon Key：**
- Service Role：后端管理操作（用 `SUPABASE_SERVICE_ROLE_KEY`）
- Anon Key：公开读（`createBrowserSupabaseClient()`）

### Next.js Build-First 发现模式

某些错误只在 `npm run build`（Turbopack）时出现，不在 dev 模式或 `tsc --noEmit` 时出现：

- 嵌套路由错误的相对导入路径
- 扩展联合类型后 `modelLabelMap` 缺少条目（如 `ModelKind` 添加新变体后）
- `useMemo` 变量顺序 TDZ：`ReferenceError: Cannot access 'X' before initialization`

**规则**：创建/修改路由文件后，始终 `npm run build` 再手动测试。

---

## 通用原则

- **无捷径**：没有调查就没有修复
- **无猜测**：系统性方法比随机尝试快
- **架构问题用架构方式解决**：不要用第4、第5个修复补丁掩盖架构问题
- **复杂任务不走捷径**：特别是 Step 1 和 Step 2 看起来花时间，实际省时间
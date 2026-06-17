# Phase 2 开发流水线 — 并行化执行模式

## 背景

本参考文档来源于物理教学平台 Phase 2 开发（2026-05-25）。该阶段从需求到交付完整跑通，验证了一种高效的并行化开发流水线。

---

## 核心模式：5阶段 + 3路并行

```
阶段1: lobster-market 调研
  → Supabase选型报告（定价/BaaS对比/国内访问/Stripe集成）

阶段2: lobster-product PRD  ←→  lobster-architect 架构设计  ←并行执行
  → phase2-prd.md                    → phase2-architecture.md

阶段3: lobster-dev-frontend    ←→    lobster-dev-3d    ←→    lobster-dev-backend   ←并行执行
  → SpringOscillator.tsx              → 物理引擎hook       → Supabase数据层
  → WaveSimulator.tsx                                           (lib/supabase.ts
  → OpticsSimulator.tsx                                        API routes重写
                                                                  init.sql/seed.sql)

阶段4: lobster-test 验收
  → test-report.md

阶段5: commander 交付
```

**关键原则**：
- 阶段2（PRD + 架构）可以完全并行，因为 product 管功能边界、architect 管技术边界，两者互不依赖
- 阶段3（三路并行）需要前端先建立好类型定义（`src/types/physics.ts`），后端/3D 依赖它
- 阶段4（测试验收）在阶段3全部完成后执行

---

## 委派任务（delegate_task）模式

### 并行委派语法
```python
# 两个任务并行
delegate_task(goal="...", role="leaf", toolsets=[...])
delegate_task(goal="...", role="leaf", toolsets=[...])

# 三个任务并行（max_concurrent_children=3）
delegate_task(goal="...", role="leaf", toolsets=[...])
delegate_task(goal="...", role="leaf", toolsets=[...])
delegate_task(goal="...", role="leaf", toolsets=[...])
```

### 委派目标写法（goal）
清晰说明：
1. 项目路径
2. 具体交付物（含文件路径）
3. 物理公式/技术要求（如有）
4. 验收标准（可测试的条目）

### 典型失败模式：子agent超时
- **症状**：`Subagent timed out after 600.0s`，只完成部分文件
- **原因**：任务过于庞大，子agent在Web查找或长文本生成时卡住
- **解法**：拆分成更小的任务单元，或手动接管直接生成

### 手动接管模式
当子agent失败时，直接用 `write_file` 或 `terminal` 手动生成：
```
lobster-dev-frontend 超时
  → 手动创建 useSpringPhysics.ts（72行）
  → 重新委派 SpringOscillator/WaveSimulator/OpticsSimulator
```

---

## 物理模型组件架构

### 模式：Hook → Component
```
src/types/physics.ts           — 统一类型定义（SpringConfig/WaveConfig/OpticsConfig）
src/hooks/useSpringPhysics.ts   — 物理引擎hook（解析解，useCallback缓存）
src/components/physics/
  SpringOscillator.tsx          — Canvas 2D，弹簧演示 + x-t图 + 能量图
  WaveSimulator.tsx             — Canvas 2D，横波/纵波，requestAnimationFrame驱动
  OpticsSimulator.tsx           — Canvas 2D，凸透镜光线追迹，三条特殊光线
```

### 物理引擎要求
- **解析解优先**：不用数值积分，保证精度
- **requestAnimationFrame**：驱动动画循环
- **Canvas 2D**：用 useRef + getContext('2d')，不用 Three.js（轻量）
- **Play/Pause/Reset**：标准控制界面

---

## Supabase 数据层模式

### 文件结构
```
src/lib/supabase.ts              — 客户端（浏览器端 + 服务端）
.env.local.example               — 环境变量模板
src/app/api/curriculum/route.ts  — 重写为从Supabase读取
src/app/api/narration/[id]/route.ts — 重写为从Supabase读取
src/app/api/webhooks/stripe/route.ts — 完整Stripe三个事件处理
supabase/
  init.sql                       — DDL + RLS + 人教版8上种子数据
  seed.sql                       — 人教版8下全册数据
```

### RLS策略（重要）
- profiles：用户只能读写自己的
- user_progress：用户只能读写自己的
- subscriptions：用户只能读写自己的

---

## 验证方法

### TypeScript类型快速检查（不用build）
```bash
cd /home/ubuntu/physics-visual-platform
npx tsc --noEmit
```
比 `npm run build` 快（不触发Turbopack全量构建），适合快速验证新增文件。

### 完整build（耗时120s+）
```bash
npm run build
```
验证通过 = 所有路由 + 所有组件 + 所有API routes全部通过Turbopack类型检查。

### 开发服务器启动（后台进程）
```bash
# 启动（后台）
terminal(background=true, command="cd $PROJECT && npm run dev")

# 健康检查
curl -s --max-time 5 http://localhost:3000/api/health

# API验证
curl -s http://localhost:3000/api/curriculum
```

---

## 陷阱与限制

1. **子agent超时**：任务过大致超时，拆小或手动接管
2. **npm run build 超时**：Turbopack全量构建耗时120s+，用 `npx tsc --noEmit` 替代快速验证
3. **Supabase未配置时**：API返回友好错误，不暴露内部细节
4. **Stripe Webhook**：需要类型扩展 `& { current_period_end?: number }` 解决TS报错
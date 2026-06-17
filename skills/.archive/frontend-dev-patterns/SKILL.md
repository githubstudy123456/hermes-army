---
name: frontend-dev-patterns
description: "Frontend development patterns: React + TypeScript + Next.js component architecture, state management, and build troubleshooting."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [frontend, react, typescript, nextjs, component-architecture, state-management]
    related_skills: [systematic-debugging, task-closure-sop]
---

# Frontend Development Patterns

## Overview

React + TypeScript + Next.js frontend work. Covers component architecture, state management patterns, TypeScript strict mode issues, and build troubleshooting.

## Common Patterns

### 1. Dynamic Import with Strict Null Check

When using `await import('module')` inside `useEffect`, TypeScript infers the module as potentially `null`:

```typescript
let THREE: typeof import('three') | null = null

const init = async () => {
  THREE = await import('three')
  const mesh = new THREE!.Mesh(geometry, material)  // Assert at usage sites
}
```

**Why:** TypeScript doesn't narrow the type when assignment happens inside an async function callback to a variable declared outside.

**Fix:** Use non-null assertion (`!`) at every usage site, not at assignment.

### 2. React Component Closure Pitfall

Avoid referencing parent-closure functions in components defined after the parent return statement:

```typescript
// WRONG — reference error at runtime
function App() {
  const handleStepChange = useCallback((step: number) => { ... }, [])
  return <ChildComponent />  // handleStepChange not yet in scope
}
```

**Fix:** Pass as explicit prop to component defined later:

```typescript
function App() {
  const handleStepChange = useCallback((step: number) => { ... }, [])
  return <ChildComponent handleStepChange={handleStepChange} />
}
```

### 3. forwardRef with Generic Props

When creating wrapper components that forward refs:

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

### 4. State Sync: External Control vs Internal State

When a component needs to both accept external state AND manage internal state:

```typescript
function Player({ initialStep = 0, onStepChange }: PlayerProps) {
  const [step, setStep] = useState(initialStep)
  
  // Sync when prop changes
  useEffect(() => {
    setStep(initialStep)
  }, [initialStep])
  
  // Local transitions update internal state AND notify parent
  const goToStep = (s: number) => {
    setStep(s)
    onStepChange?.(s)
  }
}
```

### 5. Next.js Build Issues

| Error | Fix |
|-------|-----|
| `Cannot find name 'ComponentName'` | Missing import — check all component references are imported |
| `'THREE' is possibly null` | Use `!` assertion at usage sites for dynamic imports |
| Missing `next/dynamic` for client components | Add `'use client'` to component file, not just import |

## TypeScript Strict Mode

- **Never disable `strict: true`** — the errors it catches are real bugs
- For Next.js, add `"strict": true` to `tsconfig.json` if not present
- Use `as Type` assertions sparingly; prefer proper type narrowing

## Build Verification

Always run `npm run build` after component changes. Next.js with Turbopack may surface errors not visible in dev mode.

## Next.js App Router Patterns

### Nested Route Import Depth

API routes nested more than 2 levels deep need `../../../../lib/` style imports. See `references/nextjs-nested-route-imports.md`.

### Webhook Routes

Webhook routes must use `export const dynamic = 'force-dynamic'` to disable static optimization (required for raw body parsing).

### Supabase SSR Query Patterns

When using `createClient` from `@supabase/supabase-js` in route handlers, use `SUPABASE_SERVICE_ROLE_KEY` (not the anon key) for admin operations:

```typescript
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL ?? '',
  process.env.SUPABASE_SERVICE_ROLE_KEY ?? ''
)
```

For public-read queries, the anon key via `createBrowserSupabaseClient()` is sufficient.

### 6. Educational Content Platform: Content-First → Model-Second Pattern

For physics/science teaching platforms, the UI should follow a **learn before explore** sequence:

```
知识点精讲区（默认展开）
  └─ 标题 / 学习目标 / 原理讲解 / 典型例子 / 易错点 / 练习
  └─ 底部："🔷 进入模型演示 →" 按钮（点击展开模型区）

模型区（默认隐藏，点击按钮才展开）
  └─ 3D 交互 + 参数控制面板
  └─ 右上角 × 关闭按钮
```

**为什么：** 学习的认知顺序是：先建立基础概念，再通过交互模型深化理解。上来就展示模型会分散注意力。

**实现要点：**
- 模型区用 `isModelExpanded` state 控制，默认 `false`
- 知识点卡片底部条件渲染模型入口按钮（`{point.model !== 'none' && modelOptions.length > 0 && ...}`)
- 点击按钮 → `setModelExpanded(true)` + slideDown 动画
- 关闭按钮 → `setModelExpanded(false)`
- `npm run build` 验证编译通过后重启服务

**相关项目：** `/home/ubuntu/physics-visual-platform/`（物理教学平台，人教版初中物理）

## Session References

- `references/typescript-strict-null-dynamic-import.md` — Detailed TypeScript strict null + dynamic import patterns
- `references/nextjs-nested-route-imports.md` — Import path depth for nested App Router routes
- `references/physics-platform-ui-patterns.md` — Physical education platform specific patterns (知识点→模型 staged layout, drawer hierarchy, data sourcing from curriculum.json)
- `references/nextjs-prerender-circular-ref.md` — **Next.js static prerendering TDZ/ReferenceError from circular type imports** — fix: `force-dynamic` or reordering `useMemo` declarations before their first references
- `references/nextjs-supabase-stripe-backend.md` — **Next.js + Supabase SSR + Stripe Checkout + webhooks + curriculum API** — patterns for service-role clients, webhook raw body, checkout session creation
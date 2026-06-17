---
name: nextjs-prerender-circular-ref
version: 1.0.0
description: Fix Next.js static prerendering ReferenceError from circular type imports
triggers: ["build error", "ReferenceError", "prerender", "Cannot access before initialization"]
---

# Next.js Build Error Debugging

## Prerendering `ReferenceError: Cannot access 'X' before initialization`

### Symptoms
```
Error occurred prerendering page "/".
ReferenceError: Cannot access 'U' before initialization
Export encountered an error on /page: /, exiting the build.
⨯ Next.js build worker exited with code 1 and signal: 1
```
Or `Cannot access 'Y' before initialization` — variable name changes but pattern is consistent.

### Root Cause
Circular or bidirectional type imports between a data file and a component:
- `physicsContent.ts` — exports large `chapters` array + type definitions
- Component imports `type { AnimationKind, Introduction }` from data file
- Data file does NOT import from component, but the file is large enough that bundler creates separate chunks
- Next.js static prerendering tries to evaluate both modules in same worker
- Module evaluation order violations cause TDZ (Temporal Dead Zone) errors for variables that reference each other

Key enablers:
- File is large (~88KB `physicsContent.ts`)
- Data module has no default export — only named exports
- Component does `import type` (only types), not runtime imports from data
- `moduleResolution: "bundler"` in tsconfig may widen the problem

### Fix
Add to the page entry point (`src/app/page.tsx`):

```typescript
import App from '../App'

export const dynamic = 'force-dynamic'

export default function HomePage() {
  return <App />
}
```

`force-dynamic` forces SSR (server-rendered on demand) instead of static prerendering. Eliminates the prerendering worker entirely.

### Additional Root Cause (today's session)

Even after adding `force-dynamic`, the dev server can still report TDZ errors if **useMemo declarations are placed after their first references** in the component:

```typescript
// WRONG — hasIntro uses `point` before the useMemo that defines `point`
const hasIntro = point.introduction      // ← ReferenceError at runtime
const point = useMemo(() => ..., [])     // ← too late
```

```typescript
// CORRECT — useMemo declarations come BEFORE their first use
const chapter = useMemo(...)  // ← define before use
const point = useMemo(...)   // ← define before use
const hasIntro = point.introduction  // ← safe
```

**Lesson:** `force-dynamic` bypasses static prerendering, but in-development reloading can still expose TDZ ordering bugs if `useMemo`/`useState` declarations reference each other out of order. Next.js 16 Turbopack is stricter than the old webpack bundler about this.

### Why This Works
Static prerendering uses isolated workers that evaluate imports independently — susceptible to circular-ref TDZ errors. SSR shares the Node.js module cache, resolving bindings correctly. The runtime behavior is identical.

### Alternative Fixes (if force-dynamic has tradeoffs)
1. **Inline types** in the component instead of importing from data file:
   ```typescript
   type AnimationKind = 'ruler' | 'train' | 'race' | 'slope'
   type Introduction = { title: string; scene: string; visual: string; animationKind: AnimationKind }
   ```
   — This breaks when App.tsx also imports types from physicsContent (dual import creates same problem)

2. **Extract types to separate file** `src/types/physics.ts` — both data file and component import from there, breaking the cycle

3. **Add dummy default export** to data file — sometimes helps bundler resolve module boundaries

### Verification
```bash
cd /home/ubuntu/physics-visual-platform
rm -rf .next && npm run build 2>&1 | grep -E "Error|✓|⨯"
```
Should show `✓ Compiled successfully` and `ƒ` (Dynamic) route, not static prerender.

Then restart server and verify with curl.

### Related Errors
- `"U" before initialization` — same pattern, different minified variable name
- Build compiles but prerender fails — classic circular import during SSG
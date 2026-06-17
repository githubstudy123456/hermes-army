# Next.js App Router — Relative Import Path Depth

## The Problem

When creating API routes in `src/app/api/<path>/<subpath>/route.ts`, relative imports to shared libraries (`src/lib/`) require the correct number of `../` levels based on directory depth.

## Rule

From `src/app/api/<a>/<b>/route.ts`:
- `src/lib/` is at depth 2 from `src/app/api/`
- Count `../` from route file up to `src/app/` then down to `src/lib/`
- Formula: `../` × (number of dir segments below `api/`) + `lib/`

```
src/app/api/webhooks/stripe/route.ts
         └── api/webhooks/stripe/   = 3 segments below api/
         └── go UP 3 times → src/app/
         └── go DOWN to lib/       → ../../../../lib/stripe
```

### Depth Reference Table

| Route file location | `../` count | Example import |
|---------------------|-------------|----------------|
| `src/app/api/x/route.ts` | 3 | `'../../../lib/stripe'` |
| `src/app/api/x/y/route.ts` | 4 | `'../../../../lib/stripe'` |
| `src/app/api/webhooks/stripe/route.ts` | 4 | `'../../../../lib/stripe'` |

## Wrong Import → Build Error

```
Module not found: Can't resolve '../../../lib/stripe'
```

This compiles without TypeScript errors (string paths are untyped) but fails at Turbopack build time.

## Verification

After creating any nested route, confirm imports resolve:
```bash
npm run build
```
Expected: `✓ Compiled successfully`
Error: `Module not found` → count path depth, add or remove one `../`

## Also Note

Webhook routes must use `export const dynamic = 'force-dynamic'` to prevent static optimization, which would break raw body parsing.
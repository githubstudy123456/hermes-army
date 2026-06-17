---
name: nextjs-supabase-stripe-backend
description: "Next.js App Router backend patterns: Supabase SSR, Stripe Checkout + webhooks, curriculum API design"
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [nextjs, supabase, stripe, backend, api-design, webhooks, app-router]
    related_skills: [frontend-dev-patterns, systematic-debugging]
---

# Next.js + Supabase + Stripe Backend Patterns

## Overview

Next.js App Router backend API design for multi-tenant SaaS platforms using Supabase (Postgres + Auth + RLS) and Stripe (checkout + webhooks).

## Supabase SSR in Route Handlers

### Admin Client (Service Role Key)

For operations that bypass RLS (reading all data, writing user records):

```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL ?? ''
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY ?? ''

const supabase = createClient(supabaseUrl, supabaseKey)
```

**Security:** Never expose `SUPABASE_SERVICE_ROLE_KEY` to the browser — route handlers only.

### Public Client (Anon Key)

For public-read operations, use `createBrowserSupabaseClient()` from `src/lib/supabase.ts`.

## Stripe Checkout

### Checkout Session Creation

```typescript
const session = await stripe.checkout.sessions.create({
  mode: 'payment',
  line_items: [{ price: process.env.STRIPE_PRICE_ID_PRO, quantity: 1 }],
  success_url: `${process.env.NEXT_PUBLIC_APP_URL}/?checkout=success`,
  cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/?checkout=cancel`,
  metadata: { user_id: userId, tier: 'pro' },
})
```

**Key:** Always pass `metadata.user_id` — needed by webhook to link payment to user.

## Stripe Webhook Handler

### Structure

```typescript
export const dynamic = 'force-dynamic'  // REQUIRED — raw body needed

export async function POST(request: Request) {
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET
  const body = await request.text()  // NOT json()
  const signature = request.headers.get('stripe-signature') ?? ''

  let event = stripe.webhooks.constructEvent(body, signature, webhookSecret)

  switch (event.type) {
    case 'checkout.session.completed':
      // Link session to user, create order record
      break
    case 'payment_intent.succeeded':
      // Mark order completed
      break
    case 'customer.subscription.deleted':
      // Mark subscription canceled
      break
  }

  return NextResponse.json({ received: true })
}
```

### Required Env Vars

```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Key Rules

- Must use `export const dynamic = 'force-dynamic'` or Next.js will cache the route as static, breaking raw body parsing
- Use `request.text()` not `request.json()` — Stripe sends raw body for signature verification
- Always return `200` within 30s or Stripe retries the webhook
- Log event type for debugging: `console.log('Stripe event:', event.type)`

## Curriculum API Design

### GET /api/curriculum

Query curriculum tree: books → chapters → lesson_sections → knowledge_points.

```typescript
const { data } = await supabase
  .from('books')
  .select(`
    id, title, stage, grade, volume, source,
    chapters (
      id, chapter_no, title, domain, sort_order,
      lesson_sections (
        id, title, knowledge, sort_order,
        lesson_models ( model_id, sort_order )
      )
    )
  `)
  .order('stage', { ascending: true })
```

### GET /api/narration/:id

Fetch single knowledge point with narration scripts and related models.

## Schema Extensions for SaaS

When extending a curriculum/supabase schema for subscriptions and orders:

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `subscriptions` | User subscription status | user_id, stripe_customer_id, status, tier, period_end |
| `checkout_orders` | Payment records | user_id, stripe_session_id, amount, status |
| `narration_scripts` | Per-step narration scripts | knowledge_point_id, step, title, narration, highlight, formula |

## Trigger Conditions

Load this skill when:
- Designing new API routes for a Next.js App Router project
- Implementing Stripe checkout or webhook handling
- Querying Supabase with complex nested relations
- Building curriculum / content management backends
# Stack & Dependencies

## Frontend (web/)
- Next.js 15 (App Router, React Server Components)
- TypeScript 5.x (strict mode)
- Tailwind CSS 3.x + shadcn/ui (Radix primitives)
- Recharts (charts), Mapbox GL (activity maps)
- @supabase/ssr (auth + data)
- React Hook Form + Zod (forms)
- Vitest + Testing Library (tests)
- ESLint + Prettier

## Backend (api/)
- Python 3.12+
- FastAPI + Uvicorn
- SQLAlchemy 2.x (async) + Alembic
- Supabase (PostgreSQL, Auth, RLS)
- python-jose (JWT validation)
- anthropic (Claude SDK)
- python-garminconnect (unofficial, behind GarminProvider)
- ARQ + Redis (background jobs)
- Resend (transactional email)
- Paddle SDK (payments)
- pytest + pytest-asyncio + httpx (tests)
- Ruff (lint)

## Infrastructure
- Vercel (frontend hosting)
- Railway or Fly.io (backend, EU region)
- Supabase (database + auth, eu-central-1)
- Redis (Upstash or Railway Redis)

## Design Tokens (vibe-hybrid: A × D)
- Display: Inter Tight (600, 700)
- Body: Inter (400, 500, 600)
- Data: JetBrains Mono (tabular-nums)
- Palette: warm stone #E9E4D8, paper #F3EFE5, ink #38382C, slate #7C7765, accent #D9703A, olive #6E7644, rust #C4612F
- Spacing: base-4 grid, hairline borders 1px
- Radius: 3px max (sharp corners)

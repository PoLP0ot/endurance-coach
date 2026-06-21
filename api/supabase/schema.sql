-- Endurance Coach — Supabase schema
-- Run in the Supabase SQL editor (or via migrations). RLS enabled so each
-- athlete sees only their own data. auth.users is managed by Supabase Auth.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- users — 1:1 profile extension of auth.users
-- ---------------------------------------------------------------------------
create table if not exists public.users (
    id uuid primary key references auth.users (id) on delete cascade,
    email text unique,
    display_name text,
    primary_goal text check (
        primary_goal in ('marathon', 'weight_loss', 'hyrox', 'triathlon', 'health')
    ),
    onboarding_complete boolean not null default false,
    subscription_status text not null default 'free',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- garmin_connections — encrypted credentials/tokens at rest
-- ---------------------------------------------------------------------------
create table if not exists public.garmin_connections (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null unique references public.users (id) on delete cascade,
    encrypted_tokens text not null,
    garmin_username text,
    status text not null default 'connected',
    last_sync_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- activities — imported from Garmin
-- ---------------------------------------------------------------------------
create table if not exists public.activities (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references public.users (id) on delete cascade,
    garmin_activity_id text not null,
    activity_type text not null,
    name text,
    start_time timestamptz not null,
    duration_s integer,
    distance_m double precision,
    avg_hr integer,
    max_hr integer,
    elevation_gain_m double precision,
    avg_power_w double precision,
    tss double precision,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (user_id, garmin_activity_id)
);
create index if not exists ix_activities_user on public.activities (user_id);
create index if not exists ix_activities_start on public.activities (start_time);

-- ---------------------------------------------------------------------------
-- activity_metrics — streams / laps / zones (JSONB payloads)
-- ---------------------------------------------------------------------------
create table if not exists public.activity_metrics (
    id uuid primary key default gen_random_uuid(),
    activity_id uuid not null references public.activities (id) on delete cascade,
    kind text not null check (kind in ('stream', 'laps', 'zones')),
    data jsonb not null,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists ix_activity_metrics_activity on public.activity_metrics (activity_id);

-- ---------------------------------------------------------------------------
-- ai_analyses — cached coach narrative per activity
-- ---------------------------------------------------------------------------
create table if not exists public.ai_analyses (
    id uuid primary key default gen_random_uuid(),
    activity_id uuid not null references public.activities (id) on delete cascade,
    model text not null,
    facts jsonb not null,
    narrative text not null,
    prompt_version text not null default 'v1',
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);
create index if not exists ix_ai_analyses_activity on public.ai_analyses (activity_id);

-- ---------------------------------------------------------------------------
-- Row Level Security — owner-only access
-- ---------------------------------------------------------------------------
alter table public.users enable row level security;
alter table public.garmin_connections enable row level security;
alter table public.activities enable row level security;
alter table public.activity_metrics enable row level security;
alter table public.ai_analyses enable row level security;

create policy "own profile" on public.users
    for all using (auth.uid() = id) with check (auth.uid() = id);

create policy "own garmin" on public.garmin_connections
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "own activities" on public.activities
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "own metrics" on public.activity_metrics
    for all using (
        exists (
            select 1 from public.activities a
            where a.id = activity_metrics.activity_id and a.user_id = auth.uid()
        )
    );

create policy "own analyses" on public.ai_analyses
    for all using (
        exists (
            select 1 from public.activities a
            where a.id = ai_analyses.activity_id and a.user_id = auth.uid()
        )
    );

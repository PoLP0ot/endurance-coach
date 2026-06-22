# Build Plan — Endurance Coach → « pleinement fonctionnel + design identique au prototype »

> Contrat d'exécution piloté par une loop. Source de vérité visuelle : `docs/design/prototype.html`.
> Source de vérité fonctionnelle : `docs/qa-checklist.md` (IDs AC) + `docs/tech-plan.md`.
> Suivi : `docs/acceptance-tracker.md` (généré en setup de loop, coché au fil de l'eau).
>
> Décisions cadrantes (2026-06-22) :
> - **Provisioning** : l'utilisateur fournit les vraies clés (Supabase, Anthropic, Garmin, Paddle, Resend, Mapbox).
> - **Scope design** : tout le prototype (reskin complet light/pierre/orange + tous les écrans manquants).
> - **Validation loop** : auto (pytest + vitest + build + lint) + visuel piloté (navigateur Chrome/Playwright, comparaison aux captures du prototype), AC cochés un par un.

## Écart fondamental constaté

| Axe | Actuel | Cible (prototype) |
|---|---|---|
| Thème | **Dark** (forcé `className="dark"`) | **Light** uniquement |
| Fond | `#0b1220` bleu-nuit | `--bg #E9E4D8` pierre chaude / `--paper #F3EFE5` |
| Accent | bleu `#3b82f6` + lime `#10b981` | orange brûlé `--accent #D9703A` |
| Radius | 12px (`0.75rem`) | **3px** (tranchant) ; pills 100px |
| Polices | Inter Tight / Inter / JetBrains Mono (déjà bonnes) | idem — **on garde** |
| Écrans | 10 écrans, style shadcn par défaut | + Signals/Explore, onboarding conversationnel, pricing, goal-banner, insights `[▸]`, sparklines, table « This Week », push-to-watch, bottom-sheet « More », dashboards par objectif |

→ « exactement comme le design » = **reskin complet**, pas un ajustement.

---

## PHASE 0 — Fondations & déblocage

Objectif : repo sain + app qui boote de bout en bout avec les vraies clés.

- **0.1 Housekeeping audit** : retirer `api/dev.db` du suivi git + l'ajouter au `.gitignore` ; ajouter `ruff` aux dépendances dev (`api/pyproject.toml`) ; restaurer le workflow CI `.github/workflows/ci.yml` (pytest + ruff + vitest + lint + build).
- **0.2 Parité locale** : `docker-compose.yml` (Postgres + Redis) pour ARQ et dev local — Redis est requis pour les jobs (import Garmin, emails, analyse).
- **0.3 Credentials (utilisateur)** : remplir `api/.env` et `web/.env.local` (gitignorés — **ne jamais coller de clé dans le chat**). Variables exactes : voir §Credentials ci-dessous.
- **0.4 DB réelle** : `alembic upgrade head` sur le Postgres Supabase ; appliquer `api/supabase/schema.sql` (RLS) ; vérifier `GET /health`, `GET /me` avec un vrai JWT Supabase.
- **0.5 Smoke e2e** : `uvicorn` + `pnpm dev` ; login Supabase réel → dashboard se charge (vide, sans Garmin encore).
- **GATE 0** : app boote web↔api↔Supabase↔Redis ; `pytest` + `vitest` + `build` + `lint` + `ruff` verts ; CI verte.

## PHASE 1 — Design system (socle visuel)

Tout le reskin dépend de ça. **Aucun écran n'est traité avant GATE 1.**

- **1.1 Tokens** : réécrire `web/src/app/globals.css` avec la palette exacte du prototype (`--bg`, `--paper`, `--paper-2`, `--ink`, `--ink-soft`, `--slate`, `--line`, `--accent #D9703A`, `--accent-dk`, `--olive`, `--rust`…), radius 3px ; passer le thème en **light par défaut** (retirer `className="dark"` de `layout.tsx`).
- **1.2 Tailwind** : mapper les noms de couleurs aux nouveaux tokens dans `tailwind.config.ts` ; radius 3px ; pills 100px.
- **1.3 Primitives signature** (composants réutilisables, CSS exact du prototype) :
  `Button` (primary/ghost/sm/block), `Pill`/`Badge` (free/premium), `Field` (label mono uppercase), `CoachCard` (ai-dot + badge), `Metric` (grille 4-up, valeur 40px tabular), `GoalBanner` (gradient sombre + barre progression), `ChatBubble` (coach/user), `BottomNav` (62px) + `MoreSheet`, `Sidebar` (240px + séparateurs + athlete card), `InsightToggle` (`[▸]` rotation + panel expandable), `SignalChip` (chip + sparkline + detail expandable), `Sparkline` (SVG), `Toast`, `Dialog`/`Modal` (radix, déjà en deps), `WeekCard` (timeline).
- **1.4 Baselines visuelles** : rendre `prototype.html` dans le navigateur et capturer chaque écran/état → références de comparaison (`_bmad-output/playwright-audits/screenshots/prototype-baselines/`).
- **GATE 1** : page interne `/_design` rend toutes les primitives ; diff visuel OK vs prototype ; `build` + `lint` verts.

## PHASE 2 — Shell & navigation

- **2.1 App shell** : sidebar desktop 240px (liens, séparateurs, athlete card, état actif border-left orange) ; bottom nav mobile 62px 4 onglets **Progress / Coach / Plan / More** ; **More sheet** (Activities, Signals, Settings, Pricing & Upgrade, Log Out) ; topbar mobile (logo + plan badge + avatar menu).
- **2.2 Shell marketing** : `SiteHeader`/`SiteFooter` au nouveau thème.
- **AC couverts** : MN1.1–MN1.4, DL1.1–DL1.5.

## PHASE 3 — Reskin écrans existants (pixel-match)

Chaque écran = une unité de loop (implémente → valide auto+visuel → coche ses AC + universels U1–U6).

| Écran | Fichier | AC |
|---|---|---|
| Landing | `marketing/*` | L1–L7 |
| Signup / Login / Forgot | `auth/*` | S1–S3 |
| Onboarding Connect Garmin | `onboarding/connect-garmin` | O1–O4 |
| Dashboard | `dashboard/*` | D1–D7 (+ goal-banner, This Week, key signals, coach-card insights) |
| Activity Detail | `activities/activity-detail` | A1–A5 |
| Coach Chat | `chat/chat-view` | C1–C6 |
| Training Plan | `plan/*` | P1–P4 |
| Settings | `settings/settings-view` | ST1–ST6 |
| Privacy / Data | `settings/privacy-view` | (ST5) + DI |
| Subscription | `subscription/*` | (PR via settings) |

## PHASE 4 — Nouveaux écrans du prototype

- **4.1 Signals / Explore** (`/explore`) : « question cards » + interprétation coach. Endpoint dérivé de l'analytics (réutiliser dashboard facts ; ajouter `GET /signals` si besoin). AC : (Signals dans U/D).
- **4.2 Onboarding conversationnel** (`/coachonboard`, US1b/A15) : machine à états welcome→goal-kind→follow-ups→hand-off ; chips de suggestion ; coach référence les données importées ; persistance du goal côté API. AC : ON1.1–ON1.6.
- **4.3 Pricing** (`/pricing`, US-pricing) : Free/Premium, toggle mensuel/annuel, badge « Save 18% », CTA checkout Paddle. AC : PR1.1–PR2.6.
- **4.4 Dashboards par objectif** (A13/US13) : lentilles marathon / weight-loss / health (hyrox & triathlon → fallback health). AC : GV1.1–GV1.5.
- **4.5 Push to Watch** (A14/US5b) : `GarminProvider.push_workouts()` + bouton plan + modal + états. AC : PW1.1–PW1.5.
- **4.6 Weekly email** : reskin template au nouveau thème (email-safe). AC : E1.1–E3.4.

## PHASE 5 — Fonctionnel bout-en-bout (vraies intégrations)

- **Garmin réel** : import via `python-garminconnect` (creds runtime) → pipeline complet → dashboard affiche données réelles. AC : O2.6, D2–D6 (données vraies), DI1.
- **Anthropic réel** : chat / analyse / plan (Sonnet/Opus). AC : A4.*, C3.*, P1.*.
- **Paddle réel** : checkout + webhook signé → upgrade premium. AC : E2E.2, PR2.*.
- **Resend réel** : weekly email Lundi 07:00 (TZ user), premium-only, skip si 0 activité. AC : E2.*.
- **Mapbox réel** : carte GPS activité + marqueurs + fallback no-GPS. AC : A1.3–A1.5.
- **Sécurité** : auth gating routes app, RLS, pas de fuite token/password, HTTPS. AC : SEC1–SEC5.

## PHASE 6 — Durcissement & balayage d'acceptation

- Universels U1–U6 sur chaque écran (375/768/1440px, états, a11y clavier, API errors).
- Performance : Lighthouse desktop >80 / mobile >50, pas d'appel API >5s (PF1–PF3).
- Régression RG1–RG8 après chaque story.
- E2E happy paths E2E.1–E2E.3 ; intégrité données DI1–DI3.
- **GATE FINAL** : 100% des AC de `docs/acceptance-tracker.md` au vert.

---

## Mécanisme de LOOP

1. **Tracker** : `docs/acceptance-tracker.md` liste tous les IDs AC (L*, S*, O*, D*, A*, C*, P*, ST*, PR*, E*, ON1*, GV1*, PW1*, MN1*, DL1*, U*, RG*, E2E*, PF*, SEC*, DI*) avec statut `[ ]/[x]` + note.
2. **Harnais de validation** (chaque itération) :
   - `cd api && pytest -q && ruff check .`
   - `cd web && pnpm vitest run && pnpm lint && pnpm build`
   - Lancer `uvicorn` + `pnpm dev`, piloter le navigateur (Chrome CDP/Playwright), exécuter les scénarios de l'écran courant, capturer + comparer aux baselines prototype.
3. **Itération** : prendre le prochain lot d'AC non cochés (par écran, ordre des phases) → implémenter (TDD : RED→GREEN→REFACTOR) → harnais → cocher pass/fail → commit conventionnel → mémoire `.claude/memory/active-context.md` si impactant → suivant.
4. **Règle QA Hermes** : aucun passage à l'écran N+1 avec bug ouvert ; RG1–RG8 à chaque tour.
5. **Sortie** : tous les AC verts → GATE FINAL.

---

## Credentials requis (à mettre dans les fichiers .env gitignorés)

`api/.env` :
```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=
DATABASE_URL=               # chaîne Postgres Supabase (EU)
REDIS_URL=                  # Upstash/Fly/local docker
ANTHROPIC_API_KEY=
RESEND_API_KEY=
PADDLE_API_KEY=
PADDLE_WEBHOOK_SECRET=
MAPBOX_API_KEY=
ENCRYPTION_KEY=             # Fernet — généré (python -c "from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())")
FRONTEND_URL=http://localhost:3000
```
`web/.env.local` :
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAPBOX_TOKEN=   # si carte côté client
```
Garmin : pas de clé API — identifiants utilisateur saisis au runtime (chiffrés Fernet). Paddle : price IDs sandbox à configurer.

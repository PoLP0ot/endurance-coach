# AUDIT BUSINESS — Endurance Coach (2026-07-06)

Basé sur l'inventaire réel du code : 27 endpoints FastAPI (12 routers), 12 modèles
SQLAlchemy (migrations 0001–0010), 6 jobs ARQ (4 crons), 18 écrans Next.js,
intégrations Garmin (python-garminconnect derrière `GarminProvider`), Paddle
(webhook signé), Resend (lazy), OpenAI (`llm.py` — note : le code utilise
gpt-4o/gpt-4o-mini, pas Anthropic, contrairement à CLAUDE.md).

## 1. Parcours utilisateur bout-en-bout

signup → onboarding (connexion Garmin + poll import) → coachonboard (objectif
conversationnel) → dashboard (GoalHero, Today, assessment, métriques, signaux,
chart) → chat / plan / activités → settings (profil, Garmin, abonnement, RGPD).

**Ce qui marche** : le happy path complet est câblé, testé (~166 pytest,
62 vitest), avec états loading/empty/error partout et gating premium (402 →
upsell) systématique.

**Où ça casse :**

| # | Lacune | Sévérité | Impact business | Effort |
|---|--------|----------|-----------------|--------|
| P1 | **Compte Garmin avec MFA = activation impossible.** `GarminMFARequired` → 409, mais aucun flux de saisie du code (ni endpoint resume, ni UI). Une grosse fraction des comptes Garmin a la 2FA activée. | **Bloquant** | Perte sèche d'utilisateurs à l'activation, churn jour 0 | M |
| P2 | Le frontend écrase toutes les erreurs de connexion Garmin (401 mauvais mot de passe / 423 compte verrouillé / 409 MFA) en un seul message générique. | Important | L'utilisateur ne sait pas quoi corriger → abandon | S |
| P3 | Token Garmin expiré/révoqué après onboarding : `garmin/status` peut le savoir, mais aucun bandeau « reconnecter Garmin » dans l'app. | Important | Le produit se vide silencieusement de sa donnée | S-M |

## 2. Acquisition & activation

Landing complète (hero, comparatif, pricing, FAQ, témoignage fondateur) ;
onboarding en 2 temps avec « I'll do this later » ; time-to-value correct
(import ~30 s annoncé, poll avec labels de progression).

| # | Lacune | Sévérité | Impact | Effort |
|---|--------|----------|--------|--------|
| A1 | **Liens footer `/privacy`, `/terms`, `/contact` morts** (routes inexistantes). Paddle exige des CGV/politique de confidentialité publiques pour approuver un compte marchand ; c'est aussi une obligation RGPD (l'app traite des données de santé !). | **Bloquant vente** | Pas de compte Paddle approuvé = pas de revenus ; risque légal | S |
| A2 | Confirmation d'email Supabase désactivée (item user-blocked 1.5). | Important | Spam/abus, délivrabilité email | Config (user) |
| A3 | Pas d'essai gratuit : free tier permanent (30 j d'historique) vs premium. Le trial Paddle (statuts `trialing` déjà gérés côté code) n'est pas configuré ni annoncé. | Nice-to-have | Conversion probablement sous-optimale ; à A/B tester | Config + copy S |

## 3. Monétisation

Checkout Paddle (config client + custom_data.user_id), webhook signé HMAC
constant-time, upsert Subscription + statut user, gating serveur `require_premium`.

| # | Lacune | Sévérité | Impact | Effort |
|---|--------|----------|--------|--------|
| M1 | **Aucune annulation d'abonnement** — pas d'endpoint, pas d'UI, alors que la page abonnement affiche « cancel anytime ». Le seul moyen d'annuler serait d'écrire au support. Illégal dans l'UE (résiliation aussi simple que la souscription) et motif de refus Paddle. | **Bloquant** | Confiance, conformité, chargebacks | M |
| M2 | **Dunning brutal** : `past_due` → `free` immédiat. Une carte qui échoue = un client payant qui perd l'accès pendant que Paddle retente le prélèvement. On perd des clients récupérables. | **Bloquant** | Churn involontaire (typiquement 20-40 % des churns SaaS) | S |
| M3 | `subscription.scheduled_change` (annulation programmée) non stocké → impossible d'afficher « actif jusqu'au X, ne se renouvellera pas ». | Important | UX d'annulation opaque | S (avec M1) |
| M4 | Factures/reçus : rien dans l'app (Paddle envoie ses reçus par email — acceptable en MoR ; le mentionner dans l'UI). | Nice-to-have | Support tickets | S |
| M5 | Upgrade/downgrade : un seul prix ($8/mo) + toggle annuel sur la landing **non câblé** au checkout (un seul `paddle_price_id` en config). | Important | Revenus annuels perdus | M (2e price id) |

## 4. Core value loop

Import Garmin idempotent (activités + santé + streams downsamplés), AnalyticsEngine
déterministe (TSS/CTL/ATL/TSB, invariant « l'IA ne calcule jamais » respecté via
coach_facts/coach_tools), chat agentique avec outils, plan périodisé + microcycle
jour par jour, adaptation hebdo (cron dim. 18:00) depuis CTL réel + adhérence,
push-to-watch.

| # | Lacune | Sévérité | Impact | Effort |
|---|--------|----------|--------|--------|
| C1 | **Le brief quotidien (B4) n'est affiché nulle part.** Généré chaque matin à 05:30 pour tous les premium (LLM + facts), endpoint `GET /coach/brief` prêt — zéro appel côté web. La boucle de rétention centrale est construite mais pas branchée. | **Bloquant valeur** | La feature retention la plus chère (LLM quotidien) est invisible | S |
| C2 | Adaptation de plan : aucune notification à l'utilisateur quand son plan a été adapté (le cron modifie silencieusement les semaines à venir). | Important | Confiance dans le coach (« pourquoi ça a changé ? ») | M |
| C3 | Multi-sport : TSS course ok ; vélo/natation passent par le même modèle HR — acceptable MVP, à documenter. | Nice-to-have | Précision analytics triathlètes | L |

## 5. Rétention & engagement

Brief quotidien (voir C1), email hebdo (cron lun. 07:00, opt-in, préview),
Today card, adhérence hebdo, bandes on-track.

| # | Lacune | Sévérité | Impact | Effort |
|---|--------|----------|--------|--------|
| R1 | Envoi réel des emails bloqué par l'infra (pas de clé Resend, pas de Redis prod) — item user-blocked connu. | Important | Rétention | Config (user) |
| R2 | Pas de push/notifications (PWA ou email quotidien du brief). Le brief n'existe que si l'utilisateur ouvre l'app. | Important | DAU | M-L |
| R3 | Streaks/gamification : interdits par la direction design (assumé, pas une lacune). | — | — | — |

## 6. Trust & compliance

JWT Supabase vérifié (JWKS), tokens Garmin chiffrés Fernet au repos, RGPD complet
(export JSON+CSV, purge cascade + audit log FK-free), consentement affiché au
connect, erreurs LLM typées → 502/503 propres, envelope d'erreur uniforme.

| # | Lacune | Sévérité | Impact | Effort |
|---|--------|----------|--------|--------|
| T1 | **Aucun rate limiting.** `/chat` (coût LLM par requête !), `/garmin/connect` (credential stuffing vers Garmin), `/plans` (LLM). Un seul utilisateur hostile = facture OpenAI ouverte. | **Bloquant prod** | Coût direct + risque de blocage IP par Garmin | S-M |
| T2 | Pages légales absentes (voir A1) alors que l'app traite des données de santé (HRV, sommeil, poids) — la politique de confidentialité est une obligation, pas un nice-to-have. | **Bloquant** | Légal | S |
| T3 | Garmin non-officiel : disclaimer absent des CGV/FAQ (risque de rupture du service si Garmin bloque). À dire honnêtement. | Important | Attentes clients, refunds | S (avec T2) |
| T4 | Sweep sécurité prod (headers, HTTPS only, secrets) — item user-blocked 1.6/1.7. | Important | — | M (user) |

## 7. Ops & production-readiness

Logging JSON structuré + X-Request-ID, healthcheck `/health`, Dockerfile +
compose (pg/redis/api/worker), CI GitHub Actions, fallback import inline sans
Redis, crons ARQ définis.

| # | Lacune | Sévérité | Impact | Effort |
|---|--------|----------|--------|--------|
| O1 | Pas d'error tracking (Sentry ou équivalent) — les exceptions prod partent dans les logs sans alerte. Nouvelle dépendance → à valider explicitement. | Important | MTTR | S (dep à valider) |
| O2 | Jobs ARQ : pas de retry/backoff configuré sur `import_garmin_activities` ; un échec = job `error`, l'utilisateur doit relancer à la main (l'UI le permet via Sync now). Acceptable MVP. | Nice-to-have | Support | S |
| O3 | i18n : app 100 % anglais, aucune infra i18n. Choix assumé pour le lancement (marché EN) ; la règle react (useIntl) n'est pas appliquée dans ce repo. | Nice-to-have | Marchés FR/DE plus tard | L |
| O4 | Infra prod (Postgres géré, Redis géré, domaine, deploy) — items user-blocked 0.2/1.1/4.3/4.4. | Bloquant mise en ligne | — | Config (user) |

## Décisions produit à fort impact (2 options, reco incluse)

**D1 — Dunning (M2).**
- Option A : `past_due` conserve l'accès premium pendant la fenêtre de retry
  Paddle, avec bandeau « paiement échoué, mettez à jour votre moyen de paiement »
  (lien Paddle). Downgrade seulement sur `canceled`.
- Option B : statu quo (downgrade immédiat), plus simple, plus sûr côté revenus.
- **Reco : A.** Le churn involontaire est du revenu perdu récupérable ; Paddle
  retente automatiquement. J'implémente A.

**D2 — Stockage de l'état MFA (P1).**
- Option A : store en mémoire process avec TTL (l'état garth n'est pas
  sérialisable proprement). Contrainte : API mono-instance — vrai aujourd'hui
  (1 uvicorn Railway/Fly). Documenté.
- Option B : sérialisation pickle chiffrée en DB — multi-instance safe mais
  pickle d'objets tiers = fragile et risqué.
- **Reco : A**, avec TTL 5 min et suppression après usage. J'implémente A.

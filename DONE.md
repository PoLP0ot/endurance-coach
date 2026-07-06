# DONE — Audit business & productisation (2026-07-06)

## Mise à jour (même jour) — « fix tout ce qui est fixable »

S6–S8 et S10 livrées à leur tour (5 commits de plus, mêmes QA gates —
107 pytest, 79 vitest, ruff/eslint/build verts) :

- **S6** : un échec d'import qui « sent » l'auth (401/403) marque la connexion
  `auth_expired` (les échecs transitoires non) ; le dashboard affiche un bandeau
  « Reconnect Garmin » vers l'onboarding.
- **S7** : facturation annuelle réellement câblée — `paddle_price_id_annual`,
  checkout accepte `{interval}` (503 typé si non configuré), sélecteur
  Monthly/Annual · save 18 % sur la page abonnement.
- **S8** : l'adaptation du dimanche écrit `last_adaptation {at, adherence_pct,
  changes[week, from→to]}` dans la structure du plan (pas de migration) ; la
  page plan affiche l'encart pendant 7 jours — quelles semaines ont bougé et de
  combien. Faits déterministes uniquement.
- **S10** : les échecs transitoires d'import sont retentés (backoff linéaire,
  3 essais, le job repasse « queued » avec label visible par le poll) ; les
  échecs d'auth ne retentent jamais (S6 prend le relais).
- **Docs/deps** : CLAUDE.md + memory disent enfin la vérité (LLM = OpenAI) ;
  `anthropic` et `paddle-billing-client` retirés de requirements (importés
  nulle part).

**S9 (Sentry) livrée après validation explicite de la dépendance** :
`sentry-sdk[fastapi]` (API + worker ARQ via `core/monitoring.init_sentry`) et
`@sentry/nextjs` (instrumentation Next 15). Inerte sans `SENTRY_DSN` /
`NEXT_PUBLIC_SENTRY_DSN` ; PII et corps de requêtes jamais envoyés, pas de
session replay (données de santé). Il reste à créer le projet Sentry et
fournir les deux DSN. Le backlog code est donc **entièrement livré (S1–S10)**.
Supabase vérifié câblé localement (URL/JWT/clés publiques présents) — seul le
toggle « email confirmation » du dashboard reste à activer.


## Livré (6 commits, chaque story passée au QA gate complet)

| Story | Commit | Ce que ça débloque |
|-------|--------|--------------------|
| Audit + backlog | `docs: business audit + prioritized productization backlog` | `AUDIT.md` (7 axes, sévérités, décisions D1/D2) + `BACKLOG.md` priorisé |
| S1 Pages légales | `feat(legal)` | `/terms`, `/privacy`, `/contact` réels (données santé, sous-traitants, disclaimer Garmin, résiliation). Prérequis d'approbation Paddle + obligation RGPD. |
| S2 MFA Garmin | `feat(garmin)` | Les comptes Garmin avec 2FA peuvent s'activer : login via `garth.sso(return_on_mfa)`, `POST /garmin/mfa`, store TTL 5 min, UI de saisie du code, erreurs 401/423/409 distinguées. |
| S3 Cancel + dunning | `feat(billing)` | `POST /subscription/cancel` (API Paddle, cancel at period end), `cancel_at_period_end` (migration 0011, webhook `scheduled_change`), `past_due` garde le premium pendant les retries (D1-A), UI cancel + bandeau paiement échoué. « Cancel anytime » est maintenant vrai. |
| S4 Brief quotidien | `feat(dashboard)` | Le brief LLM généré chaque matin est affiché (BriefCard, fallback assessment hebdo pour free/erreur). La boucle de rétention est branchée. |
| S5 Rate limiting | `feat(security)` | Fenêtre glissante par user : chat 20/min, login Garmin 5/5 min, plans 5/h. 429 + Retry-After. Coût LLM et réputation IP Garmin protégés. |

**État des gates au moment de la clôture** : 104 pytest verts, 73 vitest verts,
`ruff check` clean, `next lint` clean, `next build` OK, migration 0011 appliquée
sur dev.db, captures Playwright vérifiées (brief visible, cancel visible).

## Parcours vendable — état

S'inscrire ✅ → connecter Garmin (y compris MFA) ✅ → plan + coaching quotidien
(brief, today, chat, adaptation) ✅ → payer ✅ → **annuler** ✅ → exporter/
supprimer ses données ✅ → pages légales publiques ✅.

## Ce qui reste (backlog, non bloquant pour un lancement early-access)

- **S6** Bandeau « reconnecter Garmin » quand le token expire.
- **S7** Prix annuel réellement câblé (la landing l'affiche déjà).
- **S8** Notification d'adaptation de plan (le cron modifie en silence).
- **S9** Error tracking Sentry — nouvelle dépendance, à valider.
- **S10** Retries ARQ sur l'import.

## User-blocked avant mise en vente (hors code) — état 2026-07-07

1. **Paddle** (seul vrai bloquant restant) : compte + api key + client token +
   webhook secret + price ids mensuel/annuel + URL publique du webhook.
2. ~~Sentry~~ **FAIT** : DSN fourni, branché api (`SENTRY_DSN`) + web
   (`NEXT_PUBLIC_SENTRY_DSN`), événement de test livré (`c062f36b…`).
3. **Resend — clé FAITE, domaine restant** : clé « sending only » validée par
   envoi réel (`b313a454…` via l'expéditeur sandbox onboarding@resend.dev).
   Reste à vérifier le domaine `endurancecoach.app` sur resend.com/domains
   (DNS DKIM/SPF) — sans ça, `EMAIL_FROM=coach@endurancecoach.app` est refusé.
4. ~~Supabase~~ **FAIT** : câblage vérifié + toggle « Confirm email » activé
   (confirmé par le fondateur 2026-07-07).
5. Infra : Postgres + Redis managés, deploy API (Railway/Fly, EU) + web
   (Vercel), domaine, secrets prod, HTTPS/headers.
6. Renseigner l'entité juridique réelle dans /terms et /privacy (aujourd'hui
   « Endurance Coach » + support@endurancecoach.app).

## Risques restants avant vente

- **Garmin non-officiel** : risque structurel assumé et maintenant disclosé
  dans les CGV. Un blocage Garmin dégrade le produit cœur ; le provider est
  isolé pour basculer sur l'API officielle si accès obtenu.
- **Mono-instance** : store MFA et rate limiting sont en mémoire process.
  Documenté ; à migrer vers Redis quand l'API sera scalée horizontalement.
- **LLM = OpenAI** (gpt-4o/-mini) alors que CLAUDE.md dit Anthropic — écart
  documenté en memory ; décision à trancher (coût/qualité) avant le lancement.
- **Emails jamais envoyés en réel** (pas de clé) : le rendu est testé, pas la
  délivrabilité multi-clients.
- **Pas d'alerting prod** tant que S9 n'est pas validée.

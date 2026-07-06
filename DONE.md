# DONE — Audit business & productisation (2026-07-06)

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

## User-blocked avant mise en vente (hors code)

1. Compte Paddle live : price id(s), webhook secret, URL publique du webhook,
   et vérification marchand (les pages /terms et /privacy sont maintenant là
   pour ça).
2. Resend : clé + domaine vérifié (DKIM/SPF) pour brief/hebdo/transactionnel.
3. Supabase : activer la confirmation d'email.
4. Infra : Postgres + Redis managés, deploy API (Railway/Fly, EU) + web
   (Vercel), domaine, secrets prod, HTTPS/headers.
5. Renseigner l'entité juridique réelle dans /terms et /privacy (aujourd'hui
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

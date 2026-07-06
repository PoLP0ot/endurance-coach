# BACKLOG PRIORISÉ — vers un produit vendable

Ordonné par impact business / effort. Les bloquants du parcours payant d'abord.
Une story = un commit. QA gate obligatoire entre chaque.

## S1 — Pages légales + liens footer réels `[x]`
**Problème** : liens footer `/privacy`, `/terms`, `/contact` morts ; Paddle exige
des CGV et une politique de confidentialité publiques ; l'app traite des données
de santé (obligation RGPD).
**Critères d'acceptation** :
- `/terms`, `/privacy`, `/contact` rendent des pages réelles (contenu honnête :
  données santé, sous-traitants Supabase/OpenAI/Paddle/Resend, disclaimer
  intégration Garmin non-officielle, résiliation à tout moment, remboursements
  via Paddle, contact).
- Le footer marketing pointe vers ces routes ; test vitest vérifie le rendu.
**Fichiers** : `web/src/app/(legal)/terms|privacy|contact/page.tsx`,
`site-footer.tsx`, tests.
**Dépendances** : aucune.

## S2 — Flux MFA Garmin complet `[x]`
**Problème** : un compte Garmin avec 2FA ne peut pas s'activer (409 sans suite) ;
toutes les erreurs de connexion sont écrasées en un message générique.
**Critères d'acceptation** :
- `POST /garmin/connect` sur compte MFA → 409 `garmin_mfa_required` ET l'état de
  reprise est conservé (TTL 5 min, mono-instance documenté).
- `POST /garmin/mfa {code}` → reprend le login, chiffre le token, upsert la
  connexion, enqueue l'import (mêmes garanties que /connect). Code invalide →
  401 typé ; état expiré → 410.
- UI onboarding : 409 → champ « code de vérification » ; 401 → « identifiants
  incorrects » ; 423 → « compte temporairement verrouillé, réessayez plus tard ».
- pytest (provider stub MFA) + vitest (3 branches d'erreur + happy path MFA).
**Fichiers** : `api/app/services/garmin.py`, `api/app/routers/garmin.py`,
`web/src/components/onboarding/connect-garmin.tsx`, `web/src/lib/api.ts` (code
d'erreur), tests des deux côtés.
**Dépendances** : aucune.

## S3 — Annulation d'abonnement + grace period dunning `[x]`
**Problème** : « cancel anytime » affiché mais aucune annulation possible ;
`past_due` downgrade immédiatement un client payant pendant les retries Paddle.
**Critères d'acceptation** :
- `POST /subscription/cancel` → appel API Paddle (cancel at period end),
  répond avec l'état ; 409 si pas d'abonnement actif ; 503 si Paddle non configuré.
- Webhook : `scheduled_change.action == "cancel"` → `cancel_at_period_end`
  stocké (migration 0011) ; `past_due` conserve le premium (décision D1-A),
  `canceled`/`paused` → free.
- `GET /subscription/status` expose `cancel_at_period_end` et le statut brut.
- UI abonnement premium : période courante, bouton « Cancel subscription »
  (confirmation), état « ends on <date> » ; bandeau si `past_due`.
- pytest (webhook scheduled_change, past_due premium, cancel endpoint avec client
  Paddle stubé) + vitest (cancel flow, états).
**Fichiers** : `api/app/services/subscriptions.py`, `routers/subscriptions.py`,
`models/subscription.py`, migration 0011, `subscription-view.tsx`, tests.
**Dépendances** : aucune (paddle_api_key déjà en config ; httpx déjà présent).

## S4 — Brief quotidien visible sur le dashboard `[x]`
**Problème** : le brief coach (LLM, généré chaque matin à 05:30 pour les premium)
n'est affiché nulle part — la boucle de rétention est construite mais débranchée.
**Critères d'acceptation** :
- Dashboard premium : carte « Coach's brief — <date> » (headline + corps +
  prescription) à la place du Coach's Assessment quand le brief charge ;
  free/erreur/402 → fallback sur l'assessment actuel (aucune régression).
- vitest : brief affiché quand 200 ; fallback quand 402/erreur.
**Fichiers** : `web/src/components/dashboard/brief-card.tsx` (nouveau),
`dashboard-view.tsx`, `schemas/brief.ts`, tests.
**Dépendances** : aucune.

## S5 — Rate limiting endpoints sensibles `[x]`
**Problème** : `/chat` (coût LLM/req), `/garmin/connect` (stuffing → blocage IP
Garmin), `/plans` (LLM) sans aucune limite.
**Critères d'acceptation** :
- Limiteur fenêtre glissante en mémoire (aucune dépendance nouvelle), par
  user_id, configurable via settings ; 429 avec `Retry-After`.
- Limites par défaut : chat 20/min, garmin/connect + mfa 5/5 min, plans 5/h.
- Désactivable via settings pour les tests existants ; pytest dédié (429 après N).
**Fichiers** : `api/app/core/ratelimit.py` (nouveau), routers chat/garmin/plans,
`core/config.py`, tests.
**Dépendances** : aucune.

## S6 — Bandeau « reconnecter Garmin » `[x]`
**Problème** : token Garmin expiré/révoqué → l'app se vide silencieusement.
**Critères** : statut `error`/token invalide détecté à la sync → connexion
marquée, dashboard affiche un bandeau avec CTA vers /onboarding ; vitest+pytest.
**Dépendances** : S2 (erreurs typées réutilisées).

## S7 — Toggle annuel réellement câblé `[x]`
**Problème** : la landing affiche « Annual −18 % » mais un seul price_id existe.
**Critères** : `paddle_price_id_annual` en config ; checkout accepte
`{interval}` ; pricing page passe l'intervalle ; 503 si non configuré.
**Dépendances** : S3 (surface abonnement propre).

## S8 — Notification d'adaptation de plan `[x]`
**Problème** : le cron du dimanche modifie le plan sans prévenir l'athlète.
**Critères** : l'adaptation écrit un événement ; le dashboard/plan affiche
« Plan adapté dimanche : volume semaine 7 ajusté (−12 %) — pourquoi » ; le brief
du lundi le mentionne (fact déterministe, le LLM narre).
**Dépendances** : S4.

## S9 — Error tracking (Sentry) `[x]`
**Nouvelle dépendance — à valider explicitement avant.** sentry-sdk (api) +
@sentry/nextjs (web), DSN par env, sampling léger.

## S10 — Retries jobs ARQ import `[x]`
Backoff sur `import_garmin_activities` (max_tries=3), idempotence déjà en place.

---
### User-blocked (hors code, à faire par le fondateur avant vente)
- Compte Paddle live + price ids (+ annual) + webhook URL publique.
- Clé Resend + domaine d'envoi vérifié (DKIM/SPF).
- Supabase : activer la confirmation d'email.
- Postgres + Redis managés, déploiement api (Railway/Fly EU) + web (Vercel), domaine.
- Sweep sécurité prod (headers, secrets, HTTPS).

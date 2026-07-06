# DESIGN BACKLOG — priorisé (impact perçu / effort)

La direction (palette, typo, principes, décisions dark/i18n) vit dans
`.claude/memory/ux-direction.md` — source de vérité, mise à jour à chaque story.

## D1 — Couvrir et vérifier les états jamais vus `[ ]`
**Problème (B1)** : MFA, annulation/won't-renew/past_due, légal, adaptation,
reconnexion Garmin, chat vide — non couverts par le harness de capture.
**Critères visuels** :
- `e2e` capture ces états (fixtures dédiées ou routes) en desktop + mobile.
- Chaque capture relue ; toute casse corrigée dans la même story.
**Touche** : `web/e2e/*.spec.ts`, fixes éventuels dans les composants concernés.

## D2 — Accessibilité : cibles, focus, daltonisme `[ ]`
**Problème (B2, B3, I3)**.
**Critères visuels** :
- Cibles tactiles ≥ 44 px : bouton icône (`size="icon"`), radio d'intervalle.
- Focus visible net (anneau `ring`) sur Input, radio d'intervalle, chips — au
  clavier uniquement (`focus-visible`).
- Chart : ATL en pointillés, TSB en tirets longs — les 3 séries distinguables
  sans couleur ; légende reflète les styles de trait.
**Touche** : `ui/button.tsx`, `ui/input.tsx`, `subscription-view.tsx`,
`training-load-chart.tsx`.

## D3 — Le moment d'import Garmin `[ ]`
**Problème (I1)** : spinner nu au premier moment de vérité.
**Critères visuels** :
- Écran d'import = checklist verticale des étapes du pipeline (Fetching
  activities → Health → Analyzing → Building), état par étape (fait ✓ olive /
  en cours spinner / à venir muet), montage warm-stone.
- Piloté par les `progress_label` réels du backend — zéro donnée de démo.
- États gérés : erreur (message + CTA réessayer/settings), MFA inchangé.
**Touche** : `connect-garmin.tsx` (+ petit composant d'étapes), tests vitest.

## D4 — Standards d'interaction : documentés → réels `[ ]`
**Problème (I2)**.
**Critères visuels** :
- Fade-in de page 200 ms (template.tsx du groupe (app)), respecte
  `prefers-reduced-motion`.
- Hover/active boutons : transition douce déjà là — ajouter un « press »
  (active:translate-y-px) sobre ; hover cartes cliquables cohérent.
- Aucun mouvement décoratif gratuit (interdits ux-direction respectés).
**Touche** : `app/(app)/template.tsx` (nouveau), `globals.css`, `ui/button.tsx`.

## D5 — Poids et cohérences résiduels `[ ]`
**Problème (P1, P2, P3)**.
**Critères visuels** :
- « Your Body » : plus de vide en fin de grille (dernière tuile s'étend).
- Landing : le toggle annuel affiche le prix correspondant ($8/mo ↔ $79/yr,
  « 2 months free ») et le CTA reste honnête.
- « Sync now » passe en `outline`.
**Touche** : `body-card.tsx`, `marketing/pricing.tsx`, `settings/garmin-card.tsx`.

## D6 — Thème « night trail » `[ ]` (post-lancement, décision A)
Étude de palette sombre dédiée + toggle système. Ne pas inverser les tokens.

## D7 — i18n react-intl `[ ]` (post-lancement, décision A)
Infra + extraction des chaînes. Dérogation react.md documentée d'ici là.

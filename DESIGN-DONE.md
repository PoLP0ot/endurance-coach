# DESIGN DONE — productisation UX (2026-07-06)

Sixième et dernière passe de la journée. Base de départ : identité warm-stone
déjà forte (deux passes design + une passe produit livrées plus tôt — voir
git log). Cette passe a fermé les finitions qui séparent « propre » de
« vendable ». 6 commits, gates verts à chaque story : 82 vitest, eslint,
next build, captures Playwright relues en desktop + mobile.

## Avant / après des moments clés

| Moment | Avant | Après |
|--------|-------|-------|
| Import Garmin (1re minute du produit) | Spinner nu + ligne grise | Checklist vivante des 4 étapes réelles du pipeline (✓ olive / spinner / à venir), labels backend, aria-live ; l'attente raconte ce que le produit fait |
| États sensibles (MFA, annulation, dunning, adaptation, reconnexion, chat vide, légal) | Jamais screenshotés — QA aveugle | 11 états capturés desktop+mobile dans le harness (`state-*.png`), relus, zéro casse |
| Chart de charge | 3 séries distinguées par la couleur seule (olive/rouille convergent en deutéranopie) | CTL solide · ATL pointillé · TSB tirets longs — lisible sans couleur, légende cohérente |
| Navigation clavier / tactile | Focus input = bordure 1 px ; icônes 36 px ; radio facturation sans focus | Anneaux focus-visible partout, cibles 44 px (envoi chat), radio accessible |
| Sensation générale | 100 % statique | Fade de page 200 ms (documenté depuis le départ, jamais implémenté) + press 1 px sur les boutons ; tout s'annule sous `prefers-reduced-motion` |
| Your Body | Vide papier en fin de grille | La dernière tuile absorbe le reste (2 et 3 colonnes) |
| Poids des actions | « Sync now » habillé comme un CTA d'achat | Outline — la hiérarchie des poids suit la hiérarchie des intentions |

## Ce qui a été unifié / décidé

- **Direction consolidée dans `ux-direction.md`** (source de vérité) :
  light-only assumé (pas d'inversion de tokens — un vrai thème « night trail »
  est backlogué en D6), EN-only au lancement (dérogation react.md documentée,
  D7), standards de motion réellement implémentés, règle data-viz « jamais la
  couleur seule ».
- Aucun one-off introduit : tout passe par les tokens, cva, et les composants
  ui/ existants.

## Ce qui reste (backlogué, non bloquant)

- **D6 — thème night trail** : étude de palette sombre dédiée (cas d'usage réel :
  brief consulté à 5 h 30). Post-lancement.
- **D7 — i18n react-intl** : nouvelle dépendance + churn ~60 composants.
  Post-lancement.
- Sous-titre du shell d'onboarding (« This takes about 30 seconds ») légèrement
  décalé pendant l'étape MFA — cosmétique, non trompeur.

## Risques visuels restants avant vente

1. **Emails** : le rendu de l'email hebdo n'a jamais été vérifié dans de vrais
   clients (Gmail/Outlook/Apple Mail) — item user-blocked (clé Resend).
2. **Vrais volumes** : les captures utilisent des fixtures ; un athlète avec
   300 activités ou un plan de 24 semaines n'a pas été observé (la pagination
   et le truncate existent, mais l'œil n'est pas passé dessus).
3. **Devices réels** : tout est vérifié en viewports Playwright (1280/768/390),
   pas sur appareil physique (Lighthouse device = item user-blocked connu).

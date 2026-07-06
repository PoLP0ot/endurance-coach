# DESIGN AUDIT — Endurance Coach (2026-07-06)

Jugé comme un produit avant lancement. Base : 21 routes réelles (18 app/marketing
+ 3 légales), design system warm-stone documenté dans `ux-direction.md`, deux
passes design déjà livrées cette itération (dédup dashboard, GoalHero, plan
day-rows, destructive brick, signals inline…). Cet audit porte sur **ce qui
reste**.

## Verdict de direction artistique

**Ce n'est pas un template ShadCN.** L'identité « field laboratory » est réelle
et tenue : fond pierre #E9E4D8, hairlines taupe, un seul accent rouille, eyebrows
mono uppercase, chiffres tabulaires en héros, radius 3 px, zéro ombre. La
personnalité est différenciante (aucun SaaS fitness ne ressemble à ça — ils sont
tous en dark-mode néon) et alignée au public (athlètes sérieux, données).
La dette n'est pas identitaire, elle est dans **les finitions** : états récents
non vérifiés, standards d'interaction documentés mais jamais implémentés,
accessibilité fine.

## Problèmes, par sévérité

### Bloquants (avant vente)

| # | Problème | Impact perception | Effort |
|---|----------|-------------------|--------|
| B1 | **Six états récents jamais vérifiés visuellement** : étape MFA, flux d'annulation + « won't renew » + bandeau past_due, pages légales, encart d'adaptation de plan, bandeau reconnexion Garmin, chips du chat vide. Le harness de capture (source de vérité du QA visuel) ne les couvre pas — on vend potentiellement des écrans jamais regardés. | Risque de casse invisible sur les moments les plus sensibles (argent, sécurité) | S-M |
| B2 | **Cibles tactiles sous 44 px** : bouton icône 36 px (envoi chat), radio d'intervalle de facturation ~30 px de haut. Standard documenté : 44 px min. | Frustration mobile sur les 2 actions les plus répétées/critiques | S |
| B3 | **Focus clavier faible sur les inputs** (changement de bordure 1 px, pas d'anneau) et absent sur le radio Monthly/Annual. WCAG 2.4.7/2.4.11. | Accessibilité + impression de négligence au clavier | S |

### Importants

| # | Problème | Impact | Effort |
|---|----------|--------|--------|
| I1 | **Le moment d'import Garmin est un spinner nu.** C'est LE moment d'attente du produit (30–60 s, première impression, l'utilisateur vient de confier son mot de passe). Le backend streame déjà des étapes (« Fetching activities… → Building your dashboard… ») ; l'UI les affiche en une ligne grise. Time-to-wow raté. | Premier moment de vérité du produit | M |
| I2 | **Standards d'interaction documentés, jamais implémentés** : fade de page 200 ms, hover boutons, etc. (`ux-direction.md` § Interaction Standards). L'app est 100 % statique — propre mais sans vie. À faire sobrement + `prefers-reduced-motion`. | « Premium feel » — la différence se sent sans se voir | S-M |
| I3 | **Daltonisme sur le chart de charge** : olive (CTL) vs rouille (ATL) convergent en deutéranopie ; seule la couleur les distingue. Il faut une redondance de forme (styles de trait). | Public data-literate, graphe central | S |
| I4 | **Dark mode absent** — choix assumé (« Light only » dans globals.css) mais jamais posé comme décision de design. Cas d'usage réel : l'athlète consulte son brief à 5 h 30 dans le noir. Voir « Partis pris » ci-dessous. | Confort d'usage réel, attente SaaS | L |
| I5 | **i18n absent** alors que la règle react.md prescrit useIntl. Aucune infra installée ; l'ajouter = nouvelle dépendance + churn massif de chaque écran. | Marchés non-EN (plus tard) | L |

### Polish

| # | Problème | Impact | Effort |
|---|----------|--------|--------|
| P1 | « Your Body » : la dernière rangée laisse un vide papier quand 7 tuiles ne remplissent pas la grille 3 col. Propre depuis le fix hairline, mais un `col-span` sur la dernière tuile fermerait la composition. | Détail de rigueur | S |
| P2 | Landing : le toggle Monthly/Annual est purement décoratif (n'influence ni le CTA ni le prix affiché en gros). Depuis S7 l'intervalle existe réellement. | Cohérence promesse→produit | S |
| P3 | Le bouton « Sync now » (Settings) est en variante pleine primaire — même poids que les CTA d'achat. Une action utilitaire mérite `outline`. | Hiérarchie des poids | S |

## États & robustesse — état des lieux

Loading/empty/error/disabled : **systématiquement gérés** (LoadingState /
EmptyState / ErrorState réutilisés partout, gates premium → upsell, erreurs LLM
typées → message coach + retry). Longues chaînes : truncate en place sur les
listes ; GoalHero wrap. Reste à vérifier en captures les six états de B1 —
c'est l'objet de la story D1.

## Partis pris à trancher (2 directions, reco incluse)

**Dark mode (I4)**
- **Direction A — Light-only assumé (reco).** L'identité warm-stone EST la
  marque ; un dark thème demanderait sa propre étude de palette (les hairlines
  taupe et le rouille ne survivent pas à une simple inversion). On assume :
  « calme comme le papier d'un carnet de terrain ». Backlog : thème « night
  trail » étudié après lancement, avec de vrais tokens (pas un invert).
- **Direction B — Night trail maintenant.** Palette sombre dédiée (fond
  #201F1A, papier #2A2924, encre inversée chaude, mêmes accents), toggle
  système. Coût : retest complet de 21 routes × contrastes, retard de lancement.
- **Décision : A.** Documentée dans ux-direction.md ; B reste au backlog.

**i18n (I5)**
- **Direction A — EN-only au lancement (reco).** Marché initial anglophone,
  aucune infra installée, la règle « aucune nouvelle dépendance UI sans
  justification » prime. Textes centralisés au fil de l'eau (copy dans les
  composants, pas de dispersion).
- **Direction B — react-intl maintenant** : churn de ~60 composants avant vente.
- **Décision : A.** Notée comme dérogation explicite à react.md dans
  ux-direction.md.

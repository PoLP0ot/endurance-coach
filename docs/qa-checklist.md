# Endurance Coach — QA Checklist (Exhaustive)

> Cette checklist est exécutée APRÈS CHAQUE user story.
> Une story n'est PAS "done" tant que TOUS les checks ne sont pas passés.
> On ne passe PAS à la story suivante tant que la story courante n'est pas 100% validée.

---

## QA Process par Story

```
1. Tests backend (pytest)     → 100% pass
2. Tests frontend (vitest)    → 100% pass
3. Build production (build)   → zéro erreur
4. Lint (eslint)              → zéro warning
5. QA manuelle navigateur     → tous les checks ci-dessous
6. QA régression              → stories précédentes re-testées
7. Commit + push
```

Si UN SEUL check échoue → retour à Claude pour fix → on recommence le cycle.

---

## QA MANUELLE — Checks Universels (toute story, tout écran)

### U1. Rendu & Layout
- [ ] **U1.1** La page load sans erreur JS dans la console
- [ ] **U1.2** Aucune 404/500 dans l'onglet Network
- [ ] **U1.3** Aucun élément qui dépasse / overlap sur viewport 375px, 768px, 1440px
- [ ] **U1.4** Les polices sont chargées (pas de fallback system font visible)
- [ ] **U1.5** Les images ont des dimensions correctes (pas d'étirement/déformation)
- [ ] **U1.6** Les espacements sont cohérents (pas de marges qui collent au bord)
- [ ] **U1.7** Le scroll fonctionne (pas de contenu coupé non accessible)
- [ ] **U1.8** z-index correct (pas de modale derrière le contenu, pas de dropdown caché)

### U2. Responsive
- [ ] **U2.1** Mobile 375px : lisible, pas de scroll horizontal
- [ ] **U2.2** Tablet 768px : grilles correctes, pas de cassure
- [ ] **U2.3** Desktop 1440px : layout complet, pas de vide bizarre
- [ ] **U2.4** Les boutons sont cliquables au doigt (min 44x44px sur mobile)
- [ ] **U2.5** La navigation mobile fonctionne (burger menu si présent)

### U3. États (chaque état doit être visuellement vérifié)
- [ ] **U3.1** Loading state : skeleton loader ou spinner visible, pas de flash blanc
- [ ] **U3.2** Empty state : message + CTA affiché, pas de layout cassé
- [ ] **U3.3** Error state : message d'erreur visible, bouton retry fonctionnel
- [ ] **U3.4** Success state : données affichées correctement
- [ ] **U3.5** Edge case : données extrêmes (très long texte, chiffres énormes, dates futures/passées)

### U4. Performance
- [ ] **U4.1** First Contentful Paint < 2 secondes
- [ ] **U4.2** Largest Contentful Paint < 3 secondes
- [ ] **U4.3** Pas de layout shift pendant le chargement (CLS < 0.1)
- [ ] **U4.4** Les images sont lazy-loadées si sous la fold

### U5. Accessibilité (basique)
- [ ] **U5.1** Tab navigation : tous les éléments interactifs sont focusables dans l'ordre
- [ ] **U5.2** Enter/Espace activent les boutons
- [ ] **U5.3** Escape ferme les modales
- [ ] **U5.4** Les labels de formulaire sont liés aux inputs
- [ ] **U5.5** Les messages d'erreur sont annoncés (aria-describedby)

### U6. API
- [ ] **U6.1** Tous les appels API retournent 200 (ou le code attendu)
- [ ] **U6.2** Pas d'erreur CORS dans la console
- [ ] **U6.3** L'API gère le cas "token expiré" (401 → redirect login)
- [ ] **U6.4** L'API gère le cas "rate limited" (429 → message utilisateur)
- [ ] **U6.5** L'API gère le cas "backend down" (timeout → message utilisateur)

---

## QA PAR ÉCRAN — Checks Spécifiques

### ÉCRAN 1 : LANDING PAGE

#### L1. Hero
- [ ] **L1.1** Headline + subheadline lisibles sur tous les viewports
- [ ] **L1.2** CTA `Connect Your Garmin — It's Free` cliquable → `/signup`
- [ ] **L1.3** CTA secondaire `See how it works ↓` scroll vers How It Works
- [ ] **L1.4** L'image/illustration ne déborde pas, pas pixelisée

#### L2. How It Works
- [ ] **L2.1** 3 étapes affichées, icônes visibles
- [ ] **L2.2** 3 colonnes desktop → 1 colonne mobile (vérifier l'ordre)

#### L3. Features
- [ ] **L3.1** 3 colonnes avec contenu
- [ ] **L3.2** Bullet lists sous chaque feature

#### L4. Comparison Table
- [ ] **L4.1** Toutes les colonnes visibles (scroll horizontal OK sur mobile)
- [ ] **L4.2** Notre colonne visuellement différenciée
- [ ] **L4.3** Les ✅ et ❌ sont clairs

#### L5. Pricing
- [ ] **L5.1** Deux plans affichés (Free + Premium)
- [ ] **L5.2** Toggle Monthly/Annual fonctionnel
- [ ] **L5.3** Badge "Save 18%" sur Annual
- [ ] **L5.4** CTA `Start Free` → `/signup`
- [ ] **L5.5** CTA `Go Premium` → `/signup` (ou `/pricing` si connecté)

#### L6. FAQ
- [ ] **L6.1** Accordéon : clic ouvre/ferme
- [ ] **L6.2** Tout le texte est lisible
- [ ] **L6.3** Un seul item ouvert à la fois

#### L7. Footer
- [ ] **L7.1** Tous les liens fonctionnent (Features, Pricing, FAQ = ancres; Privacy, Terms = pages)
- [ ] **L7.2** Copyright dynamique (2026)

---

### ÉCRAN 2 : SIGNUP / LOGIN

#### S1. Signup
- [ ] **S1.1** Formulaire : Email + Password + bouton
- [ ] **S1.2** Validation email : "test" → erreur, "test@test.com" → OK
- [ ] **S1.3** Validation password : "123" → erreur "min 8 chars", "12345678" → OK
- [ ] **S1.4** Toggle visibility password (👁) fonctionnel
- [ ] **S1.5** Bouton désactivé pendant loading, spinner visible
- [ ] **S1.6** Email déjà utilisé → message erreur + lien "Log in?"
- [ ] **S1.7** Création réussie → redirection `/onboarding`
- [ ] **S1.8** Lien "Already have an account?" → `/login`

#### S2. Login
- [ ] **S2.1** Formulaire : Email + Password + bouton
- [ ] **S2.2** Mauvais credentials → "Invalid email or password"
- [ ] **S2.3** Connexion réussie → `/dashboard` (ou `/onboarding` si pas Garmin)
- [ ] **S2.4** Lien "Forgot password?" → flow reset
- [ ] **S2.5** Lien "Don't have an account?" → `/signup`

#### S3. Forgot Password
- [ ] **S3.1** Email envoyé → message "Check your email"
- [ ] **S3.2** Email non trouvé → message "If this email exists, we sent a link" (pas de fuite d'info)
- [ ] **S3.3** Lien "Back to login" → `/login`

---

### ÉCRAN 3 : ONBOARDING — CONNECT GARMIN

#### O1. État initial
- [ ] **O1.1** Titre + sous-titre + bouton `Connect Garmin` affichés
- [ ] **O1.2** Texte rassurant (🔒) visible
- [ ] **O1.3** Lien "I'll do this later" visible et discret

#### O2. Flow OAuth Garmin
- [ ] **O2.1** Clic `Connect Garmin` → redirection vers Garmin (ou page simulée si test)
- [ ] **O2.2** Au retour : barre de progression "Importing your data..."
- [ ] **O2.3** Les étapes textuelles changent ("Fetching activities..." → "Analyzing metrics..." → "Building dashboard...")
- [ ] **O2.4** Durée < 5 secondes (sinon c'est cassé)
- [ ] **O2.5** Succès → redirection auto `/dashboard`
- [ ] **O2.6** Dashboard affiche les VRAIES données (pas du demo data)

#### O3. Erreurs
- [ ] **O3.1** Timeout Garmin → message "Couldn't connect" + bouton Retry
- [ ] **O3.2** Refus utilisateur → message + bouton Retry
- [ ] **O3.3** Token expiré → message + bouton Reconnect
- [ ] **O3.4** Bouton Retry fonctionnel (relance le flux)

#### O4. Skip
- [ ] **O4.1** Clic "I'll do this later" → `/dashboard` vide
- [ ] **O4.2** Bandeau jaune "Connect your Garmin" visible en haut du dashboard
- [ ] **O4.3** Bandeau cliquable → `/onboarding`

---

### ÉCRAN 4 : DASHBOARD

#### D1. Top Bar & Navigation
- [ ] **D1.1** Logo + nav (Dashboard, Coach, Plan) affichés
- [ ] **D1.2** Mobile : icônes seules en bottom nav
- [ ] **D1.3** Avatar dropdown : Settings, Upgrade (si free), Logout fonctionnels
- [ ] **D1.4** Badge Premium/Free correct selon abonnement

#### D2. Header "This Week"
- [ ] **D2.1** Période correcte (semaine en cours, dynamique)
- [ ] **D2.2** Sous-titre IA généré (si connecté)
- [ ] **D2.3** Si pas de données : message adapté

#### D3. Metric Cards (4 cartes)
- [ ] **D3.1** Distance, Duration, Training Load, Recovery affichés
- [ ] **D3.2** Les valeurs sont correctes (vérifier calcul : somme distance, durée cumulée...)
- [ ] **D3.3** Les tendances (🔺/🔻) sont correctes (comparaison vs last week)
- [ ] **D3.4** Les couleurs de tendance sont correctes (vert = positif, rouge = négatif)
- [ ] **D3.5** Cas "pas de données la semaine dernière" → tendance grisée ou absente

#### D4. Training Load Chart
- [ ] **D4.1** Graphique affiché avec vraies données
- [ ] **D4.2** ATL, CTL, TSB visibles (barres + ligne)
- [ ] **D4.3** Tooltip au hover fonctionnel
- [ ] **D4.4** Zones de couleur (vert/jaune/rouge) correctes
- [ ] **D4.5** Légende visible
- [ ] **D4.6** État < 2 semaines : message "Need more data"

#### D5. Recent Activities
- [ ] **D5.1** Liste affichée (max 10)
- [ ] **D5.2** Chaque ligne : date, type icône, distance, durée, pace
- [ ] **D5.3** Badge "✨ AI Analysis" si analyse dispo
- [ ] **D5.4** Clic → `/activity/{id}` fonctionnel
- [ ] **D5.5** Filtres par type (All, Run, Ride, Swim) fonctionnels
- [ ] **D5.6** Filtres n'affichent que les types présents dans les données
- [ ] **D5.7** État vide : "No activities yet..."

#### D6. AI Insight (Coach's Note)
- [ ] **D6.1** Carte affichée avec texte IA personnalisé
- [ ] **D6.2** Texte pertinent (mentionne des chiffres réels de l'utilisateur)
- [ ] **D6.3** Bouton `Ask Coach More →` → `/coach`
- [ ] **D6.4** État pas de données : "Connect your Garmin..."
- [ ] **D6.5** Mise à jour après nouvelle activité importée

#### D7. États dashboard
- [ ] **D7.1** Loading : skeleton loader, pas de flash
- [ ] **D7.2** Empty (nouvel user, pas de Garmin) : message + CTA connect
- [ ] **D7.3** Empty (Garmin connecté, 0 activités) : message + "Go for a run!"
- [ ] **D7.4** Error API : message + bouton retry
- [ ] **D7.5** Données partielles (ex: a des activités mais pas assez pour le graphique) : afficher ce qui est dispo, message pour le reste

---

### ÉCRAN 5 : ACTIVITY DETAIL

#### A1. Header & Map
- [ ] **A1.1** Flèche retour → `/dashboard`
- [ ] **A1.2** Titre : type + date corrects
- [ ] **A1.3** Carte GPS affichée si l'activité a des coordonnées
- [ ] **A1.4** Start/End markers visibles
- [ ] **A1.5** Activité sans GPS (tapis, piscine) : icône de remplacement

#### A2. Metrics Grid
- [ ] **A2.1** Toutes les métriques dispos sont affichées
- [ ] **A2.2** Les valeurs sont correctes (vérifier vs données brutes Garmin)
- [ ] **A2.3** Les comparaisons sont correctes (avg 4 weeks, max...)
- [ ] **A2.4** Les unités respectent la préférence utilisateur (km ou miles)

#### A3. HR/Pace/Elevation Chart
- [ ] **A3.1** Graphique affiché si données dispo
- [ ] **A3.2** Les 3 courbes sont visibles et distinctes
- [ ] **A3.3** Tooltip au hover
- [ ] **A3.4** Activité sans données HR : adapter (pas de courbe fantôme)

#### A4. AI Analysis
- [ ] **A4.1** Texte IA généré et affiché
- [ ] **A4.2** Le texte est pertinent (mentionne des chiffres spécifiques à l'activité)
- [ ] **A4.3** Pas d'hallucination évidente (ne pas inventer des métriques)
- [ ] **A4.4** 3-5 paragraphes structurés (bien, inquiétant, recommandation)
- [ ] **A4.5** Bouton `Discuss this run` → `/coach` avec contexte pré-rempli
- [ ] **A4.6** Loading : skeleton + "Analyzing your run..."
- [ ] **A4.7** Erreur IA : message + Retry
- [ ] **A4.8** Activité < 10 min : message "Too short for full analysis"

#### A5. Laps
- [ ] **A5.1** Tableau affiché si l'activité a des laps
- [ ] **A5.2** Colonnes : Lap#, Distance, Time, Pace, HR, Elevation
- [ ] **A5.3** Pas de laps → section masquée

---

### ÉCRAN 6 : CHAT COACH

#### C1. Interface
- [ ] **C1.1** Header "Coach" + status Online
- [ ] **C1.2** Zone messages : bulles distinctes (utilisateur vs coach)
- [ ] **C1.3** Input texte + bouton Envoyer
- [ ] **C1.4** Envoyer au clavier (Enter) fonctionne
- [ ] **C1.5** Shift+Enter = nouvelle ligne (pas d'envoi)

#### C2. Suggestions
- [ ] **C2.1** 3-4 questions suggérées affichées sous l'input
- [ ] **C2.2** Les suggestions sont pertinentes (basées sur les données)
- [ ] **C2.3** Clic suggestion → envoie la question

#### C3. Conversation
- [ ] **C3.1** Le coach répond avec des infos personnalisées (mentionne les données)
- [ ] **C3.2** Le coach ne répond PAS avec des données inventées
- [ ] **C3.3** Le coach peut répondre à des questions de suivi (contexte maintenu)
- [ ] **C3.4** Le coach dit "je ne sais pas" si la question est hors scope
- [ ] **C3.5** Le coach ne donne PAS de conseils médicaux (red flag éthique)

#### C4. Historique
- [ ] **C4.1** Scroll vers le haut charge l'historique (pagination)
- [ ] **C4.2** Messages groupés par date
- [ ] **C4.3** Les anciens messages (>7j) sont visuellement différents

#### C5. États
- [ ] **C5.1** Loading réponse : "Coach is thinking..." + animation dots
- [ ] **C5.2** Empty (première visite) : message de bienvenue automatique personnalisé
- [ ] **C5.3** Timeout IA (15s+) : message erreur + retry
- [ ] **C5.4** Utilisateur Free quota atteint : message + CTA Upgrade
- [ ] **C5.5** Pas de données Garmin : message adapté + réponses générales OK

#### C6. Contexte
- [ ] **C6.1** Si arrivée depuis Activity Detail : premier message du coach mentionne l'activité
- [ ] **C6.2** Le coach a accès à l'historique complet (pas juste la session courante)

---

### ÉCRAN 7 : TRAINING PLAN

#### P1. Génération
- [ ] **P1.1** Formulaire complet : distance, date, objectif temps, jours/sem, niveau
- [ ] **P1.2** Validation : date dans le futur, distance valide
- [ ] **P1.3** Loading : "Building your plan..." + progression
- [ ] **P1.4** Résultat : plan affiché avec timeline
- [ ] **P1.5** Pas assez de données (<2 sem) : message + "Keep logging"

#### P2. Timeline
- [ ] **P2.1** Timeline horizontale scrollable
- [ ] **P2.2** Semaine passée : grisée ✓
- [ ] **P2.3** Semaine en cours : surbrillance
- [ ] **P2.4** Semaine future : normale
- [ ] **P2.5** Clic semaine → vue détaillée

#### P3. Vue Semaine
- [ ] **P3.1** Titre "Week X of Y — Phase"
- [ ] **P3.2** Barre de charge : volume prévu vs réalisé
- [ ] **P3.3** Couleurs barre : vert (>80%), jaune (50-80%), rouge (<50%)
- [ ] **P3.4** Chaque jour : icône + type + description + statut
- [ ] **P3.5** Statuts corrects : ✓ Completed, ⏳ Planned, ✗ Missed, 🔄 Adapted
- [ ] **P3.6** Note coach par jour si pertinent

#### P4. Adapt Plan
- [ ] **P4.1** Bouton `Adapt Plan` → régénère le plan
- [ ] **P4.2** Confirmation avant regénération
- [ ] **P4.3** Loading + résultat mis à jour

---

### ÉCRAN 8 : SETTINGS

#### ST1. Profile
- [ ] **ST1.1** First name, Last name éditables
- [ ] **ST1.2** Email read-only
- [ ] **ST1.3** Toggle km/miles fonctionnel → met à jour toutes les pages
- [ ] **ST1.4** Save : toast "Profile updated"

#### ST2. Goal Race
- [ ] **ST2.1** Distance, Date, Target time éditables
- [ ] **ST2.2** Save → met à jour le plan d'entraînement

#### ST3. Garmin Connection
- [ ] **ST3.1** Status affiché (Connected ✓ ou Not connected)
- [ ] **ST3.2** Dernière synchro affichée (datetime)
- [ ] **ST3.3** `Sync Now` → déclenche import + toast
- [ ] **ST3.4** `Disconnect Garmin` → modal confirmation
- [ ] **ST3.5** Annuler dans la modal → rien ne se passe
- [ ] **ST3.6** Confirmer disconnect → status mis à jour

#### ST4. Subscription
- [ ] **ST4.1** Plan actuel affiché
- [ ] **ST4.2** Date expiration si Premium
- [ ] **ST4.3** `Upgrade` → `/pricing` (si Free)
- [ ] **ST4.4** `Manage` → Stripe Customer Portal (si Premium)

#### ST5. Data & Privacy
- [ ] **ST5.1** `Export My Data` → téléchargement fichier JSON/CSV
- [ ] **ST5.2** Le fichier contient toutes les données utilisateur
- [ ] **ST5.3** `Delete Account` → modal confirmation "taper DELETE"
- [ ] **ST5.4** Annuler delete → rien
- [ ] **ST5.5** Confirmer delete → compte supprimé, données purgées, redirect landing page

#### ST6. Logout
- [ ] **ST6.1** `Log Out` → session terminée, redirect `/login`

---

### ÉCRAN 9 : PRICING / UPGRADE

#### PR1. Plans
- [ ] **PR1.1** Free et Premium affichés
- [ ] **PR1.2** Badge "Current Plan" sur le plan actif
- [ ] **PR1.3** Toggle Monthly/Annual fonctionnel
- [ ] **PR1.4** Prix mis à jour selon toggle

#### PR2. Checkout
- [ ] **PR2.1** `Upgrade` → redirection checkout (Stripe/Paddle)
- [ ] **PR2.2** Paiement réussi → retour `/settings?upgrade=success`
- [ ] **PR2.3** Toast vert + badge Premium mis à jour
- [ ] **PR2.4** Paiement annulé → `/pricing?upgrade=cancelled`
- [ ] **PR2.5** Toast gris
- [ ] **PR2.6** Erreur paiement → toast rouge + possibilité réessayer

---

### ÉCRAN 10 : EMAIL HEBDOMADAIRE

#### E1. Contenu
- [ ] **E1.1** Subject dynamique avec métriques
- [ ] **E1.2** Logo visible
- [ ] **E1.3** 4 métriques en mini-cartes (HTML email compatible)
- [ ] **E1.4** Coach's Note personnalisé
- [ ] **E1.5** Next Week Preview
- [ ] **E1.6** CTA `View Dashboard` → lien fonctionnel

#### E2. Delivery
- [ ] **E2.1** Envoyé lundi 7h00 (timezone utilisateur)
- [ ] **E2.2** Uniquement utilisateurs Premium
- [ ] **E2.3** Ne pas envoyer si 0 activité dans la semaine (sauf email "We missed you")

#### E3. Email Client
- [ ] **E3.1** Rendu correct sur Gmail (web + mobile)
- [ ] **E3.2** Rendu correct sur Apple Mail
- [ ] **E3.3** Rendu correct sur Outlook
- [ ] **E3.4** Unsubscribe fonctionnel (1 clic)

---

### ON : ONBOARDING COACH CHAT

#### ON1. Conversation
- [ ] **ON1.1** Conversation flow correct pour chaque type d'objectif (race, weight loss, hyrox, triathlon, health, not sure)
- [ ] **ON1.2** Les suggestion chips apparaissent et sont cliquables
- [ ] **ON1.3** Le coach référence les données Garmin importées
- [ ] **ON1.4** Le typing indicator s'affiche entre les messages
- [ ] **ON1.5** Error state : le coach ne répond pas → message + gestion d'erreur
- [ ] **ON1.6** Le bouton "Let's go" navigue vers la bonne variante de dashboard

---

### GV : GOAL-VARIANT DASHBOARDS

#### GV1. Variantes
- [ ] **GV1.1** Marathon : la goal banner affiche la date de course, le finish projeté, la barre de progression
- [ ] **GV1.2** Weight Loss : affiche la tendance poids, la balance calorique, le nombre de pas
- [ ] **GV1.3** Health : affiche le sommeil, la HRV, les pas, la FC au repos
- [ ] **GV1.4** Chaque variante affiche les bons signaux clés
- [ ] **GV1.5** L'assessment du coach est goal-appropriate

---

### PW : PUSH TO WATCH

#### PW1. Envoi vers la montre
- [ ] **PW1.1** Le bouton "Send to Watch" est visible sur l'écran du plan
- [ ] **PW1.2** La modal de confirmation apparaît
- [ ] **PW1.3** Loading state avec icône de synchro
- [ ] **PW1.4** Succès : indicateur "workouts on watch"
- [ ] **PW1.5** Erreur : bouton retry avec message

---

### MN : MOBILE NAVIGATION

#### MN1. Bottom Nav
- [ ] **MN1.1** Bottom nav 4 tabs visible sur les écrans app <768px
- [ ] **MN1.2** Non visible sur landing/signup/onboarding
- [ ] **MN1.3** Tab actif surligné en accent
- [ ] **MN1.4** Tous les tabs naviguent correctement

---

### DL : DESKTOP LAYOUT

#### DL1. Sidebar
- [ ] **DL1.1** Sidebar visible ≥1024px sur les écrans app
- [ ] **DL1.2** Sidebar masquée sur landing/signup/onboarding
- [ ] **DL1.3** Bottom nav masquée sur desktop
- [ ] **DL1.4** Tous les liens de nav de la sidebar fonctionnent
- [ ] **DL1.5** Le contenu prend la largeur restante (pas de chevauchement avec la sidebar)

---

## QA RÉGRESSION — Après Chaque Story

Après qu'une story est marquée "done", re-tester RAPIDEMENT les stories précédentes :

### Régression rapide (5 min)
- [ ] **RG1.** Signup flow fonctionne toujours
- [ ] **RG2.** Login flow fonctionne toujours
- [ ] **RG3.** Dashboard load sans erreur
- [ ] **RG4.** Navigation complète (chaque lien du menu)
- [ ] **RG5.** `npm run build` passe toujours
- [ ] **RG6.** `pytest` passe toujours (0 failure)
- [ ] **RG7.** `vitest` passe toujours (0 failure)
- [ ] **RG8.** `eslint` 0 warning

Si UNE régression → la story courante n'est PAS done. Retour à Claude avec le bug exact.

---

## QA FINALE — Avant Delivery

Après que TOUTES les stories sont done, avant de livrer :

### E2E Tests (manuel)
- [ ] **E2E.1** Happy path complet : Landing → Signup → Connect Garmin → Dashboard → Activity Detail → AI Analysis → Chat Coach → Training Plan → Settings → Logout → Login → Dashboard (données toujours là)
- [ ] **E2E.2** Paiement : Free → Upgrade → Checkout → Paiement → Premium actif → Coach illimité → Cancel subscription → Retour Free
- [ ] **E2E.3** Edge cases : Signup sans connecter Garmin, import Garmin qui échoue, activité sans GPS, coach hors quota free

### Performance
- [ ] **PF1.** Lighthouse score > 80 (desktop)
- [ ] **PF2.** Lighthouse score > 50 (mobile) — objectif réaliste pour MVP
- [ ] **PF3.** Aucune requête API > 5 secondes

### Sécurité (basique)
- [ ] **SEC1.** Auth required sur `/dashboard`, `/coach`, `/plan`, `/settings`, `/activity/*`
- [ ] **SEC2.** Impossible d'accéder aux données d'un autre utilisateur (vérifier en changeant l'ID dans l'URL)
- [ ] **SEC3.** Password jamais dans les réponses API
- [ ] **SEC4.** Token Garmin jamais dans les réponses API publiques
- [ ] **SEC5.** HTTPS forcé (redirection HTTP → HTTPS)

### Data Integrity
- [ ] **DI1.** Les données Garmin importées sont correctes (comparer 3-5 activités avec Garmin Connect)
- [ ] **DI2.** La suppression de compte supprime TOUTES les données (vérifier DB)
- [ ] **DI3.** L'export de données contient TOUT l'historique

---

## BUG SEVERITY — Triage

| Sévérité | Critère | Action |
|----------|---------|--------|
| 🔴 CRITICAL | App crash, page blanche, data perdue, paiement cassé, auth bypass | Bloque la story. Fix immédiat requis. |
| 🟡 MEDIUM | Feature cassée mais contournable, UI incorrecte, mauvaise donnée affichée | Bloque la story. Fix requis avant de passer à la suivante. |
| 🟢 LOW | Cosmétique, alignement, faute de frappe, micro-animation manquante | Ticket créé. Fix en batch après la story ou en phase bugfix finale. |

---

## SIGN-OFF PAR STORY

Chaque story doit avoir ce bloc rempli avant de passer à la suivante :

```
Story: [US1] Import Garmin OAuth
Date: 2026-06-XX

Backend tests:  ▢ PASS (X/Y)  ▢ FAIL
Frontend tests: ▢ PASS (X/Y)  ▢ FAIL
Build:          ▢ PASS        ▢ FAIL
Lint:           ▢ PASS        ▢ FAIL
QA manuelle:    ▢ PASS        ▢ FAIL (items failed: ___)
Régression:     ▢ PASS        ▢ FAIL (items failed: ___)

Status: ▢ DONE  ▢ NEEDS FIX
```

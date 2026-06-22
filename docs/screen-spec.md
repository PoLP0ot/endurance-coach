# Endurance Coach — Screen Specification (Exhaustive)

> Document de référence pour le design et l'implémentation.
> Chaque écran est décrit élément par élément, état par état.
> Avant tout mockup ou code, ce document doit être validé.

---

## Architecture de navigation

```
LANDING PAGE
    │
    ▼
SIGNUP / LOGIN
    │
    ▼
ONBOARDING — Connect Garmin (import)
    │
    ▼
CONVERSATIONAL ONBOARDING COACH  ◄─── chat qui détermine l'objectif (pas de menu statique)
    │   (Race · Weight Loss · Hyrox · Triathlon · Health · Not sure)
    ▼
DASHBOARD MODULAIRE ("Your Progress") ◄─── écran principal ; s'adapte au type d'objectif
    │
    ├──▶ ACTIVITY DETAIL ("What This Run Means" — coach-first)
    │
    ├──▶ COACH CHAT (persistant + utilisé pendant l'onboarding)
    │
    ├──▶ TRAINING PLAN ("Road to Paris" + Push to Watch)
    │
    ├──▶ SIGNALS / DATA EXPLORER ("Your Signals" — depuis "See all signals")
    │
    ├──▶ ACTIVITIES (historique complet)
    │
    ├──▶ SETTINGS / ACCOUNT
    │
    └──▶ PRICING / UPGRADE

EMAIL HEBDOMADAIRE (hors app, déclenché automatiquement)
```

### Navigation persistante (in-app)

> Le produit réel est une **app téléphone d'abord** (mobile-first), avec un layout desktop complet.

| Viewport | Chrome de navigation |
|----------|----------------------|
| **Mobile (≤1023px, cadre 420px centré)** | Top bar mince (logo + badge plan + avatar) **+ bottom nav 4 onglets** |
| **Desktop (≥1024px)** | **Sidebar fixe 240px** (remplace top + bottom nav) avec carte athlète en pied |

**Bottom nav (mobile) — 4 onglets :**

| Onglet | Icône | Route | Notes |
|--------|-------|-------|-------|
| **Progress** | maison | `/dashboard` | Le dashboard modulaire |
| **Coach** | bulle | `/coach` | Chat coach |
| **Plan** | calendrier | `/plan` | Plan d'entraînement |
| **More** | ••• | bottom sheet | Ouvre une feuille : Activities · Signals · Settings · Pricing & Upgrade · Log out |

**Sidebar (desktop) :** Progress · Coach · Road to Paris (Plan) · — · Activities · Signals · — · Settings, puis carte athlète (avatar + nom + appareil + plan) cliquable vers Settings.

---

## ÉCRAN 1 : LANDING PAGE

### Objectif
Convertir un visiteur froid en inscription. Expliquer le produit en <10 secondes.

### URL
`/` (racine)

### Structure (de haut en bas)

#### 1.1 Header / Navbar
| Élément | Détail |
|---------|--------|
| Logo | Nom du produit + icône (montagne/running simplifié) |
| Navigation | `Features` `Pricing` `FAQ` — ancres vers les sections |
| CTA droite | Bouton `Get Started — Free` → scroll vers CTA ou `/signup` |
| Burger menu | Sur mobile < 768px, remplace la nav |
| État scroll | Fixe en haut, fond transparent → opaque blanc au scroll |

#### 1.2 Hero Section
| Élément | Détail |
|---------|--------|
| Headline (H1) | "Your Garmin data, finally decoded." |
| Subheadline (H2) | "AI coaching that analyzes your training data and tells you exactly what to do next — 10x cheaper than a human coach." |
| CTA primaire | Bouton `Connect Your Garmin — It's Free` → `/signup` |
| CTA secondaire | Texte lien `See how it works ↓` → ancre vers How It Works |
| Image/illustration | Mockup dashboard (flottant, slight shadow) OU animation simplifiée |
| Social proof | Texte "Join 200+ runners already training smarter" (dynamique si possible) |

**État :** Si compteur users > 0, afficher le vrai chiffre.
**Mobile :** Image sous le texte, CTA full-width.

#### 1.3 How It Works (3 étapes)
| Étape | Icône | Titre | Description |
|-------|-------|-------|-------------|
| 1 | 🔗 | Connect Garmin | "Link your Garmin account in 2 clicks. We import your entire history automatically." |
| 2 | 📊 | Get Your Dashboard | "See your training load, recovery, and trends in 30 seconds. Finally understand what your watch is telling you." |
| 3 | 🤖 | AI Coaching | "Your personal AI coach analyzes every run and tells you what to do tomorrow. No more guessing." |

**Layout :** 3 colonnes desktop, 1 colonne mobile. Icône + titre + description centrés.

#### 1.4 Features (3 colonnes)
| Colonne | Icône | Titre | Description |
|---------|-------|-------|-------------|
| Deep Analytics | 📊 | Understand Every Metric | Training load (CTL/ATL/TSB), recovery scores, HRV trends. All the data Garmin collects — explained. |
| AI Coach | 🤖 | Ask Anything | "Am I overtraining?" "When should I do my next speed workout?" Your coach knows YOUR data. |
| Training Plans | 📅 | Adaptive Plans | Personalized plans for 5K to marathon that adapt to your actual performance and fatigue. |

**Sous chaque feature :** mini bullet list de 2-3 bénéfices concrets.

#### 1.5 Comparison Table
| Feature | Endurance Coach | Garmin Connect | Strava | TrainingPeaks |
|---------|:--------------:|:-------------:|:------:|:-------------:|
| Import Garmin data | ✅ | ✅ (natif) | ✅ (via upload) | ✅ (via upload) |
| Deep analytics | ✅ | ⚠️ (basique) | ✅ (Summit payant) | ✅ |
| AI Coach (chat) | ✅ | ❌ | ❌ | ❌ |
| Adaptive training plan | ✅ | ⚠️ (Garmin Coach basique) | ❌ | ❌ |
| Prix/mois | $8 | $6.99 (Connect+) | $11.99 | $19.95 |

**Layout :** Tableau responsive (horizontal scroll sur mobile). Notre colonne en surbrillance (accent color).

#### 1.6 Pricing Section
| Plan | Prix | Features |
|------|------|----------|
| **Free** | $0 forever | Dashboard analytics, last 30 days history, basic metrics |
| **Premium** | $8/mo or $79/yr | Full history, AI Coach (unlimited), adaptive training plans, weekly email reports |

**CTA :** Bouton `Start Free` sous Free, bouton `Go Premium — $8/mo` sous Premium (highlighted).
**Note :** "10x cheaper than a human coach ($100-300/mo). Cancel anytime."
**Toggle :** Monthly / Annual (avec badge "Save 18%" sur Annual).

#### 1.7 Testimonials (3 citations)
| Citation | Auteur |
|----------|--------|
| "Finally an app that tells me WHY I feel tired and what to do about it. Replaced my $200/mo coach." | Beta tester (runner, marathon) |
| "I've been exporting Garmin data to ChatGPT for months. This does it automatically and better." | Beta tester (triathlete) |
| "The AI caught my overtraining pattern before I got injured. That alone is worth the subscription." | Beta tester (runner, ultra) |

**Layout :** 3 cartes en grille. Photo + nom + citation. Sur mobile, 1 colonne.
**État initial (pre-lancement) :** Remplacer par 1 témoignage du founder + "Be one of the first" CTA.

#### 1.8 FAQ (accordéon)
| Question | Réponse |
|----------|---------|
| Is my Garmin data safe? | Yes. Your data is encrypted at rest and in transit. We never sell your data. GDPR compliant. You can export or delete your data anytime. |
| How is this different from Garmin Coach? | Garmin Coach offers static, pre-built plans. Our AI coach analyzes YOUR actual data, adapts daily, and you can have a conversation with it. It's like a human coach, but powered by AI. |
| Do I need a Garmin watch? | Currently, yes — we start with Garmin integration. COROS, Polar, Suunto, and Strava import coming in V2. |
| Can I import from Strava too? | Not yet — Strava import is planned for V2. For now, connect your Garmin directly. |
| What's included in the free plan? | Full dashboard analytics for the last 30 days, basic metrics, and weekly training load trend. Premium unlocks unlimited history, AI coach, and training plans. |
| Can I cancel anytime? | Yes. Cancel with one click. No questions asked. Your data remains accessible in read-only mode. |

**Layout :** Accordéon (cliquer pour expand). Question en gras, réponse en texte normal.

#### 1.9 Footer
| Élément | Détail |
|---------|--------|
| Logo + nom | Petit, à gauche |
| Liens | `Features` `Pricing` `FAQ` `Privacy Policy` `Terms of Service` `Contact` |
| Copyright | `© 2026 Endurance Coach. All rights reserved.` |
| Social icons | Twitter/X, GitHub (optionnel), Discord |

---

## ÉCRAN 2 : SIGNUP / LOGIN

### URL
`/signup` et `/login`

### Objectif
Créer un compte ou se connecter. Le plus rapide possible.

### Signup
| Élément | Détail |
|---------|--------|
| Titre | "Create your account" |
| Sous-titre | "Start your free trial. No credit card required." |
| Champ Email | Input text, validation email |
| Champ Password | Input password, min 8 chars, avec toggle visibility (👁) |
| Bouton | `Create Account` (ou `Continue with Google` si OAuth Google) |
| Séparateur | "or" entre email et Google |
| Lien | "Already have an account? Log in" → `/login` |

**États :**
- **Loading :** Bouton désactivé + spinner "Creating your account..."
- **Error (email invalide) :** Message rouge sous le champ "Please enter a valid email"
- **Error (password trop court) :** Message rouge "Password must be at least 8 characters"
- **Error (email déjà utilisé) :** Message rouge "An account with this email already exists. Log in?"
- **Success :** Redirection vers `/onboarding`

### Login
| Élément | Détail |
|---------|--------|
| Titre | "Welcome back" |
| Champ Email | Input text |
| Champ Password | Input password + "Forgot password?" lien |
| Bouton | `Log In` |
| Lien | "Don't have an account? Sign up" → `/signup` |

**États :**
- **Loading :** Spinner "Logging in..."
- **Error (mauvais credentials) :** "Invalid email or password"
- **Success :** Redirection vers `/dashboard` (ou `/onboarding` si pas encore connecté Garmin)

### Forgot Password
| Élément | Détail |
|---------|--------|
| Titre | "Reset your password" |
| Champ Email | Input text |
| Bouton | `Send reset link` |
| Success | "Check your email. We sent you a reset link." |
| Lien | "Back to login" |

---

## ÉCRAN 3 : ONBOARDING — CONNECT GARMIN

### URL
`/onboarding`

### Objectif
Connecter le compte Garmin de l'utilisateur. Écran critique : si l'utilisateur abandonne ici, il ne revient pas.

### Structure
| Élément | Détail |
|---------|--------|
| Icône | Montre Garmin + flèche → logo Endurance Coach (connexion visuelle) |
| Titre | "Connect your Garmin account" |
| Sous-titre | "We'll import your activity history, health metrics, and training data. This takes about 30 seconds." |
| Bouton principal | `Connect Garmin` (large, visible, branding Garmin discret) |
| Texte rassurant | 🔒 "Your data is encrypted. We never share it. You can revoke access anytime." |
| Skip option | Texte lien discret "I'll do this later" → `/dashboard` (dashboard vide) |

**États :**
- **Idle :** Bouton `Connect Garmin` affiché
- **Redirect Garmin OAuth :** L'utilisateur est redirigé vers Garmin Connect pour autoriser
- **Callback — Loading :** Après retour de Garmin. Spinner + "Importing your Garmin data..."
  - Barre de progression simulée : "Fetching activities..." → "Analyzing metrics..." → "Building your dashboard..."
  - Durée réelle : 2-5 secondes (selon volume de données)
- **Callback — Error :** "We couldn't connect to Garmin. Please try again." + bouton `Retry`
  - Erreurs possibles : timeout, refus utilisateur, token expiré
- **Callback — Success :** Redirection automatique vers la **Conversational Onboarding Coach** (`/coachonboard`), PAS directement vers le dashboard. Toast : "Garmin connected · N activities imported".

**Si skip ("I'll do this later") :** On passe quand même par la Conversational Onboarding Coach (l'objectif peut être défini sans données), puis dashboard vide avec bandeau jaune : "Connect your Garmin to unlock full analytics → `Connect Garmin`".

**Responsive :** Écran centré, pleine hauteur, identique mobile/desktop (carte unique).

---

## ÉCRAN 3.5 : CONVERSATIONAL ONBOARDING COACH

### URL
`/coachonboard`

### Objectif
**Remplace l'ancien menu statique de sélection d'objectif.** Après l'import Garmin, le coach IA ouvre une conversation, se présente, **référence naturellement les données importées**, et détermine l'objectif de l'utilisateur **par le dialogue**. La conversation choisit la variante de dashboard à afficher (architecture modulaire — cf Écran 4).

### Structure
| Élément | Détail |
|---------|--------|
| Header mince | Logo Endurance Coach + libellé d'étape "Step 3 of 3 · Your goal" |
| Zone chat | Mêmes bulles que le Coach Chat (coach à gauche, utilisateur à droite), indicateur "typing" (3 dots) avant chaque message coach |
| Message d'accueil | Le coach se présente **en citant les données Garmin** : "Hi Marc! 👋 I've just imported **14 activities** from your Garmin FR965. You're running about **42 km/week** with a threshold pace of **4:24/km**. Your HRV is stable at **48 ms** — you're in good shape. So — what are you training for right now?" |
| Suggestion chips | Sous l'input, cliquables : **🏃 Race · ⚖️ Weight Loss · 💪 Hyrox / functional fitness · 🏊 Triathlon · ❤️ Just staying healthy · 🤷 Not sure yet** |
| Input libre | Texte libre accepté à chaque étape ; classifié vers un type d'objectif (race / weightloss / hyrox / triathlon / health / other) par mots-clés |
| CTA de hand-off | À la fin de chaque branche, un bouton plein largeur ("Let's go →", "Start tracking →", "Let's build this →"…) bascule vers la variante de dashboard correspondante (toast "Goal set · …") |

### Branches conversationnelles (chaque chemin se déroule par le dialogue)
| Chip / intention | Questions de suivi | Issue (variante dashboard) |
|------------------|--------------------|-----------------------------|
| **Race** | distance (5K/10K/Half/Marathon/Ultra/pas de date) → cible (temps visé ou simplement finir) | `marathon` (Running) — plan 12 semaines |
| **Weight Loss** | poids cible (texte libre, ex "78 kg") | `weightloss` |
| **Hyrox** | accès matériel (full gym / home / bodyweight) → date de l'event | `hyrox` (architecture prête ; variante de dashboard servie via le lens santé/hybride en MVP) |
| **Triathlon** | distance (Sprint/Olympic/70.3/Ironman) → date | `triathlon` (architecture prête ; lens 3-sports) |
| **Health / Not sure** | confirmation ("General Health : sleep, HRV, movement, stress") | `health` |
| **Autre (catch-all)** | "I love the ambition…" → propose de tracker base + santé, ajuste quand l'objectif se précise | `health` (base flexible) |

### États
| État | Affichage |
|------|-----------|
| **Coach is typing** | Bulle avec 3 dots animés avant chaque réponse |
| **Free text non reconnu** | Catch-all gracieux : le coach reformule et propose la liste, ou démarre une base flexible |
| **Reprise / reload direct** | La conversation redémarre proprement au message d'accueil |

**Note design :** Le coach **ne dump jamais** les données — il les référence dans la conversation ("votre HRV est stable à 48 ms"). C'est le premier contact "coach-first".

**Responsive :** Le chat occupe la hauteur entre le header mince et le bas de l'écran ; identique mobile/desktop (pas de bottom nav pendant l'onboarding).

---

## ÉCRAN 4 : DASHBOARD (principal — modulaire)

### URL
`/dashboard` (libellé écran : **"Your Progress"**)

### Objectif
En 30 secondes, l'utilisateur doit comprendre où il en est **par rapport à SON objectif** et savoir quoi faire. C'est le "aha moment". Philosophie **coach-first** : la narration du coach passe avant la donnée brute ; chaque écran répond à **une seule question**.

### Architecture modulaire (le dashboard s'adapte au type d'objectif)

Le dashboard est un **lens** déterminé par l'objectif choisi en onboarding conversationnel (Écran 3.5). Chaque variante change : quelles métriques sont primaires, ce sur quoi le coach se concentre, et ce que "réussir" veut dire. Toutes les variantes partagent la même ossature **coach-first** : *bannière objectif (north star) → assessment du coach → tableau "this week / vs goal" → key signals → activités récentes*.

| Variante | `goalType` | Métriques primaires | Bannière / north star |
|----------|-----------|---------------------|------------------------|
| **Dashboard/Running** (marathon) | `marathon` | Pace, TSS/Load, readiness, projection finish | "Road to Paris" — barre de progression semaines + finish projeté |
| **Dashboard/WeightLoss** | `weightloss` | Calorie balance, weight trend, steps/jour, active minutes | Barre poids départ → cible (kg) + tendance |
| **Dashboard/Health** | `health` | Sleep score, HRV, steps/jour, resting HR | "Stay active · feel good" (pas de cible chiffrée) |
| **Dashboard/Hyrox** | `hyrox` | Running compromis + force endurance (hybride) | Event hybride (architecture prête ; MVP rend le lens santé/hybride) |
| **Dashboard/Triathlon** | `triathlon` | Équilibre 3 sports (swim/bike/run), récup | Event tri (architecture prête ; lens 3-sports) |

> **MVP :** les variantes `marathon`, `weightloss` et `health` sont entièrement rendues. `hyrox` et `triathlon` sont supportés par l'onboarding et l'architecture ; leur dashboard réutilise le lens santé/hybride en attendant la variante dédiée.

### Structure

#### 4.1 Top Bar (mobile) / Sidebar (desktop)
| Élément | Détail |
|---------|--------|
| Logo + nom | À gauche, lien vers `/dashboard` |
| Navigation (mobile) | **Bottom nav 4 onglets** : Progress · Coach · Plan · More (cf "Navigation persistante" plus haut). La top bar mobile ne contient que logo + badge plan + avatar. |
| Navigation (desktop ≥1024px) | **Sidebar fixe 240px** (Progress · Coach · Road to Paris · Activities · Signals · Settings) + carte athlète |
| Avatar utilisateur | À droite (top bar), dropdown : `Settings` `Upgrade plan` `Log out` |
| Badge Premium | Si premium : badge doré "PREMIUM". Si free : badge "FREE" gris |

#### 4.2 Header "This Week"
| Élément | Détail |
|---------|--------|
| Titre | "This Week" |
| Période | Lundi 16 Juin — Dimanche 22 Juin (dynamique, semaine en cours) |
| Sous-titre IA | Une phrase générée : "Your training load is well balanced. You're ready for a quality session tomorrow." (si connecté) |

#### 4.3 Metric Cards (4 cartes en grille)
| Carte | Valeur | Unité | Sous-texte | Tendance |
|-------|--------|-------|-----------|----------|
| **Distance** | 42.3 | km | "3 runs this week" | 🔺 +12% vs last week |
| **Duration** | 3h42 | h | "Avg 1h14/run" | 🔺 +8% |
| **Training Load** | 487 | TSS | "Optimal zone" | → stable |
| **Recovery** | 82 | /100 | "Well recovered" | 🔺 +5% |

**Layout :** 4 cartes en grille 2x2 desktop, 2x2 mobile.
**Chaque carte :** Fond blanc/bg-card, bordure légère, ombre subtile.
**Couleur tendance :** Vert (🔺 positif), Rouge (🔻 négatif), Gris (→ stable).

#### 4.4 Training Load Chart (carte large)
| Élément | Détail |
|---------|--------|
| Titre | "Training Load — Last 4 Weeks" |
| Graphique | Barres empilées ou aires : Charge aiguë (ATL) vs Charge chronique (CTL) |
| Ligne TSB | Training Stress Balance (forme) en overlay |
| Zones | Couleurs de fond : vert (optimal), jaune (attention), rouge (surentraînement) |
| Tooltip | Au hover : date + valeur ATL/CTL/TSB |
| Légende | ATL (7-day avg), CTL (42-day avg), TSB (CTL - ATL) |

**État empty (nouvel utilisateur) :** "Need at least 2 weeks of data to show training load trends. Keep training!"

#### 4.5 Recent Activities (liste)
| Élément | Détail |
|---------|--------|
| Titre | "Recent Activities" |
| Filtre | Onglets : `All` `Run` `Ride` `Swim` (basé sur les types dispo) |
| Ligne activité | Date + Type icône + Titre + Distance + Duration + Pace/HR + badge Analyse |
| Badge IA | Si l'analyse IA a été générée : pastille "✨ AI Analysis" |
| Clic | → `/activity/{id}` |

**Layout :** Liste scrollable, max 10 activités. "View all" en bas.
**État empty :** "No activities yet. Connect your Garmin and go for a run! 🏃"

#### 4.6 AI Insight (carte)
| Élément | Détail |
|---------|--------|
| Titre | "Coach's Note" |
| Icône | 🤖 ou avatar coach |
| Texte | 2-3 phrases d'analyse IA : ce qui va bien, ce qui est inquiétant, recommandation |
| Bouton | `Ask Coach More →` → `/coach` |

**Régénération :** L'insight est mis à jour après chaque nouvelle activité importée.
**État empty :** "Connect your Garmin and complete your first activity to get AI insights."

> **Note coach-first :** dans le produit réel, sections 4.2–4.6 sont fusionnées en une narration. L'ossature exacte par variante est détaillée en 4.7. Les insights dans l'assessment du coach sont **expandables** via un bouton `[▸]` inline qui révèle la donnée de support (valeurs + sparkline + explication) sans quitter l'écran.

#### 4.7 Variantes de dashboard (ossature coach-first)

Toutes les variantes suivent : **Bannière objectif → Coach's Assessment → tableau hebdo → Key Signals → Recent Activities**. Chaque variante n'expose que les signaux pertinents pour l'objectif ; les autres données (HRV, sleep, body battery, stress, VO2Max, resting HR, training status) restent disponibles mais non dumpées.

##### Dashboard/Running (`marathon`)
- **Bannière "Road to Paris" :** course cible + date + barre de progression (semaines done/total) + finish projeté ("3h28 · ± 4 min · On Track") vs target.
- **Coach's Assessment :** narration de la semaine avec insights `[▸]` (HRV stable, resting HR ↓, séance threshold, sleep). CTA "Discuss this week with your coach →".
- **This Week at a glance :** tableau Distance / Load (TSS) / Sessions / Readiness — colonnes *this week · last week · plan next*.
- **Key Signals :** chips color-codées (HRV stable · Load optimal · Resting HR ↓ · Sleep attention), chacune ouvre un panneau détail (sparkline + lecture "For Paris:").
- **Recent Activities :** liste compacte avec verdict coach 1-ligne par séance.

##### Dashboard/WeightLoss (`weightloss`)
- **Bannière :** barre poids départ (86 kg) → cible (78 kg) · poids actuel · % · "Current trend −0.5 kg/wk · On Track".
- **Métriques (4) :** Calorie Balance (déficit, 7-day avg) · Weight Trend (kg/wk) · Steps / Day · Active Minutes.
- **Coach's Assessment :** insights `[▸]` sur déficit calorique, steps, sommeil.
- **Weekly Targets :** Calorie goal / Steps / Active minutes / Weight — *this week · last · goal*.
- **Key Signals :** Calorie deficit · Step consistency · Weight trend · Sleep quality (lecture "For your goal:").

##### Dashboard/Health (`health`)
- **Bannière :** "General Health · Stay active · feel good" (pas de cible chiffrée).
- **Métriques (4) :** Sleep Score · HRV · Steps / Day · Resting HR (avec status dots g/y/r).
- **Coach's Assessment :** insights `[▸]` sur sommeil, HRV, mouvement quotidien ; ton rassurant, propose de basculer vers un objectif spécifique à tout moment.
- **Weekly Summary :** Activity (jours actifs) / Sleep avg / Steps avg / Stress.
- **Key Signals :** HRV balanced · Sleep healthy · Daily movement (lecture "For your wellbeing:").

##### Dashboard/Hyrox (`hyrox`) — architecture prête
- Lens **hybride** : running compromis (pace sous fatigue) + force endurance (2–3 séances hybrides/semaine) + vitesse de transition. MVP : rend le lens santé/hybride.

##### Dashboard/Triathlon (`triathlon`) — architecture prête
- Lens **3 sports** : équilibre swim / bike / run, protection de la récupération entre disciplines. MVP : rend le lens santé/3-sports.

#### 4.8 Accès aux signaux
Lien **"See all signals →"** (ou onglet More → Signals) vers l'écran **Signals / Data Explorer** (Écran 11) qui répond à chaque métrique sous forme de question.

**Responsive :**
- **Mobile :** colonne unique, métriques en grille 2×2, bottom nav en bas, padding réservé pour la nav.
- **Desktop (≥1024px) :** sidebar 240px, grilles métriques 4-up restaurées, tableau hebdo sur 3 colonnes larges, sparklines des Key Signals affichées inline.

---

## ÉCRAN 5 : ACTIVITY DETAIL — "What This Run Means"

### URL
`/activity/{id}`

### Objectif
Répondre à **une seule question : "qu'est-ce que cette sortie veut dire ?"** L'analyse du coach passe **en premier** ; la donnée brute (laps, zones, métriques, carte GPS) est repliée dessous, dépliable à la demande.

### Ordre coach-first (important)
1. **Header** (titre + date + contexte "Paris · Week 6 of 18" + TSS).
2. **"What This Run Means"** — l'analyse narrative du coach (la section clé, cf 5.5), affichée immédiatement, avec CTA "Discuss this run with your coach →".
3. **"See the data behind this analysis"** — carte **collapsible** contenant : tableau laps (pace/HR par rep), temps en zones HR, grille métriques, carte GPS. Repliée par défaut sur mobile ; **dépliée par défaut sur desktop** (la donnée devient la colonne gauche, le coach la colonne droite sticky).

> Les anciennes sections 5.2 (Map), 5.3 (Metrics Grid), 5.4 (Chart), 5.6 (Laps) **vivent désormais à l'intérieur** de la carte collapsible "See the data". L'analyse IA (5.5) est promue en tête.

### Structure

#### 5.1 Header
| Élément | Détail |
|---------|--------|
| Retour | Flèche `← Back to Dashboard` |
| Titre | Type d'activité + date : "Morning Run — Mon 16 Jun" |
| Badge | Type (Run, Ride, Swim) |

#### 5.2 Map (si activité outdoor avec GPS)
| Élément | Détail |
|---------|--------|
| Carte | Trajet GPS rendu sur fond OpenStreetMap/Mapbox |
| Start/End | Marqueurs début (vert) et fin (rouge) |
| Tooltip | Distance, pace au hover |

**État pas de GPS :** Carte remplacée par icône activité (tapis de course, piscine, home trainer).

#### 5.3 Metrics Grid (8 métriques clés)
| Métrique | Valeur | Unité | Comparaison |
|----------|--------|-------|-------------|
| Distance | 12.4 | km | Avg last 4 weeks: 10.2 km |
| Duration | 54:32 | min | — |
| Pace | 4:24 | /km | Avg: 4:52/km |
| Avg HR | 152 | bpm | Max: 178 bpm |
| Elevation | 145 | m | — |
| Cadence | 172 | spm | Avg: 168 |
| Training Effect | 3.5 | Aerobic | "Maintaining" |
| Calories | 687 | kcal | — |

**Layout :** Grille 4x2 desktop, 2x4 mobile. Chaque métrique : label + valeur (grand) + comparaison (petit, gris).

#### 5.4 HR / Pace / Elevation Chart
| Élément | Détail |
|---------|--------|
| Type | Graphique linéaire avec overlay |
| Lignes | Pace (min/km), HR (bpm), Elevation (m) — 3 axes Y |
| Zoom | Sélection plage temporelle |
| Tooltip | Valeurs au hover |

#### 5.5 AI Analysis (section clé — affichée EN PREMIER, titre "What This Run Means")
| Élément | Détail |
|---------|--------|
| Titre | **"What This Run Means"** (coach-first ; remplace "Coach's Analysis") |
| Icône | 🤖 |
| Texte principal | 3-5 paragraphes narratifs IA : |
| | 1. Ce qui était bien ("Your pacing was excellent — negative split on the second half...") |
| | 2. Ce qui est inquiétant ("Your HR drifted up 12 bpm at constant pace — possible fatigue or dehydration...") |
| | 3. Recommandation concrète ("Take an easy day tomorrow. If HR stays elevated, consider a rest day Thursday.") |
| Bouton | `Discuss this run with Coach →` → `/coach` (pré-rempli avec contexte de cette activité) |

**État :**
- **Loading IA :** Skeleton loader + "Analyzing your run..."
- **Erreur IA :** "Couldn't generate analysis. Try again." + bouton Retry
- **Activité trop courte (<10 min) :** "This activity is too short for a full analysis. Keep logging your runs!"

#### 5.6 Laps / Intervals (tableau)
| Colonne | Détail |
|---------|--------|
| Lap # | Numéro |
| Distance | km |
| Time | min:sec |
| Pace | /km |
| Avg HR | bpm |
| Elevation | m |

**Si pas de laps :** Section masquée.

---

## ÉCRAN 6 : CHAT COACH

### URL
`/coach`

### Objectif
Conversation libre avec l'IA coach qui a accès à toutes les données de l'utilisateur.

### Deux usages du même moteur de chat
1. **Pendant l'onboarding** (Écran 3.5, `/coachonboard`) : la même interface chat sert à déterminer l'objectif via une machine à états guidée (chips de suggestion + texte libre).
2. **Écran persistant de l'app** (`/coach`, onglet Coach de la bottom nav / sidebar) : conversation libre, contexte athlète complet, accessible à tout moment.

> Sur desktop, le Coach Chat affiche un **rail "Athlete Context"** à droite (HRV, resting HR, sleep, load, finish projeté) — référence rapide pour la conversation.

### Structure

#### 6.1 Interface Chat
| Élément | Détail |
|---------|--------|
| Header | "Coach" + icône 🤖 + status "Online" (point vert) |
| Sous-titre | "Ask me anything about your training. I know all your Garmin data." |
| Zone messages | Bulles de conversation (utilisateur à droite en accent, coach à gauche en gris clair) |
| Input | Champ texte + bouton Envoyer (ou Enter) |
| Suggestions | 3-4 questions suggérées sous l'input (cliquables) |

**Suggestions dynamiques (basées sur les données) :**
- "Am I at risk of overtraining?"
- "When should I do my next interval session?"
- "How does my pace compare to last month?"
- "What's the best workout for me tomorrow?"

#### 6.2 Historique
- Scroll infini vers le haut (pagination)
- Groupé par date ("Today", "Yesterday", "Last Week")
- Les messages de plus de 7 jours sont grisés

#### 6.3 États
| État | Affichage |
|------|-----------|
| **Loading (réponse coach)** | "Coach is thinking..." + 3 dots animés |
| **Empty (nouvel utilisateur)** | Message de bienvenue automatique : "Hi! I'm your AI coach. I've looked at your Garmin data. You've done 3 runs this week totaling 28km. Your training load is building well. What would you like to know?" |
| **Erreur (timeout IA)** | "Sorry, I'm having trouble processing that. Try rephrasing or ask something simpler." + bouton Retry |
| **Utilisateur free (quota)** | "You've reached the free coach limit. Upgrade to Premium for unlimited coaching." + bouton `Upgrade →` |
| **Aucune donnée Garmin** | "I don't see any Garmin data yet. Once you connect your watch, I can give you personalized coaching. Until then, I can answer general training questions!" |

#### 6.4 Contexte injecté (invisible à l'utilisateur)
Quand l'utilisateur arrive depuis une activité spécifique, le premier message du coach inclut le contexte :
> "I see you just finished your 12.4km run at 4:24/km pace. Your HR averaged 152 bpm. Want to discuss this run?"

---

## ÉCRAN 7 : TRAINING PLAN

### URL
`/plan` (libellé écran pour la variante marathon : **"Road to Paris"**)

### Objectif
Afficher et gérer le plan d'entraînement généré par l'IA, et **pousser les séances structurées vers la montre Garmin**.

### Structure

#### 7.1 Header
| Élément | Détail |
|---------|--------|
| Titre | "Road to Paris" / "Your Training Plan" |
| Objectif | Course cible + date : "Paris Marathon — 14 Sep 2026" (ou "No goal race set") |
| Compte à rebours | "12 weeks to go" |
| Bouton | `Adapt Plan` → régénère le plan complet |

#### 7.2 Timeline (semaines)
| Élément | Détail |
|---------|--------|
| Layout | Timeline horizontale scrollable, 1 colonne par semaine |
| Semaine passée | Grisée, cochée ✓ |
| Semaine en cours | Surbrillance accent color, bordure |
| Semaine future | Normale, semi-transparente |
| Clic semaine | → Vue détaillée de la semaine |

#### 7.3 Vue Semaine (semaine en cours par défaut)
| Élément | Détail |
|---------|--------|
| Titre | "Week 3 of 12 — Build Phase" |
| Barre de charge | Volume prévu vs réalisé : barre de progression (vert si OK, jaune si -20%, rouge si -50%) |
| Jour | Pour chaque jour de la semaine : |
| | - Jour (Lun/Mar/...), icône météo, type séance |
| | - Description workout (ex: "Easy Run: 8km @ 5:15-5:30/km, Zone 2 HR") |
| | - Badge statut : ✓ Completd, ⏳ Planned, ✗ Missed, 🔄 Adapted |
| | - Clic → détail du workout |
| Note coach | Une phrase IA par jour si pertinent : "Your HR was elevated yesterday — I've shortened today's workout." |

#### 7.4 Push to Watch (envoyer les séances à la montre Garmin)

Pour la semaine en cours (et les semaines futures), l'app peut **envoyer les workouts structurés vers la montre Garmin** où ils apparaissent dans le Training Calendar, prêts à démarrer en un tap.

| Élément | Détail |
|---------|--------|
| CTA (non envoyé) | Bouton plein largeur avec glyphe montre : **"Send This Week to Watch →"** |
| Modal de confirmation | "Send N workouts to your Garmin? — We'll send this week's **N workouts** to your **Garmin Forerunner 965**. They'll appear in your watch's Training Calendar…" → `Cancel` / `Send to watch` |
| État envoi | Modal spinner "Sending to Garmin… Syncing N workouts to your Forerunner 965." |
| Succès | Toast "N workouts sent to Marc's FR965 ✓ · Check your watch". La carte devient un **bandeau vert** : "N/N workouts on your watch · Synced to {device}" + lien **"Re-send"**. Chaque jour avec séance affiche une **icône montre** (olive = sur la montre). |
| Erreur (montre/Garmin injoignable) | Modal warning "Couldn't sync with Garmin — Make sure your watch is connected…" + boutons `Cancel` / `Retry` |
| Portée | Bouton visible uniquement pour la semaine courante / futures (pas les semaines passées). État mémorisé par semaine. |

#### 7.5 Génération de plan (si pas de plan existant)
| Élément | Détail |
|---------|--------|
| Formulaire | Race distance (5K, 10K, Semi, Marathon) |
| | Date de la course |
| | Objectif de temps (optionnel) |
| | Jours d'entraînement/semaine (3-6) |
| | Niveau actuel (débutant, intermédiaire, avancé) |
| Bouton | `Generate My Plan` |
| Loading | "Building your personalized plan..." + barre de progression |
| Result | Plan affiché (timeline) |

**États :**
- **Aucune donnée Garmin :** "We need your training history to build a personalized plan. Connect your Garmin first." + bouton `Connect Garmin`
- **Pas assez de données (<2 semaines) :** "We need at least 2 weeks of training data. Keep logging your runs — your plan will be ready soon!"
- **Pas d'objectif défini :** Formulaire de génération affiché.

---

## ÉCRAN 8 : SETTINGS / ACCOUNT

### URL
`/settings`

### Structure

#### 8.1 Sections
| Section | Champs |
|---------|--------|
| **Profile** | First name, Last name, Email (read-only), Units (km/miles → toggle) |
| **Goal Race** | Distance, Date, Target time (optionnel), Bouton Save |
| **Garmin Connection** | Status (Connected ✓ ou Not connected), Dernière synchro, Bouton `Sync Now`, Bouton `Disconnect Garmin` (rouge, avec confirmation) |
| **Subscription** | Plan actuel (Free / Premium), Date d'expiration (si Premium), Bouton `Upgrade` ou `Manage Subscription` → Stripe Customer Portal |
| **Data & Privacy** | `Export My Data` → téléchargement JSON/CSV, `Delete My Account` → confirmation + suppression complète |
| **Logout** | Bouton `Log Out` |

**États :**
- **Disconnect Garmin :** Modal de confirmation "Are you sure? Your data will remain but won't update." → `Cancel` / `Disconnect`
- **Delete Account :** Modal de confirmation "This action is irreversible. All your data will be permanently deleted." → taper "DELETE" pour confirmer
- **Sync Now :** Bouton désactivé + spinner "Syncing..." → toast "Sync complete ✓" ou "Sync failed — try again"

---

## ÉCRAN 9 : PRICING / UPGRADE

### URL
`/pricing`

### Structure

#### 9.1 Plans
Même structure que la section Pricing de la Landing Page (cf Écran 1, section 1.6), avec en plus :

| Élément | Détail |
|---------|--------|
| Plan actuel | Badge "Current Plan" sur le plan Free ou Premium |
| CTA Free | Si déjà sur Free : bouton grisé "Your Plan". Sinon : `Downgrade` |
| CTA Premium | Si déjà sur Premium : `Manage Subscription →`. Sinon : `Upgrade — $8/mo` |

#### 9.2 Checkout (Stripe ou Paddle)
- Redirection vers Stripe Checkout / Paddle hosted checkout
- URL de retour succès : `/settings?upgrade=success`
- URL de retour annulation : `/pricing?upgrade=cancelled`

**États :**
- **Loading checkout :** "Redirecting to secure payment..."
- **Success :** Toast vert "Welcome to Premium! 🎉 Your AI coach is ready." + redirection `/dashboard`
- **Cancelled :** Toast gris "Upgrade cancelled. You can try Premium anytime."
- **Error :** Toast rouge "Payment failed. Please try again or contact support."

---

## ÉCRAN 10 : EMAIL HEBDOMADAIRE (template)

### Déclencheur
Envoyé automatiquement chaque lundi 7h00 (heure locale utilisateur).

### Destinataire
Uniquement utilisateurs Premium.

### Contenu
| Section | Détail |
|---------|--------|
| **Subject** | "Your Weekly Run-down: 42km, +12% training load, Coach's advice inside" |
| **Header** | Logo Endurance Coach |
| **Title** | "Your Training Week — June 16-22" |
| **Metric cards** | Mêmes 4 métriques que le dashboard (Distance, Duration, Load, Recovery) en mini-cartes HTML |
| **Coach's Note** | 2-3 phrases IA personnalisées |
| **Next Week Preview** | "Next week: 48km planned, including an interval session Wednesday" |
| **CTA** | Bouton `View Full Dashboard →` → lien `/dashboard` |
| **Footer** | Unsubscribe link, Privacy, © 2026 |

**Pas de data :** Si l'utilisateur n'a pas sync cette semaine, email adapté : "We missed you this week! Your Garmin hasn't synced. Reconnect to get your insights."

---

## ÉCRAN 11 : SIGNALS / DATA EXPLORER

### URL
`/explore` (libellé écran : **"Your Signals"**)

### Objectif
Donner accès à **toutes** les données riches (HRV, sleep, body battery, stress, VO2Max, resting HR, training status, SpO₂, respiration, weight…) **organisées par question, jamais en dump**. Accessible depuis le dashboard ("See all signals →") ou l'onglet More → Signals (mobile) / sidebar → Signals (desktop).

### Principe
Sous-titre : "Every metric, answered as a question · not a dump." Chaque bloc est une **carte-question** avec un graphique, des mini-stats, et **une interprétation du coach** ("Coach: …").

### Cartes-questions (MVP)
| Carte | Question | Contenu | Interprétation coach |
|-------|----------|---------|----------------------|
| **Fitness** | "How is my fitness trending?" | Courbe CTL/ATL/TSB + mini-stats CTL · VO₂max · Threshold | "Votre CTL a grimpé de 50 à 78 en 8 semaines…" |
| **Recovery** | "Am I recovering well?" | Sparklines HRV (7 nuits, bande baseline) · Resting HR (7j) · Sleep (7 nuits) | "Récup en bonne forme avec un point d'attention…" |
| **Training Load** | "What's my training load mix?" | Barre empilée easy/tempo/threshold + mini-stats Weekly TSS · Easy:Hard · Ramp | "Distribution polarisée 80/20…" |
| **Health** | "How is my health?" | Grille Stress · SpO₂ · Respiration · Weight (status dots) | "Rien ici ne demande votre attention — c'est exactement ce qu'on veut…" |

### États
- **Loading / Empty / Error :** mêmes primitives globales que les autres écrans.
- **Donnée manquante pour une carte :** masquer la carte ou afficher "Pas encore assez de données".

**Responsive :**
- **Mobile :** cartes-questions empilées en colonne unique.
- **Desktop (≥1024px) :** grille 2 colonnes de cartes-questions ; sparklines des signaux inline.

---

## ÉTATS GLOBAUX (tous écrans)

### Loading States
Chaque écran a un état de chargement :
- **Skeleton loader** (pas un spinner blanc) — des rectangles gris animés qui minent la structure
- Durée max avant timeout : 10 secondes → message d'erreur

### Empty States
Chaque écran a un état "pas de données" :
- Icône illustrative
- Texte expliquant pourquoi c'est vide
- CTA vers l'action suivante

### Error States
- **API down :** Bandeau rouge "We're having trouble connecting. Retrying in 10s..." + compteur
- **Auth expired :** Redirection vers `/login` avec message "Session expired. Please log in again."
- **404 :** Page standard "Page not found" + lien vers Dashboard
- **500 :** Page standard "Something went wrong" + bouton `Try Again` + lien `Contact Support`

### Responsive Behavior
**Le produit réel est une app téléphone d'abord.** Le mobile (375px, cadre 420px centré sur desktop) est la cible primaire ; le desktop est un vrai layout responsive, pas un simple élargissement.

- **Mobile (≤1023px) :** cadre 420px centré, top bar mince + **bottom nav 4 onglets** (Progress · Coach · Plan · More), colonne unique, grilles métriques 2×2, cibles tactiles ≥44×44px, régions denses en scroll horizontal (chips, tableaux). Padding bas réservé pour la bottom nav. Onglet "More" → bottom sheet (Activities · Signals · Settings · Pricing · Log out).
- **Tablet (768-1023px) :** mêmes règles mobile, grilles 2 colonnes.
- **Desktop (≥1024px) :** le cadre téléphone disparaît ; **sidebar fixe 240px** (remplace top + bottom nav) avec carte athlète ; grilles métriques 4-up restaurées ; layouts multi-colonnes spécifiques : Activity Detail (données gauche / coach sticky droite), Coach Chat (conversation + rail Athlete Context), Signals (grille 2 colonnes), Auth (panneau brand + formulaire).
- **Filet de sécurité overflow :** aucun scroll horizontal de 375px à 1440px ; les chaînes longues wrap, les tableaux gèrent leur propre scroll.

### Dark Mode
Pas dans le MVP. Light mode uniquement.

---

## MICRO-INTERACTIONS & ANIMATIONS

| Élément | Animation |
|---------|-----------|
| Transition page | Fade 200ms (pas de slide) |
| Bouton hover | Scale 1.02 + border-color transition 200ms |
| Carte métrique hover | Shadow légère augmentation |
| Accordéon FAQ | Expand/collapse 300ms ease |
| Toast notification | Slide-in depuis le haut-droite, 4s affichage, auto-dismiss |
| Skeleton loader | Pulse animation (opacity 0.3 → 0.6 → 0.3) |
| Connexion Garmin loading | Barre progression simulée + étapes textuelles |

---

## ACCESSIBILITÉ (MVP minimum)

- Tous les boutons ont un label accessible
- Images ont des alt text
- Contrast ratio ≥ 4.5:1 pour le texte
- Navigation au clavier fonctionnelle (Tab, Enter, Esc)
- Messages d'erreur liés aux champs par aria-describedby

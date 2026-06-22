# Project Brief: Garmin Coach

## Elevator Pitch
A web-based coaching platform that imports Garmin watch data, delivers deep actionable analytics, generates AI-powered adaptive training plans, and acts as a virtual coach — replacing Garmin Connect's cluttered UX and resented paywall with a focused, athlete-first experience.

## Problem

Garmin Connect suffers from well-documented UX and strategy failures that frustrate its ~50M+ user base:

**Evidence from real user complaints:**

1. **"Very unpolished for premium priced hardware"** — Reddit user after 7 years of Garmin use (r/Garmin, Aug 2025, 1,300+ upvotes): _"Garmin Software is very unpolished (trying to be polite here) for premium priced hardware. And now they would like you to pay a subscription fee."_

2. **Data-rich but insight-poor** — AskVora (2026): _"Garmin Connect shows great data but never tells you what to do with it. These alternatives add AI coaching, nutrition tracking, and adaptive training."_

3. **API lock-in and hostility to developers** — Hacker News (Feb 2025): _"Garmin is such a horrible company to try to integrate with. I don't know why they lock down their stuff so hard like this."_ The unofficial garminconnect Python library exists precisely because the official API is restrictive and poorly documented for individual developers.

4. **Connect+ paywall backlash** — May 2025: Garmin introduced Connect+ at $6.99/mo, locking features behind a subscription on devices users already paid $500–$1,000+ for. Forbes, TechRadar, and Vice all reported user outrage. CEO Cliff Pemble confirmed on Q1 2025 earnings that more features will be paywalled. One blogger wrote: _"Imagine your delight as you head on over to the reports section of the Garmin Connect app, only to discover that you have to pay to share this nonsense. I mean, you only spent $1,000 on a watch."_ (the5krunner, Dec 2025)

5. **Syncing and reliability issues** — Thematic analysis of user reviews (2023): _"the majority of issues cited by customers are centered around device/app syncing."_ iOS connectivity problems persist into 2026.

**Core pain point:** Garmin collects world-class sensor data but delivers it through an unfocused, increasingly paywalled interface that doesn't help athletes understand what to DO with their data.

## Solution

A web platform that:

1. **One-click Garmin import** — Uses Garmin's Health API + the unofficial garminconnect library as fallback to pull all activities, health metrics, sleep, HRV, training load, and performance data
2. **Deep analytics dashboard** — Training load (CTL/ATL/TSB), performance trends, recovery insights, sleep quality correlation with performance, workout effectiveness scoring
3. **AI-powered training plans** — Adaptive plans that adjust based on actual performance data, recovery status, and goal races. Not static PDFs — living plans that evolve
4. **Virtual coach** — LLM-powered conversational coach that explains your data, suggests workouts, answers training questions with context from YOUR actual data
5. **Multi-sport** — Running, cycling, swimming, triathlon (Garmin users are disproportionately multi-sport)

**Key differentiator:** Unlike competitors that are either analytics-only (Intervals.icu, Runalyze) or coaching-only (TrainerRoad, Runna), we combine deep analytics WITH AI coaching in one platform, Garmin-first but brand-agnostic.

## Target Audience

- **Primary:** Serious amateur athletes (run 3-6x/week, own a Garmin watch $200-$1000) who want to improve but can't afford a human coach ($150-400/mo)
- **Secondary:** Triathletes and multi-sport athletes underserved by single-sport platforms
- **Tertiary:** Human coaches who want a platform to manage clients with Garmin data integration
- **Demographics:** 25-55, tech-comfortable, health-conscious, willing to pay $8-15/mo for tools that improve their training
- **Market size:** ~50M Garmin Connect users globally; endurance sports app market projected at $8-12B by 2028

## Competition Landscape (Pulse Check)

| Competitor | Strengths | Weaknesses | Our Edge |
|------------|-----------|------------|----------|
| **Strava** | Massive network effects (100M+ users), social features, segments | Analytics locked behind $11.99/mo Summit; no real coaching; social-first, not training-first | Training-first, not social-first; AI coaching; Garmin-deep analytics |
| **Intervals.icu** | Free, deep TrainingPeaks-style analytics (CTL/ATL/TSB), multi-brand | Solo developer, sparse UI, no mobile app, no coaching features, no AI | Polished UX, AI coaching, mobile-friendly, monetization path |
| **TrainingPeaks** | Coach-athlete marketplace, structured workout builder, trusted by pros | Expensive ($19.95/mo), dated UX, no AI, primarily a coach tool not athlete tool | Athlete-first design, AI-generated plans, modern UX, lower price point |
| **Runna** | Strong AI coaching for running, good mobile UX, growing fast | Running-only, no cycling/swimming, limited analytics depth, no Garmin import priority | Multi-sport, deeper analytics, Garmin-first import, broader use case |
| **TrainerRoad** | Best-in-class adaptive training for cycling, AI-powered plan adaptation | Cycling-only (running is secondary), $19.95/mo, no manual analytics exploration | Multi-sport, exploration-friendly analytics, lower price, conversational AI coach |
| **Runalyze** | Deep metrics, open-source spirit, free tier | German-language roots, dated UI, no coaching, no AI, one-person project | Modern UX, AI coaching, commercial sustainability, mobile-friendly |
| **Garmin Connect** | Free with watch, deepest data access, built-in Garmin Coach (free plans) | Terrible UX, paywall coming, no real analytics guidance, "data-rich, insight-poor" | Best of our data + their hardware = superior experience |

## Differentiation Hypothesis

**"Garmin-first deep analytics + AI coaching, in one platform, with a UX athletes actually enjoy using."**

This is defensible because:
- **Garmin API moat:** We build deep Garmin integration expertise that competitors (Strava, TrainingPeaks) won't prioritize since they're brand-agnostic
- **Combined analytics + coaching:** No competitor does both well. Intervals.icu has analytics but no coaching. Runna has coaching but shallow analytics. We combine them.
- **AI moat:** LLM-powered conversational coach that reasons about YOUR data is a novel UX that incumbents with legacy architectures will struggle to match quickly
- **Paywall resentment window:** Garmin Connect+ anger creates a switching moment — athletes are actively looking for alternatives

**Riskiest assumption to validate:** Will users pay for a third-party platform when Garmin Connect is "free" (included with watch)? The Connect+ paywall may actually help us — it normalizes paying for analytics.

## Monetization Model

**Freemium tier:**
- Import Garmin data, basic dashboard, last 30 days of activities
- Free forever (growth engine, SEO-optimized)

**Pro tier ($9.99/mo or $89.99/year):**
- Full historical analytics, advanced metrics (CTL/ATL/TSB, HRV correlation, performance prediction)
- AI training plan generation (one active plan)
- Conversational AI coach (50 messages/month)

**Coach tier ($19.99/mo):**
- Unlimited AI coach messages
- Multiple training plans
- Multi-athlete dashboard (for human coaches managing clients)
- Priority feature requests

**Rationale:** Undercuts TrainingPeaks ($19.95) and TrainerRoad ($19.95) while offering more features. The free tier addresses the "why pay when Garmin is free" objection by proving value first.

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Garmin API breaks or is restricted** | High | Critical | Maintain unofficial library fallback; support manual FIT/TCX file upload; expand to COROS/Polar/Suunto/Apple import to reduce dependency |
| **Strava launches AI coaching** | Medium | High | Strava is social-first; their AI efforts (Athlete Intelligence, 2024) are shallow. Move fast, build training depth they can't replicate quickly |
| **Users won't pay for analytics** | Medium | Critical | Free tier proves value; Connect+ backlash normalizes paying; target marathoners/triathletes who already spend $200+/race — $10/mo is noise in their budget |
| **AI coaching quality is poor** | Medium | High | Fine-tune on training science literature; human-in-the-loop review of plan quality; start with rule-based plans + AI wrapper, graduate to full AI as quality improves |
| **Garmin improves Connect UX** | Low | Medium | Garmin's institutional DNA is hardware-first; culture change is slow. Even if they improve, our AI coaching + multi-brand support is a moat |
| **One-person/small team burnout** | Medium | High | Scope MVP ruthlessly (running only, Garmin only); open-source community contributions; plan for sustainable development pace |
| **GDPR/data privacy (France/EU base)** | Medium | High | Host in EU; data minimization; clear privacy policy; Garmin data is user-authorized via OAuth; no health data selling |

## Scoring

- **Feasibility:** 6/10 — Garmin API exists but is fragile; unofficial libraries help; analytics + AI coaching is complex but achievable with modern AI tools and existing open-source analytics libraries
- **Impact:** 8/10 — Real, documented pain across millions of users; solving "what do I DO with this data?" is high-value; athletes are high-intent users
- **Competition:** 5/10 — Crowded space (7+ significant competitors) but none combine deep analytics + AI coaching + Garmin-first UX in one product
- **Passion:** 8/10 — User is personally frustrated with Garmin Connect, motivated to build the alternative they wish existed

**Composite: 6.8/10** — A solid idea in a competitive but fragmented market. The combination of analytics + AI coaching + Garmin-first UX is genuinely differentiated. Main risks are API dependency and willingness-to-pay. Worth proceeding to full market analysis.

## Next Phase

**Recommendation: GO → ANALYZE**

Rationale: Score is above 6.0 threshold. Market is large and growing. Pain is real and documented. Differentiation is specific and testable. Key risks (API dependency, willingness-to-pay) need deeper validation in ANALYZE phase before building.

Open questions to resolve in ANALYZE:
- Exact market size for endurance sports coaching platforms
- Willingness-to-pay survey or comparable pricing data
- Garmin API terms of service review (is a commercial analytics platform allowed?)
- Keyword search volume for "Garmin Connect alternative" / "Garmin data analysis"

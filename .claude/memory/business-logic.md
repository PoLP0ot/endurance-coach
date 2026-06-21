# Business Logic

## Training Metrics (AnalyticsEngine — pure Python, deterministic)

### TSS (Training Stress Score)
- Formula: TSS = (duration_sec × NP × IF) / (FTP × 3600) × 100
- Simplified for running: TSS = duration_min × intensity_factor × 100 / 60
- Intensity factor based on HR zone: Z1=0.5, Z2=0.65, Z3=0.80, Z4=0.95, Z5=1.10

### CTL (Chronic Training Load — Fitness)
- Exponential moving average, 42-day time constant
- CTL_today = CTL_yesterday + (TSS_today - CTL_yesterday) / 42

### ATL (Acute Training Load — Fatigue)
- Exponential moving average, 7-day time constant
- ATL_today = ATL_yesterday + (TSS_today - ATL_yesterday) / 7

### TSB (Training Stress Balance — Form)
- TSB = CTL_yesterday - ATL_yesterday
- Positive = fresh, Negative = fatigued, -10 to -30 = optimal training zone

## Goal Types & Coaching Focus

| Goal | Primary Metrics | Plan Structure | Coach Focus |
|------|----------------|---------------|-------------|
| Marathon | TSS, Threshold Pace, VO2Max, CTL/ATL/TSB | 12-18 week periodized plan | Pace targets, race projection, load management |
| Weight Loss | Calorie Balance, Steps, Weight Trend, Active Minutes | Daily/Weekly targets | Energy deficit, consistency, nutrition |
| Hyrox | Compromised Running Pace, Strength Volume, Transition Speed | 8-12 week hybrid plan | Run+strength balance, fatigue management |
| Triathlon | Swim/Bike/Run TSS, Combined Load | 12-20 week multi-sport plan | Discipline balance, brick sessions |
| Health | Sleep Score, HRV, Resting HR, Steps | Weekly activity targets | Consistency, stress, recovery |

## Subscription Tiers

- **Free:** Dashboard, last 30 days, basic metrics
- **Premium ($8/mo):** Full history, AI chat unlimited, AI activity analysis, training plans, weekly email
- All enforced server-side via `require_premium` dependency

## GDPR Requirements
- Data residency: EU (Supabase eu-central-1)
- Explicit consent at Garmin connect
- Export: full JSON+CSV bundle
- Delete: cascade purge + audit log
- Right to be forgotten: 30-day response window

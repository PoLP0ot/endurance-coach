# Endurance Coach — Project Brief

## What
AI coaching platform for endurance athletes. Users connect their Garmin watch, and the AI coach analyzes their data to provide personalized coaching, adaptive training plans, and performance insights.

## Core Differentiator
COACH-FIRST, not data-first. Garmin Connect dumps raw data on screen. We translate data into actionable coaching: "Here's where you are relative to your goal, and here's what to do next."

## Target
Serious amateur endurance athletes (runners, triathletes) who own Garmin watches ($200-1000). Data-literate, performance-oriented, willing to pay $8-15/mo for tools that improve their training.

## Tech
Next.js 15 + FastAPI + Supabase. Python-garminconnect for Garmin import. Anthropic Claude for AI coaching. Paddle for payments.

## MVP Goals (2 weeks)
- Garmin data import
- Coach-first dashboard (goal-oriented, narrative, not data dump)
- AI activity analysis ("What This Run Means")
- Conversational coach chat
- Adaptive training plans with Push to Watch
- Conversational onboarding (coach discovers goal through dialogue)
- Modular goal architecture (marathon, weight loss, hyrox, triathlon, health)
- Mobile-first + desktop responsive

## Project Docs
Full specs, research, and QA checklist in Obsidian:
/opt/data/Obsidian/HermesSecondBrain/Projects/Garmin Coach/

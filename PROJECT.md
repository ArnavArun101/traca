# DerivTrader

## What This Is

An AI-powered trading analyst built for the Deriv hackathon that combines real-time market intelligence, behavioural trading coaching, and automated social media content generation. It serves both retail day traders and prop firm traders through a split-view web interface — dashboard panels alongside a unified conversational AI chat that handles market questions, behavioural feedback, and social content creation in one place.

## Core Value

Traders get instant, plain-language explanations of what's happening in the market and why — turning complex price action, news events, and technical patterns into actionable understanding.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Real-time market data ingestion via Deriv WebSocket API across all Deriv markets (forex, crypto, stocks, indices, commodities, synthetic indices)
- [ ] AI-powered price movement explanations in plain language ("Why did EUR/USD just spike?")
- [ ] Technical pattern identification with plain-language significance
- [ ] News and event summarisation for specific instruments
- [ ] Market sentiment analysis from multiple sources
- [ ] Personalised market briefs for followed instruments
- [ ] Behavioural pattern detection (emotional/impulsive trading signals)
- [ ] Timely nudges when behaviour suggests poor decision-making
- [ ] Win/loss pattern recognition from trade history
- [ ] Break/limit/reflection suggestions when appropriate
- [ ] Celebration of sustainable trading habits (not just profits)
- [ ] AI analyst personas that post market updates on LinkedIn and X
- [ ] Platform-appropriate content generation (professional for LinkedIn, concise for X)
- [ ] Complex analysis transformed into engaging shareable posts
- [ ] Daily/weekly market summaries and educational threads
- [ ] Consistent voice and personality across personas
- [ ] Content calendars with timely market commentary
- [ ] Split-view dashboard with panels + conversational chat
- [ ] Rich chat responses with inline charts, tables, and sentiment gauges
- [ ] Unified chat that handles market, behavioural, and social content queries
- [ ] Session-based chat memory within a session
- [ ] Auto-post routine social updates via LinkedIn/X APIs
- [ ] Draft mode for opinion pieces requiring human review
- [ ] Trade history analysis via Deriv API (user auth required)

### Out of Scope

- Persistent cross-session chat memory — session-based is sufficient for hackathon MVP
- Mobile native app — web-first, responsive if time allows
- Broker integrations beyond Deriv — this is a Deriv hackathon project
- Proprietary/paid LLMs (OpenAI, Anthropic) — using open source LLMs only
- Automated trade execution — this is an analyst, not a bot
- Real money trading signals with liability — educational/analytical only

## Context

- **Hackathon project** for Deriv — polished MVP is the deliverable
- **Deriv API** provides WebSocket-based real-time pricing and trade history data across all their markets including synthetic indices (Volatility indices, Crash/Boom, etc.)
- **Open source LLMs** (Llama, Mistral, etc.) power all analysis and content generation — keeps costs down and avoids API key dependencies
- **Public data sources** supplement Deriv API for news, sentiment, and supplementary market data
- **Both retail and prop firm traders** are target users, each with different needs (prop traders have rules/risk limits, retail traders need more guidance)
- Behavioural coaching requires access to user's trade history via Deriv API with user authentication/authorization

## Constraints

- **Tech Stack**: FastAPI (Python backend) + React (frontend) — Python is natural for ML/LLM work, React for rich interactive UI
- **Data Source**: Deriv WebSocket API for pricing and trade data — must handle real-time streaming
- **AI Models**: Open source LLMs only (Llama, Mistral, etc.) — no paid API dependencies
- **Timeline**: Hackathon timeline — MVP must demo well with polish
- **Social APIs**: LinkedIn and X API access required for auto-posting — rate limits and auth flows apply

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI + React | Python natural for LLM/ML work; React for rich interactive dashboard with charts | -- Pending |
| Open source LLMs over paid APIs | No API cost/key dependencies; full control; hackathon-appropriate | -- Pending |
| Deriv API as primary data source | Hackathon is by Deriv; covers all their markets including synthetics | -- Pending |
| Split-view dashboard + chat | Best of both worlds: at-a-glance overview plus conversational depth | -- Pending |
| Session-based chat memory | Simpler to implement; sufficient for hackathon demo | -- Pending |
| Both auto-post and draft modes for social | Routine updates auto-posted; opinion pieces get human review | -- Pending |
| Deriv API for trade history (not synthetic) | Real behavioural analysis requires real trade data; more compelling demo | -- Pending |

---
*Last updated: 2026-02-07 after initialization*

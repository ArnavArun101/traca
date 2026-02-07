# TODO — traca

Tracking completed and unfinished tasks across the project.
*Last updated: 2026-02-07 19:47*

---

## ✅ Completed

### Backend Scaffolding
- [x] FastAPI application setup (`backend/app/main.py`)
- [x] Health check endpoint (`GET /health`)
- [x] Database session & table creation (`backend/app/db/session.py`)
- [x] SQLModel schemas — `Trade` and `ChatHistory` models (`backend/app/models/db_models.py`)
- [x] Pydantic request/response schemas (`backend/app/models/schemas.py`)
- [x] WebSocket connection manager (`backend/app/core/websocket_manager.py`)
- [x] WebSocket endpoint for chat (`backend/app/api/websocket_endpoints.py`)
- [x] LLM engine service stub (`backend/app/services/llm_engine.py`)
- [x] Market data service with Deriv API integration (`backend/app/services/market_data.py`)
- [x] Behavioral analyzer service — position size deviation & rapid entry detection (`backend/app/services/behavioral_analyzer.py`)
- [x] Content generator service stub (`backend/app/services/content_generator.py`)
- [x] `requirements.txt` with dependencies

### Planning & Documentation
- [x] Project definition (`Planning/PROJECT.md`)
- [x] Feature landscape research (`Planning/FEATURES.md`)
- [x] Architecture design (`Planning/ARCHITECTURE.md`)
- [x] Tech stack decisions (`Planning/STACK.md`)
- [x] Pitfalls & anti-patterns (`Planning/PITFALLS.md`)
- [x] README (`README.md`)

### Frontend — Landing Page & Theme
- [x] Landing page with hero, features, stats, how-it-works, AI chat preview, CTA, and footer (`frontend/src/components/landing/LandingPage.tsx`)
- [x] Landing → Dashboard launch flow wired in `main.tsx`
- [x] Theme colour updated to teal `#006994` across CSS variables and hardcoded values

---

## 🔧 In Progress

### Backend — Core Services
- ✅ Wire LLM engine to an actual open-source model (Llama/Mistral)
- ✅ Flesh out content generator beyond stub
- ✅ Add trade history import from Deriv API
- ✅ Persist chat history to DB in WebSocket flow

### Backend — Behavioral Coaching
- ✅ Expand behavioral patterns beyond position-size & rapid-entry detection
- ✅ Discipline scoring system (% trades following user-defined rules)
- ✅ Real-time nudge delivery through WebSocket

---

## 📋 Not Started

### Frontend
- [x] React project setup
- [x] Split-view dashboard layout (panels + chat)
- [x] Chart visualization (candlestick chart component)
- [x] Landing page with product summary & CTA
- [x] Teal `#006994` brand theme applied to both pages
- [ ] Rich chat responses (Markdown, inline charts, tables, sentiment gauges)
- [ ] Responsive / mobile-friendly styling

### Market Analysis
- [x] Real-time price streaming via Deriv WebSocket API
- [x] Basic technical indicators (RSI, MACD, moving averages)
- [x] Price alerts & notifications
- [x] Historical data storage & retrieval
- [x] Multi-asset support (forex, crypto, synthetic indices)
- [x] Plain-language market explanations ("Why did EUR/USD spike?")
- [x] News & event summarisation per instrument

### Behavioral Coaching
- [ ] Cost-of-emotion analysis ("FOMO cost you $X this month")
- [ ] Win/loss pattern recognition from trade history
- [ ] Break / limit / reflection suggestions
- [ ] Celebration of sustainable trading habits & streaks
- [ ] Psychology tagging system (FOMO, REVENGE, HESITATION)

### Social Content & AI Personas
- [ ] AI analyst persona definition & prompt engineering
- [ ] Market update content generation (LinkedIn & X formats)
- [ ] Educational thread generation
- [ ] Daily/weekly market summary generation
- [ ] LinkedIn OAuth integration & posting
- [ ] X/Twitter OAuth integration & posting
- [ ] Post scheduling system
- [ ] Draft / approval workflow
- [ ] Content calendar
- [ ] Compliance & disclaimer filters

### Infrastructure & DevOps
- [ ] Authentication & authorization
- [ ] Environment configuration (.env, secrets management)
- [ ] Docker setup (backend + frontend)
- [ ] CI/CD pipeline
- [ ] Production deployment

### Advanced / Post-MVP
- [ ] Explainable AI (SHAP/LIME) with plain-language output
- [ ] Automated candlestick pattern recognition
- [ ] Sentiment analysis (NLP on news & social media)
- [ ] Multi-timeframe correlation
- [ ] Unusual activity / anomaly detection
- [ ] Chart image upload & analysis (multi-modal)
- [ ] Voice query support
- [ ] Multiple AI personas with distinct personalities
- [ ] Persona comment engagement
- [ ] Performance attribution per persona

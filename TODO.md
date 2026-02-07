# TODO — traca

Tracking completed and unfinished tasks across the project.
*Last updated: 2026-02-07*

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

### Backend — Core Services
- [x] Wire LLM engine to Mistral API (chat + social)
- [x] Flesh out content generator beyond stub
- [x] Add trade history import from Deriv API
- [x] Persist chat history to DB in WebSocket flow

### Backend — Behavioral Coaching
- [x] Expand behavioral patterns beyond position-size & rapid-entry detection
- [x] Discipline scoring system (% trades following user-defined rules)
- [x] Real-time nudge delivery through WebSocket

### Market Analysis
- [x] Real-time price streaming via Deriv WebSocket API
- [x] Basic technical indicators (RSI, MACD, moving averages)
- [x] Price alerts & notifications
- [x] Historical data storage & retrieval
- [x] Multi-asset support (forex, crypto, synthetic indices)
- [x] Plain-language market explanations ("Why did EUR/USD spike?")
- [x] News & event summarisation per instrument

### Planning & Documentation
- [x] Project definition (`Planning/PROJECT.md`)
- [x] Feature landscape research (`Planning/FEATURES.md`)
- [x] Architecture design (`Planning/ARCHITECTURE.md`)
- [x] Tech stack decisions (`Planning/STACK.md`)
- [x] Pitfalls & anti-patterns (`Planning/PITFALLS.md`)
- [x] README (`README.md`)

---

## 🔧 In Progress

### Social Content & AI Personas
- [x] Market update content generation (LinkedIn & X formats)
- [x] Compliance & disclaimer filters
- [ ] AI analyst persona definition & prompt engineering
- [ ] Educational thread generation
- [ ] Daily/weekly market summary generation
- [ ] Draft / approval workflow
- [ ] LinkedIn OAuth integration & posting
- [ ] X/Twitter OAuth integration & posting
- [ ] Post scheduling system
- [ ] Content calendar

---

## 📋 Not Started

### Frontend
- [ ] React project setup
- [ ] Split-view dashboard layout (panels + chat)
- [ ] Chart visualization (TradingView / Recharts)
- [ ] Rich chat responses (Markdown, inline charts, tables, sentiment gauges)
- [ ] Responsive / mobile-friendly styling

### Behavioral Coaching
- [ ] Cost-of-emotion analysis ("FOMO cost you $X this month")
- [ ] Win/loss pattern recognition from trade history
- [ ] Break / limit / reflection suggestions
- [ ] Celebration of sustainable trading habits & streaks
- [ ] Psychology tagging system (FOMO, REVENGE, HESITATION)

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

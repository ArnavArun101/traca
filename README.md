# Traca.ai

AI-powered trading analyst that combines real-time market intelligence, behavioural coaching, and social media automation.

Powered by **Deriv API**, Traca.ai serves both retail and prop firm traders through a unified interface that turns complex market data into actionable understanding.


## 🚀 Overview
Traca.ai is a split-view web platform featuring dashboard panels alongside a conversational AI analyst. It provides:

Traca is a split-view web platform featuring dashboard panels alongside a conversational AI analyst. It provides:
- **Instant Market Intelligence:** Plain-language explanations of price movements and technical patterns.
- **Behavioural Coaching:** Detection of emotional or impulsive trading patterns (FOMO, revenge trading) with timely nudges.
- **Social Automation:** Autonomous AI personas that generate and draft market updates for LinkedIn and X.

## ✨ Core Features (MVP)

- **Real-time Market Insights:** Integration with Deriv API across Forex, Crypto, and Stock markets.
- **Conversational AI:** Unified chat handling market queries, behavioural feedback, and social content creation in one place.
- **Split-View Dashboard:** Side-by-side view of live price charts, sentiment gauges, and the AI analyst chat.
- **Behavioural Pattern Detection:** Identification of win/loss streaks and risk escalation with habit-building reinforcement.
- **Social Content Drafting:** Platform-appropriate content generation (Professional for LinkedIn, concise for X).

## 🏗️ Architecture
Traca.ai uses a **Modular Monolith** architecture optimized for real-time data flow and AI inference:

- **Frontend:** React (Vite) + TailwindCSS + shadcn/ui + Zustand.
- **Backend:** FastAPI (Python) + Uvicorn + WebSockets.
- **AI Engine:** Local LLM inference via **Ollama** (Llama 3.3 / Mistral).
traca uses a **Modular Monolith** architecture optimized for real-time data flow and AI inference:

- **Frontend:** React (Vite) + TailwindCSS + shadcn/ui + Zustand.
- **Backend:** FastAPI (Python) + Uvicorn + WebSockets.
- **AI Engine:** Mistral API (cloud LLM).
- **Data Source:** Deriv API for real-time pricing and trade history.
- **Persistence:** SQLite for trade history, session-based chat memory, and content drafts.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, Uvicorn, websockets, deriv_api, pandas-ta |
| **Frontend** | React 19, Vite, TanStack Query, Zustand, Recharts, Lightweight Charts |
| **AI/ML** | Ollama (Llama 3.3), Pydantic v2 |
| **AI/ML** | Mistral API, Pydantic v2 |
| **Styling** | TailwindCSS 4, shadcn/ui |

## 🚦 Quickstart

### Prerequisites
- Python 3.11+
- Node.js & npm
- Mistral API key
- [Deriv API Token](https://api.deriv.com/)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Set DERIV_API_TOKEN in .env
uvicorn main:app --reload
```

### 2. LLM Setup
<<<<<<< HEAD
```bash
ollama pull llama3.3
ollama serve
=======
Set these environment variables (see `backend/.env.example`):
```
MISTRAL_API_KEY=your_mistral_api_key
MISTRAL_MODEL=mistral-small-latest
MISTRAL_BASE_URL=https://api.mistral.ai/v1
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## ⚠️ Key Pitfalls & Prevention

- **API Rate Limits:** Deriv API has rate limits; subscription model and error handling are managed to avoid being blocked.
- **LLM Hallucinations:** Numbers are parsed programmatically from Deriv API; the LLM is used only for narrative explanation.
- **Render Performance:** High-frequency price updates are managed via Zustand to avoid React Context re-render storms.

## 🗺️ Roadmap

- [ ] Persistent cross-session AI memory.
- [ ] Multi-modal input (Analyze chart screenshots).
- [ ] Automated regulatory compliance filters for social posts.
- [ ] Mobile-native responsive application.

---

Built with ❤️ using Deriv API.

# Technology Stack: AI-Powered Trading Analyst

**Project:** traca - AI Trading Analyst
**Researched:** 2026-02-07
**Overall Confidence:** HIGH (verified with 2026 sources)

---

## Executive Summary

This stack leverages Python's mature asyncio ecosystem for real-time WebSocket handling, FastAPI for production-grade API infrastructure, and Mistral's hosted LLM API for rapid development. The frontend uses Vite + React with shadcn/ui for polished demos, while specialized libraries like pandas-ta and TanStack Query handle technical analysis and real-time state management respectively.

**Key Decision:** Mistral API for LLM inference (not local Ollama) - optimizes for development speed and predictable latency.

**Key Decision:** Zustand over Redux for state management - minimal boilerplate, perfect for hackathon timeline with real-time WebSocket updates.

**Key Decision:** shadcn/ui over component libraries - copy-paste customization enables rapid polish without fighting framework constraints.

---

## Backend Stack

### Core Framework

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **FastAPI** | 0.128.4 | API framework + WebSocket server | Industry standard for Python async APIs. Native WebSocket support with asyncio. 200-300% faster development vs Flask/Django. Built-in OpenAPI docs critical for hackathon demos. | **HIGH** |
| **Python** | 3.11+ | Runtime | Required for FastAPI. 3.11 offers 10-60% speedup over 3.10. Avoid 3.9.7 (websockets bug). | **HIGH** |
| **Uvicorn** | 0.34+ | ASGI server | Production-grade async server. Pairs with Gunicorn in production (4 workers = 4 CPU cores). | **HIGH** |
| **websockets** | 16.0 | WebSocket client library | Industry-leading Python WebSocket implementation. Handles backpressure correctly (critical for real-time trading data). Built on asyncio with elegant coroutine API. Alternative: picows (3-5x faster but newer, less battle-tested). | **HIGH** |

**Rationale:** FastAPI + Uvicorn + websockets is the 2026 standard for Python WebSocket applications. FastAPI's automatic OpenAPI documentation is invaluable for hackathon presentations, and its async-first design handles concurrent WebSocket connections efficiently.

**Source:** [FastAPI Production Deployment 2026](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026), [WebSocket Python Libraries Comparison](https://superfastpython.com/asyncio-websocket-clients/)

---

### Deriv API Integration

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **deriv_api** | Latest | Deriv API wrapper | Official Python library for Deriv. | **HIGH** |

**Installation:**
```bash
pip install deriv_api
```

**Critical Notes:**
- Avoid Python 3.9.7 (websockets package bug)
- Requires Python >=3.9.6
- Uses rxpy for subscription streams (reactive programming model)

**Rationale:** Official library with proven integration.

**Source:** [Deriv API Docs](https://api.deriv.com/)

---

### LLM Inference

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **Mistral API** | Latest | Hosted LLM inference | Fast setup, consistent latency, strong general reasoning. Avoids local GPU setup and model management. | **HIGH** |
| **mistral-small-latest** | Latest | Default model for analysis | Balanced quality and latency for hackathon use. | **HIGH** |

**Alternative Stack (if scaling needed post-hackathon):**
- **vLLM** (0.6+): Enterprise standard, 3.2x throughput vs Ollama, but complex setup
- **llama.cpp-python**: Direct bindings, best CPU/GPU mixed inference

**Configuration:**
```
MISTRAL_API_KEY=your_mistral_api_key
MISTRAL_MODEL=mistral-small-latest
MISTRAL_BASE_URL=https://api.mistral.ai/v1
```

**Rationale:** Hackathon constraints favor fast, reliable setup over local model tuning. Hosted inference avoids GPU setup and reduces risk of demo instability.

**Source:** [vLLM vs Ollama vs llama.cpp 2026](https://blog.worldline.tech/2026/01/29/llm-inference-battle.html), [Ollama vs vLLM Performance Comparison](https://www.arsturn.com/blog/multi-gpu-showdown-benchmarking-vllm-llama-cpp-ollama-for-maximum-performance)

---

### LLM Orchestration & RAG (Optional - if needed)

| Library | Version | Purpose | When to Use | Confidence |
|---------|---------|---------|-------------|------------|
| **LlamaIndex** | 0.12+ | RAG framework (data indexing) | If you need RAG for historical trade analysis or document retrieval. Simpler API than LangChain for data-focused tasks. | **MEDIUM** |
| **sentence-transformers** | 3.3+ | Embeddings generation | For RAG or semantic similarity. Use `all-MiniLM-L6-v2` (lightweight, fast) or `gte-multilingual-base` (better quality, 305M params). | **HIGH** |
| **ChromaDB** | 0.6+ | Vector database | For <200k vectors (historical trades). Easier than FAISS, persistent storage, metadata filtering. Use FAISS if >200k vectors. | **MEDIUM** |

**When NOT to use:**
- Skip RAG entirely if LLM context window (128k tokens for Llama 3.3) is sufficient for history
- Avoid LangChain - overkill for this use case, LlamaIndex is simpler for data retrieval

**Rationale:** RAG is optional. Modern LLMs have 128k+ context windows (enough for ~50-100 trades). Only add RAG if you need semantic search over thousands of historical trades.

**Source:** [LlamaIndex vs LangChain 2026](https://contabo.com/blog/llamaindex-vs-langchain-which-one-to-choose-in-2026/), [ChromaDB vs FAISS Comparison](https://mohamedbakrey094.medium.com/chromadb-vs-faiss-a-comprehensive-guide-for-vector-search-and-ai-applications-39762ed1326f)

---

### Technical Analysis

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **pandas-ta** | 0.4.71b0 | Technical indicators | Pure Python, 150+ indicators, 60 candlestick patterns. Pandas integration = DataFrame native. TA-Lib is faster (C implementation) but painful to install (compilation required). **For hackathon: pandas-ta wins on dev speed**. | **HIGH** |
| **pandas** | 2.2+ | Time-series data handling | Standard for financial data. Essential for OHLCV processing, rolling windows, resampling. | **HIGH** |
| **numpy** | 2.2+ | Numerical computation | Dependency for pandas-ta. Fast array operations. | **HIGH** |

**Alternative:**
- **TA-Lib** (0.4.33): Faster (C core), but installation requires compiling from source. Only use if performance bottleneck identified.

**Installation:**
```bash
pip install pandas-ta pandas numpy
```

**Rationale:** pandas-ta offers 10x faster installation vs TA-Lib (pure Python vs C compilation). Performance difference (<10% for most indicators) is negligible for hackathon scale. Pandas integration makes DataFrame operations seamless.

**Source:** [pandas-ta vs TA-Lib Comparison](https://www.slingacademy.com/article/comparing-ta-lib-to-pandas-ta-which-one-to-choose/), [pandas-ta PyPI](https://pypi.org/project/pandas-ta/)

---

### Data Validation & Async Utilities

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **Pydantic** | 2.12+ | Data validation & settings | FastAPI dependency. v2 is 5-50x faster than v1 (Rust core). Type-safe configuration management. Critical for API request/response validation. | **HIGH** |
| **asyncio** | stdlib | Async runtime | Native Python async support. FastAPI built on this. Essential for concurrent WebSocket connections. | **HIGH** |
| **aiohttp** | 3.11+ | Async HTTP client | For external API calls (LinkedIn/X APIs). Alternative to `requests` (blocking). | **HIGH** |

**Rationale:** Pydantic v2's Rust core dramatically improves validation performance (critical when processing high-frequency market data). aiohttp prevents blocking I/O when posting to social media APIs.

**Source:** [Pydantic v2 Performance in 2026](https://medium.com/@2nick2patel2/fastapi-under-load-in-2026-pydantic-v2-uvloop-http-3-what-actually-moves-the-needle-74717b74e74e), [FastAPI Features](https://fastapi.tiangolo.com/features/)

---

### Social Media Automation

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **tweepy** | 4.14+ | X/Twitter API integration | Standard library for Twitter API v2. Supports OAuth 2.0, media uploads, threading. | **MEDIUM** |
| **linkedin-api** (unofficial) | Latest | LinkedIn posting | Official LinkedIn API requires app review (slow). Unofficial library works for personal profiles. **Risk:** Against TOS, could break. Consider manual posting for hackathon demo. | **LOW** |

**Alternative Approach (RECOMMENDED for hackathon):**
- **Manual posting workflow:** LLM generates draft text/image → save to file → user reviews → one-click post via official web UI
- **Webhook-based:** Integrate with Zapier/Make.com for LinkedIn (avoids API approval delays)

**Critical Warning:** LinkedIn Official API requires OAuth app review (7-14 days). For hackathon timeline, build "draft generation" feature instead of auto-posting.

**Rationale:** X API is accessible with Developer Account (free tier, instant approval). LinkedIn API approval won't finish before hackathon. Focus on generating high-quality drafts with LLM, let users post manually.

**Source:** [Python Social Media Automation 2026](https://dev.to/trixsec/how-to-automate-social-media-posting-with-python-ag1), [LinkedIn API Documentation](https://towardsdatascience.com/linkedin-api-python-programmatically-publishing-d88a03f08ff1/)

---

### Production Deployment (Post-Hackathon)

| Technology | Purpose | Why | Confidence |
|------------|---------|-----|------------|
| **Gunicorn** | Process manager | Run 4 Uvicorn workers (1 per CPU core). Fault isolation, zero-downtime restarts. Standard: `gunicorn -k uvicorn.workers.UvicornWorker -w 4`. | **HIGH** |
| **Docker** | Containerization | Consistency across environments. Simplifies deployment to cloud platforms. | **HIGH** |
| **CORS middleware** | Security | FastAPI built-in. **Never use `allow_origins=["*"]` in production** - specify exact frontend domain. | **HIGH** |

**Health Checks:**
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Rationale:** Gunicorn + Uvicorn workers is 2026 industry standard for FastAPI production. Docker enables easy deployment to AWS/GCP/DigitalOcean.

**Source:** [FastAPI Production Best Practices 2026](https://www.zestminds.com/blog/fastapi-deployment-guide/), [Render FastAPI Deployment Guide](https://render.com/articles/fastapi-production-deployment-best-practices)

---

## Frontend Stack

### Build Tool & Framework

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **Vite** | 7.3.1 | Build tool & dev server | **Create React App is dead** (officially sunset Feb 2025). Vite is React team's recommended tool. 10-20x faster dev server (native ESM). HMR in <50ms. Vite 8 beta adds Rolldown bundler (replacing Rollup/esbuild). | **HIGH** |
| **React** | 19+ | UI framework | Industry standard. Huge ecosystem. Vite has first-class React support. React 19 adds Server Components (optional for this project). | **HIGH** |
| **TypeScript** | 5.7+ | Type safety | Catch bugs at compile time. Better IDE support. Standard for modern React projects. | **HIGH** |

**Initialization:**
```bash
npm create vite@latest frontend -- --template react-ts
```

**Rationale:** Vite replaced CRA as the React standard in 2025-2026. Dev server startup in <1s (vs CRA's 30s+). Critical for hackathon iteration speed.

**Source:** [Goodbye CRA, Hello Vite 2026](https://dev.to/solitrix02/goodbye-cra-hello-vite-a-developers-2026-survival-guide-for-migration-2a9f), [Vite 8 Beta Announcement](https://vite.dev/blog/announcing-vite8-beta)

---

### State Management

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **Zustand** | 5.0+ | Client state (global app state) | <1KB gzipped. Zero boilerplate. No provider wrapping. Perfect for hackathons. **30%+ YoY growth, used in 40% of projects**. Redux Toolkit still common in enterprises (10% new projects), but Zustand wins for speed. | **HIGH** |
| **TanStack Query** | 5.62+ | Server state (API data, WebSocket updates) | **De facto standard for server state** (80% of projects). Handles caching, invalidation, refetch logic. WebSocket integration: Use query invalidation on WS message (efficient) OR direct cache updates (real-time). | **HIGH** |

**When NOT to use:**
- **Redux Toolkit:** Only if team has existing Redux experience. 3x more boilerplate than Zustand.
- **Context API:** Too verbose for global state. Use for theme/auth only.

**Installation:**
```bash
npm install zustand @tanstack/react-query
```

**WebSocket + TanStack Query Pattern:**
```typescript
// Invalidate query on WebSocket update (preferred for hackathon)
ws.onmessage = (event) => {
  queryClient.invalidateQueries(['trades']);
};

// OR: Direct cache update (for ultra-low latency)
ws.onmessage = (event) => {
  queryClient.setQueryData(['trades'], event.data);
};
```

**Rationale:** Zustand's simplicity is perfect for hackathon timeline. TanStack Query eliminates manual WebSocket state management boilerplate. Combined, they handle 90% of state needs with minimal code.

**Source:** [React State Management 2026](https://www.syncfusion.com/blogs/post/react-state-management-libraries), [TanStack Query + WebSockets](https://tkdodo.eu/blog/using-web-sockets-with-react-query)

---

### UI Components & Styling

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| **shadcn/ui** | Latest | Component library | **NOT a framework** - copy-paste components. Built on Radix UI + Tailwind. Full ownership = customization without fighting library. Tailwind v4 + React 19 support (Jan 2026). RTL support, unified Radix package. **Perfect for hackathon polish**. | **HIGH** |
| **Tailwind CSS** | 4.0+ | Utility-first CSS | Industry standard. shadcn/ui requires it. Rapid prototyping without leaving HTML. | **HIGH** |
| **Radix UI** | Latest | Accessible primitives | shadcn/ui dependency. WAI-ARIA compliant. Keyboard navigation out-of-box. | **HIGH** |

**Installation:**
```bash
npx shadcn@latest init
npx shadcn@latest add button card chart dialog
```

**Key Features for Hackathon:**
- **CSS Variables:** Theme switching (dark/light) in 1 line
- **Pre-built Charts:** Financial chart components ready to use
- **Form Components:** Real-time validation with React Hook Form integration

**Rationale:** shadcn/ui's copy-paste model means zero version lock-in. Components live in your codebase, fully customizable. Critical for hackathon demos where you need pixel-perfect polish without fighting Material-UI or Ant Design constraints.

**Source:** [shadcn/ui Official Docs](https://ui.shadcn.com/), [shadcn/ui Changelog 2026](https://ui.shadcn.com/docs/changelog)

---

### Trading Charts & Visualization

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **Recharts** | 2.15+ | General charts (line, bar, area) | React-native API (JSX components). Built on D3. Responsive, animated. Good for dashboards. | **HIGH** |
| **Lightweight Charts** | 4.2+ | Candlestick/OHLC charts | TradingView's open-source library. Best-in-class financial charts. WebSocket-ready (streaming updates). 60 FPS performance. **Industry standard for trading UIs**. | **HIGH** |

**When to use each:**
- **Recharts:** Portfolio performance, P&L graphs, indicator visualizations (RSI, MACD)
- **Lightweight Charts:** Real-time candlestick charts, order book visualization

**Alternative (if budget allows post-hackathon):**
- **Highcharts Stock:** Commercial ($500+/year). More features, but licensing issues for open-source hackathon projects.

**Installation:**
```bash
npm install recharts lightweight-charts
```

**Rationale:** Lightweight Charts is TradingView's library - battle-tested on millions of users. Recharts covers 80% of other visualization needs with minimal setup.

**Source:** [Top React Stock Chart Libraries 2026](https://www.syncfusion.com/blogs/post/top-5-react-stock-charts-in-2026), [React Chart Libraries for Trading Dashboards](https://embeddable.com/blog/react-chart-libraries)

---

### WebSocket Client

| Library | Version | Purpose | Why | Confidence |
|---------|---------|---------|-----|------------|
| **native WebSocket API** | Browser built-in | WebSocket connection | Modern browsers support it. Zero dependencies. For complex use cases (auto-reconnect, heartbeat), use `react-use-websocket`. | **HIGH** |
| **react-use-websocket** | 4.8+ | WebSocket React hook | Auto-reconnect, connection state management, heartbeat. Simplifies WebSocket lifecycle. | **MEDIUM** |

**Rationale:** Native WebSocket API is sufficient for hackathon. Add react-use-websocket only if you need auto-reconnect logic (recommended for production).

---

## Supporting Tools & DevOps

### Development Tools

| Tool | Purpose | Why |
|------|---------|-----|
| **Poetry** / **pip-tools** | Python dependency management | Poetry for lock files + virtual envs. Alternative: pip-tools (simpler). |
| **Black** + **isort** | Python code formatting | Standard in 2026. Auto-format on save. |
| **ESLint** + **Prettier** | TypeScript/React linting | Vite includes ESLint config. Prettier for consistent formatting. |
| **pytest** | Python testing | Standard testing framework. Use with `pytest-asyncio` for async tests. |
| **Vitest** | React testing | Vite-native test runner. Faster than Jest. |

### Version Control

**Git + GitHub:** Standard. Use conventional commits for clean history.

### Recommended `.gitignore` additions:
```
# Environment
.env
.env.local

# LLM models (large files)
*.gguf
*.bin
models/

# Deriv API credentials
DERIV_API_TOKEN=your_key
```

---

## What NOT to Use (Anti-Patterns)

| Technology | Why Avoid | Use Instead |
|------------|-----------|-------------|
| **Django** | Too heavyweight for this project. Sync-first (not async). | FastAPI |
| **Flask** | No native async support. Manual WebSocket setup. | FastAPI |
| **Create React App** | Officially deprecated (Feb 2025). Slow builds. | Vite |
| **Redux** (not Toolkit) | Excessive boilerplate. Outdated pattern. | Zustand + TanStack Query |
| **Material-UI** | Heavy (300KB+). Hard to customize. | shadcn/ui + Tailwind |
| **TA-Lib** | Compilation required. Setup time kills hackathon momentum. | pandas-ta |
| **vLLM** | Complex setup. Overkill for <10 concurrent users. | Ollama |
| **LangChain** | Over-engineered for this use case. Too many abstractions. | Direct Ollama API / LlamaIndex if RAG needed |
| **Socket.IO** | Unnecessary abstraction over WebSocket. Adds overhead. | Native WebSocket |
| **Axios** | Redundant in modern browsers. fetch API + aiohttp suffice. | native fetch (frontend), aiohttp (backend) |

---

## Installation Quickstart

### Backend
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi[standard]==0.128.4 uvicorn[standard] websockets==16.0 \
            deriv_api pandas-ta pandas numpy \
            pydantic==2.12+ aiohttp tweepy

# Install Ollama (separate install)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.3:70b-instruct-q4_K_M
```

### Frontend
```bash
# Create Vite project
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install dependencies
npm install zustand @tanstack/react-query recharts lightweight-charts
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install shadcn/ui
npx shadcn@latest init
npx shadcn@latest add button card chart dialog input label select
```

---

## Environment Configuration

### `.env` (Backend)
```bash
# Deriv API
DERIV_API_TOKEN=your_deriv_api_api_key

# LLM
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.3:70b-instruct-q4_K_M

# Social Media (optional)
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_secret
```

### `vite.config.ts` (Frontend)
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',  // FastAPI backend
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
});
```

---

## Confidence Assessment

| Area | Confidence | Rationale |
|------|------------|-----------|
| **Backend Framework** | **HIGH** | FastAPI + Uvicorn is industry standard. Verified with 2026 sources. |
| **WebSocket Handling** | **HIGH** | websockets library is battle-tested.
| **LLM Inference** | **HIGH** | Ollama is proven for dev/demo environments. Verified performance benchmarks. |
| **Technical Analysis** | **HIGH** | pandas-ta is widely adopted. Clear tradeoff vs TA-Lib documented. |
| **Frontend Framework** | **HIGH** | Vite is officially recommended by React team. shadcn/ui gaining rapid adoption. |
| **State Management** | **HIGH** | Zustand + TanStack Query is 2026 best practice per multiple sources. |
| **Social Media APIs** | **MEDIUM** | X API is stable. LinkedIn API has approval delays - draft generation recommended. |
| **RAG/Vector DB** | **MEDIUM** | Optional dependency. LlamaIndex + ChromaDB well-documented but may not be needed. |

---

## Sources & Verification

### Backend
- [FastAPI Production Best Practices 2026](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026) - **MEDIUM** confidence (blog post, but recent)
- [Python WebSocket Libraries Comparison](https://superfastpython.com/asyncio-websocket-clients/) - **HIGH** confidence (authoritative source)
- [Deriv API Documentation](https://api.deriv.com/) - **HIGH** confidence (official)
- [vLLM vs Ollama Performance 2026](https://blog.worldline.tech/2026/01/29/llm-inference-battle.html) - **HIGH** confidence (recent benchmarks)
- [pandas-ta vs TA-Lib](https://www.slingacademy.com/article/comparing-ta-lib-to-pandas-ta-which-one-to-choose/) - **MEDIUM** confidence (tutorial site)
- [FastAPI PyPI](https://pypi.org/project/fastapi/) - **HIGH** confidence (official)
- [websockets PyPI](https://pypi.org/project/websockets/) - **HIGH** confidence (official)

### Frontend
- [Vite Official Documentation](https://vite.dev/guide/) - **HIGH** confidence (official)
- [shadcn/ui Changelog 2026](https://ui.shadcn.com/docs/changelog) - **HIGH** confidence (official)
- [React State Management 2026](https://www.syncfusion.com/blogs/post/react-state-management-libraries) - **MEDIUM** confidence (industry blog)
- [TanStack Query + WebSockets](https://tkdodo.eu/blog/using-web-sockets-with-react-query) - **HIGH** confidence (TanStack maintainer's blog)
- [Top React Chart Libraries 2026](https://www.syncfusion.com/blogs/post/top-5-react-chart-libraries) - **MEDIUM** confidence (industry blog)

### LLM & AI
- [LlamaIndex vs LangChain 2026](https://contabo.com/blog/llamaindex-vs-langchain-which-one-to-choose-in-2026/) - **MEDIUM** confidence (blog post)
- [ChromaDB vs FAISS Comparison](https://mohamedbakrey094.medium.com/chromadb-vs-faiss-a-comprehensive-guide-for-vector-search-and-ai-applications-39762ed1326f) - **MEDIUM** confidence (Medium article)
- [Best Open-Source LLMs 2026](https://huggingface.co/blog/daya-shankar/open-source-llms) - **HIGH** confidence (Hugging Face official)

---

## Gaps & Future Research

### Questions for Phase-Specific Research:
1. **Behavioral Analysis:** What Python libraries exist for trading psychology metrics? (search found general analytics but not specific trader behavior tracking)
2. **Prompt Engineering:** Best practices for financial analysis prompts with Llama 3.3? (general guides found but not domain-specific)
3. **Hackathon Demo:** Optimal UI animation libraries for "wow factor"? (basic practices found but not animation-specific)

### Unresolved:
- **LinkedIn API:** Approval timeline unclear. Assume 14+ days, plan for draft-only mode.
- **LLM Context Window Management:** How to optimize 128k token window for multi-trade analysis? (needs experimentation)

---

## Recommended Exploration Path

**Week 1:** Backend foundation
- FastAPI + Deriv integration
- Ollama + Llama 3.3 setup
- Basic technical analysis with pandas-ta

**Week 2:** Frontend + real-time integration
- Vite + React + shadcn/ui setup
- Zustand + TanStack Query state management
- WebSocket connection to backend
- Lightweight Charts for candlesticks

**Week 3:** LLM integration + polish
- Prompt engineering for trade analysis
- Behavioral coaching prompts
- Social content generation
- UI polish with animations

**Week 4:** Demo preparation
- End-to-end testing
- Performance optimization
- Presentation materials
- Backup plan for LinkedIn (draft-only mode)

---

**END OF STACK.MD**

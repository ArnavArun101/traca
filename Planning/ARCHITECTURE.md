# Architecture Patterns: AI-Powered Trading Analyst

**Domain:** AI-powered trading analyst with behavioral coaching and social content generation
**Researched:** 2026-02-07
**Overall Confidence:** HIGH

## Executive Summary

An AI-powered trading analyst combining real-time market data, LLM analysis, behavioral insights, and social publishing requires a **modular monolith architecture** with clear internal boundaries and async communication patterns. The system should be architected around three primary data flows: (1) real-time market data ingestion and distribution, (2) LLM-powered analysis and chat, and (3) content generation and social publishing.

For a hackathon context, this architecture prioritizes **demo-ability** while maintaining clean separation of concerns. The FastAPI backend acts as a central orchestrator managing WebSocket connections, LLM inference, and data persistence, while the React frontend provides dual interfaces (dashboard + chat) with real-time updates via WebSocket subscriptions.

## Recommended Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────┐
│                         REACT FRONTEND                          │
│  ┌──────────────────────┐    ┌──────────────────────────────┐  │
│  │  Dashboard View      │    │  Chat Interface              │  │
│  │  - Live price charts │    │  - Conversational UI         │  │
│  │  - Trade history     │    │  - Rich responses (charts,   │  │
│  │  - Sentiment gauges  │    │    tables, sentiment)        │  │
│  │  - Performance stats │    │  - Session-based context     │  │
│  └──────────────────────┘    └──────────────────────────────┘  │
│              │                            │                      │
│              └────────────┬───────────────┘                      │
│                           │ WebSocket                            │
└───────────────────────────┼──────────────────────────────────────┘
                            │
┌───────────────────────────┼──────────────────────────────────────┐
│                    FASTAPI BACKEND                               │
│                           │                                      │
│  ┌────────────────────────┴──────────────────────────────────┐  │
│  │         WebSocket Connection Manager                      │  │
│  │  - Client connection pooling                              │  │
│  │  - Message routing & broadcasting                         │  │
│  │  - Session state management                               │  │
│  └────────────┬──────────────┬───────────────┬───────────────┘  │
│               │              │               │                  │
│  ┌────────────┴─────┐  ┌────┴──────┐  ┌────┴─────────────┐    │
│  │  Market Data     │  │   LLM      │  │   Behavioral     │    │
│  │  Processor       │  │   Engine   │  │   Analyzer       │    │
│  │  - Deriv API     │  │  - Llama/  │  │  - Pattern       │    │
│  │    client        │  │    Mistral │  │    detection     │    │
│  │  - Price stream  │  │  - Context │  │  - Trade history │    │
│  │  - Trade events  │  │    memory  │  │    analysis      │    │
│  │  - Data buffer   │  │  - Prompt  │  │  - Bias scoring  │    │
│  │                  │  │    engine  │  └──────────────────┘    │
│  └──────────────────┘  └────────────┘                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Content Generation & Publishing                │  │
│  │  - Social content creator (LLM-powered)                  │  │
│  │  - Multi-platform publisher (LinkedIn/X)                 │  │
│  │  - Draft mode & approval queue                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────┴──────────────────────────────────┐ │
│  │              Data Persistence Layer                       │ │
│  │  - Chat history (session-based)                           │ │
│  │  - Trade history cache                                    │ │
│  │  - User preferences                                       │ │
│  │  - Content drafts                                         │ │
│  └───────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────┬────────────────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        │          Deriv API          │
                        │  - Real-time quote data     │
                        │  - Intraday trade history   │
                        │  - Global market coverage   │
                        └─────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With | Data Flow Direction |
|-----------|---------------|-------------------|---------------------|
| **WebSocket Connection Manager** | Manages all client connections, routes messages, maintains session state | All backend components → Frontend | Bidirectional |
| **Market Data Processor** | Connects to Deriv API, fetches price data, buffers trade history | WS Manager, Behavioral Analyzer, Data Persistence | External → Internal |
| **LLM Engine** | Runs local LLM inference (Llama/Mistral), manages conversation context, generates responses | WS Manager, Behavioral Analyzer, Content Generator | Request/Response |
| **Behavioral Analyzer** | Detects trading patterns, identifies biases, calculates sentiment scores | Market Data Processor, LLM Engine, WS Manager | Async processing |
| **Content Generator** | Creates social media posts, manages approval workflow, publishes to platforms | LLM Engine, WS Manager, External APIs | Request → External |
| **Data Persistence** | Stores chat history, trade cache, user preferences, content drafts | All backend components | Internal storage |
| **React Dashboard** | Displays real-time charts, metrics, trade history, sentiment gauges | WS Manager (subscribe) | Receive-only |
| **React Chat Interface** | Conversational UI, rich response rendering, session continuity | WS Manager (bidirectional) | Bidirectional |

### Clear Separation Principles

1. **Frontend-Backend Boundary**: All communication via WebSocket. No direct API calls to external services from frontend.
2. **Data Source Isolation**: Only Market Data Processor connects to Deriv API. Other components consume processed data.
3. **LLM Isolation**: LLM Engine is the single point for all model inference. Prevents scattered model loading.
4. **State Management**: WebSocket Connection Manager owns session state. No distributed state.
5. **External Service Abstraction**: Social publishing isolated in Content Generator. Easy to mock for demos.

## Data Flow Patterns

### Flow 1: Real-Time Market Data

```
Deriv API → Market Data Processor → WebSocket Manager → React Dashboard
                    ↓
            Behavioral Analyzer (async)
                    ↓
            Data Persistence (buffered writes)
```

**Key Points:**
- Market data flows **unidirectionally** from external source to frontend
- Behavioral analysis happens **asynchronously** to avoid blocking real-time updates
- Data persistence uses **buffered writes** to prevent I/O from slowing the pipeline
- WebSocket Manager **broadcasts** price updates to all connected clients

### Flow 2: Chat Interaction with LLM

```
User → React Chat → WebSocket Manager → LLM Engine
                                           ↓
                                   Context Retrieval
                                   (chat history +
                                    market data +
                                    behavioral insights)
                                           ↓
                                   LLM Inference
                                           ↓
                    WebSocket Manager ← Response
                            ↓
                      React Chat
                     (render rich
                      response)
                            ↓
                    Data Persistence
                    (save to session)
```

**Key Points:**
- Chat messages maintain **session context** via session ID in WebSocket connection
- LLM Engine aggregates **multi-source context**: chat history, current market data, behavioral analysis
- Responses are **streamed** token-by-token for better UX (optional enhancement)
- Rich responses include **structured data** (JSON with type: 'chart', 'table', 'sentiment')
- Session history persists **incrementally** after each exchange

### Flow 3: Social Content Generation & Publishing

```
Trigger (user/auto) → Content Generator → LLM Engine
                                            ↓
                                    Generate post content
                                            ↓
                        Content Generator ← Draft
                                ↓
                        ┌───────┴────────┐
                        │                │
                   Auto-post       Draft Mode
                        │                │
                        │         User approval
                        │                │
                        └───────┬────────┘
                                ↓
                    Social Media APIs
                    (LinkedIn/X)
                                ↓
                        WebSocket Manager
                        (notify frontend)
```

**Key Points:**
- Content generation is **request-based**, not real-time streaming
- **Draft mode** allows user review before publishing (crucial for demo safety)
- Publishing is **async** - frontend receives confirmation via WebSocket
- Failed posts **queue for retry** with exponential backoff
- All content saved to persistence layer for audit trail

### Flow 4: Behavioral Analysis Pipeline

```
Market Data Processor → Behavioral Analyzer
        ↓                       ↓
   Trade events         Pattern detection
                        (moving window)
                               ↓
                    Bias identification
                    (loss aversion,
                     overconfidence,
                     recency bias)
                               ↓
                    Sentiment scoring
                               ↓
                    ┌──────────┴──────────┐
                    ↓                     ↓
            WebSocket Manager      LLM Engine
            (real-time gauge       (context for
             updates)               coaching)
```

**Key Points:**
- Analysis runs on **sliding windows** (e.g., last 20 trades, last 24 hours)
- Pattern detection uses **rule-based + ML hybrid** approach for hackathon speed
- Results broadcast to dashboard **every N seconds** (throttled updates)
- Analysis results **enrich LLM context** for personalized coaching
- Behavioral scores stored in **time-series format** for trend visualization

## Technology Stack Integration

### Backend Stack

| Technology | Version | Purpose | Integration Point |
|------------|---------|---------|-------------------|
| **FastAPI** | 0.115+ | Web framework | Core application, WebSocket server |
| **uvicorn** | 0.32+ | ASGI server | Run FastAPI with WebSocket support |
| **websockets** | 14.1+ | WebSocket library | Low-level WS handling (FastAPI uses this) |
| **deriv_api** | Latest | Deriv API client | Market Data Processor component |
| **Ollama** | Latest | Local LLM server | LLM Engine - run Llama/Mistral models |
| **langchain** | 0.3+ | LLM orchestration | Context management, prompt templates |
| **Redis** | 7.4+ | In-memory cache | Session state, chat history, rate limiting |
| **SQLite** | 3.x | Persistence | Trade history, user prefs, content drafts |
| **pydantic** | 2.10+ | Data validation | Request/response models, config |
| **pandas** | 2.2+ | Data analysis | Behavioral pattern detection |

**Why these choices:**
- **FastAPI**: Native async support, built-in WebSocket, excellent for hackathon demos
- **Ollama**: Simplest way to run open-source LLMs locally, no API keys needed
- **Redis**: Necessary for session state when scaling beyond single server (optional for MVP)
- **SQLite**: Zero-config persistence, perfect for hackathon, easy to upgrade later

### Frontend Stack

| Technology | Version | Purpose | Integration Point |
|------------|---------|---------|-------------------|
| **React** | 18.3+ | UI framework | Dashboard + Chat interfaces |
| **Vite** | 6.0+ | Build tool | Dev server, hot reload |
| **TanStack Query** | 5.62+ | Server state | HTTP fallback, cache management |
| **Zustand** | 5.0+ | Client state | WebSocket state, UI state |
| **WebSocket API** | Native | Real-time comm | Connection to FastAPI backend |
| **Recharts** | 2.15+ | Charts | Price charts, sentiment gauges |
| **TailwindCSS** | 3.4+ | Styling | Rapid UI development |
| **React Markdown** | 9.0+ | Markdown rendering | Display LLM responses |

**Why these choices:**
- **Zustand over Redux**: Simpler for real-time WebSocket state, less boilerplate
- **TanStack Query**: Best-in-class for server data fetching, automatic retries
- **Recharts**: Good balance of features and bundle size for trading charts
- **Native WebSocket**: No library needed, FastAPI handles the protocol

### External APIs

| Service | Purpose | Integration Approach |
|---------|---------|---------------------|
| **Deriv API** | Real-time market data, trade history | Python client library (`deriv_api`) |
| **LinkedIn API** | Post publishing | HTTP REST via `requests` or `httpx` |
| **X (Twitter) API** | Post publishing | HTTP REST via unified social media API |
| **Ayrshare/Late** (optional) | Unified social API | Simplifies multi-platform posting |

## Build Order & Dependencies

### Phase 1: Foundation (Days 1-2)
**Goal:** Establish core architecture and data flow

```
Priority 1: Backend skeleton
├── FastAPI app structure
├── WebSocket connection manager (basic)
├── Deriv API client wrapper
└── Basic data models (Pydantic)

Priority 2: Frontend skeleton
├── React app with Vite
├── Split-view layout (dashboard + chat)
├── WebSocket client connection
└── Basic state management (Zustand)

Priority 3: Integration test
└── End-to-end WebSocket message flow
```

**Why this order:**
- WebSocket infrastructure is the **backbone** - build it first
- Deriv connection must work **before** any analysis can happen
- Frontend layout determines **component structure** downstream

**Deliverable:** Frontend receives mock messages from backend via WebSocket

### Phase 2: Market Data Pipeline (Days 2-3)
**Goal:** Real-time data flowing to dashboard

```
Priority 1: Market Data Processor
├── Deriv API integration
├── Price data normalization
├── Trade history fetching
└── Data buffering logic

Priority 2: Dashboard visualization
├── Real-time price chart (Recharts)
├── Trade history table
├── Basic metrics display
└── Auto-reconnect logic

Priority 3: Data persistence
└── SQLite schema for trade history
```

**Why this order:**
- Dashboard is most **demo-friendly** component - prioritize visual impact
- Data processor must handle rate limits
- Persistence can be **async** - doesn't block real-time display

**Deliverable:** Live dashboard showing real market data

### Phase 3: LLM Integration (Days 3-4)
**Goal:** Chat interface with context-aware responses

```
Priority 1: LLM Engine
├── Ollama setup (Llama 3.3 or Mistral)
├── Prompt template system
├── Context aggregation logic
└── Session memory management

Priority 2: Chat Interface
├── Conversational UI components
├── Message rendering (markdown support)
├── Session continuity (reconnect handling)
└── Loading states & streaming (optional)

Priority 3: Rich response rendering
└── Chart/table rendering in chat
```

**Why this order:**
- LLM setup is **time-consuming** - start early
- Basic chat **validates** LLM integration before adding complexity
- Rich responses are **polish** - defer if time-constrained

**Deliverable:** Chat that answers questions about current market data

### Phase 4: Behavioral Analysis (Days 4-5)
**Goal:** Pattern detection and coaching insights

```
Priority 1: Behavioral Analyzer
├── Trade pattern detection (rule-based)
├── Bias scoring algorithms
├── Sentiment calculation
└── Sliding window logic

Priority 2: Dashboard integration
├── Sentiment gauge component
├── Bias alert notifications
└── Pattern visualization

Priority 3: LLM context enrichment
└── Feed behavioral insights to chat context
```

**Why this order:**
- **Rule-based** patterns faster than ML for hackathon
- Dashboard gauges are **visually impressive** for demos
- LLM context integration makes chat responses **personalized**

**Deliverable:** Dashboard shows behavioral insights; chat references them

### Phase 5: Social Publishing (Days 5-6)
**Goal:** Content generation and posting

```
Priority 1: Content Generator
├── LLM-powered post creation
├── Draft storage & retrieval
└── Approval workflow (UI component)

Priority 2: Social API integration
├── LinkedIn API setup
├── X API setup (or unified API)
└── Publishing logic with error handling

Priority 3: Notification system
└── WebSocket notifications for publish status
```

**Why this order:**
- **Draft mode** prevents embarrassing auto-posts during demo
- Social APIs can be **mocked** if credentials are problematic
- Notifications are **nice-to-have** - manual refresh is acceptable

**Deliverable:** Generate and post content to social media

### Phase 6: Polish & Demo Prep (Day 6-7)
**Goal:** Make it shine for presentation

```
Priority 1: UI polish
├── Loading states everywhere
├── Error boundary components
├── Responsive design tweaks
└── Color scheme consistency

Priority 2: Error handling
├── WebSocket reconnection logic
├── API rate limit handling
├── Graceful degradation
└── User-friendly error messages

Priority 3: Demo script
├── Seed data for reliable demo
├── Pre-generated content examples
└── Fallback responses if API fails
```

**Why this order:**
- **Loading states** prevent "is it broken?" confusion
- **Error handling** prevents demo disasters
- **Demo script** ensures smooth presentation under pressure

## Patterns to Follow

### Pattern 1: Event-Driven Updates
**What:** Use WebSocket broadcasts for all real-time data updates instead of polling.

**When:** Any data that changes frequently (prices, sentiment scores, chat messages).

**Why:** Polling creates unnecessary server load and adds latency. WebSockets provide instant updates.

**Example:**
```python
# Backend: Broadcast price update to all connected clients
async def broadcast_price_update(price_data: PriceUpdate):
    message = {
        "type": "price_update",
        "data": price_data.model_dump()
    }
    await connection_manager.broadcast(message)

# Frontend: React to price updates
const handleMessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'price_update') {
    setPriceData(message.data);
  }
};
```

### Pattern 2: Session-Based Context Management
**What:** Store LLM conversation history per WebSocket session, not per user.

**When:** Chat interactions that need continuity across messages.

**Why:** Simpler than user auth for hackathon, survives page refresh with session recovery.

**Example:**
```python
# Store in Redis with session ID as key
session_key = f"chat_history:{session_id}"
redis_client.lpush(session_key, json.dumps(message))
redis_client.expire(session_key, 3600)  # 1 hour TTL

# Retrieve last N messages for context
history = redis_client.lrange(session_key, 0, 9)  # Last 10 messages
```

### Pattern 3: Async Behavioral Analysis
**What:** Run pattern detection in background tasks, don't block real-time data flow.

**When:** Computationally expensive analysis (ML models, large window calculations).

**Why:** Keeps UI responsive, prevents WebSocket message backlog.

**Example:**
```python
# FastAPI background task
from fastapi import BackgroundTasks

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, background_tasks: BackgroundTasks):
    # On new trade event
    background_tasks.add_task(analyze_behavior, trade_data)
    # Continue processing other messages immediately
```

### Pattern 4: Structured Rich Responses
**What:** LLM responses include metadata for rendering charts/tables, not just text.

**When:** Chat needs to display data visualizations inline.

**Why:** Enables richer user experience, differentiates from generic chatbots.

**Example:**
```python
# Backend: Structure response
response = {
    "type": "chat_response",
    "text": "Here's your portfolio performance:",
    "attachments": [
        {
            "type": "chart",
            "chartType": "line",
            "data": [...],
            "config": {...}
        }
    ]
}

# Frontend: Render based on type
{response.attachments.map(att =>
  att.type === 'chart' ? <Chart data={att.data} /> :
  att.type === 'table' ? <Table data={att.data} /> :
  null
)}
```

### Pattern 5: Buffered Writes for Performance
**What:** Batch database writes instead of writing every event immediately.

**When:** High-frequency data like price ticks (multiple per second).

**Why:** Reduces I/O operations, prevents database from becoming bottleneck.

**Example:**
```python
# In-memory buffer
price_buffer = []

async def buffer_price(price_data):
    price_buffer.append(price_data)
    if len(price_buffer) >= 100:  # Flush every 100 items
        await flush_buffer()

async def flush_buffer():
    if price_buffer:
        db.bulk_insert(price_buffer)
        price_buffer.clear()
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: HTTP Polling for Real-Time Data
**What:** Using repeated HTTP requests to check for new data.

**Why bad:** Creates 100x more server requests, adds latency, wastes bandwidth.

**Instead:** Use WebSocket subscriptions for push-based updates.

**Red flag:** `setInterval(() => fetch('/api/prices'), 1000)` in frontend code.

### Anti-Pattern 2: Loading Full LLM for Every Request
**What:** Loading model weights from disk on each chat message.

**Why bad:** Model loading takes 5-30 seconds, completely kills UX.

**Instead:** Keep LLM loaded in memory via Ollama server or persistent model instance.

**Red flag:** `model = LlamaCpp.from_pretrained(...)` inside request handler.

### Anti-Pattern 3: Storing Streaming Data in SQLite Without Indexing
**What:** Writing every price tick to SQLite without proper indexes or partitioning.

**Why bad:** Database grows exponentially, queries slow down, writes block reads.

**Instead:** Use time-based partitioning, create indexes on query columns, consider time-series DB.

**Red flag:** SQLite file >1GB after one day of testing.

### Anti-Pattern 4: Global State for WebSocket Connections
**What:** Storing all WebSocket client state in a single global dictionary.

**Why bad:** Doesn't scale beyond single server, race conditions, hard to debug.

**Instead:** Use connection manager class with proper lifecycle management and Redis for multi-server.

**Red flag:** `connected_clients = {}` at module level.

### Anti-Pattern 5: Synchronous LLM Calls Blocking WebSocket Handler
**What:** Awaiting LLM inference inside WebSocket message handler without async.

**Why bad:** Blocks entire WebSocket connection, other messages queue up, UX feels frozen.

**Instead:** Run LLM inference in separate async task, stream response tokens back.

**Red flag:** `response = llm.invoke(prompt)` in `websocket.receive_text()` loop.

### Anti-Pattern 6: No Error Boundaries for External APIs
**What:** Direct calls to APIs without try/catch or retry logic.

**Why bad:** Single API failure crashes entire backend, demo becomes unreliable.

**Instead:** Wrap all external calls with error handling, implement exponential backoff retries.

**Red flag:** `deriv_client.subscribe(...)` with no error handling.

### Anti-Pattern 7: Tight Coupling Between Components
**What:** Dashboard component directly imports and calls LLM Engine or Market Data Processor.

**Why bad:** Breaks component boundaries, makes testing impossible, creates circular dependencies.

**Instead:** All inter-component communication via WebSocket Manager or event bus.

**Red flag:** `from backend.llm_engine import get_analysis` in frontend code.

## Scalability Considerations

| Concern | At MVP (Hackathon) | At 100 Users | At 10K Users |
|---------|-------------------|--------------|--------------|
| **WebSocket Connections** | Single FastAPI instance handles all | Add Redis pub/sub for multi-server broadcasting | Use dedicated WebSocket gateway (e.g., API Gateway with Lambda) |
| **LLM Inference** | Single Ollama instance on same server | Separate LLM server, queue requests | Model sharding, inference optimization (quantization), or cloud API fallback |
| **Market Data** | Single Deriv connection, broadcast to all | Connection pooling, per-user subscriptions | Dedicated data ingestion service, Kafka for distribution |
| **Session Storage** | In-memory dict or single Redis | Redis cluster with replication | Distributed cache (Redis Cluster) + session DB |
| **Database Writes** | SQLite with buffering | PostgreSQL with connection pooling | Time-series DB (InfluxDB/TimescaleDB), partitioned tables |
| **Social Publishing** | Sequential posts, no queue | Background job queue (Celery/RQ) | Dedicated publishing service, rate limit management per platform |

**Hackathon Reality Check:**
- **Don't build for 10K users** - focus on clean demo with 1-5 concurrent connections
- **Single server is fine** - show architecture diagram for "how we'd scale"
- **SQLite is sufficient** - judges won't stress-test your database
- **Mock social APIs if needed** - focus on showing the flow, not actual LinkedIn posts

## Deployment Architecture (Hackathon Context)

### Recommended Setup for Demo

```
┌─────────────────────────────────────────────┐
│         Single Server / Laptop              │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Ollama (Port 11434)                │   │
│  │  - Llama 3.3 8B model loaded        │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  FastAPI Backend (Port 8000)        │   │
│  │  - WebSocket server                 │   │
│  │  - Deriv API client                 │   │
│  │  - All business logic               │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  React Frontend (Port 5173)         │   │
│  │  - Vite dev server                  │   │
│  │  - Hot reload enabled               │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Redis (Port 6379) - Optional       │   │
│  │  - Session cache                    │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  SQLite Database                    │   │
│  │  - Local file: ./data/trading.db   │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Start-up sequence:**
```bash
# Terminal 1: Start Ollama and load model
ollama serve
ollama pull llama3.3:8b

# Terminal 2: Start backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3: Start frontend
cd frontend
npm run dev
```

**Why this works for hackathon:**
- **Single machine** - no network complexity, easy to debug
- **Dev mode** - hot reload for rapid iteration
- **Visible terminals** - judges can see all components running
- **Local data** - no cloud dependencies, works offline if needed

## Key Architectural Decisions

### Decision 1: Modular Monolith vs Microservices
**Choice:** Modular monolith with clear internal boundaries

**Rationale:**
- Hackathon timeline too short for distributed system complexity
- Single deployment simplifies demo setup
- Internal modules still enforce separation of concerns
- Can extract to microservices post-hackathon if needed

**Trade-off:** Scaling requires scaling entire backend, not individual components

### Decision 2: Local LLM vs Cloud API
**Choice:** Local LLM via Ollama (Llama/Mistral)

**Rationale:**
- No API costs or rate limits during hackathon
- Works offline (reliable demos)
- Shows technical sophistication (running models locally)
- Aligns with project requirement for open-source LLMs

**Trade-off:** Requires decent hardware (16GB+ RAM), slower than cloud APIs

### Decision 3: WebSocket vs HTTP Polling
**Choice:** WebSocket for all real-time communication

**Rationale:**
- Required for real-time market data streaming
- Better UX for chat (instant responses)
- Single connection for all data types
- Industry standard for trading platforms

**Trade-off:** More complex than REST, requires connection management

### Decision 4: Session-Based vs User-Based Auth
**Choice:** Session-based (WebSocket session ID), defer user auth

**Rationale:**
- Faster to implement for hackathon
- Sufficient for single-user demo
- Easier to test (no login flow)
- Can add auth layer later without architecture changes

**Trade-off:** Can't persist data across sessions (acceptable for demo)

### Decision 5: SQLite vs PostgreSQL
**Choice:** SQLite for initial implementation

**Rationale:**
- Zero configuration (file-based)
- Sufficient for demo load
- Easy to inspect with DB browser tools
- Can migrate to Postgres later (same SQL)

**Trade-off:** Not suitable for production concurrent writes

### Decision 6: Direct Social APIs vs Unified Service
**Choice:** Direct API integration with fallback to unified service (Ayrshare/Late)

**Rationale:**
- Direct APIs show technical capability
- Unified service as backup if credential issues
- Can mock both for demo reliability

**Trade-off:** More API credential management

## Component Implementation Guide

### WebSocket Connection Manager

**Responsibilities:**
- Accept and manage client WebSocket connections
- Route messages to appropriate backend handlers
- Broadcast updates to specific clients or all clients
- Maintain session state (session ID → connection mapping)

**Key Methods:**
```python
class ConnectionManager:
    async def connect(self, websocket: WebSocket, session_id: str)
    async def disconnect(self, session_id: str)
    async def send_personal(self, message: dict, session_id: str)
    async def broadcast(self, message: dict)
    async def send_to_group(self, message: dict, group: str)
```

**Error Handling:**
- Auto-reconnect logic on client side
- Heartbeat/ping messages to detect stale connections
- Graceful cleanup on disconnect

### Market Data Processor

**Responsibilities:**
- Establish connection to Deriv API
- Poll price data for specified instruments
- Fetch historical intraday data on startup
- Normalize and buffer incoming data
- Emit events for price updates and trade events

**Key Interfaces:**
```python
class MarketDataProcessor:
    async def connect(self)
    async def subscribe_prices(self, symbols: List[str])
    async def fetch_trade_history(self, symbol: str, limit: int = 100)
```

**Data Normalization:**
- Convert Deriv-specific formats to internal models
- Handle missing/null values
- Timestamp standardization (UTC)

### LLM Engine

**Responsibilities:**
- Initialize and manage Ollama client connection
- Aggregate context from multiple sources (chat history, market data, behavioral insights)
- Construct prompts using templates
- Execute model inference
- Parse and structure responses

**Key Interfaces:**
```python
class LLMEngine:
    def __init__(self, model_name: str = "llama3.3:8b")
    async def generate_response(
        self,
        user_message: str,
        session_id: str,
        context: Optional[Dict] = None
    ) -> ChatResponse
    async def generate_social_content(
        self,
        topic: str,
        tone: str = "professional"
    ) -> str
```

**Context Aggregation Strategy:**
1. Load last N chat messages from session history
2. Fetch current market snapshot (latest prices, trends)
3. Retrieve latest behavioral analysis results
4. Combine into structured prompt

**Prompt Template Example:**
```python
SYSTEM_PROMPT = """You are an expert trading analyst and coach.
Current market context: {market_data}
Recent trades: {trade_history}
Behavioral insights: {behavioral_analysis}

Provide concise, actionable advice. Use charts and tables when helpful."""
```

### Behavioral Analyzer

**Responsibilities:**
- Detect trading patterns (win/loss streaks, position sizing changes)
- Identify cognitive biases (loss aversion, overconfidence, recency bias)
- Calculate sentiment scores
- Run analysis on sliding time windows

**Key Interfaces:**
```python
class BehavioralAnalyzer:
    async def analyze_patterns(self, trades: List[Trade]) -> PatternReport
    def detect_biases(self, trades: List[Trade]) -> List[BiasDetection]
    def calculate_sentiment(self, trades: List[Trade]) -> float  # -1 to 1
```

**Pattern Detection Algorithms (Rule-Based for MVP):**
- **Win/Loss Streak**: Count consecutive wins/losses
- **Risk Escalation**: Detect position size increases after losses
- **Overtrading**: Frequency of trades vs. historical average
- **Revenge Trading**: Large trades immediately after significant loss

**Bias Scoring:**
```python
biases = {
    "loss_aversion": 0.7,  # Higher after loss streaks
    "overconfidence": 0.3,  # Lower = more cautious
    "recency_bias": 0.5    # Weight on recent vs. all trades
}
```

### Content Generator

**Responsibilities:**
- Generate social media post content using LLM
- Store drafts for user approval
- Publish approved content to social platforms
- Handle API rate limits and errors
- Track publication status

**Key Interfaces:**
```python
class ContentGenerator:
    async def generate_draft(
        self,
        topic: str,
        platform: str,  # "linkedin" or "x"
        market_data: Optional[Dict] = None
    ) -> ContentDraft

    async def approve_and_publish(
        self,
        draft_id: str,
        platforms: List[str]
    ) -> PublishResult

    async def get_drafts(self) -> List[ContentDraft]
```

**Publishing Strategy:**
- **Draft mode by default** - require explicit approval
- **Auto-post option** - configurable per content type
- **Error handling** - retry logic with exponential backoff
- **Status tracking** - pending, published, failed

## Testing Strategy for Hackathon

### What to Test (Prioritized)

1. **WebSocket Connection Flow** (Critical)
   - Client connects successfully
   - Messages route correctly
   - Reconnection works after disconnect

2. **Deriv API Integration** (Critical)
   - Connection establishes
   - Price data streams correctly
   - Handles API errors gracefully

3. **LLM Response Generation** (High)
   - Model loads and responds
   - Context aggregation works
   - Responses are coherent

4. **End-to-End Chat Flow** (High)
   - User message → LLM → Response rendering

5. **Dashboard Real-Time Updates** (Medium)
   - Price updates reflect immediately
   - Charts render correctly

### What NOT to Test (Defer)

- Unit tests for every function (too time-consuming)
- Load testing (not needed for demo)
- Security testing (not in scope)
- Browser compatibility (pick one browser)

### Demo Reliability Checklist

- [ ] Seed database with realistic trade history
- [ ] Pre-load LLM model before demo starts
- [ ] Test full flow 3x in a row without errors
- [ ] Have mock data ready if Deriv API fails
- [ ] Screenshot key screens as backup
- [ ] Practice demo script with timer

## Sources

### Real-Time Trading Systems
- [Best AI for stock trading: 12 powerful tools for investors in 2026](https://monday.com/blog/ai-agents/best-ai-for-stock-trading/)
- [AI-Powered Multi-Agent Trading Workflow | by Bijit Ghosh | Medium](https://medium.com/@bijit211987/ai-powered-multi-agent-trading-workflow-90722a2ada3b)
- [Event-Driven Architecture for Trading Systems](https://www.thefullstack.co.in/event-driven-architecture-trading-systems/)
- [Building real-time streaming pipelines for market data | Google Cloud Blog](https://cloud.google.com/blog/topics/financial-services/building-real-time-streaming-pipelines-for-market-data)

### WebSocket Architecture
- [WebSocket architecture best practices to design robust realtime system](https://ably.com/topic/websocket-architecture-best-practices)
- [How to Incorporate Advanced WebSocket Architectures in FastAPI for High Performance Real Time Systems | by Hex Shift | Nov, 2025 | Medium](https://hexshift.medium.com/how-to-incorporate-advanced-websocket-architectures-in-fastapi-for-high-performance-real-time-b48ac992f401)
- [How to Build WebSocket Servers with FastAPI and Redis](https://oneuptime.com/blog/post/2026-01-25-websocket-servers-fastapi-redis/view)

### LLM Integration
- [TradingAgents: Multi-Agents LLM Financial Trading Framework](https://tradingagents-ai.github.io/)
- [I Built a Full-Stack AI Stock Trading App with LLMs | by Thomas Tarler | Jan, 2026 | Medium](https://medium.com/@ttarler/i-built-a-full-stack-ai-trading-app-with-llms-52f9cc235321)
- [An End-To-End LLM Enhanced Trading System](https://arxiv.org/html/2502.01574v1)
- [Best Open Source LLMs: Complete 2026 Guide | Contabo Blog](https://contabo.com/blog/open-source-llms/)
- [Top 5 Local LLM Tools and Models in 2026 - Pinggy](https://pinggy.io/amp/blog/top_5_local_llm_tools_and_models/)

### Session Management & Memory
- [Context Engineering - Short-Term Memory Management with Sessions from OpenAI Agents SDK | OpenAI Cookbook](https://cookbook.openai.com/examples/agents_sdk/session_memory)
- [How Should I Manage Memory for my LLM Chatbot?](https://www.vellum.ai/blog/how-should-i-manage-memory-for-my-llm-chatbot)
- [Design Patterns for Long-Term Memory in LLM-Powered Architectures](https://serokell.io/blog/design-patterns-for-long-term-memory-in-llm-powered-architectures)

### React & State Management
- [Top 5 React State Management Tools Developers Actually Use in 2026 and Why | Syncfusion Blogs](https://www.syncfusion.com/blogs/post/react-state-management-libraries)
- [I Built a Real-Time Dashboard in React Using WebSockets and Recoil | by Hash Block | Medium](https://medium.com/@connect.hashblock/i-built-a-real-time-dashboard-in-react-using-websockets-and-recoil-076d69b4eeff)
- [Top 5 React Stock Chart Libraries for 2026 | Syncfusion Blogs](https://www.syncfusion.com/blogs/post/top-5-react-stock-charts-in-2026)

### Social Media Publishing
- [Late - Unified Social Media API](https://getlate.dev)
- [Social Media API: Automate Posting and Analytics to Social Networks like Instagram, TikTok, X/Twitter, Facebook, LinkedIn, Reddit, YouTube, and Telegram](https://github.com/ayrshare/social-media-api)
- [Social Media Content Generator And Publisher | X, Linkedin | n8n workflow template](https://n8n.io/workflows/3082-social-media-content-generator-and-publisher-or-x-linkedin/)

### Behavioral Analysis
- [Behaviorally informed deep reinforcement learning for portfolio optimization with loss aversion and overconfidence | Scientific Reports](https://www.nature.com/articles/s41598-026-35902-x)
- [Deep learning for algorithmic trading: A systematic review of predictive models and optimization strategies - ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2590005625000177)
- [GitHub - Ronitt272/LLM-Enhanced-Trading: A sentiment-driven trading system leveraging FinGPT for real-time financial news and social media sentiment extraction to enhance trading outcomes.](https://github.com/Ronitt272/LLM-Enhanced-Trading)

### Architecture Patterns
- [Microservices vs Monoliths in 2026: When Each Architecture Wins - Java Code Geeks](https://www.javacodegeeks.com/2025/12/microservices-vs-monoliths-in-2026-when-each-architecture-wins.html)
- [Low Latency Trading Systems in 2026 | The Complete Guide - Tuvoc Technologies](https://www.tuvoc.com/blog/low-latency-trading-systems-guide/)
- [MVP Tech Stack Guide 2026: Build Fast, Stay Compliant | by Cabot Technology Solutions | Medium](https://medium.com/@cabotsolutions/mvp-tech-stack-guide-2026-build-fast-stay-compliant-94e1bc34fee7)

### Deriv API
- [Deriv API Documentation](https://api.deriv.com/)
- [Deriv Python Library](https://github.com/RomelTorres/deriv_api)

## Confidence Assessment

| Area | Confidence | Rationale |
|------|-----------|-----------|
| **WebSocket Architecture** | HIGH | Multiple authoritative sources on FastAPI + WebSocket patterns, real-world trading examples |
| **LLM Integration** | HIGH | Recent 2026 sources on local LLM deployment (Ollama), trading-specific frameworks documented |
| **Component Boundaries** | MEDIUM-HIGH | Based on established event-driven architecture patterns, validated by trading system examples |
| **Build Order** | MEDIUM | Derived from MVP best practices and hackathon timelines, not trading-specific |
| **Data Flow** | HIGH | Real-time trading pipelines well-documented, WebSocket pub/sub patterns standard |
| **Scalability Path** | MEDIUM | Based on general scalability patterns, not tested at scale for this specific stack |

## Open Questions for Implementation

1. **LLM Context Window Management**: How to handle long chat sessions when context exceeds model's window (8K-32K tokens)? Consider implementing automatic summarization or sliding window.

2. **Deriv API Rate Limits**: What are the actual rate limits for Deriv? Need to test with real API.

3. **Social API Credentials**: LinkedIn/X API access requirements in 2026? May need developer accounts in advance.

4. **Chart Rendering Performance**: Can Recharts handle real-time updates (multiple per second) without lag? May need to throttle updates or use canvas-based library.

5. **LLM Response Time**: What's acceptable latency for chat responses in a trading context? May need to show loading indicators or stream responses.

## Ready for Roadmap

This architecture research provides:
- ✅ Clear component boundaries for phase planning
- ✅ Data flow diagrams for dependency mapping
- ✅ Suggested build order based on dependencies
- ✅ Technology stack with rationale for each choice
- ✅ Scalability considerations (though hackathon focus is MVP)
- ✅ Patterns and anti-patterns for implementation guidance

**Recommended phase structure:**
1. **Foundation** - WebSocket infrastructure, basic frontend
2. **Market Data** - Real-time data pipeline, dashboard visualization
3. **LLM Chat** - Conversational interface with context
4. **Behavioral Analysis** - Pattern detection, coaching insights
5. **Social Publishing** - Content generation and posting
6. **Polish** - UI refinement, error handling, demo prep

The modular monolith architecture enables parallel development (frontend/backend teams) while maintaining integration simplicity for the hackathon timeline.

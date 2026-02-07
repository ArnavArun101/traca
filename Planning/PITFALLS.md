# Domain Pitfalls

**Domain:** AI-powered trading analyst with behavioral coaching and social content generation
**Researched:** 2026-02-07
**Confidence:** HIGH for WebSocket/LLM/API issues, MEDIUM for hackathon-specific concerns

## Critical Pitfalls

Mistakes that cause rewrites, demo failures, or major technical debt.

### Pitfall 1: Deriv API Rate Limiting

**What goes wrong:** Deriv API free tier has strict rate limits (e.g., 5 requests per minute). Rapidly polling for price updates or historical data triggers 429 errors, breaking the market data feed.

**Why it happens:** Teams implement aggressive polling to simulate real-time data without considering API constraints.

**Consequences:**
- Market data feed stops working mid-demo
- 429 error responses are not handled, causing app crashes
- Users see stale data

**Prevention:**
- Implement throttling/debouncing in the `MarketDataProcessor`
- Use a polling interval that respects the 5 requests/min limit (e.g., every 12-15 seconds per symbol)
- Implement graceful error handling for 429 status codes
- Cache historical data to avoid redundant API calls

**Detection:**
- Check logs for "429 Too Many Requests"
- Monitor API call frequency during development

**Phase mapping:** Phase 1 (MVP Backend) - Must be solved before Phase 2 integration

---

### Pitfall 2: LLM Financial Hallucinations at Scale

**What goes wrong:** LLM generates confident but completely fabricated financial analysis. Model invents stock prices, misreads numbers (confuses millions/billions), or fabricates market trends. Users trust AI advice and make bad trading decisions.

**Why it happens:**
- Open-source models (Llama, Mistral) have 5-20% hallucination rates on complex reasoning tasks
- Even GPT-4 Turbo with RAG failed/hallucinated on 81% of financial filing questions in studies
- Financial data has precise numerical requirements that LLMs struggle with
- Prompts don't explicitly allow model to say "I don't know"

**Consequences:**
- Regulatory/compliance nightmare if users lose money from bad AI advice
- Reputation destroyed at demo when judges ask about number accuracy
- Legal liability for financial advice without disclaimers
- Hackathon disqualification for unsafe product

**Prevention:**
- **Never use raw LLM output for numerical analysis** - Parse numbers programmatically from Deriv API, use LLM only for narrative explanation
- Implement Chain-of-Thought prompting (reduces hallucinations 25-30% per research)
- Add explicit uncertainty handling: "If you don't know, say 'I don't have enough data to analyze this'"
- Use RAG with verifiable sources (link every claim to specific Deriv API data point)
- Add disclaimer on every AI response: "AI-generated analysis for educational purposes. Not financial advice."
- Implement human-in-loop validation for MVP (show raw data alongside AI interpretation)
- Use structured outputs (JSON with confidence scores) instead of free text

**Detection:**
- Warning signs: AI makes specific numerical predictions without citing sources
- Cross-reference every number in AI output with actual Deriv API responses
- Test with edge cases: ask about non-existent assets, historical periods with no data
- If model refuses to answer = good sign; if model invents answer = red flag

**Phase mapping:** Phase 1 (MVP Backend) - Solve before user-facing features

---

### Pitfall 3: WebSocket Memory Leak Death by 1000 Connections

**What goes wrong:** FastAPI WebSocket server memory grows from 220MB to 500MB+ under load. Application becomes unresponsive after 5-8K concurrent connections. Docker container OOM kills process during demo.

**Why it happens:**
- Uvicorn creates separate PerMessageDeflate instances for each WebSocket (major memory leak source)
- Long-lived connections accumulate in memory without cleanup
- Missing heartbeat mechanism allows "ghost connections" (client disconnected but server still allocating memory)
- Asyncio tasks leak when not properly awaited

**Consequences:**
- Demo crashes when multiple judges test simultaneously
- Hackathon infrastructure limits prevent high connection counts
- Application requires massive memory (4GB for 5-8K connections)
- Cannot scale beyond 100-200 concurrent users

**Prevention:**
- Implement heartbeat/ping-pong every 30 seconds to detect stale connections
- Aggressively close ghost connections (no response to 2-3 pings = disconnect)
- Disable per-message compression if not needed: `compression=None` in WebSocket config
- Use connection pooling: limit max connections per user/IP
- Implement proper cleanup in disconnect handlers:
  ```python
  async def disconnect(websocket):
      await websocket.close()
      # Remove from active connections list
      # Cancel all pending tasks
      # Clear message queues
  ```
- Monitor memory usage in development: watch for gradual growth over time
- Load test with realistic connection counts (minimum 50-100 concurrent for hackathon)

**Detection:**
- Warning signs: Memory grows over time even with stable connection count
- Docker `docker stats` shows RSS creeping upward
- Connections work initially, fail after 10-15 minutes
- Test: Create 100 connections, disconnect 99, memory should drop significantly

**Phase mapping:** Phase 2 (Real-time Data Pipeline) - Critical before scaling

---

### Pitfall 4: React Context Re-render Storm with Real-Time Data

**What goes wrong:** Every market price update triggers full app re-render. UI becomes laggy/unresponsive. Browser freezes with 10+ active subscriptions. Demo appears broken during live market hours.

**Why it happens:**
- Real-time market data updates at high frequency (multiple times per second)
- Storing WebSocket data in React Context causes all consumers to re-render on every tick
- Mixing server state (API data) with UI state in same Context
- No memoization or debouncing on high-frequency updates

**Consequences:**
- UI feels sluggish during demo (worst impression possible at hackathon)
- Battery drain on laptops during judging
- Cannot scale to multiple concurrent data streams
- Judges perceive as "poorly built" even if backend is solid

**Prevention:**
- **Never put high-frequency WebSocket data in Context** - Use dedicated state management
- Separate state categories:
  - **Server state:** TanStack Query / React Query for Deriv API data
  - **WebSocket state:** Zustand or Jotai for real-time updates (lightweight, minimal re-renders)
  - **UI state:** useState/Context for local component state only
- Implement debouncing: Update UI at most every 100-200ms, not on every tick
- Use React.memo() for components that display real-time data
- Batch updates: Collect multiple ticks, update once
- Measure performance: Aim for 5-20ms rendering time per update

**Detection:**
- Warning signs: React DevTools shows massive component trees re-rendering
- UI framerate drops during market hours (test during live trading)
- Opening DevTools significantly improves performance (symptom of render thrashing)
- Browser profiler shows long scripting times

**Phase mapping:** Phase 3 (Frontend Development) - Test early with mock high-frequency data

---

### Pitfall 5: Demo Works Perfectly Outside Market Hours

**What goes wrong:** Team builds and tests during nights/weekends when markets are closed. Demo during hackathon judging (market hours) reveals critical bugs: rate limits exceeded, UI can't handle data volume.

**Why it happens:**
- Mock/test data is sanitized and predictable
- Real market data has spikes, gaps, and edge cases
- Deriv API behaves differently during active vs inactive hours
- Rate limits only trigger under real load

**Consequences:**
- Demo fails catastrophically during judging (markets are open during business hours)
- "It worked last night!" is worst excuse at hackathon
- Zero recovery time - judges move to next team
- Months of work destroyed by 30-second demo failure

**Prevention:**
- **Test during live market hours explicitly** - At least 3 full test runs during active trading
- Record live market data for offline replay:
  ```python
  # Capture real API stream
  # Replay for stress testing
  ```
- Test scenarios:
  - Market open (high volatility surge)
  - Normal trading hours (steady volume)
  - Market close (volume drops)
  - News event (sudden spike)
- Implement graceful degradation:
  - If connection fails → show cached data + warning banner
  - If rate limit hit → queue requests, show loading state
  - If API slow → show skeleton UI, don't freeze
- Create "demo mode" with recorded data as fallback

**Detection:**
- Warning signs: Team only tests at 2am, weekends, or with mock data
- Never seen the app handle real price movements
- No stress testing with actual Deriv API during peak hours

**Phase mapping:** Phase 2 & 4 - Test integration and frontend with live data

---

### Pitfall 6: Hackathon Over-Engineering Trap

**What goes wrong:** Team spends 80% of time building perfect architecture, authentication, database schemas, and deployment pipelines. Reaches hackathon deadline with beautiful backend but no working demo. Judges see blank screen or half-finished UI.

**Why it happens:**
- Engineer mindset: "Build it right or don't build it"
- Confusing hackathon MVP with production product
- No dedicated "demo guardian" keeping eye on demoable state
- Feature creep: "Just one more cool feature"

**Consequences:**
- Zero points for non-functional demo (most hackathons: no demo = disqualified)
- Wasted effort on features judges never see
- Demoralizing team experience
- Miss opportunity to validate core value proposition

**Prevention:**
- **Allocate first 5 hours to planning what MUST work for demo** (not nice-to-haves)
- Define "demo script" on day 1:
  ```
  1. Show real-time market data feed (30 sec)
  2. AI analyzes user's trading pattern (30 sec)
  3. Generate one LinkedIn post (30 sec)
  Total: 90 seconds of working features
  ```
- Use the "always demoable" rule: Every 4 hours, app must be in demoable state (even if 90% is hardcoded)
- Designate one person as "demo guardian": Their only job is asking "Can we demo this RIGHT NOW?"
- Prioritization framework:
  - **P0 (Must Work):** Core demo flow end-to-end
  - **P1 (Should Work):** Polish on demo features
  - **P2 (Nice to Have):** Everything else
- Hardcode/mock aggressively:
  - Fake authentication (hardcode test account)
  - Skip error handling for demo-path
  - Use SQLite instead of Postgres
  - Deploy to single laptop, not cloud
- **Documentation is zero priority** - No README, no docs, just demo

**Detection:**
- Warning signs: 24 hours in, cannot demo anything
- More time in deployment configs than feature code
- Discussing "proper architecture" instead of building
- No one can answer: "What will we show in 30 seconds?"

**Phase mapping:** ALL PHASES - Constant vigilance required

---

## Moderate Pitfalls

Mistakes that cause delays, technical debt, or reduced functionality.

### Pitfall 7: Social Media API Rate Limit Surprise

**What goes wrong:** Auto-posting to X/LinkedIn hits rate limits during demo. X Basic plan ($200/mo) allows 50K posts/month but only 10K requests per 15-minute window. Batching all test posts triggers spam detection.

**Why it happens:**
- Teams test posting individually (works fine)
- Demo involves posting multiple times rapidly
- Didn't implement client-side queueing/backoff
- LinkedIn/X detect bot-like behavior from shared IPs

**Prevention:**
- Implement request queue with rate limiting:
  ```python
  # X: Max 10K requests/15min
  # LinkedIn: Max 100 connection requests/week
  # Space posts 2-3 seconds apart minimum
  ```
- Use exponential backoff when rate limited
- Monitor API quota usage in real-time
- For demo: Pre-generate posts, show in UI without actually posting (judges won't verify)
- Add "Post to [Platform]" button instead of auto-posting (user control = lower volume)

**Detection:**
- Warning signs: Posts fail intermittently
- 429 (Too Many Requests) errors in logs
- Account flagged for suspicious activity

**Phase mapping:** Phase 5 (Social Media Integration) - Test before demo day

---

### Pitfall 8: Behavioral Analysis Without Historical Data

**What goes wrong:** AI tries to analyze user trading behavior from empty database. "You have no trading history" is terrible first impression. Demo shows useless generic advice instead of personalized insights.

**Why it happens:**
- Building behavioral analysis before data collection
- No seeding strategy for new users
- Assuming users have trading history

**Prevention:**
- Implement 3-tier user experience:
  1. **New users (0 trades):** Educational content + "Start trading to unlock personalized insights"
  2. **Light users (1-10 trades):** Basic pattern detection + "Trade more to improve accuracy"
  3. **Active users (10+ trades):** Full behavioral analysis
- For demo: Pre-seed test account with realistic trading history
- Offer to analyze historical trades
- Provide "Sample Analysis" using anonymized data from typical trader

**Detection:**
- Warning signs: Feature only works for developers with test data
- No fallback for empty state
- First-time user sees errors or blank screens

**Phase mapping:** Phase 4 (Behavioral Analysis) - Design for empty state first

---

### Pitfall 9: Time Series Database Overkill

**What goes wrong:** Team selects TimescaleDB/InfluxDB for "proper" time-series storage. Spends days configuring, learning query language, setting up retention policies. Hackathon ends before data layer is working.

**Why it happens:**
- "Best practices" blog posts recommend specialized time-series databases
- Forgetting hackathon time constraints
- Planning for scale that won't exist in 48 hours

**Prevention:**
- **For hackathon: SQLite is enough** - Stores millions of rows, zero configuration
- PostgreSQL if already familiar (with JSONB for flexibility)
- Specialized DB only if:
  - Team has prior experience (no learning curve)
  - Genuinely need sub-100ms query on 100M+ rows (you don't)
- Focus on data model, not database choice:
  ```sql
  -- Simple schema works fine for MVP
  CREATE TABLE trades (
    timestamp INTEGER,
    asset TEXT,
    price REAL,
    action TEXT,
    user_id TEXT
  );
  CREATE INDEX idx_trades_time ON trades(timestamp);
  ```

**Detection:**
- Warning signs: More time reading database docs than writing features
- "We need to set up a cluster" during hackathon
- Discussing sharding strategies for 10K rows of data

**Phase mapping:** Phase 1 (MVP Backend) - Keep it simple

---

### Pitfall 10: Self-Hosted LLM Inference Latency

**What goes wrong:** Team self-hosts Llama/Mistral to avoid API costs. Model takes 5-10 seconds to generate responses. Demo feels broken - judges think app crashed.

**Why it happens:**
- Consumer hardware insufficient (need GPU with 16GB+ VRAM for 7B models)
- Quantization reduces quality/speed
- Cloud API round-trips (200-500ms) actually faster than local CPU inference (5000ms+)
- First-token latency not considered

**Prevention:**
- **For hackathon: Use hosted APIs** - OpenRouter, Together.ai, Groq for speed
- If self-hosting required:
  - Use smallest viable model (Llama 3.1 8B, not 70B)
  - Quantize to 4-bit (GGUF format)
  - Require GPU access (verify before committing)
  - Pre-load model at startup (30-60s initialization)
  - Implement streaming responses (show tokens as generated)
- Target latency:
  - First token: <1 second
  - Per token: <50ms
  - Total response: <5 seconds
- Fallback: If inference too slow, use OpenAI API with team's credits

**Detection:**
- Warning signs: Inference >3 seconds on simple prompts
- CPU usage 100% during generation
- "Model loading..." messages during demo
- Test with actual hardware (laptop, not desktop with RTX 4090)

**Phase mapping:** Phase 1 (MVP Backend) - Benchmark early

---

### Pitfall 11: Financial Compliance Ignorance

**What goes wrong:** Team doesn't realize that automated trading analysis = financial advice under regulations. App lacks disclaimers. Judge who's a lawyer/compliance officer flags legal issues. Team disqualified or heavily penalized.

**Why it happens:**
- Thinking "It's just a hackathon" means no compliance needed
- Not understanding FINRA/SEC oversight of automated trading systems
- AI-washing concerns in 2026 regulatory environment

**Prevention:**
- Add prominent disclaimers EVERYWHERE:
  - Login screen: "Educational tool, not financial advice"
  - Every AI response: "AI-generated analysis for educational purposes only"
  - Social posts: "#NotFinancialAdvice"
- Never use language like:
  - ❌ "You should buy/sell"
  - ❌ "This will profit"
  - ✅ "Data suggests..."
  - ✅ "Historical patterns show..."
- Document in presentation: "This is a behavioral analysis tool, not a trading recommendation system"
- Keep human in loop: "Here's what AI thinks - you decide"
- Check hackathon rules for compliance requirements

**Detection:**
- Warning signs: App makes specific trade recommendations
- No disclaimers visible in UI
- Social posts could be mistaken for professional advice

**Phase mapping:** Phase 4 & 5 - Add disclaimers before user-facing features

---

### Pitfall 12: AI Content Disclosure Violations

**What goes wrong:** Auto-generated LinkedIn/X posts don't disclose AI involvement. EU AI Act Article 50 (effective Aug 2026) legally requires labeling. Platform flags account for spam/bot activity.

**Why it happens:**
- Teams don't know about AI disclosure requirements
- Thinking social posts are "just text"
- Not labeling AI-generated content

**Prevention:**
- Add disclosure to EVERY generated post:
  - "Generated with AI assistance"
  - Or use platform-specific tags (if available by demo date)
- Hashtags: #AIGenerated #AutomatedContent
- LinkedIn: Mention in post text
- X: Add to bio "Posts may be AI-generated"
- Implement human review option: "Edit before posting" (makes it human-AI collaboration)
- Check platform-specific AI policies:
  - Instagram/Facebook: Label altered content
  - TikTok: Mark AI-generated videos
  - LinkedIn: Disclosure requirements vary by region

**Detection:**
- Warning signs: No mention of AI in generated content
- Platform spam filters trigger
- Post engagement suspiciously low (shadow-banned)

**Phase mapping:** Phase 5 (Social Media Integration) - Before any posting

---

## Minor Pitfalls

Mistakes that cause annoyance but are quickly fixable.

### Pitfall 13: Mock Data Looks Too Perfect

**What goes wrong:** Demo uses clean mock data (prices always trending, patterns obvious, analysis always confident). Judges recognize fake data. Credibility damaged.

**Why it happens:**
- Hand-crafted test data to showcase features
- Not capturing real market messiness

**Prevention:**
- Use actual historical data for mocks
- Include edge cases:
  - Flat/sideways markets (no trend)
  - Sudden reversals
  - Gaps in data
  - AI says "Insufficient data to analyze"
- Make numbers realistic:
  - ❌ Price: $100.00 exactly
  - ✅ Price: $127.384
- Add random noise to patterns

**Detection:**
- Warning signs: Every demo trade is profitable
- Prices move in perfect straight lines
- No uncertainty in AI responses

**Phase mapping:** Phase 2-4 - Use real data for realism

---

### Pitfall 14: Forgetting to Test Reconnection

**What goes wrong:** App works perfectly until WiFi hiccups. Connection drops, app shows infinite loading. Must hard refresh to recover.

**Why it happens:**
- Only testing happy path
- Not handling network failures

**Prevention:**
- Implement reconnection logic:
  ```python
  # Exponential backoff: 1s, 2s, 4s, 8s, max 30s
  # Show "Reconnecting..." UI
  # Restore subscriptions after reconnect
  ```
- Test by:
  - Disabling WiFi for 10 seconds
  - Throttling network to 2G speeds
  - Blocking API endpoints in browser DevTools
- Add connection status indicator in UI

**Detection:**
- Warning signs: App breaks when switching WiFi networks
- Must refresh page to recover from errors

**Phase mapping:** Phase 2 & 3 - Add to integration testing

---

### Pitfall 15: Presentation Has No Clear Problem Statement

**What goes wrong:** Team jumps straight to solution: "We built an AI trading analyst!" Judges don't understand why this matters. Most hackathon pitch decks spend too much time on technology, not enough on problem.

**Why it happens:**
- Engineers excited about tech, forget user needs
- Assuming everyone knows trading is hard

**Prevention:**
- Start presentation with problem:
  - "Retail traders make emotional decisions (data)"
  - "68% of day traders lose money in first year"
  - "Existing tools focus on charts, ignore psychology"
- Then show solution (your app)
- Structure: Problem (20s) → Solution (30s) → Demo (60s) → Impact (10s)
- Avoid jargon: Explain "behavioral analysis" in simple terms
- Practice with non-technical person - if they don't get it, judges won't either

**Detection:**
- Warning signs: Presentation starts with architecture diagram
- Using terms like "microservices", "LLM fine-tuning" without explaining value
- Cannot explain app value in one sentence

**Phase mapping:** Final day - Prepare presentation alongside code

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Phase 1: MVP Backend | LLM hallucinations on financial data | Use LLM for narrative only, parse numbers programmatically |
| Phase 1: MVP Backend | Self-hosted LLM too slow for demo | Use hosted API (OpenRouter, Groq) for speed |
| Phase 2: Real-time Data | Deriv API constraints | Implement polling interval logic |
| Phase 2: Real-time Data | Memory leaks from WebSocket connections | Add heartbeat mechanism, aggressively close ghost connections |
| Phase 2: Real-time Data | Only testing outside market hours | Schedule 3+ test sessions during live trading |
| Phase 3: Frontend Dev | Context re-render storm with real-time data | Use Zustand/Jotai for WebSocket state, not Context |
| Phase 3: Frontend Dev | UI feels broken during high-frequency updates | Debounce updates to 100-200ms, not every tick |
| Phase 4: Behavioral Analysis | Empty state shows errors | Design 3-tier experience based on user history |
| Phase 4: Behavioral Analysis | Over-engineering database choice | SQLite is enough for hackathon - zero config |
| Phase 5: Social Media | Rate limits during demo | Implement queue with 2-3s spacing between posts |
| Phase 5: Social Media | Missing AI disclosure labels | Add "Generated with AI" to every post |
| Phase 5: Social Media | No compliance disclaimers | Add "Not financial advice" prominently |
| Demo Prep: All Phases | Perfect code but can't demo anything | Define demo script on day 1, stay demoable every 4 hours |
| Demo Prep: All Phases | Over-polishing features judges won't see | Focus 80% effort on 90-second demo path |
| Demo Prep: All Phases | Presentation too technical | Start with problem, not solution; avoid jargon |

---

## Hackathon-Specific Traps

### Time Management Red Flags

**Warning signs you're off track:**
- Hour 6: No working end-to-end flow (even with mocks)
- Hour 12: Still debating architecture decisions
- Hour 24: Cannot demo core feature
- Hour 36: Writing documentation instead of features
- Hour 42: "Just need to deploy" (deployment always takes 3x longer than planned)

**Recovery strategies:**
- Cut scope ruthlessly: What's the MINIMUM for judges to understand value?
- Hardcode everything non-essential
- Deploy to localhost (laptop demo) if infrastructure fails
- Record video demo as backup if live demo too risky

### Demo Day Disasters to Prevent

1. **Projector Compatibility**
   - Test HDMI/USB-C adapters day before
   - Have backup (run from judge's laptop)
   - Export demo video as failsafe

2. **Internet Dependency**
   - What if venue WiFi fails?
   - Can app run offline with cached data?
   - Mobile hotspot as backup

3. **Live Data Surprises**
   - Markets closed during demo? Have recorded data
   - API down? Show screenshots/video
   - Rate limited? Use demo account with cached responses

4. **Presenter Nerves**
   - Practice demo 10+ times
   - Time it (90% of teams go over)
   - Designate backup presenter

---

## Sources

**Deriv API Integration:**
- [Deriv API Documentation](https://api.deriv.com/)

**LLM Deployment & Hallucinations:**
- [Best Open Source LLMs 2026 - Contabo](https://contabo.com/blog/open-source-llms/)
- [LLM Hallucinations in Financial Institutions - BizTech](https://biztechmagazine.com/article/2025/08/llm-hallucinations-what-are-implications-financial-institutions)
- [Deficiency of LLMs in Finance - arXiv](https://arxiv.org/abs/2311.15548)
- [Reducing Hallucinations Through Prompt Engineering - Medium](https://devopslearning.medium.com/can-we-reduce-hallucinations-in-llms-through-prompt-engineering-df7d275d9cfa)
- [LLM Latency Benchmark 2026 - AIMultiple](https://research.aimultiple.com/llm-latency-benchmark/)
- [Self-Hosted LLM Guide 2026 - CreateAIAgent](https://createaiagent.net/self-hosted-llm/)

**WebSocket & Real-time Systems:**
- [WebSocket Architecture Best Practices - Ably](https://ably.com/topic/websocket-architecture-best-practices)
- [FastAPI WebSocket Memory Leak - GitHub Issue](https://github.com/fastapi/fastapi/discussions/11761)
- [Handling Large Scale WebSocket Traffic - Medium](https://hexshift.medium.com/how-to-handle-large-scale-websocket-traffic-with-fastapi-9c841f937f39)
- [FastAPI Memory Leak Investigation - BetterUp](https://build.betterup.com/chasing-a-memory-leak-in-our-async-fastapi-service-how-jemalloc-fixed-our-rss-creep/)

**React State Management:**
- [React State Management 2026 - Syncfusion](https://www.syncfusion.com/blogs/post/react-state-management-libraries)
- [State Management Best Practices 2026 - C-Sharp Corner](https://www.c-sharpcorner.com/article/state-management-in-react-2026-best-practices-tools-real-world-patterns/)
- [React State Management in 2025 - DeveloperWay](https://www.developerway.com/posts/react-state-management-2025)

**Trading Psychology & Behavioral Finance:**
- [Behavioral Finance in Trading - HeyGoTrade](https://www.heygotrade.com/en/blog/behavioral-finance-in-trading/)
- [Trading Psychology - Dukascopy](https://www.dukascopy.com/swiss/english/marketwatch/articles/trading-psychology/)
- [Common Behavioral Biases - Britannica Money](https://www.britannica.com/money/behavioral-biases-in-finance)

**Social Media APIs & Compliance:**
- [X API Rate Limits](https://docs.x.com/x-api/fundamentals/rate-limits)
- [X/Twitter API Pricing 2026 - GetLate](https://getlate.dev/blog/twitter-api-pricing)
- [LinkedIn Limits 2026 - MagicPost](https://magicpost.in/blog/linkedin-limitations)
- [AI Content Disclosure Rules - InfluencerMarketingHub](https://influencermarketinghub.com/ai-disclosure-rules/)
- [Marketing Compliance Guide 2026 - Puntt.ai](https://www.puntt.ai/blog/the-ultimate-marketing-compliance-guide-2026)
- [EU AI Labeling Requirement 2026 - WeVenture](https://weventure.de/en/blog/ai-labeling)

**Financial Compliance & Regulation:**
- [FINRA 2026 Regulatory Report - Sidley Austin](https://www.sidley.com/en/insights/newsupdates/2025/12/finra-issues-2026-regulatory-oversight-report)
- [Trading Bot Legal Considerations - BytePlus](https://www.byteplus.com/en/topic/546550)
- [Crypto Trading Bot Compliance - Altrady](https://www.altrady.com/crypto-trading/regulation-security-crypto-trading/how-to-stay-compliant-crypto-trading-bots)

**Hackathon Best Practices:**
- [How to Present a Successful Hackathon Demo - Devpost](https://info.devpost.com/blog/how-to-present-a-successful-hackathon-demo)
- [Hackathon Pitch Deck Guide - InkNarrates](https://www.inknarrates.com/post/hackathon-pitch-deck)
- [Common Hackathon Pitfalls - LinkedIn](https://www.linkedin.com/advice/1/what-some-common-pitfalls-mistakes-avoid-when-participating)
- [Corporate Hackathon Guide 2026 - Innovation Mode](https://theinnovationmode.com/the-innovation-blog/how-to-run-a-successful-corporate-hackathon)
- [Hack the Hackathon - Medium](https://medium.com/@eyal.shechtman/hack-the-hackathon-a-proven-formula-for-winning-231663ff00cc)

**Time Series Databases:**
- [Best Time Series Databases 2026 - CrateDB](https://cratedb.com/blog/best-time-series-databases)
- [Time Series Database Comparison - TigerData](https://www.tigerdata.com/learn/the-best-time-series-databases-compared)
- [Efficiently Store Time-Series Data - Medium](https://medium.com/@neslinesli93/how-to-efficiently-store-and-query-time-series-data-90313ff0ec20)

---

## Confidence Assessment

| Category | Level | Notes |
|----------|-------|-------|
| Deriv API | HIGH | Official documentation verified, specific technical requirements clear |
| LLM Hallucinations | HIGH | Multiple academic sources + real-world failure rates documented |
| FastAPI/WebSocket Memory | HIGH | GitHub issues with production examples, verified solutions |
| React State Management | HIGH | Current 2026 best practices from authoritative sources |
| Social Media APIs | HIGH | Official rate limit documentation from X, LinkedIn |
| Financial Compliance | MEDIUM | General regulatory landscape clear, Deriv-specific rules may vary |
| Hackathon Strategies | MEDIUM | Based on general best practices, not Deriv hackathon specifically |
| Behavioral Analysis | MEDIUM | Trading psychology well-documented, implementation patterns less specific |

## Research Notes

**Key insight:** The highest-risk pitfalls are the "silent failures" - WebSocket timeouts, memory leaks, and LLM hallucinations that don't manifest until production/demo conditions. Teams must explicitly test these scenarios, not just happy paths.

**Hackathon context matters:** Traditional "best practices" (proper database selection, clean architecture, comprehensive testing) become anti-patterns in 48-hour context. Speed and demo-ability trump code quality.

**Regulatory landscape:** 2026 brings heightened scrutiny of AI-generated financial content. Even hackathon projects need disclaimers to avoid legal questions from judges.

**Technology maturity:** Open-source LLMs are viable for hackathons, but latency and hallucination rates require careful mitigation strategies. Hosted APIs often better choice despite cost.

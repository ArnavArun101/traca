# DerivTrader Backend

This is the FastAPI backend for the DerivTrader AI Trading Analyst.

## Features
- **WebSocket Connection Manager**: Handles real-time client sessions.
- **Market Data Processor**: Integrates with Deriv API for market data updates.
- **LLM Engine**: Connects to local Ollama server for market analysis and coaching.
- **Behavioral Analyzer**: Detects trading patterns (win streaks, risk escalation).
- **Social Content Generator**: Drafts LinkedIn and X posts based on market trends.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Copy `.env.example` to `.env` and fill in your Deriv API token and other credentials.
   ```bash
   cp .env.example .env
   ```

3. **Run the Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Key Pitfall Preventions
- **API Rate Limiting**: The `MarketDataProcessor` uses Deriv's subscription model to efficiently receive updates while staying within API limits.
- **Hallucination Guardrails**: LLM prompts are structured to force the model to use only provided data and avoid fabricating numbers.
- **Async Processing**: Computationally expensive tasks (like LLM inference) are handled asynchronously to keep the WebSocket responsive.

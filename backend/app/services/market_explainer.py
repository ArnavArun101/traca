import logging
import json
from typing import Dict, List, Optional
from app.services.llm_engine import llm_engine

logger = logging.getLogger(__name__)


class MarketExplainer:
    """
    Provides plain-language market explanations and news/event summarisation
    using the LLM engine. Covers TODO items:
    - Plain-language market explanations ("Why did EUR/USD spike?")
    - News & event summarisation per instrument
    """

    async def explain_price_action(
        self, symbol: str, candles: List[Dict], indicators: Dict
    ) -> str:
        """
        Generate a plain-language explanation of recent price action for a symbol.
        Uses candle data and technical indicator results as context.
        """
        latest = indicators.get("latest", {})
        signals = indicators.get("signals", [])

        recent_candles = candles[-10:] if len(candles) > 10 else candles
        price_changes = []
        for i in range(1, len(recent_candles)):
            prev_close = recent_candles[i - 1]["close"]
            curr_close = recent_candles[i]["close"]
            change_pct = ((curr_close - prev_close) / prev_close) * 100
            price_changes.append(round(change_pct, 3))

        context = {
            "symbol": symbol,
            "current_price": latest.get("price"),
            "rsi": latest.get("rsi"),
            "macd_line": latest.get("macd_line"),
            "signal_line": latest.get("signal_line"),
            "sma_20": latest.get("sma_20"),
            "sma_50": latest.get("sma_50"),
            "recent_price_changes_pct": price_changes,
            "signals": signals,
        }

        system_prompt = (
            "You are a friendly trading analyst who explains market movements in simple, "
            "plain language that a beginner can understand. Avoid jargon unless you immediately "
            "explain it. Be concise (3-5 sentences). Use the provided data — do NOT invent numbers. "
            "If data is insufficient, say so honestly."
        )

        prompt = (
            f"Explain what's happening with {symbol} right now.\n\n"
            f"Market data:\n{json.dumps(context, indent=2)}\n\n"
            f"Give a brief, plain-language explanation."
        )

        result = await llm_engine.generate_response(prompt, system_prompt=system_prompt)
        return result.get("response", "Unable to generate explanation at this time.")

    async def answer_market_question(self, question: str, market_context: Dict) -> str:
        """
        Answer a specific user question about market behaviour in plain language.
        Example: 'Why did EUR/USD spike?'
        """
        system_prompt = (
            "You are an expert trading analyst who answers questions in plain, accessible language. "
            "Use the provided market context to ground your answer. "
            "IMPORTANT: Do not hallucinate numbers. Only reference data that is provided. "
            "If you don't have enough information, say so and suggest what data would help."
        )

        prompt = (
            f"User question: {question}\n\n"
            f"Available market context:\n{json.dumps(market_context, indent=2)}\n\n"
            f"Answer clearly and concisely."
        )

        result = await llm_engine.generate_response(prompt, system_prompt=system_prompt)
        return result.get("response", "Unable to answer at this time.")

    async def summarise_news(self, symbol: str, headlines: Optional[List[str]] = None) -> str:
        """
        Summarise recent news and events relevant to a given instrument.
        When real headlines aren't available, generates a contextual summary based on
        the instrument type and known market dynamics.
        """
        asset_context = ASSET_CONTEXT.get(symbol, {})
        asset_name = asset_context.get("name", symbol)
        asset_type = asset_context.get("type", "unknown")

        system_prompt = (
            "You are a financial news analyst. Provide a brief, factual summary of "
            "recent market events and news relevant to the given trading instrument. "
            "Be specific to the instrument type. Keep it under 5 sentences. "
            "IMPORTANT: Clearly label any statements as general context vs. breaking news. "
            "Do not fabricate specific headlines or events."
        )

        if headlines:
            headlines_text = "\n".join(f"- {h}" for h in headlines)
            prompt = (
                f"Summarise these recent news items for {asset_name} ({symbol}):\n\n"
                f"{headlines_text}\n\n"
                f"Provide a concise summary of how these could affect the price."
            )
        else:
            prompt = (
                f"Provide general market context for {asset_name} ({symbol}), "
                f"which is a {asset_type} instrument. "
                f"Mention the key factors that typically drive this instrument's price "
                f"and any general market conditions a trader should be aware of. "
                f"Be honest that you're providing general context, not real-time news."
            )

        result = await llm_engine.generate_response(prompt, system_prompt=system_prompt)
        return result.get("response", "Unable to generate news summary at this time.")


# -- Asset context for multi-asset awareness ----------------------------------

ASSET_CONTEXT: Dict[str, Dict] = {
    # Forex
    "frxEURUSD": {"name": "EUR/USD", "type": "forex", "category": "major"},
    "frxGBPUSD": {"name": "GBP/USD", "type": "forex", "category": "major"},
    "frxUSDJPY": {"name": "USD/JPY", "type": "forex", "category": "major"},
    "frxAUDUSD": {"name": "AUD/USD", "type": "forex", "category": "major"},
    "frxUSDCAD": {"name": "USD/CAD", "type": "forex", "category": "major"},
    "frxUSDCHF": {"name": "USD/CHF", "type": "forex", "category": "major"},
    "frxEURGBP": {"name": "EUR/GBP", "type": "forex", "category": "cross"},
    "frxEURJPY": {"name": "EUR/JPY", "type": "forex", "category": "cross"},
    # Crypto
    "cryBTCUSD": {"name": "BTC/USD", "type": "crypto", "category": "major"},
    "cryETHUSD": {"name": "ETH/USD", "type": "crypto", "category": "major"},
    "cryLTCUSD": {"name": "LTC/USD", "type": "crypto", "category": "altcoin"},
    # Synthetic indices (Deriv-specific)
    "R_10": {"name": "Volatility 10 Index", "type": "synthetic", "category": "volatility"},
    "R_25": {"name": "Volatility 25 Index", "type": "synthetic", "category": "volatility"},
    "R_50": {"name": "Volatility 50 Index", "type": "synthetic", "category": "volatility"},
    "R_75": {"name": "Volatility 75 Index", "type": "synthetic", "category": "volatility"},
    "R_100": {"name": "Volatility 100 Index", "type": "synthetic", "category": "volatility"},
    "1HZ10V": {"name": "Volatility 10 (1s) Index", "type": "synthetic", "category": "volatility"},
    "1HZ25V": {"name": "Volatility 25 (1s) Index", "type": "synthetic", "category": "volatility"},
    "1HZ50V": {"name": "Volatility 50 (1s) Index", "type": "synthetic", "category": "volatility"},
    "1HZ75V": {"name": "Volatility 75 (1s) Index", "type": "synthetic", "category": "volatility"},
    "1HZ100V": {"name": "Volatility 100 (1s) Index", "type": "synthetic", "category": "volatility"},
    "RDBULL": {"name": "Bull Market Index", "type": "synthetic", "category": "daily_reset"},
    "RDBEAR": {"name": "Bear Market Index", "type": "synthetic", "category": "daily_reset"},
}


market_explainer = MarketExplainer()

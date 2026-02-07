import logging
from typing import List, Dict, Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Calculates basic technical indicators: RSI, MACD, and moving averages.
    Operates on lists of candle dicts with 'close', 'high', 'low', 'open', 'epoch' keys.
    """

    def compute_all(self, candles: List[Dict]) -> Dict:
        """Compute all supported indicators for a set of candles."""
        if not candles or len(candles) < 2:
            return {"status": "insufficient_data", "message": "Need at least 2 candles for analysis."}

        closes = [c["close"] for c in candles]

        result: Dict = {"status": "success", "indicators": {}}

        sma_20 = self.sma(closes, period=20)
        sma_50 = self.sma(closes, period=50)
        ema_12 = self.ema(closes, period=12)
        ema_26 = self.ema(closes, period=26)

        result["indicators"]["sma_20"] = sma_20
        result["indicators"]["sma_50"] = sma_50
        result["indicators"]["ema_12"] = ema_12
        result["indicators"]["ema_26"] = ema_26

        rsi_values = self.rsi(closes)
        result["indicators"]["rsi"] = rsi_values

        macd_data = self.macd(closes)
        result["indicators"]["macd"] = macd_data

        result["latest"] = {
            "price": closes[-1],
            "sma_20": sma_20[-1] if sma_20 else None,
            "sma_50": sma_50[-1] if sma_50 else None,
            "ema_12": ema_12[-1] if ema_12 else None,
            "ema_26": ema_26[-1] if ema_26 else None,
            "rsi": rsi_values[-1] if rsi_values else None,
            "macd_line": macd_data["macd_line"][-1] if macd_data.get("macd_line") else None,
            "signal_line": macd_data["signal_line"][-1] if macd_data.get("signal_line") else None,
            "macd_histogram": macd_data["histogram"][-1] if macd_data.get("histogram") else None,
        }

        result["signals"] = self._generate_signals(result["latest"])

        return result

    # -- Moving Averages --------------------------------------------------

    def sma(self, closes: List[float], period: int = 20) -> List[Optional[float]]:
        """Simple Moving Average."""
        if len(closes) < period:
            return []
        series = pd.Series(closes)
        sma_series = series.rolling(window=period).mean()
        return [round(v, 5) if not np.isnan(v) else None for v in sma_series.tolist()]

    def ema(self, closes: List[float], period: int = 12) -> List[Optional[float]]:
        """Exponential Moving Average."""
        if len(closes) < period:
            return []
        series = pd.Series(closes)
        ema_series = series.ewm(span=period, adjust=False).mean()
        return [round(v, 5) if not np.isnan(v) else None for v in ema_series.tolist()]

    # -- RSI ---------------------------------------------------------------

    def rsi(self, closes: List[float], period: int = 14) -> List[Optional[float]]:
        """Relative Strength Index (Wilder's smoothing)."""
        if len(closes) < period + 1:
            return []

        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0.0)
        losses = np.where(deltas < 0, -deltas, 0.0)

        avg_gain = float(np.mean(gains[:period]))
        avg_loss = float(np.mean(losses[:period]))

        rsi_values: List[Optional[float]] = [None] * period  # first `period` values undefined

        for i in range(period, len(deltas)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period

            if avg_loss == 0:
                rsi_values.append(100.0)
            else:
                rs = avg_gain / avg_loss
                rsi_values.append(round(100.0 - (100.0 / (1.0 + rs)), 2))

        return rsi_values

    # -- MACD --------------------------------------------------------------

    def macd(
        self,
        closes: List[float],
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> Dict:
        """MACD (Moving Average Convergence Divergence)."""
        if len(closes) < slow_period:
            return {"macd_line": [], "signal_line": [], "histogram": []}

        series = pd.Series(closes)
        ema_fast = series.ewm(span=fast_period, adjust=False).mean()
        ema_slow = series.ewm(span=slow_period, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            "macd_line": [round(v, 5) for v in macd_line.tolist()],
            "signal_line": [round(v, 5) for v in signal_line.tolist()],
            "histogram": [round(v, 5) for v in histogram.tolist()],
        }

    # -- Signal Generation -------------------------------------------------

    def _generate_signals(self, latest: Dict) -> List[str]:
        """Generate human-readable trading signals from latest indicator values."""
        signals: List[str] = []

        rsi_val = latest.get("rsi")
        if rsi_val is not None:
            if rsi_val >= 70:
                signals.append(f"RSI is {rsi_val} — overbought territory. Price may pull back.")
            elif rsi_val <= 30:
                signals.append(f"RSI is {rsi_val} — oversold territory. Price may bounce up.")

        macd_line = latest.get("macd_line")
        signal_line = latest.get("signal_line")
        if macd_line is not None and signal_line is not None:
            if macd_line > signal_line:
                signals.append("MACD is above signal line — bullish momentum.")
            else:
                signals.append("MACD is below signal line — bearish momentum.")

        price = latest.get("price")
        sma_20 = latest.get("sma_20")
        sma_50 = latest.get("sma_50")
        if price is not None and sma_20 is not None:
            if price > sma_20:
                signals.append("Price is above the 20-period SMA — short-term uptrend.")
            else:
                signals.append("Price is below the 20-period SMA — short-term downtrend.")
        if sma_20 is not None and sma_50 is not None:
            if sma_20 > sma_50:
                signals.append("20 SMA is above 50 SMA — golden cross (bullish).")
            else:
                signals.append("20 SMA is below 50 SMA — death cross (bearish).")

        if not signals:
            signals.append("No strong signals detected at this time.")

        return signals


technical_indicators = TechnicalIndicators()

import logging
from typing import List, Dict
from app.models.db_models import Trade

logger = logging.getLogger(__name__)

class BehavioralAnalyzer:
    def __init__(self):
        self.default_rules = {
            "max_trade_size_multiple": 2.0,
            "min_seconds_between_trades": 60,
            "max_trades_per_hour": 5,
        }

    def analyze_trades(self, trades: List[Trade]) -> Dict:
        """
        Analyze trade history for patterns and biases.
        - Win/loss streaks
        - Risk escalation
        - Overtrading
        """
        if not trades:
            return {"status": "no_data", "message": "No trade history to analyze."}

        streaks = self._detect_streaks(trades)
        risk_alerts = self._analyze_risk(trades)
        overtrading_alerts = self._detect_overtrading(trades)
        rapid_entry_alerts = self._detect_rapid_entries(trades)
        discipline = self._calculate_discipline_score(trades, self.default_rules)
        sentiment = self._calculate_sentiment(trades)
        nudges = self._generate_nudges(
            risk_alerts + overtrading_alerts + rapid_entry_alerts, streaks
        )

        return {
            "status": "success",
            "metrics": {
                "total_trades": len(trades),
                "win_rate": self._calculate_win_rate(trades),
                "streaks": streaks,
                "discipline_score": discipline,
            },
            "alerts": {
                "risk": risk_alerts,
                "overtrading": overtrading_alerts,
                "rapid_entries": rapid_entry_alerts,
            },
            "nudges": nudges,
            "sentiment": sentiment,
        }

    def _detect_streaks(self, trades: List[Trade]) -> Dict:
        results = []
        for trade in trades:
            profit = getattr(trade, "profit", None)
            if profit is None:
                continue
            results.append(1 if profit > 0 else -1 if profit < 0 else 0)
        if not results:
            return {"current_streak": 0, "type": "unknown"}

        current = results[-1]
        streak = 1
        for i in range(len(results) - 2, -1, -1):
            if results[i] == current:
                streak += 1
            else:
                break
        streak_type = "win" if current == 1 else "loss" if current == -1 else "neutral"
        return {"current_streak": streak, "type": streak_type}

    def _analyze_risk(self, trades: List[Trade]) -> List[str]:
        alerts = []
        if len(trades) > 1:
            last_trade = trades[-1]
            avg_amount = sum(t.amount for t in trades[:-1]) / (len(trades) - 1)
            if last_trade.amount > avg_amount * 2:
                alerts.append("Risk escalation: last trade size is significantly higher than average.")
        return alerts

    def _detect_overtrading(self, trades: List[Trade]) -> List[str]:
        alerts = []
        if not trades:
            return alerts
        latest_ts = max(t.timestamp for t in trades)
        window = [t for t in trades if (latest_ts - t.timestamp) <= 3600]
        if len(window) > self.default_rules["max_trades_per_hour"]:
            alerts.append("Overtrading: high trade frequency in the last hour.")
        return alerts

    def _detect_rapid_entries(self, trades: List[Trade]) -> List[str]:
        alerts = []
        if len(trades) < 2:
            return alerts
        gaps = []
        sorted_trades = sorted(trades, key=lambda t: t.timestamp)
        for i in range(1, len(sorted_trades)):
            gaps.append(sorted_trades[i].timestamp - sorted_trades[i - 1].timestamp)
        rapid = [g for g in gaps if g < self.default_rules["min_seconds_between_trades"]]
        if len(rapid) >= 2:
            alerts.append("Rapid entries: multiple trades placed in quick succession.")
        return alerts

    def _calculate_win_rate(self, trades: List[Trade]) -> float:
        results = []
        for trade in trades:
            profit = getattr(trade, "profit", None)
            if profit is None:
                continue
            results.append(1 if profit > 0 else 0)
        if not results:
            return 0.0
        return sum(results) / len(results)

    def _calculate_sentiment(self, trades: List[Trade]) -> float:
        # -1.0 to 1.0
        results = []
        for trade in trades:
            profit = getattr(trade, "profit", None)
            if profit is None:
                continue
            results.append(1 if profit > 0 else -1 if profit < 0 else 0)
        if not results:
            return 0.0
        return sum(results) / len(results)

    def _calculate_discipline_score(self, trades: List[Trade], rules: Dict) -> Dict:
        if not trades:
            return {"score": 0.0, "rule_breaks": {}}

        max_multiple = rules.get("max_trade_size_multiple", 2.0)
        min_gap = rules.get("min_seconds_between_trades", 60)
        max_per_hour = rules.get("max_trades_per_hour", 5)

        avg_amount = sum(t.amount for t in trades) / len(trades)
        sorted_trades = sorted(trades, key=lambda t: t.timestamp)

        rule_breaks = {
            "oversized_trade": 0,
            "rapid_entry": 0,
            "overtrading": 0,
        }

        latest_ts = max(t.timestamp for t in trades)
        recent = [t for t in trades if (latest_ts - t.timestamp) <= 3600]
        if len(recent) > max_per_hour:
            rule_breaks["overtrading"] += len(recent) - max_per_hour

        for idx, trade in enumerate(sorted_trades):
            if avg_amount > 0 and trade.amount > avg_amount * max_multiple:
                rule_breaks["oversized_trade"] += 1
            if idx > 0:
                gap = trade.timestamp - sorted_trades[idx - 1].timestamp
                if gap < min_gap:
                    rule_breaks["rapid_entry"] += 1

        total_breaks = sum(rule_breaks.values())
        total_trades = len(trades)
        score = max(0.0, 1.0 - (total_breaks / max(1, total_trades)))
        return {"score": round(score, 2), "rule_breaks": rule_breaks}

    def _generate_nudges(self, alerts: List[str], streaks: Dict) -> List[str]:
        nudges = []
        for alert in alerts:
            if "Risk escalation" in alert:
                nudges.append("Your last position size is larger than usual. Was that intentional?")
            if "Overtrading" in alert:
                nudges.append("High trade frequency detected. Consider pausing to review your plan.")
            if "Rapid entries" in alert:
                nudges.append("Multiple rapid entries detected. Take a short break to reset.")
        if streaks.get("type") == "loss" and streaks.get("current_streak", 0) >= 3:
            nudges.append("You’re on a loss streak. Consider a short break or reducing size.")
        return nudges

behavioral_analyzer = BehavioralAnalyzer()

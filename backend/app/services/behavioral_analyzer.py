import logging
from typing import List, Dict
from app.models.db_models import Trade

logger = logging.getLogger(__name__)

class BehavioralAnalyzer:
    def __init__(self):
        pass

    def analyze_trades(self, trades: List[Trade]) -> Dict:
        """
        Analyze trade history for patterns and biases.
        - Win/loss streaks
        - Risk escalation
        - Overtrading
        """
        if not trades:
            return {"status": "no_data", "message": "No trade history to analyze."}

        # Simple streak detection
        streaks = self._detect_streaks(trades)
        
        # Risk analysis (comparing last trade size with average)
        risk_alert = self._analyze_risk(trades)

        return {
            "status": "success",
            "metrics": {
                "total_trades": len(trades),
                "win_rate": self._calculate_win_rate(trades),
                "streaks": streaks
            },
            "alerts": risk_alert,
            "sentiment": self._calculate_sentiment(trades)
        }

    def _detect_streaks(self, trades: List[Trade]) -> Dict:
        # Placeholder logic
        return {"current_streak": 0, "type": "neutral"}

    def _analyze_risk(self, trades: List[Trade]) -> List[str]:
        alerts = []
        if len(trades) > 1:
            last_trade = trades[-1]
            avg_amount = sum(t.amount for t in trades[:-1]) / (len(trades) - 1)
            if last_trade.amount > avg_amount * 2:
                alerts.append("Risk Escalation: Last trade size is significantly higher than average.")
        return alerts

    def _calculate_win_rate(self, trades: List[Trade]) -> float:
        # This requires knowing if a trade was a win or loss, which we might need to fetch from the history data
        return 0.5 

    def _calculate_sentiment(self, trades: List[Trade]) -> float:
        # -1.0 to 1.0
        return 0.0

behavioral_analyzer = BehavioralAnalyzer()

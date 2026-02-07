"""
Trading Psychology Models.

Defines psychological patterns, emotional states, and behavioral tags
for analyzing trader behavior and providing coaching feedback.
"""

from enum import Enum
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from datetime import datetime


class PsychologyTag(Enum):
    """
    Psychological patterns detected in trading behavior.
    Based on common behavioral finance research.
    """
    # Fear-based patterns
    FOMO = "fomo"                      # Fear of missing out - chasing entries
    PANIC_EXIT = "panic_exit"          # Exiting on fear, not plan
    HESITATION = "hesitation"          # Missing planned entries due to fear
    
    # Greed-based patterns
    OVERTRADING = "overtrading"        # Too many trades, often after wins
    OVERSIZING = "oversizing"          # Position too large for account/plan
    GREED_HOLD = "greed_hold"          # Holding winners too long, giving back gains
    
    # Revenge/Frustration patterns
    REVENGE_TRADE = "revenge_trade"    # Trading to recover losses quickly
    TILT = "tilt"                      # Emotional spiral, multiple bad decisions
    AVERAGING_DOWN = "averaging_down"  # Adding to losers (when not planned)
    
    # Discipline patterns
    PLAN_DEVIATION = "plan_deviation"  # Straying from trading plan
    EARLY_EXIT = "early_exit"          # Closing winners too early
    MOVING_STOPS = "moving_stops"      # Widening stop losses
    
    # Positive patterns
    DISCIPLINED = "disciplined"        # Following plan consistently
    PATIENT_ENTRY = "patient_entry"    # Waiting for proper setup
    PROPER_SIZING = "proper_sizing"    # Correct position sizing


class EmotionalState(Enum):
    """Current emotional state assessment."""
    CALM = "calm"
    CONFIDENT = "confident"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    EUPHORIC = "euphoric"
    FEARFUL = "fearful"
    NEUTRAL = "neutral"


class RiskLevel(Enum):
    """Risk level of current trading behavior."""
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BehaviorSignal:
    """
    A detected behavioral signal from trade analysis.
    """
    tag: PsychologyTag
    confidence: float  # 0.0 to 1.0
    detected_at: datetime
    trade_ids: List[int] = field(default_factory=list)
    evidence: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "tag": self.tag.value,
            "confidence": self.confidence,
            "detected_at": self.detected_at.isoformat(),
            "trade_ids": self.trade_ids,
            "evidence": self.evidence
        }


@dataclass
class EmotionCost:
    """
    Quantified cost of emotional trading decisions.
    """
    tag: PsychologyTag
    period_start: datetime
    period_end: datetime
    estimated_cost: float  # In account currency
    trade_count: int
    avg_loss_per_trade: float
    comparison_baseline: float  # What disciplined trades averaged
    
    def to_dict(self) -> Dict:
        return {
            "tag": self.tag.value,
            "period": {
                "start": self.period_start.isoformat(),
                "end": self.period_end.isoformat()
            },
            "estimated_cost": round(self.estimated_cost, 2),
            "trade_count": self.trade_count,
            "avg_loss_per_trade": round(self.avg_loss_per_trade, 2),
            "comparison_baseline": round(self.comparison_baseline, 2)
        }


@dataclass
class TradingSession:
    """
    Represents a trading session for behavioral analysis.
    """
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    trade_count: int = 0
    win_count: int = 0
    loss_count: int = 0
    net_pnl: float = 0.0
    detected_tags: List[BehaviorSignal] = field(default_factory=list)
    emotional_state: EmotionalState = EmotionalState.NEUTRAL
    risk_level: RiskLevel = RiskLevel.LOW
    discipline_score: float = 100.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "trade_count": self.trade_count,
            "win_rate": self.win_count / self.trade_count if self.trade_count > 0 else 0,
            "net_pnl": round(self.net_pnl, 2),
            "detected_tags": [t.to_dict() for t in self.detected_tags],
            "emotional_state": self.emotional_state.value,
            "risk_level": self.risk_level.value,
            "discipline_score": round(self.discipline_score, 1)
        }


@dataclass 
class DisciplineMetrics:
    """
    Discipline scoring metrics.
    """
    total_trades: int
    planned_trades: int  # Trades that followed the plan
    rule_breaks: int
    position_size_violations: int
    stop_loss_moves: int
    revenge_trades: int
    fomo_entries: int
    
    @property
    def discipline_score(self) -> float:
        """Calculate overall discipline score (0-100)."""
        if self.total_trades == 0:
            return 100.0
        
        violations = (
            self.rule_breaks + 
            self.position_size_violations + 
            self.stop_loss_moves +
            self.revenge_trades +
            self.fomo_entries
        )
        
        score = max(0, 100 - (violations / self.total_trades * 100))
        return round(score, 1)
    
    @property
    def plan_adherence(self) -> float:
        """Percentage of trades following the plan."""
        if self.total_trades == 0:
            return 100.0
        return round(self.planned_trades / self.total_trades * 100, 1)
    
    def to_dict(self) -> Dict:
        return {
            "total_trades": self.total_trades,
            "planned_trades": self.planned_trades,
            "plan_adherence": f"{self.plan_adherence}%",
            "discipline_score": self.discipline_score,
            "violations": {
                "rule_breaks": self.rule_breaks,
                "position_size_violations": self.position_size_violations,
                "stop_loss_moves": self.stop_loss_moves,
                "revenge_trades": self.revenge_trades,
                "fomo_entries": self.fomo_entries
            }
        }


@dataclass
class Streak:
    """
    Represents a trading streak (winning or losing).
    """
    type: str  # "win" or "loss"
    count: int
    start_date: datetime
    end_date: Optional[datetime] = None
    total_pnl: float = 0.0
    is_current: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "count": self.count,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "total_pnl": round(self.total_pnl, 2),
            "is_current": self.is_current
        }


# Detection thresholds for behavioral patterns
DETECTION_THRESHOLDS = {
    # Position sizing
    "oversizing_multiplier": 1.5,      # Position > 1.5x average = oversizing
    "undersizing_multiplier": 0.5,     # Position < 0.5x average after loss = hesitation
    
    # Time-based
    "rapid_entry_seconds": 60,         # Entry within 60s of previous exit = potential revenge
    "session_overtrade_count": 10,     # More than 10 trades in a session = overtrading
    
    # Loss-based
    "revenge_loss_threshold": 2,       # 2+ losses before rapid re-entry = revenge trading
    "tilt_consecutive_losses": 3,      # 3+ consecutive losses with increasing size = tilt
    
    # Win-based  
    "euphoria_win_streak": 4,          # 4+ consecutive wins may lead to overconfidence
    "size_increase_after_wins": 1.3,   # 30% size increase after wins = potential greed
    
    # Discipline
    "discipline_excellent": 90,
    "discipline_good": 75,
    "discipline_needs_work": 50,
    "discipline_poor": 25
}


# Human-readable descriptions for feedback
TAG_DESCRIPTIONS = {
    PsychologyTag.FOMO: {
        "name": "FOMO (Fear of Missing Out)",
        "description": "Entering trades impulsively, often chasing price moves",
        "impact": "Usually results in poor entry prices and higher risk",
        "coaching": "Wait for your setup. The market will always offer new opportunities."
    },
    PsychologyTag.PANIC_EXIT: {
        "name": "Panic Exit",
        "description": "Closing positions due to fear rather than your trading plan",
        "impact": "Often exits at the worst time, right before price reverses",
        "coaching": "Trust your analysis. Set stops based on technicals, not emotions."
    },
    PsychologyTag.HESITATION: {
        "name": "Hesitation",
        "description": "Missing planned entries due to fear or second-guessing",
        "impact": "Missed opportunities and frustration from watching trades work without you",
        "coaching": "If the setup matches your criteria, execute. Review, don't regret."
    },
    PsychologyTag.OVERTRADING: {
        "name": "Overtrading",
        "description": "Taking too many trades, often driven by boredom or the need for action",
        "impact": "Higher transaction costs, lower quality setups, mental fatigue",
        "coaching": "Quality over quantity. Your best trades come from patience."
    },
    PsychologyTag.OVERSIZING: {
        "name": "Oversizing",
        "description": "Position size larger than your risk management rules allow",
        "impact": "A single loss can significantly damage your account",
        "coaching": "Risk 1-2% per trade maximum. Consistent sizing builds consistent results."
    },
    PsychologyTag.REVENGE_TRADE: {
        "name": "Revenge Trading",
        "description": "Trading to quickly recover losses, often with larger size or poor setups",
        "impact": "Usually compounds losses and leads to emotional spiral",
        "coaching": "Losses are part of trading. Step away, review your plan, trade fresh tomorrow."
    },
    PsychologyTag.TILT: {
        "name": "Tilt",
        "description": "Emotional state where decisions become increasingly irrational",
        "impact": "Can turn a bad day into a devastating one",
        "coaching": "Recognize the signs. When you're tilting, the best trade is no trade."
    },
    PsychologyTag.DISCIPLINED: {
        "name": "Disciplined Trading",
        "description": "Following your trading plan consistently",
        "impact": "Long-term profitability and reduced emotional stress",
        "coaching": "Keep it up! Discipline is your edge."
    },
    PsychologyTag.PLAN_DEVIATION: {
        "name": "Plan Deviation",
        "description": "Straying from your defined trading rules",
        "impact": "Makes it impossible to evaluate what actually works",
        "coaching": "If you want to change your plan, do it before the market opens, not during."
    },
    PsychologyTag.EARLY_EXIT: {
        "name": "Early Exit",
        "description": "Closing winning trades before reaching your target",
        "impact": "Reduces average win size, hurts risk/reward ratio",
        "coaching": "Let winners run. Your targets exist for a reason."
    }
}


def get_tag_description(tag: PsychologyTag) -> Dict:
    """Get human-readable description for a psychology tag."""
    return TAG_DESCRIPTIONS.get(tag, {
        "name": tag.value.replace("_", " ").title(),
        "description": "Behavioral pattern detected",
        "impact": "May affect trading performance",
        "coaching": "Review your trading plan and decision process."
    })

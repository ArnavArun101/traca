"""
Behavioral Coaching Service.

Provides real-time coaching nudges, reflection prompts, and personalized
feedback to help traders maintain discipline and emotional balance.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from app.models.db_models import Trade
from app.models.psychology_models import (
    PsychologyTag,
    EmotionalState,
    RiskLevel,
    BehaviorSignal,
    DisciplineMetrics,
    DETECTION_THRESHOLDS,
    get_tag_description
)
from app.services.behavioral_analyzer import behavioral_analyzer
from app.services.llm_engine import llm_engine

logger = logging.getLogger(__name__)


class NudgeType(Enum):
    """Types of coaching nudges."""
    WARNING = "warning"           # Risk/concern alert
    SUGGESTION = "suggestion"     # Gentle recommendation
    REFLECTION = "reflection"     # Prompt for self-reflection
    CELEBRATION = "celebration"   # Positive reinforcement
    BREAK = "break"              # Suggest taking a break
    LIMIT = "limit"              # Suggest setting limits


class NudgeUrgency(Enum):
    """Urgency level of nudges."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Nudge:
    """A coaching nudge delivered to the trader."""
    id: str
    type: NudgeType
    urgency: NudgeUrgency
    title: str
    message: str
    action_suggestion: str
    trigger: str  # What triggered this nudge
    created_at: datetime = field(default_factory=datetime.now)
    dismissed: bool = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "urgency": self.urgency.value,
            "title": self.title,
            "message": self.message,
            "action_suggestion": self.action_suggestion,
            "trigger": self.trigger,
            "created_at": self.created_at.isoformat(),
            "dismissed": self.dismissed
        }


# Pre-defined nudge templates
NUDGE_TEMPLATES = {
    PsychologyTag.OVERSIZING: {
        "type": NudgeType.WARNING,
        "urgency": NudgeUrgency.MEDIUM,
        "title": "Position Size Check",
        "message": "Your position size is {ratio}x your average. Is this intentional?",
        "action": "Review your risk management rules before confirming this trade."
    },
    PsychologyTag.REVENGE_TRADE: {
        "type": NudgeType.WARNING,
        "urgency": NudgeUrgency.HIGH,
        "title": "Pause and Reflect",
        "message": "You've had {loss_count} recent losses and are entering quickly. This pattern often leads to more losses.",
        "action": "Step away for 15 minutes. The market will still be here."
    },
    PsychologyTag.FOMO: {
        "type": NudgeType.SUGGESTION,
        "urgency": NudgeUrgency.MEDIUM,
        "title": "Check Your Setup",
        "message": "You're entering quickly after the last trade. Does this match your trading plan?",
        "action": "Verify this setup meets your criteria before entering."
    },
    PsychologyTag.TILT: {
        "type": NudgeType.BREAK,
        "urgency": NudgeUrgency.CRITICAL,
        "title": "Take a Break",
        "message": "Your recent trading pattern suggests emotional decision-making. Continuing now increases risk.",
        "action": "Close your trading platform. Come back tomorrow with fresh eyes."
    },
    PsychologyTag.OVERTRADING: {
        "type": NudgeType.LIMIT,
        "urgency": NudgeUrgency.MEDIUM,
        "title": "Daily Limit Approaching",
        "message": "You've taken {count} trades today. Your best results usually come from fewer, higher-quality setups.",
        "action": "Consider setting a daily trade limit. Quality over quantity."
    },
    PsychologyTag.DISCIPLINED: {
        "type": NudgeType.CELEBRATION,
        "urgency": NudgeUrgency.LOW,
        "title": "Great Discipline!",
        "message": "You're following your trading plan consistently. This is how long-term success is built.",
        "action": "Keep it up! Your discipline is your edge."
    }
}


# Reflection prompts for different situations
REFLECTION_PROMPTS = {
    "post_loss": [
        "What did you learn from this trade?",
        "Was this loss due to the market or your execution?",
        "Did you follow your trading plan? If not, what caused the deviation?",
        "What would you do differently next time?"
    ],
    "post_win": [
        "What went right with this trade?",
        "Did you follow your plan, or did you get lucky?",
        "How can you replicate this success?",
        "Did you take profits according to your plan?"
    ],
    "end_of_day": [
        "What was your best decision today?",
        "What was your worst decision today?",
        "Did you stick to your trading plan?",
        "What will you do differently tomorrow?"
    ],
    "before_trading": [
        "What is your plan for today?",
        "What setups are you looking for?",
        "What is your maximum risk for today?",
        "How are you feeling? Are you in the right state to trade?"
    ],
    "after_streak": [
        "How are you feeling after this streak?",
        "Is there any urge to change your approach?",
        "Are you staying within your risk parameters?",
        "What's your plan for the next trade?"
    ]
}


class BehavioralCoach:
    """
    Provides real-time coaching and nudges to help traders maintain discipline.
    """
    
    def __init__(self):
        self._session_nudges: Dict[str, List[Nudge]] = {}
        self._nudge_cooldowns: Dict[str, datetime] = {}  # Prevent spam
        self._cooldown_minutes = 5
    
    def evaluate_trade(
        self, 
        trade: Trade, 
        recent_trades: List[Trade],
        session_id: str
    ) -> List[Nudge]:
        """
        Evaluate a trade and generate appropriate nudges.
        
        Args:
            trade: The trade being evaluated
            recent_trades: Recent trade history for context
            session_id: Current session identifier
            
        Returns:
            List of nudges to display
        """
        nudges = []
        all_trades = recent_trades + [trade]
        
        # Analyze with behavioral analyzer
        analysis = behavioral_analyzer.analyze_trades(all_trades, session_id)
        
        if analysis.get("status") != "success":
            return nudges
        
        # Check detected patterns
        patterns = analysis.get("psychology", {}).get("detected_patterns", [])
        risk_level = analysis.get("psychology", {}).get("risk_level", "low")
        
        for pattern in patterns[-3:]:  # Focus on recent patterns
            tag_str = pattern.get("tag")
            try:
                tag = PsychologyTag(tag_str)
            except ValueError:
                continue
            
            nudge = self._create_nudge_from_pattern(tag, pattern, session_id)
            if nudge and self._can_send_nudge(session_id, tag):
                nudges.append(nudge)
                self._record_nudge(session_id, nudge)
        
        # Check risk level for additional nudges
        if risk_level == "critical":
            nudges.append(self._create_break_nudge(session_id))
        elif risk_level == "high":
            nudges.append(self._create_caution_nudge(session_id, analysis))
        
        # Check for positive reinforcement
        discipline = analysis.get("discipline", {})
        if discipline.get("discipline_score", 0) >= 90:
            celebration = self._create_celebration_nudge(session_id, discipline)
            if celebration:
                nudges.append(celebration)
        
        return nudges
    
    def _create_nudge_from_pattern(
        self, 
        tag: PsychologyTag, 
        pattern: Dict,
        session_id: str
    ) -> Optional[Nudge]:
        """Create a nudge from a detected pattern."""
        template = NUDGE_TEMPLATES.get(tag)
        if not template:
            return None
        
        evidence = pattern.get("evidence", {})
        
        # Format message with evidence
        message = template["message"]
        if "{ratio}" in message:
            message = message.format(ratio=evidence.get("ratio", "N/A"))
        if "{loss_count}" in message:
            message = message.format(loss_count=evidence.get("recent_losses", "multiple"))
        if "{count}" in message:
            message = message.format(count=evidence.get("trade_count", "many"))
        
        nudge_id = f"{session_id}_{tag.value}_{datetime.now().strftime('%H%M%S')}"
        
        return Nudge(
            id=nudge_id,
            type=template["type"],
            urgency=template["urgency"],
            title=template["title"],
            message=message,
            action_suggestion=template["action"],
            trigger=tag.value
        )
    
    def _create_break_nudge(self, session_id: str) -> Nudge:
        """Create a nudge suggesting a break."""
        return Nudge(
            id=f"{session_id}_break_{datetime.now().strftime('%H%M%S')}",
            type=NudgeType.BREAK,
            urgency=NudgeUrgency.CRITICAL,
            title="Time to Step Away",
            message="Your recent trading pattern shows signs of emotional decision-making. The best trade right now is no trade.",
            action_suggestion="Close your charts. Take at least a 30-minute break. Come back when you feel calm.",
            trigger="high_risk_level"
        )
    
    def _create_caution_nudge(self, session_id: str, analysis: Dict) -> Nudge:
        """Create a caution nudge for elevated risk."""
        return Nudge(
            id=f"{session_id}_caution_{datetime.now().strftime('%H%M%S')}",
            type=NudgeType.WARNING,
            urgency=NudgeUrgency.HIGH,
            title="Elevated Risk Detected",
            message="Your trading behavior suggests increased emotional involvement. Consider reducing position sizes.",
            action_suggestion="Review your last few trades. Are they following your plan?",
            trigger="elevated_risk"
        )
    
    def _create_celebration_nudge(self, session_id: str, discipline: Dict) -> Optional[Nudge]:
        """Create a celebration nudge for good discipline."""
        if not self._can_send_nudge(session_id, PsychologyTag.DISCIPLINED):
            return None
        
        score = discipline.get("discipline_score", 0)
        return Nudge(
            id=f"{session_id}_celebration_{datetime.now().strftime('%H%M%S')}",
            type=NudgeType.CELEBRATION,
            urgency=NudgeUrgency.LOW,
            title="Excellent Discipline!",
            message=f"Your discipline score is {score}%. You're trading like a professional.",
            action_suggestion="Keep following your plan. Consistency is your competitive advantage.",
            trigger="high_discipline"
        )
    
    def _can_send_nudge(self, session_id: str, tag: PsychologyTag) -> bool:
        """Check if we can send a nudge (cooldown check)."""
        key = f"{session_id}_{tag.value}"
        last_sent = self._nudge_cooldowns.get(key)
        
        if last_sent:
            if datetime.now() - last_sent < timedelta(minutes=self._cooldown_minutes):
                return False
        
        return True
    
    def _record_nudge(self, session_id: str, nudge: Nudge):
        """Record that a nudge was sent."""
        # Update cooldown
        self._nudge_cooldowns[f"{session_id}_{nudge.trigger}"] = datetime.now()
        
        # Store in session
        if session_id not in self._session_nudges:
            self._session_nudges[session_id] = []
        self._session_nudges[session_id].append(nudge)
    
    def get_reflection_prompts(self, context: str) -> List[str]:
        """
        Get reflection prompts for a specific context.
        
        Args:
            context: One of "post_loss", "post_win", "end_of_day", etc.
        
        Returns:
            List of reflection questions
        """
        return REFLECTION_PROMPTS.get(context, REFLECTION_PROMPTS["end_of_day"])
    
    def get_session_nudges(self, session_id: str) -> List[Dict]:
        """Get all nudges sent in a session."""
        nudges = self._session_nudges.get(session_id, [])
        return [n.to_dict() for n in nudges]
    
    def dismiss_nudge(self, session_id: str, nudge_id: str) -> bool:
        """Mark a nudge as dismissed."""
        nudges = self._session_nudges.get(session_id, [])
        for nudge in nudges:
            if nudge.id == nudge_id:
                nudge.dismissed = True
                return True
        return False
    
    async def generate_personalized_coaching(
        self, 
        analysis: Dict, 
        context: str = "general"
    ) -> str:
        """
        Generate personalized coaching message using LLM.
        
        Args:
            analysis: Output from behavioral_analyzer.analyze_trades()
            context: Context for the coaching (e.g., "post_loss", "end_of_day")
        
        Returns:
            Personalized coaching message
        """
        system_prompt = """You are a supportive trading coach. Your role is to help traders 
improve their discipline and emotional control. Be encouraging but honest. Focus on:
- Acknowledging what they did well
- Gently pointing out areas for improvement
- Providing specific, actionable advice
- Maintaining a supportive, non-judgmental tone

IMPORTANT: Never be preachy or condescending. Speak like a trusted mentor."""

        # Build context from analysis
        discipline_score = analysis.get("discipline", {}).get("discipline_score", "N/A")
        emotional_state = analysis.get("psychology", {}).get("emotional_state", "neutral")
        patterns = analysis.get("psychology", {}).get("detected_patterns", [])
        alerts = analysis.get("alerts", [])
        
        prompt = f"""Based on this trading session analysis, provide brief, personalized coaching:

Discipline Score: {discipline_score}%
Emotional State: {emotional_state}
Detected Patterns: {[p.get('tag') for p in patterns]}
Alerts: {[a.get('type') for a in alerts]}
Context: {context}

Provide 2-3 sentences of coaching feedback. Be specific and actionable."""

        result = await llm_engine.generate_response(prompt, system_prompt=system_prompt)
        return result.get("response", "Keep following your trading plan and stay disciplined.")
    
    def suggest_daily_limits(self, recent_trades: List[Trade]) -> Dict:
        """
        Suggest daily trading limits based on historical performance.
        
        Args:
            recent_trades: Recent trade history
        
        Returns:
            Suggested limits
        """
        if len(recent_trades) < 10:
            return {
                "max_trades": 5,
                "max_loss_percent": 2.0,
                "reason": "Not enough data. Starting with conservative limits."
            }
        
        # Analyze performance by trade count per day
        from collections import defaultdict
        daily_stats = defaultdict(lambda: {"trades": 0, "pnl": 0})
        
        for trade in recent_trades:
            date = datetime.fromtimestamp(trade.timestamp).strftime("%Y-%m-%d")
            daily_stats[date]["trades"] += 1
            daily_stats[date]["pnl"] += getattr(trade, "pnl", 0)
        
        # Find optimal trade count
        profitable_days = [d for d in daily_stats.values() if d["pnl"] > 0]
        if profitable_days:
            avg_trades_profitable = sum(d["trades"] for d in profitable_days) / len(profitable_days)
        else:
            avg_trades_profitable = 5
        
        return {
            "max_trades": min(10, max(3, int(avg_trades_profitable + 2))),
            "max_loss_percent": 2.0,
            "suggested_break_after_losses": 3,
            "reason": f"Based on your best days averaging {avg_trades_profitable:.1f} trades."
        }
    
    def get_pre_trade_checklist(self) -> List[Dict]:
        """Get a pre-trade checklist to review before entering."""
        return [
            {
                "item": "Does this setup match my trading plan?",
                "category": "plan_adherence"
            },
            {
                "item": "Is my position size within my risk rules?",
                "category": "risk_management"
            },
            {
                "item": "Do I have a clear stop loss level?",
                "category": "risk_management"
            },
            {
                "item": "Do I have a clear profit target?",
                "category": "trade_management"
            },
            {
                "item": "Am I trading because of FOMO or my analysis?",
                "category": "emotional_check"
            },
            {
                "item": "Am I trying to recover recent losses?",
                "category": "emotional_check"
            },
            {
                "item": "Would I take this trade if I just had a big win?",
                "category": "objectivity"
            }
        ]


behavioral_coach = BehavioralCoach()

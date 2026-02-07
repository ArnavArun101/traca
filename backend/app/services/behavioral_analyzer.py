"""Behavioral Analysis Service.

Analyzes trading patterns to detect psychological biases, calculate
discipline scores, and identify emotional trading behaviors.
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from app.models.db_models import Trade
from app.models.psychology_models import (
    PsychologyTag,
    EmotionalState,
    RiskLevel,
    BehaviorSignal,
    EmotionCost,
    DisciplineMetrics,
    Streak,
    DETECTION_THRESHOLDS,
    get_tag_description
)

logger = logging.getLogger(__name__)


class BehavioralAnalyzer:
    """
    Analyzes trading behavior for psychological patterns and biases.
    
    Detects patterns like FOMO, revenge trading, overtrading, and provides
    quantified metrics on the cost of emotional trading.
    """
    
    def __init__(self):
        self._session_data: Dict[str, Dict] = {}
    
    def analyze_trades(self, trades: List[Trade], session_id: Optional[str] = None) -> Dict:
        """
        Comprehensive trade analysis for patterns and biases.
        
        Args:
            trades: List of Trade objects to analyze
            session_id: Optional session identifier for context
        
        Returns:
            Dict containing metrics, detected patterns, and coaching suggestions
        """
        if not trades:
            return {"status": "no_data", "message": "No trade history to analyze."}
        
        # Sort trades by timestamp
        sorted_trades = sorted(trades, key=lambda t: t.timestamp)
        
        # Core metrics
        metrics = self._calculate_metrics(sorted_trades)
        
        # Detect psychological patterns
        signals = self._detect_patterns(sorted_trades)
        
        # Calculate discipline score
        discipline = self._calculate_discipline(sorted_trades, signals)
        
        # Detect streaks
        streaks = self._detect_streaks(sorted_trades)
        
        # Assess emotional state
        emotional_state = self._assess_emotional_state(sorted_trades, signals)
        
        # Calculate cost of emotions
        emotion_costs = self._calculate_emotion_costs(sorted_trades, signals)
        
        # Generate alerts
        alerts = self._generate_alerts(sorted_trades, signals, discipline)
        
        # Cache session data
        if session_id:
            self._session_data[session_id] = {
                "last_analysis": datetime.now(),
                "trade_count": len(trades),
                "signals": signals
            }
        
        return {
            "status": "success",
            "metrics": metrics,
            "discipline": discipline.to_dict(),
            "psychology": {
                "detected_patterns": [s.to_dict() for s in signals],
                "emotional_state": emotional_state.value,
                "risk_level": self._assess_risk_level(signals, discipline).value
            },
            "streaks": {
                "current": streaks["current"].to_dict() if streaks.get("current") else None,
                "best_win": streaks["best_win"].to_dict() if streaks.get("best_win") else None,
                "worst_loss": streaks["worst_loss"].to_dict() if streaks.get("worst_loss") else None
            },
            "emotion_costs": [ec.to_dict() for ec in emotion_costs],
            "alerts": alerts
        }
    
    def _calculate_metrics(self, trades: List[Trade]) -> Dict:
        """Calculate core trading metrics."""
        if not trades:
            return {}
        
        total = len(trades)
        amounts = [t.amount for t in trades]
        avg_amount = sum(amounts) / total
        
        # Calculate win rate (simplified - assumes positive amount = win)
        wins = sum(1 for t in trades if getattr(t, 'pnl', t.amount) > 0)
        
        # Time between trades
        if len(trades) > 1:
            time_diffs = [
                trades[i+1].timestamp - trades[i].timestamp 
                for i in range(len(trades)-1)
            ]
            avg_time_between = sum(time_diffs) / len(time_diffs)
        else:
            avg_time_between = 0
        
        return {
            "total_trades": total,
            "win_rate": round(wins / total * 100, 1) if total > 0 else 0,
            "avg_position_size": round(avg_amount, 2),
            "largest_position": round(max(amounts), 2),
            "smallest_position": round(min(amounts), 2),
            "avg_time_between_trades_seconds": round(avg_time_between, 0)
        }
    
    def _detect_patterns(self, trades: List[Trade]) -> List[BehaviorSignal]:
        """Detect psychological patterns in trading behavior."""
        signals = []
        
        if len(trades) < 2:
            return signals
        
        avg_amount = sum(t.amount for t in trades) / len(trades)
        thresholds = DETECTION_THRESHOLDS
        
        # Track recent losses for revenge detection
        recent_losses = 0
        last_loss_time = None
        
        for i, trade in enumerate(trades):
            trade_signals = []
            
            # --- Oversizing Detection ---
            if trade.amount > avg_amount * thresholds["oversizing_multiplier"]:
                trade_signals.append(BehaviorSignal(
                    tag=PsychologyTag.OVERSIZING,
                    confidence=min(0.9, (trade.amount / avg_amount - 1) / 2),
                    detected_at=datetime.fromtimestamp(trade.timestamp),
                    trade_ids=[trade.id] if trade.id else [],
                    evidence={
                        "trade_size": trade.amount,
                        "avg_size": round(avg_amount, 2),
                        "ratio": round(trade.amount / avg_amount, 2)
                    }
                ))
            
            # --- Rapid Entry / Revenge Trading Detection ---
            if i > 0:
                time_since_last = trade.timestamp - trades[i-1].timestamp
                
                # Check for rapid entry after loss
                if time_since_last < thresholds["rapid_entry_seconds"]:
                    if recent_losses >= thresholds["revenge_loss_threshold"]:
                        trade_signals.append(BehaviorSignal(
                            tag=PsychologyTag.REVENGE_TRADE,
                            confidence=min(0.85, 0.5 + (recent_losses * 0.15)),
                            detected_at=datetime.fromtimestamp(trade.timestamp),
                            trade_ids=[trade.id] if trade.id else [],
                            evidence={
                                "seconds_since_last_trade": time_since_last,
                                "recent_losses": recent_losses
                            }
                        ))
                    else:
                        # Might be FOMO if entering quickly without losses
                        trade_signals.append(BehaviorSignal(
                            tag=PsychologyTag.FOMO,
                            confidence=0.6,
                            detected_at=datetime.fromtimestamp(trade.timestamp),
                            trade_ids=[trade.id] if trade.id else [],
                            evidence={
                                "seconds_since_last_trade": time_since_last,
                                "rapid_entry": True
                            }
                        ))
            
            # --- Size Increase After Wins (Greed) ---
            if i > 0:
                prev_trade = trades[i-1]
                if trade.amount > prev_trade.amount * thresholds["size_increase_after_wins"]:
                    # Check if previous was a win
                    if getattr(prev_trade, 'pnl', prev_trade.amount) > 0:
                        trade_signals.append(BehaviorSignal(
                            tag=PsychologyTag.GREED_HOLD,
                            confidence=0.65,
                            detected_at=datetime.fromtimestamp(trade.timestamp),
                            trade_ids=[trade.id] if trade.id else [],
                            evidence={
                                "size_increase_pct": round((trade.amount / prev_trade.amount - 1) * 100, 1)
                            }
                        ))
            
            # Update loss tracking
            if getattr(trade, 'pnl', -1) < 0 or (hasattr(trade, 'action') and trade.action == 'sell'):
                recent_losses += 1
                last_loss_time = trade.timestamp
            else:
                recent_losses = max(0, recent_losses - 1)  # Decay
            
            signals.extend(trade_signals)
        
        # --- Overtrading Detection (Session Level) ---
        session_trade_counts = self._count_trades_by_session(trades)
        for session_date, count in session_trade_counts.items():
            if count > thresholds["session_overtrade_count"]:
                signals.append(BehaviorSignal(
                    tag=PsychologyTag.OVERTRADING,
                    confidence=min(0.9, 0.5 + (count - 10) * 0.05),
                    detected_at=datetime.strptime(session_date, "%Y-%m-%d"),
                    evidence={
                        "trade_count": count,
                        "threshold": thresholds["session_overtrade_count"]
                    }
                ))
        
        # --- Tilt Detection ---
        tilt_detected = self._detect_tilt(trades, thresholds)
        if tilt_detected:
            signals.append(tilt_detected)
        
        return signals
    
    def _detect_tilt(self, trades: List[Trade], thresholds: Dict) -> Optional[BehaviorSignal]:
        """Detect tilt pattern: consecutive losses with increasing size."""
        consecutive_losses = 0
        sizes_during_losses = []
        tilt_start = None
        
        for trade in trades:
            is_loss = getattr(trade, 'pnl', 0) < 0
            
            if is_loss:
                consecutive_losses += 1
                sizes_during_losses.append(trade.amount)
                if tilt_start is None:
                    tilt_start = trade.timestamp
            else:
                consecutive_losses = 0
                sizes_during_losses = []
                tilt_start = None
            
            # Check for tilt: 3+ losses with increasing sizes
            if consecutive_losses >= thresholds["tilt_consecutive_losses"]:
                if len(sizes_during_losses) >= 3:
                    # Check if sizes are increasing
                    if sizes_during_losses[-1] > sizes_during_losses[0]:
                        return BehaviorSignal(
                            tag=PsychologyTag.TILT,
                            confidence=0.8,
                            detected_at=datetime.fromtimestamp(tilt_start) if tilt_start else datetime.now(),
                            evidence={
                                "consecutive_losses": consecutive_losses,
                                "size_progression": sizes_during_losses[-3:]
                            }
                        )
        return None
    
    def _count_trades_by_session(self, trades: List[Trade]) -> Dict[str, int]:
        """Count trades per calendar day."""
        counts = defaultdict(int)
        for trade in trades:
            date_str = datetime.fromtimestamp(trade.timestamp).strftime("%Y-%m-%d")
            counts[date_str] += 1
        return dict(counts)
    
    def _calculate_discipline(self, trades: List[Trade], signals: List[BehaviorSignal]) -> DisciplineMetrics:
        """Calculate discipline score from detected patterns."""
        tag_counts = defaultdict(int)
        for signal in signals:
            tag_counts[signal.tag] += 1
        
        total = len(trades)
        violations = sum(tag_counts.values())
        
        return DisciplineMetrics(
            total_trades=total,
            planned_trades=max(0, total - violations),
            rule_breaks=tag_counts.get(PsychologyTag.PLAN_DEVIATION, 0),
            position_size_violations=tag_counts.get(PsychologyTag.OVERSIZING, 0),
            stop_loss_moves=tag_counts.get(PsychologyTag.MOVING_STOPS, 0),
            revenge_trades=tag_counts.get(PsychologyTag.REVENGE_TRADE, 0),
            fomo_entries=tag_counts.get(PsychologyTag.FOMO, 0)
        )
    
    def _detect_streaks(self, trades: List[Trade]) -> Dict:
        """Detect win/loss streaks."""
        if not trades:
            return {}
        
        current_streak = Streak(
            type="neutral",
            count=0,
            start_date=datetime.fromtimestamp(trades[0].timestamp)
        )
        best_win = None
        worst_loss = None
        
        streak_count = 0
        streak_type = None
        streak_start = trades[0].timestamp
        streak_pnl = 0.0
        
        for trade in trades:
            is_win = getattr(trade, 'pnl', trade.amount) > 0
            trade_type = "win" if is_win else "loss"
            trade_pnl = getattr(trade, 'pnl', trade.amount if is_win else -trade.amount)
            
            if trade_type == streak_type:
                streak_count += 1
                streak_pnl += trade_pnl
            else:
                # Save previous streak if notable
                if streak_count > 0:
                    completed_streak = Streak(
                        type=streak_type,
                        count=streak_count,
                        start_date=datetime.fromtimestamp(streak_start),
                        end_date=datetime.fromtimestamp(trade.timestamp),
                        total_pnl=streak_pnl,
                        is_current=False
                    )
                    
                    if streak_type == "win":
                        if best_win is None or streak_count > best_win.count:
                            best_win = completed_streak
                    else:
                        if worst_loss is None or streak_count > worst_loss.count:
                            worst_loss = completed_streak
                
                # Start new streak
                streak_type = trade_type
                streak_count = 1
                streak_start = trade.timestamp
                streak_pnl = trade_pnl
        
        # Current streak
        if streak_count > 0:
            current_streak = Streak(
                type=streak_type or "neutral",
                count=streak_count,
                start_date=datetime.fromtimestamp(streak_start),
                total_pnl=streak_pnl,
                is_current=True
            )
        
        return {
            "current": current_streak,
            "best_win": best_win,
            "worst_loss": worst_loss
        }
    
    def _assess_emotional_state(self, trades: List[Trade], signals: List[BehaviorSignal]) -> EmotionalState:
        """Assess current emotional state based on patterns."""
        if not signals:
            return EmotionalState.NEUTRAL
        
        # Count recent signals (last 5 trades)
        recent_tags = [s.tag for s in signals[-5:]]
        
        # Check for tilt or revenge (frustrated)
        if PsychologyTag.TILT in recent_tags or PsychologyTag.REVENGE_TRADE in recent_tags:
            return EmotionalState.FRUSTRATED
        
        # Check for FOMO or overtrading (anxious)
        if PsychologyTag.FOMO in recent_tags or PsychologyTag.OVERTRADING in recent_tags:
            return EmotionalState.ANXIOUS
        
        # Check for oversizing after wins (euphoric)
        if PsychologyTag.OVERSIZING in recent_tags:
            recent_pnl = sum(getattr(t, 'pnl', 0) for t in trades[-5:])
            if recent_pnl > 0:
                return EmotionalState.EUPHORIC
        
        # Check for hesitation (fearful)
        if PsychologyTag.HESITATION in recent_tags:
            return EmotionalState.FEARFUL
        
        return EmotionalState.NEUTRAL
    
    def _assess_risk_level(self, signals: List[BehaviorSignal], discipline: DisciplineMetrics) -> RiskLevel:
        """Assess current risk level based on behavior."""
        high_risk_tags = {PsychologyTag.TILT, PsychologyTag.REVENGE_TRADE, PsychologyTag.OVERSIZING}
        medium_risk_tags = {PsychologyTag.FOMO, PsychologyTag.OVERTRADING}
        
        recent_tags = {s.tag for s in signals[-5:]} if signals else set()
        
        if PsychologyTag.TILT in recent_tags:
            return RiskLevel.CRITICAL
        
        high_risk_count = len(recent_tags & high_risk_tags)
        if high_risk_count >= 2:
            return RiskLevel.HIGH
        if high_risk_count == 1:
            return RiskLevel.ELEVATED
        
        medium_risk_count = len(recent_tags & medium_risk_tags)
        if medium_risk_count >= 1:
            return RiskLevel.MODERATE
        
        if discipline.discipline_score < DETECTION_THRESHOLDS["discipline_poor"]:
            return RiskLevel.HIGH
        if discipline.discipline_score < DETECTION_THRESHOLDS["discipline_needs_work"]:
            return RiskLevel.ELEVATED
        
        return RiskLevel.LOW
    
    def _calculate_emotion_costs(self, trades: List[Trade], signals: List[BehaviorSignal]) -> List[EmotionCost]:
        """Calculate the financial cost of emotional trading."""
        costs = []
        
        if not signals or len(trades) < 5:
            return costs
        
        # Group signals by tag
        signals_by_tag = defaultdict(list)
        for signal in signals:
            signals_by_tag[signal.tag].append(signal)
        
        # Calculate baseline (trades without emotional flags)
        emotional_trade_ids = set()
        for signal in signals:
            emotional_trade_ids.update(signal.trade_ids)
        
        disciplined_trades = [t for t in trades if t.id not in emotional_trade_ids]
        if disciplined_trades:
            baseline_pnl = sum(getattr(t, 'pnl', 0) for t in disciplined_trades) / len(disciplined_trades)
        else:
            baseline_pnl = 0
        
        # Calculate cost per emotional pattern
        for tag, tag_signals in signals_by_tag.items():
            if tag in {PsychologyTag.DISCIPLINED, PsychologyTag.PATIENT_ENTRY, PsychologyTag.PROPER_SIZING}:
                continue  # Skip positive patterns
            
            # Find trades associated with this pattern
            pattern_trade_ids = set()
            for s in tag_signals:
                pattern_trade_ids.update(s.trade_ids)
            
            pattern_trades = [t for t in trades if t.id in pattern_trade_ids]
            if not pattern_trades:
                continue
            
            pattern_pnl = sum(getattr(t, 'pnl', -t.amount) for t in pattern_trades)
            avg_pattern_pnl = pattern_pnl / len(pattern_trades)
            estimated_cost = (baseline_pnl - avg_pattern_pnl) * len(pattern_trades)
            
            if estimated_cost > 0:  # Only report if there's a cost
                costs.append(EmotionCost(
                    tag=tag,
                    period_start=datetime.fromtimestamp(min(t.timestamp for t in pattern_trades)),
                    period_end=datetime.fromtimestamp(max(t.timestamp for t in pattern_trades)),
                    estimated_cost=estimated_cost,
                    trade_count=len(pattern_trades),
                    avg_loss_per_trade=avg_pattern_pnl,
                    comparison_baseline=baseline_pnl
                ))
        
        return costs
    
    def _generate_alerts(self, trades: List[Trade], signals: List[BehaviorSignal], discipline: DisciplineMetrics) -> List[Dict]:
        """Generate actionable alerts based on analysis."""
        alerts = []
        
        # Recent signals (last 3)
        recent_signals = signals[-3:] if signals else []
        recent_tags = {s.tag for s in recent_signals}
        
        # Critical: Tilt detected
        if PsychologyTag.TILT in recent_tags:
            alerts.append({
                "level": "critical",
                "type": "tilt_warning",
                "message": "Tilt pattern detected. Consider stepping away from trading.",
                "action": "Take a break. Review your trading plan before the next session."
            })
        
        # High: Revenge trading
        if PsychologyTag.REVENGE_TRADE in recent_tags:
            alerts.append({
                "level": "high",
                "type": "revenge_warning",
                "message": "Possible revenge trading detected after recent losses.",
                "action": "Pause and assess. The market will be here tomorrow."
            })
        
        # Medium: Oversizing
        if PsychologyTag.OVERSIZING in recent_tags:
            alerts.append({
                "level": "medium",
                "type": "position_size_warning",
                "message": "Your recent position sizes are larger than your average.",
                "action": "Review your risk management rules. Is this intentional?"
            })
        
        # Low: Discipline score dropping
        if discipline.discipline_score < DETECTION_THRESHOLDS["discipline_needs_work"]:
            alerts.append({
                "level": "medium",
                "type": "discipline_warning",
                "message": f"Discipline score is {discipline.discipline_score}%. Room for improvement.",
                "action": "Review your recent trades against your trading plan."
            })
        
        # Positive: Good streak
        streaks = self._detect_streaks(trades)
        if streaks.get("current") and streaks["current"].type == "win" and streaks["current"].count >= 3:
            alerts.append({
                "level": "positive",
                "type": "streak_celebration",
                "message": f"Great work! You're on a {streaks['current'].count}-trade winning streak!",
                "action": "Stay disciplined. Don't let success lead to oversizing."
            })
        
        # Positive: High discipline
        if discipline.discipline_score >= DETECTION_THRESHOLDS["discipline_excellent"]:
            alerts.append({
                "level": "positive",
                "type": "discipline_praise",
                "message": f"Excellent discipline! Score: {discipline.discipline_score}%",
                "action": "Keep following your plan. Consistency is your edge."
            })
        
        return alerts
    
    def get_pattern_description(self, tag: PsychologyTag) -> Dict:
        """Get human-readable description for a pattern."""
        return get_tag_description(tag)
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get cached session analysis summary."""
        return self._session_data.get(session_id)


behavioral_analyzer = BehavioralAnalyzer()

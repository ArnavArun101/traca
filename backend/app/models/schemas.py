from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from enum import Enum


# =============================================================================
# MARKET DATA SCHEMAS
# =============================================================================

class MarketData(BaseModel):
    symbol: str
    price: float
    timestamp: int


class IndicatorResult(BaseModel):
    status: str
    indicators: Optional[Dict] = None
    latest: Optional[Dict] = None
    signals: Optional[List[str]] = None
    message: Optional[str] = None


class PriceAlertRequest(BaseModel):
    symbol: str
    target_price: float
    direction: str  # "above" or "below"


class PriceAlertResponse(BaseModel):
    status: str
    alert_id: Optional[int] = None
    symbol: Optional[str] = None
    target_price: Optional[float] = None
    direction: Optional[str] = None
    message: Optional[str] = None


class AssetListResponse(BaseModel):
    synthetic: List[str]
    forex: List[str]
    crypto: List[str]


# =============================================================================
# CHAT SCHEMAS
# =============================================================================

class ChatMessage(BaseModel):
    session_id: str
    message: str
    timestamp: Optional[int] = None


class AIResponse(BaseModel):
    type: str = "chat_response"
    text: str
    attachments: Optional[List[Any]] = None


# =============================================================================
# PERSONA & CONTENT SCHEMAS
# =============================================================================

class PlatformEnum(str, Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


class ContentTypeEnum(str, Enum):
    MARKET_UPDATE = "market_update"
    EDUCATIONAL = "educational"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    TRADE_IDEA = "trade_idea"
    NEWS_REACTION = "news_reaction"


class PersonaInfo(BaseModel):
    """Basic persona information."""
    id: str
    name: str
    title: str
    style: str
    expertise: List[str]


class ContentGenerationRequest(BaseModel):
    """Request to generate social media content."""
    topic: str = Field(..., description="Topic or market event to cover")
    platform: PlatformEnum = Field(default=PlatformEnum.LINKEDIN)
    persona_id: Optional[str] = Field(default=None, description="Persona ID (defaults to marcus_reid)")
    content_type: ContentTypeEnum = Field(default=ContentTypeEnum.MARKET_UPDATE)
    market_data: Optional[Dict] = Field(default=None, description="Optional market data context")
    require_approval: bool = Field(default=True, description="Whether content needs human approval")


class ComplianceResult(BaseModel):
    """Content compliance check result."""
    passed: bool
    notes: List[str] = []


class ContentGenerationResponse(BaseModel):
    """Response from content generation."""
    status: str
    content_id: Optional[str] = None
    persona: Optional[PersonaInfo] = None
    platform: Optional[str] = None
    content_type: Optional[str] = None
    content: Optional[str] = None
    workflow_status: Optional[str] = None
    compliance: Optional[ComplianceResult] = None
    message: Optional[str] = None


class MarketUpdateRequest(BaseModel):
    """Request for market update content."""
    symbol: str
    price_data: Dict
    persona_id: Optional[str] = None
    platform: PlatformEnum = PlatformEnum.LINKEDIN


class DailySummaryRequest(BaseModel):
    """Request for daily summary content."""
    market_events: List[Dict]
    persona_id: Optional[str] = None
    platform: PlatformEnum = PlatformEnum.LINKEDIN


class EducationalThreadRequest(BaseModel):
    """Request for educational thread content."""
    concept: str = Field(..., description="Trading concept to explain")
    persona_id: Optional[str] = Field(default="sarah_martinez")
    platform: PlatformEnum = Field(default=PlatformEnum.TWITTER)


class NewsReactionRequest(BaseModel):
    """Request for news reaction content."""
    news_headline: str
    news_summary: str
    affected_assets: List[str]
    persona_id: Optional[str] = None
    platform: PlatformEnum = PlatformEnum.TWITTER


class ContentApprovalRequest(BaseModel):
    """Request to approve or reject content."""
    content_id: str
    action: str = Field(..., description="'approve' or 'reject'")
    reason: Optional[str] = Field(default=None, description="Reason for rejection")


# =============================================================================
# BEHAVIORAL COACHING SCHEMAS
# =============================================================================

class PsychologyTagEnum(str, Enum):
    """Psychology tags for trade analysis."""
    FOMO = "fomo"
    PANIC_EXIT = "panic_exit"
    HESITATION = "hesitation"
    OVERTRADING = "overtrading"
    OVERSIZING = "oversizing"
    GREED_HOLD = "greed_hold"
    REVENGE_TRADE = "revenge_trade"
    TILT = "tilt"
    AVERAGING_DOWN = "averaging_down"
    PLAN_DEVIATION = "plan_deviation"
    EARLY_EXIT = "early_exit"
    MOVING_STOPS = "moving_stops"
    DISCIPLINED = "disciplined"
    PATIENT_ENTRY = "patient_entry"
    PROPER_SIZING = "proper_sizing"


class EmotionalStateEnum(str, Enum):
    """Emotional state assessment."""
    CALM = "calm"
    CONFIDENT = "confident"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    EUPHORIC = "euphoric"
    FEARFUL = "fearful"
    NEUTRAL = "neutral"


class RiskLevelEnum(str, Enum):
    """Risk level assessment."""
    LOW = "low"
    MODERATE = "moderate"
    ELEVATED = "elevated"
    HIGH = "high"
    CRITICAL = "critical"


class BehaviorPattern(BaseModel):
    """Detected behavioral pattern."""
    tag: str
    confidence: float
    detected_at: str
    trade_ids: List[int] = []
    evidence: Dict = {}


class DisciplineMetricsResponse(BaseModel):
    """Discipline scoring metrics."""
    total_trades: int
    planned_trades: int
    plan_adherence: str
    discipline_score: float
    violations: Dict


class StreakInfo(BaseModel):
    """Trading streak information."""
    type: str
    count: int
    start_date: str
    end_date: Optional[str] = None
    total_pnl: float
    is_current: bool


class EmotionCostInfo(BaseModel):
    """Cost of emotional trading."""
    tag: str
    period: Dict
    estimated_cost: float
    trade_count: int
    avg_loss_per_trade: float
    comparison_baseline: float


class BehavioralAlert(BaseModel):
    """Behavioral coaching alert."""
    level: str
    type: str
    message: str
    action: str


class TradeAnalysisRequest(BaseModel):
    """Request for trade analysis."""
    session_id: str
    include_coaching: bool = Field(default=True)


class TradeAnalysisResponse(BaseModel):
    """Response from trade analysis."""
    status: str
    metrics: Optional[Dict] = None
    discipline: Optional[DisciplineMetricsResponse] = None
    psychology: Optional[Dict] = None
    streaks: Optional[Dict] = None
    emotion_costs: Optional[List[EmotionCostInfo]] = None
    alerts: Optional[List[BehavioralAlert]] = None
    message: Optional[str] = None


class NudgeResponse(BaseModel):
    """Coaching nudge."""
    id: str
    type: str
    urgency: str
    title: str
    message: str
    action_suggestion: str
    trigger: str
    created_at: str
    dismissed: bool = False


class ReflectionPromptsRequest(BaseModel):
    """Request for reflection prompts."""
    context: str = Field(..., description="One of: post_loss, post_win, end_of_day, before_trading, after_streak")


class ReflectionPromptsResponse(BaseModel):
    """Reflection prompts for self-review."""
    context: str
    prompts: List[str]


# =============================================================================
# AUTH SCHEMAS
# =============================================================================

class AuthUser(BaseModel):
    id: int
    name: str
    email: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    confirm_password: Optional[str] = None
    model_config = {"extra": "ignore"}


class LoginRequest(BaseModel):
    email: str
    password: str
    model_config = {"extra": "ignore"}


class AuthResponse(BaseModel):
    status: str
    message: str
    user: Optional[AuthUser] = None
    token: Optional[str] = None

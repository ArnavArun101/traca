from pydantic import BaseModel
from typing import Optional, List, Any, Dict

class MarketData(BaseModel):
    symbol: str
    price: float
    timestamp: int

class ChatMessage(BaseModel):
    session_id: str
    message: str
    timestamp: Optional[int] = None

class AIResponse(BaseModel):
    type: str = "chat_response"
    text: str
    attachments: Optional[List[Any]] = None

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

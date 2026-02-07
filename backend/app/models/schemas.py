from pydantic import BaseModel
from typing import Optional, List, Any

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

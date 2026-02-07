from typing import Optional
from sqlmodel import Field, SQLModel
import time

class Trade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    price: float
    action: str  # buy/sell
    amount: float
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    session_id: str

class ChatHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    role: str  # user/assistant
    content: str
    timestamp: int = Field(default_factory=lambda: int(time.time()))

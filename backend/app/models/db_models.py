from typing import Optional
from sqlmodel import Field, SQLModel
import time

class Trade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    price: float
    action: str  # buy/sell
    amount: float
    pnl: Optional[float] = Field(default=None)
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    session_id: str

class ChatHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str
    role: str  # user/assistant
    content: str
    timestamp: int = Field(default_factory=lambda: int(time.time()))

class PriceHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str = Field(index=True)
    open: float
    high: float
    low: float
    close: float
    epoch: int = Field(index=True)

class PriceAlert(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    symbol: str
    target_price: float
    direction: str  # "above" or "below"
    is_active: bool = Field(default=True)
    created_at: int = Field(default_factory=lambda: int(time.time()))
    triggered_at: Optional[int] = Field(default=None)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: int = Field(default_factory=lambda: int(time.time()))

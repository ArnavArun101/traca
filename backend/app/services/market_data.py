import asyncio
import logging
import os
import json
from deriv_api import DerivAPI
from app.core.websocket_manager import manager
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class MarketDataProcessor:
    def __init__(self):
        self.api_token = os.getenv("DERIV_API_TOKEN")
        self.app_id = os.getenv("DERIV_APP_ID", "1010")  # Default to 1010 if not provided
        self.api = None
        self.is_connected = False
        self.subscribed_symbols = set()
        self.subscriptions = {} # symbol -> subscription_id

    async def connect(self):
        if not self.api_token:
            logger.error("DERIV_API_TOKEN not found in environment")
            return
        
        try:
            self.api = DerivAPI(app_id=self.app_id)
            # Authenticate
            await self.api.authorize(self.api_token)
            self.is_connected = True
            logger.info("Deriv API initialized and authorized")
        except Exception as e:
            logger.error(f"Failed to initialize Deriv: {e}")
            self.is_connected = False

    async def _handle_tick(self, data):
        """Handle incoming tick data from Deriv subscription"""
        if 'tick' in data:
            tick = data['tick']
            symbol = tick['symbol']
            tick_data = {
                "type": "price_update",
                "symbol": symbol,
                "price": float(tick['quote']),
                "timestamp": tick['epoch']
            }
            await manager.broadcast(tick_data)

    async def subscribe_ticks(self, symbol: str):
        if not self.is_connected:
            await self.connect()
        
        if not self.is_connected:
            return

        if symbol in self.subscribed_symbols:
            return

        try:
            # Deriv API uses 'ticks' call for subscription
            source = await self.api.subscribe({"ticks": symbol})
            self.subscribed_symbols.add(symbol)
            
            # Start a task to listen to the stream
            async def listen_to_ticks(subscription_source):
                async for tick in subscription_source:
                    await self._handle_tick(tick)

            asyncio.create_task(listen_to_ticks(source))
            logger.info(f"Subscribed to updates for {symbol}")
        except Exception as e:
            logger.error(f"Failed to subscribe to {symbol}: {e}")

    async def fetch_trade_history(self, symbol: str, limit: int = 50):
        if not self.is_connected:
            await self.connect()
        
        if not self.is_connected:
            return []
        
        try:
            # Deriv API uses 'ticks_history'
            response = await self.api.ticks_history({
                "ticks_history": symbol,
                "adjust_start_time": 1,
                "count": limit,
                "end": "latest",
                "start": 1,
                "style": "candles"
            })
            
            candles = []
            if 'candles' in response:
                for candle in response['candles']:
                    candles.append({
                        'epoch': candle['epoch'],
                        'open': float(candle['open']),
                        'high': float(candle['high']),
                        'low': float(candle['low']),
                        'close': float(candle['close']),
                    })
            return candles
        except Exception as e:
            logger.error(f"Failed to fetch history for {symbol}: {e}")
            return []

market_data_processor = MarketDataProcessor()

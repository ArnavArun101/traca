import asyncio
import logging
import os
import json
from typing import List, Dict, Optional
from deriv_api import DerivAPI
from sqlmodel import Session, select
from app.core.websocket_manager import manager
from app.models.db_models import PriceHistory
from app.db.session import engine
from app.services.price_alerts import price_alert_service
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Supported asset groups for multi-asset support
SUPPORTED_ASSETS: Dict[str, List[str]] = {
    "synthetic": [
        "R_10", "R_25", "R_50", "R_75", "R_100",
        "1HZ10V", "1HZ25V", "1HZ50V", "1HZ75V", "1HZ100V",
    ],
    "forex": [
        "frxEURUSD", "frxGBPUSD", "frxUSDJPY",
        "frxAUDUSD", "frxUSDCAD", "frxUSDCHF",
        "frxEURGBP", "frxEURJPY",
    ],
    "crypto": [
        "cryBTCUSD", "cryETHUSD", "cryLTCUSD",
    ],
}


class MarketDataProcessor:
    def __init__(self):
        self.api_token = os.getenv("DERIV_API_TOKEN")
        self.app_id = os.getenv("DERIV_APP_ID", "1010")  # Default to 1010 if not provided
        self.api = None
        self.is_connected = False
        self.subscribed_symbols: set = set()
        self.subscriptions: Dict = {}  # symbol -> subscription_id
        self.latest_prices: Dict[str, float] = {}  # symbol -> latest price
<<<<<<< HEAD
=======
        self.keepalive_task = None
        self.keepalive_interval = 30
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51

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
<<<<<<< HEAD
=======
            self._start_keepalive()
            await self._resubscribe()
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51
        except Exception as e:
            logger.error(f"Failed to initialize Deriv: {e}")
            self.is_connected = False

<<<<<<< HEAD
=======
    def _start_keepalive(self):
        if self.keepalive_task and not self.keepalive_task.done():
            return
        self.keepalive_task = asyncio.create_task(self._keepalive_loop())

    async def _keepalive_loop(self):
        while True:
            if not self.is_connected or not self.api:
                await asyncio.sleep(self.keepalive_interval)
                continue
            try:
                await self.api.ping()
            except Exception as e:
                logger.warning(f"Deriv keepalive failed: {e}. Reconnecting...")
                self.is_connected = False
                await asyncio.sleep(5)
                await self.connect()
            await asyncio.sleep(self.keepalive_interval)

    async def _resubscribe(self):
        if not self.subscribed_symbols:
            return
        symbols = list(self.subscribed_symbols)
        self.subscribed_symbols.clear()
        for symbol in symbols:
            await self.subscribe_ticks(symbol)

>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51
    async def _handle_tick(self, data):
        """Handle incoming tick data from Deriv subscription."""
        if 'tick' in data:
            tick = data['tick']
            symbol = tick['symbol']
            price = float(tick['quote'])
            self.latest_prices[symbol] = price

            tick_data = {
                "type": "price_update",
                "symbol": symbol,
                "price": price,
                "timestamp": tick['epoch']
            }
            await manager.broadcast(tick_data)

            # Check price alerts for this symbol
            await price_alert_service.check_price(symbol, price)

    async def subscribe_ticks(self, symbol: str):
        """Subscribe to real-time price streaming for a symbol via Deriv WebSocket API."""
        if not self.is_connected:
            await self.connect()
        
        if not self.is_connected:
            return

        if symbol in self.subscribed_symbols:
            return

        try:
            source = await self.api.subscribe({"ticks": symbol})
            self.subscribed_symbols.add(symbol)
            
            async def listen_to_ticks(subscription_source):
<<<<<<< HEAD
                async for tick in subscription_source:
                    await self._handle_tick(tick)
=======
                # python-deriv-api returns an rx Observable, not an async iterator
                def on_next(tick):
                    asyncio.create_task(self._handle_tick(tick))

                def on_error(err):
                    logger.error(f"Tick stream error for {symbol}: {err}")

                try:
                    subscription_source.subscribe(on_next=on_next, on_error=on_error)
                except Exception as e:
                    logger.error(f"Failed to subscribe to tick stream for {symbol}: {e}")
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51

            asyncio.create_task(listen_to_ticks(source))
            logger.info(f"Subscribed to real-time updates for {symbol}")
        except Exception as e:
            logger.error(f"Failed to subscribe to {symbol}: {e}")

    async def subscribe_multiple(self, symbols: List[str]):
        """Subscribe to real-time price streaming for multiple symbols."""
        for symbol in symbols:
            await self.subscribe_ticks(symbol)

    async def subscribe_asset_group(self, group: str):
        """Subscribe to all symbols in an asset group (forex, crypto, synthetic)."""
        symbols = SUPPORTED_ASSETS.get(group, [])
        if not symbols:
            logger.warning(f"Unknown asset group: {group}")
            return
        await self.subscribe_multiple(symbols)

    async def fetch_trade_history(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Fetch historical candle data from Deriv API."""
        if not self.is_connected:
            await self.connect()
        
        if not self.is_connected:
            return []
        
        try:
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

    # -- Historical Data Storage & Retrieval ----------------------------------

    def store_candles(self, symbol: str, candles: List[Dict]):
        """Persist candle data to the database for historical retrieval."""
        with Session(engine) as session:
            for c in candles:
                # Avoid duplicates based on symbol + epoch
                existing = session.exec(
                    select(PriceHistory)
                    .where(PriceHistory.symbol == symbol)
                    .where(PriceHistory.epoch == c["epoch"])
                ).first()
                if not existing:
                    record = PriceHistory(
                        symbol=symbol,
                        open=c["open"],
                        high=c["high"],
                        low=c["low"],
                        close=c["close"],
                        epoch=c["epoch"],
                    )
                    session.add(record)
            session.commit()
        logger.info(f"Stored {len(candles)} candles for {symbol}")

    def retrieve_candles(
        self, symbol: str, limit: int = 100, start_epoch: Optional[int] = None
    ) -> List[Dict]:
        """Retrieve stored historical candles from the database."""
        with Session(engine) as session:
            statement = (
                select(PriceHistory)
                .where(PriceHistory.symbol == symbol)
                .order_by(PriceHistory.epoch.desc())
            )
            if start_epoch is not None:
                statement = statement.where(PriceHistory.epoch >= start_epoch)
            statement = statement.limit(limit)
            records = session.exec(statement).all()

        # Return in chronological order
        records.reverse()
        return [
            {
                "epoch": r.epoch,
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
            }
            for r in records
        ]

    async def fetch_and_store_history(self, symbol: str, limit: int = 100) -> List[Dict]:
        """Fetch historical data from Deriv API and persist it to the database."""
        candles = await self.fetch_trade_history(symbol, limit=limit)
        if candles:
            self.store_candles(symbol, candles)
        return candles

    # -- Multi-asset helpers --------------------------------------------------

    def get_supported_assets(self) -> Dict[str, List[str]]:
        """Return the registry of supported assets grouped by type."""
        return SUPPORTED_ASSETS

    def get_latest_prices(self) -> Dict[str, float]:
        """Return the latest cached prices for all subscribed symbols."""
        return dict(self.latest_prices)

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Return the latest cached price for a specific symbol."""
        return self.latest_prices.get(symbol)
<<<<<<< HEAD

=======
    async def fetch_account_trade_history(self, limit: int = 50):
        if not self.is_connected:
            await self.connect()

        if not self.is_connected:
            return {"status": "error", "message": "Deriv API not connected."}

        try:
            response = await self.api.statement({"limit": limit})
            transactions = response.get("statement", {}).get("transactions", [])
            normalized = []
            for tx in transactions:
                normalized.append(
                    {
                        "transaction_id": tx.get("transaction_id"),
                        "symbol": tx.get("symbol"),
                        "amount": float(tx.get("amount", 0)) if tx.get("amount") is not None else None,
                        "balance": float(tx.get("balance", 0)) if tx.get("balance") is not None else None,
                        "transaction_time": tx.get("transaction_time"),
                        "action_type": tx.get("action_type"),
                        "longcode": tx.get("longcode"),
                    }
                )
            return {"status": "success", "count": len(normalized), "trades": normalized}
        except Exception as e:
            logger.error(f"Failed to fetch account trade history: {e}")
            return {"status": "error", "message": "Failed to fetch account trade history."}
>>>>>>> 76a861085ca3295a412df0a1c7debd59dedfbe51

market_data_processor = MarketDataProcessor()

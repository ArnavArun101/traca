from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlmodel import Session, select
from app.core.websocket_manager import manager
from app.core.auth import authenticate_token
from app.db.session import get_session
from app.models.db_models import ChatHistory, Trade
from app.services.market_data import market_data_processor
from app.services.llm_engine import llm_engine
from app.services.behavioral_analyzer import behavioral_analyzer
from app.services.behavioral_coach import behavioral_coach
from app.services.content_generator import content_generator
from app.services.technical_indicators import technical_indicators
from app.services.price_alerts import price_alert_service
from app.services.market_explainer import market_explainer
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

def _parse_trades(raw_trades, session_id: str):
    trades = []
    if not raw_trades:
        return trades
    for idx, item in enumerate(raw_trades, start=1):
        try:
            trade_id = item.get("id") if item.get("id") is not None else idx
            trades.append(
                Trade(
                    id=trade_id,
                    symbol=item.get("symbol", "UNKNOWN"),
                    price=float(item.get("price", 0)),
                    action=item.get("action", "buy"),
                    amount=float(item.get("amount", 0)),
                    pnl=float(item.get("pnl", item.get("profit"))) if item.get("pnl", item.get("profit")) is not None else None,
                    timestamp=int(item.get("timestamp", 0)),
                    session_id=session_id,
                )
            )
        except Exception:
            continue
    return trades

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    session: Session = Depends(get_session),
):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Authentication required."})
        await websocket.close(code=1008)
        return
    try:
        authenticate_token(token, session)
    except Exception:
        await websocket.accept()
        await websocket.send_json({"type": "error", "message": "Invalid or expired token."})
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid JSON format"},
                    session_id,
                )
                continue

            if not isinstance(message, dict) or "type" not in message:
                await manager.send_personal_message(
                    {"type": "error", "message": "Invalid message format"},
                    session_id,
                )
                continue
            
            msg_type = message.get("type")
            
            if msg_type == "subscribe":
                symbol = message.get("symbol", "R_100")
                await market_data_processor.subscribe_ticks(symbol)
                await manager.send_personal_message(
                    {"type": "info", "message": f"Subscribed to {symbol}"},
                    session_id
                )

            elif msg_type == "subscribe_group":
                # Multi-asset: subscribe to an entire asset group
                group = message.get("group", "synthetic")
                await market_data_processor.subscribe_asset_group(group)
                await manager.send_personal_message(
                    {"type": "info", "message": f"Subscribed to {group} assets"},
                    session_id
                )

            elif msg_type == "list_assets":
                # Multi-asset: return supported asset registry
                assets = market_data_processor.get_supported_assets()
                await manager.send_personal_message(
                    {"type": "asset_list", "data": assets},
                    session_id
                )

            elif msg_type == "get_prices":
                # Return latest cached prices for all subscribed symbols
                prices = market_data_processor.get_latest_prices()
                await manager.send_personal_message(
                    {"type": "latest_prices", "data": prices},
                    session_id
                )
            
            elif msg_type == "chat":
                user_msg = message.get("message")
                if not user_msg:
                    await manager.send_personal_message(
                        {"type": "error", "message": "Missing chat message"},
                        session_id,
                    )
                    continue
                session.add(
                    ChatHistory(session_id=session_id, role="user", content=user_msg)
                )
                session.commit()
                recent_chats = session.exec(
                    select(ChatHistory)
                    .where(ChatHistory.session_id == session_id)
                    .order_by(ChatHistory.timestamp.desc())
                    .limit(10)
                ).all()
                history = [
                    {"role": c.role, "content": c.content}
                    for c in reversed(recent_chats)
                ]
                analysis = await llm_engine.analyze_market(
                    {"note": "User asked: " + user_msg, "chat_history": history}
                )
                session.add(
                    ChatHistory(session_id=session_id, role="assistant", content=analysis)
                )
                session.commit()
                await manager.send_personal_message(
                    {"type": "chat_response", "text": analysis},
                    session_id
                )
            
            elif msg_type == "analyze_behavior":
                raw_trades = message.get("trades", [])
                trades = _parse_trades(raw_trades, session_id)
                report = behavioral_analyzer.analyze_trades(trades, session_id=session_id)
                await manager.send_personal_message(
                    {"type": "behavioral_report", "data": report},
                    session_id
                )

                if trades:
                    nudges = behavioral_coach.evaluate_trade(trades[-1], trades[:-1], session_id)
                else:
                    nudges = []
                if nudges:
                    await manager.send_personal_message(
                        {"type": "nudges", "data": [n.to_dict() for n in nudges]},
                        session_id
                    )

            elif msg_type == "generate_social":
                topic = message.get("topic", "Market update")
                platform = message.get("platform", "linkedin")
                draft = await content_generator.generate_post(topic, platform)
                await manager.send_personal_message(
                    {"type": "social_draft", "platform": platform, "text": draft},
                    session_id
                )

            elif msg_type == "trade_history":
                limit = int(message.get("limit", 50))
                data = await market_data_processor.fetch_account_trade_history(limit=limit)
                await manager.send_personal_message(
                    {"type": "trade_history", "data": data},
                    session_id
                )

            elif msg_type == "candles_history":
                symbol = message.get("symbol", "R_100")
                limit = int(message.get("limit", 50))
                data = await market_data_processor.fetch_trade_history(symbol, limit=limit)
                await manager.send_personal_message(
                    {"type": "candles_history", "symbol": symbol, "data": data},
                    session_id
                )

            elif msg_type == "trade_event":
                raw_trades = message.get("recent_trades", [])
                raw_trades.append(message.get("trade", {}))
                trades = _parse_trades(raw_trades, session_id)
                report = behavioral_analyzer.analyze_trades(trades)
                if trades:
                    nudges = behavioral_coach.evaluate_trade(trades[-1], trades[:-1], session_id)
                else:
                    nudges = []
                if nudges:
                    await manager.send_personal_message(
                        {"type": "nudges", "data": [n.to_dict() for n in nudges]},
                        session_id
                    )

            # -- Market Analysis: Technical Indicators -------------------------

            elif msg_type == "indicators":
                symbol = message.get("symbol", "R_100")
                limit = message.get("limit", 100)
                candles = await market_data_processor.fetch_trade_history(symbol, limit=limit)
                if not candles:
                    # Try stored data
                    candles = market_data_processor.retrieve_candles(symbol, limit=limit)
                result = technical_indicators.compute_all(candles)
                await manager.send_personal_message(
                    {"type": "indicator_result", "symbol": symbol, "data": result},
                    session_id
                )

            # -- Market Analysis: Price Alerts ---------------------------------

            elif msg_type == "create_alert":
                symbol = message.get("symbol")
                target_price = message.get("target_price")
                direction = message.get("direction")
                result = price_alert_service.create_alert(
                    session_id, symbol, float(target_price), direction
                )
                await manager.send_personal_message(
                    {"type": "alert_created", "data": result},
                    session_id
                )

            elif msg_type == "list_alerts":
                alerts = price_alert_service.get_alerts(session_id)
                await manager.send_personal_message(
                    {"type": "alert_list", "data": alerts},
                    session_id
                )

            elif msg_type == "cancel_alert":
                alert_id = message.get("alert_id")
                result = price_alert_service.cancel_alert(int(alert_id), session_id)
                await manager.send_personal_message(
                    {"type": "alert_cancelled", "data": result},
                    session_id
                )

            # -- Market Analysis: Historical Data ------------------------------

            elif msg_type == "fetch_history":
                symbol = message.get("symbol", "R_100")
                limit = message.get("limit", 100)
                candles = await market_data_processor.fetch_and_store_history(symbol, limit=limit)
                await manager.send_personal_message(
                    {"type": "history_data", "symbol": symbol, "candles": candles},
                    session_id
                )

            elif msg_type == "get_stored_history":
                symbol = message.get("symbol", "R_100")
                limit = message.get("limit", 100)
                start_epoch = message.get("start_epoch")
                candles = market_data_processor.retrieve_candles(
                    symbol, limit=limit, start_epoch=start_epoch
                )
                await manager.send_personal_message(
                    {"type": "stored_history", "symbol": symbol, "candles": candles},
                    session_id
                )

            # -- Market Analysis: Plain-Language Explanations -------------------

            elif msg_type == "explain":
                symbol = message.get("symbol", "R_100")
                candles = await market_data_processor.fetch_trade_history(symbol, limit=100)
                indicator_data = technical_indicators.compute_all(candles) if candles else {}
                explanation = await market_explainer.explain_price_action(
                    symbol, candles, indicator_data
                )
                await manager.send_personal_message(
                    {"type": "market_explanation", "symbol": symbol, "text": explanation},
                    session_id
                )

            elif msg_type == "ask_market":
                question = message.get("question", "")
                symbol = message.get("symbol")
                market_context = {}
                if symbol:
                    market_context["symbol"] = symbol
                    market_context["latest_price"] = market_data_processor.get_latest_price(symbol)
                    candles = await market_data_processor.fetch_trade_history(symbol, limit=50)
                    if candles:
                        indicator_data = technical_indicators.compute_all(candles)
                        market_context["indicators"] = indicator_data.get("latest", {})
                        market_context["signals"] = indicator_data.get("signals", [])
                answer = await market_explainer.answer_market_question(question, market_context)
                await manager.send_personal_message(
                    {"type": "market_answer", "text": answer},
                    session_id
                )

            # -- Market Analysis: News & Event Summarisation -------------------

            elif msg_type == "news_summary":
                symbol = message.get("symbol", "R_100")
                headlines = message.get("headlines")  # optional list
                summary = await market_explainer.summarise_news(symbol, headlines=headlines)
                await manager.send_personal_message(
                    {"type": "news_summary", "symbol": symbol, "text": summary},
                    session_id
                )

    except WebSocketDisconnect:
        await manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error in {session_id}: {e}")
        await manager.disconnect(session_id)

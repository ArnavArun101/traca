from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
from app.services.market_data import market_data_processor
from app.services.llm_engine import llm_engine
from app.services.behavioral_analyzer import behavioral_analyzer
from app.services.content_generator import content_generator
from app.services.technical_indicators import technical_indicators
from app.services.price_alerts import price_alert_service
from app.services.market_explainer import market_explainer
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
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
                # Aggregate context (market, behavioral)
                # For now, just call LLM
                analysis = await llm_engine.analyze_market({"note": "User asked: " + user_msg})
                await manager.send_personal_message(
                    {"type": "chat_response", "text": analysis},
                    session_id
                )
            
            elif msg_type == "analyze_behavior":
                # Mock analysis for now
                report = behavioral_analyzer.analyze_trades([])
                await manager.send_personal_message(
                    {"type": "behavioral_report", "data": report},
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
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error in {session_id}: {e}")
        manager.disconnect(session_id)

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.websocket_manager import manager
from app.services.market_data import market_data_processor
from app.services.llm_engine import llm_engine
from app.services.behavioral_analyzer import behavioral_analyzer
from app.services.content_generator import content_generator
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

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error in {session_id}: {e}")
        manager.disconnect(session_id)

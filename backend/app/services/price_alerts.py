import logging
import time
from typing import List, Dict, Optional
from sqlmodel import Session, select
from app.db.session import engine
from app.models.db_models import PriceAlert
from app.core.websocket_manager import manager

logger = logging.getLogger(__name__)


class PriceAlertService:
    """Manages price alerts: create, check against live ticks, and notify via WebSocket."""

    def create_alert(
        self, session_id: str, symbol: str, target_price: float, direction: str
    ) -> Dict:
        """Create a new price alert. Direction is 'above' or 'below'."""
        if direction not in ("above", "below"):
            return {"status": "error", "message": "Direction must be 'above' or 'below'."}

        alert = PriceAlert(
            session_id=session_id,
            symbol=symbol,
            target_price=target_price,
            direction=direction,
        )
        with Session(engine) as session:
            session.add(alert)
            session.commit()
            session.refresh(alert)

        logger.info(f"Alert created: {symbol} {direction} {target_price} for {session_id}")
        return {
            "status": "created",
            "alert_id": alert.id,
            "symbol": symbol,
            "target_price": target_price,
            "direction": direction,
        }

    def get_alerts(self, session_id: str, active_only: bool = True) -> List[Dict]:
        """Retrieve alerts for a given session."""
        with Session(engine) as session:
            statement = select(PriceAlert).where(PriceAlert.session_id == session_id)
            if active_only:
                statement = statement.where(PriceAlert.is_active == True)
            alerts = session.exec(statement).all()
            return [
                {
                    "alert_id": a.id,
                    "symbol": a.symbol,
                    "target_price": a.target_price,
                    "direction": a.direction,
                    "is_active": a.is_active,
                    "created_at": a.created_at,
                    "triggered_at": a.triggered_at,
                }
                for a in alerts
            ]

    def cancel_alert(self, alert_id: int, session_id: str) -> Dict:
        """Cancel (deactivate) a specific alert."""
        with Session(engine) as session:
            alert = session.get(PriceAlert, alert_id)
            if not alert or alert.session_id != session_id:
                return {"status": "error", "message": "Alert not found."}
            alert.is_active = False
            session.add(alert)
            session.commit()
        return {"status": "cancelled", "alert_id": alert_id}

    async def check_price(self, symbol: str, current_price: float):
        """
        Check all active alerts for a symbol against the current price.
        Triggers and notifies via WebSocket when conditions are met.
        """
        with Session(engine) as session:
            statement = (
                select(PriceAlert)
                .where(PriceAlert.symbol == symbol)
                .where(PriceAlert.is_active == True)
            )
            alerts = session.exec(statement).all()

            for alert in alerts:
                triggered = False
                if alert.direction == "above" and current_price >= alert.target_price:
                    triggered = True
                elif alert.direction == "below" and current_price <= alert.target_price:
                    triggered = True

                if triggered:
                    alert.is_active = False
                    alert.triggered_at = int(time.time())
                    session.add(alert)
                    session.commit()

                    notification = {
                        "type": "price_alert_triggered",
                        "alert_id": alert.id,
                        "symbol": symbol,
                        "target_price": alert.target_price,
                        "current_price": current_price,
                        "direction": alert.direction,
                        "message": (
                            f"🔔 {symbol} is now {'above' if alert.direction == 'above' else 'below'} "
                            f"{alert.target_price} (current: {current_price})"
                        ),
                    }
                    await manager.send_personal_message(notification, alert.session_id)
                    logger.info(
                        f"Alert {alert.id} triggered: {symbol} {alert.direction} {alert.target_price}"
                    )


price_alert_service = PriceAlertService()

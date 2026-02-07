import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from app.api import websocket_endpoints
from app.api import auth
from app.db.session import create_db_and_tables
from app.services.market_data import market_data_processor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="traca API")

origins_env = os.getenv("ALLOWED_ORIGINS", "")
origins = [o.strip() for o in origins_env.split(",") if o.strip()]
if not origins:
    origins = ["*"]

allow_credentials = "*" not in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()
    logger.info("Database tables created")
    await market_data_processor.connect()
    logger.info("Market data processor initialized")

# Include websocket routes
app.include_router(websocket_endpoints.router)
app.include_router(auth.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

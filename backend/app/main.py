import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.websocket_manager import manager
from app.api import websocket_endpoints
from app.db.session import create_db_and_tables

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="traca API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    logger.info("Database tables created")

# Include websocket routes
app.include_router(websocket_endpoints.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

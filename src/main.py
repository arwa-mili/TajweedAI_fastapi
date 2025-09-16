import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.db.database import init_db
from src.apis.websocket.audio_ws import websocket_endpoint
from src.apis.routes import router

app = FastAPI(title="Real-time Audio Streaming Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure audio AUDIO_STORAGE_DIR exists
os.makedirs(settings.AUDIO_STORAGE_DIR, exist_ok=True)

# Init DB
init_db()

# Routes
app.include_router(router, prefix="/api")

# WebSocket
app.websocket("/ws/audio")(websocket_endpoint)

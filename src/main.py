import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import init_db
from .routes import sessions
from .web_socket import websocket_endpoint

app = FastAPI(title="Real-time Audio Streaming Server")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.AUDIO_STORAGE_DIR, exist_ok=True)

init_db()

app.include_router(sessions.router)

# WebSocket route
app.websocket("/ws/audio")(websocket_endpoint)

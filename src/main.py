import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.database import init_db
from src.routes import sessions
from src.web_socket import websocket_endpoint
from src.model import load_model



app = FastAPI(title="Real-time Audio Streaming Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.AUDIO_STORAGE_DIR, exist_ok=True)

init_db()

app.include_router(sessions.router)

app.websocket("/ws/audio")(websocket_endpoint)

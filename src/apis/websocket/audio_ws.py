import json
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, Query
from src.services.audio_service import AudioService
from src.services.model_service import transcribe

audio_service = AudioService()

async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    await websocket.accept()
    session_id, sequence = None, 0

    try:
        await websocket.send_json({"type": "connection_established", "message": "Connected"})

        while True:
            message = await websocket.receive()

            # Text message = meta
            if message["type"] == "websocket.receive" and "text" in message:
                data = json.loads(message["text"])
                if data.get("type") == "meta":
                    session_id = data.get(
                        "session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                    audio_service.sessions[session_id] = data
                    audio_service.timings[session_id] = {"start": datetime.now(), "last": None}
                    await websocket.send_json({"type": "meta_ack", "session_id": session_id})

            # Binary = audio chunk
            elif message["type"] == "websocket.receive" and "bytes" in message:
                if not session_id:
                    await websocket.send_json({"type": "error", "message": "Send meta first"})
                    continue

                chunk = message["bytes"]
                now = datetime.now()
                last_time = audio_service.timings[session_id].get("last")
                actual_ms = (now - last_time).total_seconds() * 1000 if last_time else None
                audio_service.timings[session_id]["last"] = now
                sequence += 1

                # Save chunk
                path = await audio_service.save_chunk(session_id, chunk, sequence, actual_ms)

                # If not decodable yet, inform client we're buffering
                if path is None:
                    await websocket.send_json({
                        "type": "chunk_buffered",
                        "session_id": session_id,
                        "sequence": sequence,
                        "timestamp": now.isoformat()
                    })
                    continue

                # Transcription
                try:
                    text = await transcribe(path)
                except Exception:
                    text = None

                await websocket.send_json({
                    "type": "chunk_processed",
                    "session_id": session_id,
                    "sequence": sequence,
                    "file_path": path,
                    "timestamp": now.isoformat(),
                    "transcription": text
                })

            elif message["type"] == "websocket.disconnect":
                break

    except WebSocketDisconnect:
        print(f"Disconnected: {session_id}")
    finally:
        if session_id in audio_service.timings:
            del audio_service.timings[session_id]

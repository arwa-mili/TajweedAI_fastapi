import json
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect, Query
from .audio_processor import AudioProcessor

audio_processor = AudioProcessor()

async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    await websocket.accept()
    session_id = None
    sequence = 0

    try:
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": "Connected to audio streaming server"
        }))
        
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.receive" and "text" in message:
                try:
                    data = json.loads(message["text"])
                    if data.get("type") == "meta":
                        session_id = data.get("session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                        sample_rate = data.get("sample_rate")
                        channels = data.get("channels")
                        sura_number = data.get("sura_number")
                        ayat_begin = data.get("ayat_begin")
                        ayat_end = data.get("ayat_end")

                        audio_processor.sessions[session_id] = {
                            "sample_rate": sample_rate,
                            "channels": channels,
                            "sequence": 0,
                            "sura_number": sura_number,
                            "ayat_begin": ayat_begin,
                            "ayat_end": ayat_end
                        }

                        audio_processor.session_timings[session_id] = {
                            "start_time": datetime.now(),
                            "last_chunk_time": None,
                            "expected_interval_ms": 500
                        }

                        await websocket.send_text(json.dumps({
                            "type": "meta_ack",
                            "session_id": session_id,
                            "sample_rate": sample_rate,
                            "channels": channels,
                            "sura_number": sura_number,
                            "ayat_begin": ayat_begin,
                            "ayat_end": ayat_end,
                            "expected_chunk_duration_ms": 500
                        }))
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))
            
            elif message["type"] == "websocket.receive" and "bytes" in message:
                if not session_id:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Session not initialized. Send metadata first."
                    }))
                    continue
                
                chunk_data = message["bytes"]
                current_time = datetime.now()
                actual_duration_ms = None
                timing_info = audio_processor.session_timings.get(session_id, {})

                if timing_info.get("last_chunk_time"):
                    time_diff = current_time - timing_info["last_chunk_time"]
                    actual_duration_ms = time_diff.total_seconds() * 1000
                
                audio_processor.session_timings[session_id]["last_chunk_time"] = current_time
                sequence += 1

                # Save audio chunk without conversion
                file_path = await audio_processor.save_audio_chunk(
                    session_id, chunk_data, sequence, actual_duration_ms
                )
                
                await websocket.send_text(json.dumps({
                    "type": "chunk_processed",
                    "session_id": session_id,
                    "sequence": sequence,
                    "file_path": file_path,
                    "size": len(chunk_data),
                    "expected_duration_ms": 500,
                    "actual_duration_ms": actual_duration_ms,
                    "timestamp": current_time.isoformat()
                }))
            
            elif message["type"] == "websocket.disconnect":
                break

    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    finally:
        if session_id and session_id in audio_processor.session_timings:
            del audio_processor.session_timings[session_id]


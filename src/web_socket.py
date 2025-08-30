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

                        audio_processor.sessions[session_id] = {
                            "sample_rate": sample_rate,
                            "channels": channels,
                            "sequence": 0
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

                mp3_data = audio_processor.convert_to_mp3(chunk_data)
                if mp3_data:
                    file_path = await audio_processor.save_audio_chunk(session_id, mp3_data, sequence, actual_duration_ms)
                    await websocket.send_text(json.dumps({
                        "type": "chunk_processed",
                        "session_id": session_id,
                        "sequence": sequence,
                        "file_path": file_path,
                        "size": len(mp3_data),
                        "original_size": len(chunk_data),
                        "expected_duration_ms": 500,
                        "actual_duration_ms": actual_duration_ms,
                        "timestamp": current_time.isoformat()
                    }))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": f"Failed to convert chunk {sequence} to MP3"
                    }))
            
            elif message["type"] == "websocket.disconnect":
                break

    except WebSocketDisconnect:
        print(f"Client disconnected: {session_id}")
    finally:
        if session_id and session_id in audio_processor.session_timings:
            del audio_processor.session_timings[session_id]

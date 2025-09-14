import os
import torch
import soundfile as sf
import librosa
from src.model import load_model 

# -----------------------------
# CONFIGURATION
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"

# ✅ load model and processor once via your helper
model, processor = load_model()
model.to(device)

def transcribe(audio_path: str) -> str:
    audio, sr = sf.read(audio_path)

    # If stereo, convert to mono
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    # Ensure 16kHz sample rate
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        sr = 16000

    audio = audio.astype("float32")

    # Process input
    inputs = processor(audio, sampling_rate=sr, return_tensors="pt").input_features.to(device)

    # Run inference
    with torch.no_grad():
        predicted_ids = model.generate(
            inputs,
            suppress_tokens=None,
            max_new_tokens=400,
        )

    # Decode output
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription[0]

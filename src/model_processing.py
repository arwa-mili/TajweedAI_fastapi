import os
import torch
import soundfile as sf
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# -----------------------------
# CONFIGURATION
# -----------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
local_model_dir = "./whisper-tiny-ar-quran-local"

processor = WhisperProcessor.from_pretrained(local_model_dir)
model = WhisperForConditionalGeneration.from_pretrained(local_model_dir)
model.to(device)

def transcribe(audio_path):
    audio, sr = sf.read(audio_path)

    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        sr = 16000

    audio = audio.astype("float32")

    inputs = processor(audio, sampling_rate=sr, return_tensors="pt").input_features.to(device)

    with torch.no_grad():
        predicted_ids = model.generate(
            inputs,
            suppress_tokens=None,  
            max_new_tokens=400     
        )
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription[0]



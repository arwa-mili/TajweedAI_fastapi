import os
import torch
import soundfile as sf
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration

MODEL_NAME = "tarteel-ai/whisper-tiny-ar-quran"
LOCAL_DIR = os.path.abspath("./whisper-tiny-ar-quran-local")

_model = None
_processor = None
_device = "cuda" if torch.cuda.is_available() else "cpu"


def load_model():
    global _model, _processor
    if _model is not None and _processor is not None:
        return _model, _processor

    local_config = os.path.join(LOCAL_DIR, "preprocessor_config.json")
    if os.path.exists(local_config):
        _processor = WhisperProcessor.from_pretrained(LOCAL_DIR)
        _model = WhisperForConditionalGeneration.from_pretrained(LOCAL_DIR)
    else:
        _processor = WhisperProcessor.from_pretrained(MODEL_NAME)
        _model = WhisperForConditionalGeneration.from_pretrained(MODEL_NAME)
        os.makedirs(LOCAL_DIR, exist_ok=True)
        _model.save_pretrained(LOCAL_DIR)
        _processor.save_pretrained(LOCAL_DIR)

    _model.to(_device)
    _model.generation_config.language = "arabic"
    _model.generation_config.task = "transcribe"

    if not hasattr(_model.generation_config, "lang_to_id"):
        _model.generation_config.lang_to_id = {"arabic": 50361}
    if not hasattr(_model.generation_config, "task_to_id"):
        _model.generation_config.task_to_id = {"transcribe": 0}

    return _model, _processor


async def transcribe(audio_path: str) -> str:
    import asyncio
    return await asyncio.to_thread(_sync_transcribe, audio_path)


def _sync_transcribe(audio_path: str) -> str:
    model, processor = load_model()
    audio, sr = sf.read(audio_path)

    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        sr = 16000
    audio = audio.astype("float32")

    inputs = processor(audio, sampling_rate=sr, return_tensors="pt").input_features.to(_device)
    with torch.no_grad():
        ids = model.generate(inputs, suppress_tokens=None, max_new_tokens=400)
    text = processor.batch_decode(ids, skip_special_tokens=True)
    return text[0]

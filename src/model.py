import os
from transformers import WhisperProcessor, WhisperForConditionalGeneration

model_name = "tarteel-ai/whisper-tiny-ar-quran"
local_save_dir = os.path.abspath("./whisper-tiny-ar-quran-local") 

_model = None
_processor = None


def load_model():
    """
    Load Whisper model + processor.
    - If already loaded in memory, reuse.
    - If saved locally, load from disk.
    - Otherwise, download from HuggingFace and save.
    """
    global _model, _processor

    if _model is not None and _processor is not None:
        return _model, _processor

    local_config_file = os.path.join(local_save_dir, "preprocessor_config.json")

    if os.path.exists(local_config_file):
        _processor = WhisperProcessor.from_pretrained(local_save_dir)
        _model = WhisperForConditionalGeneration.from_pretrained(local_save_dir)
    else:
        _processor = WhisperProcessor.from_pretrained(model_name)
        _model = WhisperForConditionalGeneration.from_pretrained(model_name)

        os.makedirs(local_save_dir, exist_ok=True)
        _model.save_pretrained(local_save_dir)
        _processor.save_pretrained(local_save_dir)

    # Patch configs
    if not hasattr(_model.generation_config, "lang_to_id"):
        _model.generation_config.lang_to_id = {"arabic": 50361}
    if not hasattr(_model.generation_config, "task_to_id"):
        _model.generation_config.task_to_id = {"transcribe": 0}

    _model.generation_config.language = "arabic"
    _model.generation_config.task = "transcribe"

    print(f"✅ Model and processor loaded from: {local_save_dir}")
    return _model, _processor

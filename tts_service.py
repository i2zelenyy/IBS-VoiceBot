# tts_service.py 
from TTS.api import TTS
from langdetect import detect

# Load TTS models
tts_en = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
tts_de = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=False, gpu=False)

def generate_tts(text):
    language = detect(text)
    if language == "en":
        file_path = "output_en.wav"
        tts_en.tts_to_file(text=text, file_path=file_path)
    elif language == "de":
        file_path = "output_de.wav"
        tts_de.tts_to_file(text=text, file_path=file_path)
    else:
        raise ValueError("Unsupported language")
    return file_path

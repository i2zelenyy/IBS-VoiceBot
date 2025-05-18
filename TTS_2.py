from TTS.api import TTS
import os
from langdetect import detect  # Import langdetect for language detection

# Load the English and German Coqui TTS models
tts_en = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True, gpu=False)
tts_de = TTS(model_name="tts_models/de/thorsten/tacotron2-DDC", progress_bar=True, gpu=False)

# Function to detect language
def detect_language(text):
    return detect(text)  # Detects language and returns 'en' for English or 'de' for German

# Function to speak based on detected language
def speak_automatically(text):
    # Detect the language of the text
    language = detect_language(text)
    print(f"Detected language: {language}")

    if language == "en":
        # Use the English model for TTS
        tts_en.tts_to_file(text=text, file_path="output_en.wav")
        os.system("start output_en.wav")  # Play the English audio file
    elif language == "de":
        # Use the German model for TTS
        tts_de.tts_to_file(text=text, file_path="output_de.wav")
        os.system("start output_de.wav")  # Play the German audio file
    else:
        print("Language not supported. Please speak in English or German.")

# Example text input (this would be transcribed text from Bassem's STT)
text_from_stt = "Hallo! Wie geht es dir?"  # Example in German

# Call the function to automatically detect language and speak
speak_automatically(text_from_stt)

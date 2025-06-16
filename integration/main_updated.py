
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from voice_transcriber import transcribe_from_microphone
from Start_Bot_refactored import generate_response
# from TTS_2 import speak_tts  # Uncomment when integrating TTS

app = FastAPI()

# Enable CORS for frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "VoiceBot API is running!"}

@app.post("/transcribe")
def transcribe():
    """
    Capture voice from microphone, transcribe it, and return the text.
    """
    transcript = transcribe_from_microphone()
    return {"transcript": transcript}

@app.post("/respond")
async def respond(request: Request):
    """
    Accept transcribed text and return a response from the LLM.
    """
    data = await request.json()
    user_input = data.get("text", "")
    reply = generate_response(user_input)
    return {"response": reply}

@app.post("/speak")
async def speak(request: Request):
    """
    Convert text to speech and return path to audio file.
    """
    data = await request.json()
    response_text = data.get("text", "")
    # audio_path = speak_tts(response_text)  # Enable this once TTS_2.py is ready
    # return {"audio_path": audio_path}
    return {"audio_path": f"/static/audio/{response_text[:10]}.wav"}  # Placeholder

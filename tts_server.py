from flask import Flask, request, send_file
from tts_service import generate_tts

app = Flask(__name__)

@app.route("/tts", methods=["POST"])
def tts_endpoint():
    try:
        text = request.json.get("text", "")
        if not text:
            return {"error": "Missing 'text' in request"}, 400

        audio_path = generate_tts(text)
        return send_file(audio_path, mimetype="audio/wav")

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, render_template, jsonify
from vosk import Model, KaldiRecognizer
from tempfile import NamedTemporaryFile
import os, wave, json, subprocess

app = Flask(__name__)

# Đường dẫn tới model Vosk
MODEL_PATH = "models/vn"
if not os.path.exists(MODEL_PATH):
    raise Exception(f"Không tìm thấy model tại: {MODEL_PATH}")

model = Model(MODEL_PATH)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio_data" not in request.files:
        return jsonify({"error": "Không có file audio được gửi."}), 400

    audio = request.files["audio_data"]

    try:
        # Save input audio to temp
        with NamedTemporaryFile(delete=False, suffix=".wav") as tmp_input:
            audio.save(tmp_input.name)

            # Convert to PCM 16kHz mono WAV
            with NamedTemporaryFile(delete=False, suffix=".wav") as tmp_output:
                command = [
                    "ffmpeg", "-y",
                    "-i", tmp_input.name,
                    "-ac", "1",
                    "-ar", "16000",
                    "-sample_fmt", "s16",
                    tmp_output.name
                ]
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                wf = wave.open(tmp_output.name, "rb")

        rec = KaldiRecognizer(model, wf.getframerate())
        results = []

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                results.append(json.loads(rec.Result()))
        results.append(json.loads(rec.FinalResult()))
        text = " ".join([r.get("text", "") for r in results])
        return jsonify({"text": text})

    except subprocess.CalledProcessError:
        return jsonify({"error": "Lỗi khi convert audio với ffmpeg"}), 500
    except Exception as e:
        return jsonify({"error": f"Lỗi xử lý audio: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)

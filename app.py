from flask import Flask, request, jsonify, render_template
from vosk import Model, KaldiRecognizer
import os, wave, json, subprocess, uuid

app = Flask(__name__)
model = Model("models/vn")  # Đặt mô hình ở đây

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio_data" not in request.files:
        return jsonify({"error": "Không có file audio"}), 400

    audio_file = request.files["audio_data"]
    original_path = f"temp/{uuid.uuid4().hex}_{audio_file.filename}"
    converted_path = original_path + ".wav"

    os.makedirs("temp", exist_ok=True)
    audio_file.save(original_path)

    # Chuyển đổi về WAV 16kHz mono PCM
    try:
        subprocess.run([
            "ffmpeg", "-i", original_path,
            "-ar", "16000", "-ac", "1", "-f", "wav", converted_path
        ], check=True)
    except subprocess.CalledProcessError:
        return jsonify({"error": "Chuyển đổi audio thất bại"}), 500

    # Nhận diện bằng Vosk
    wf = wave.open(converted_path, "rb")
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

    # Xóa file tạm
    os.remove(original_path)
    os.remove(converted_path)

    return jsonify({"text": text})

if __name__ == "__main__":
    app.run(debug=True)

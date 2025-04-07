from flask import Flask, request, render_template, jsonify
from vosk import Model, KaldiRecognizer
import os
import wave
import json
import subprocess
import uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

model = Model("models/vn")  # Đường dẫn model đã tải

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    try:
        audio = request.files.get("audio_data")
        if not audio or audio.filename == "":
            return jsonify({"error": "Không có file audio"}), 400

        # Lưu file tạm
        input_path = f"temp_input_{uuid.uuid4()}"
        output_path = f"temp_output_{uuid.uuid4()}.wav"
        audio.save(input_path)

        # Chuyển đổi bằng ffmpeg: mono, 16-bit PCM, 16000Hz
        convert = subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-ac", "1", "-ar", "16000", "-f", "wav", output_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if convert.returncode != 0 or not os.path.exists(output_path):
            os.remove(input_path)
            return jsonify({"error": "Lỗi khi chuyển đổi audio"}), 500

        wf = wave.open(output_path, "rb")

        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            wf.close()
            os.remove(input_path)
            os.remove(output_path)
            return jsonify({"error": "File không đúng định dạng WAV mono 16kHz"}), 400

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

        wf.close()
        os.remove(input_path)
        os.remove(output_path)

        return jsonify({"text": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

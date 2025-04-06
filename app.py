import os
import zipfile
import urllib.request
from flask import Flask, request
from flask_sock import Sock
from vosk import Model, KaldiRecognizer
import wave

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-vn-0.4.zip"
MODEL_ZIP = "model.zip"
MODEL_DIR = "model"
MODEL_SUBDIR = os.path.join(MODEL_DIR, "vosk-model-vn-0.4")

app = Flask(__name__)
sock = Sock(app)

def download_model():
    print("📝 Đang tải mô hình từ URL...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_ZIP)
    print("✅ Tải mô hình thành công!")

    with zipfile.ZipFile(MODEL_ZIP, "r") as zip_ref:
        zip_ref.extractall(MODEL_DIR)
    print("✅ Giải nén mô hình thành công!")

# Tải và load model
if not os.path.exists(MODEL_SUBDIR):
    download_model()

try:
    model = Model(MODEL_SUBDIR)
    print("✅ Mô hình đã sẵn sàng!")
except Exception as e:
    print("❌ Lỗi khi tạo mô hình Vosk:", str(e))

# WebSocket handler
@sock.route('/ws')
def recognize(ws):
    recognizer = KaldiRecognizer(model, 16000)
    audio_data = b''

    while True:
        data = ws.receive()
        if data is None:
            break
        if isinstance(data, str):
            data = data.encode("latin1")
        audio_data += data

        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            print("📤 Sending result:", result)
            ws.send(result)
        else:
            partial = recognizer.PartialResult()
            print("📤 Sending partial:", partial)
            ws.send(partial)

    final_result = recognizer.FinalResult()
    ws.send(final_result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=True, host="0.0.0.0", port=port)

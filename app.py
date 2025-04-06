import os
import urllib.request
import zipfile
from flask import Flask
from flask_sock import Sock
from vosk import Model, KaldiRecognizer
import json

app = Flask(__name__)
sock = Sock(app)

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-vi-0.3.zip"
MODEL_DIR = "model/vosk-model-small-vi-0.3"

def download_model():
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        print("📝 Đang tải mô hình từ URL...")
        # Tải mô hình zip về
        urllib.request.urlretrieve(MODEL_URL, "model.zip")
        with zipfile.ZipFile("model.zip", "r") as zip_ref:
            zip_ref.extractall(MODEL_DIR)
        os.remove("model.zip")
        print("✅ Tải và giải nén mô hình thành công!")
    else:
        print("✅ Mô hình đã có sẵn!")

# Tải mô hình khi ứng dụng khởi động
download_model()

# Khởi tạo mô hình Vosk
model = Model(MODEL_DIR)

@sock.route('/ws')
def recognize(ws):
    recognizer = KaldiRecognizer(model, 16000)
    
    while True:
        data = ws.receive()
        if data is None:
            break

        # Đảm bảo data là bytes
        if isinstance(data, str):
            data = data.encode("latin1")  # Giải pháp an toàn cho WebSocket gửi string

        # Gửi kết quả cuối cùng hoặc tạm thời
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            ws.send(json.dumps({"text": result.get("text", "")}))
        else:
            partial = json.loads(recognizer.PartialResult())
            ws.send(json.dumps({"partial": partial.get("partial", "")}))

@app.route('/')
def index():
    return "✅ Vosk WebSocket server is running!"

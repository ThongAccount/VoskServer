from flask import Flask
from flask_sock import Sock
from vosk import Model, KaldiRecognizer
import json

app = Flask(__name__)
sock = Sock(app)

# Load Vosk model (đảm bảo thư mục 'model' chứa model Vosk)
model = Model("model")

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

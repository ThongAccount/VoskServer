from flask import Flask
from flask_sock import Sock
import json
import wave
import os
from vosk import Model, KaldiRecognizer
import soundfile as sf
import io

app = Flask(__name__)
sock = Sock(app)

model = Model(lang="vn")  # tải mô hình tiếng Việt

@sock.route('/ws')
def recognize(ws):
    audio_data = b""
    while True:
        data = ws.receive()
        if data is None:
            break
        if isinstance(data, str):
            data = data.encode('latin1')  # hoặc 'utf-8' nếu frontend dùng utf-8
        audio_data += data

        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            ws.send(result)
        else:
            partial = recognizer.PartialResult()
            ws.send(partial)

    final_result = recognizer.FinalResult()
    ws.send(final_result)

@app.route('/')
def home():
    return '✅ Vosk server is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

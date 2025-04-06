import os
import urllib.request
import zipfile
from flask import Flask, render_template
from flask_sock import Sock
from vosk import Model, KaldiRecognizer

# Khởi tạo Flask và Flask-Sock
app = Flask(__name__)
sock = Sock(app)

# URL mô hình Vosk tiếng Việt
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-vn-0.4.zip"

# Hàm tải mô hình
def download_model():
    print("📝 Đang tải mô hình từ URL...")
    try:
        # Tải mô hình về
        urllib.request.urlretrieve(MODEL_URL, "model.zip")
        print("✅ Tải mô hình thành công!")
        
        # Giải nén mô hình
        with zipfile.ZipFile("model.zip", "r") as zip_ref:
            zip_ref.extractall("model")
        
        print("✅ Giải nén mô hình thành công!")
        os.remove("model.zip")  # Xóa file zip đã tải
    except Exception as e:
        print(f"❌ Lỗi tải mô hình: {e}")

# Tải mô hình khi khởi động ứng dụng
download_model()

# Khởi tạo mô hình Vosk
try:
    model = Model("model")
    recognizer = KaldiRecognizer(model, 16000)
    print("✅ Mô hình Vosk đã được tải thành công!")
except Exception as e:
    print(f"❌ Lỗi khi tạo mô hình Vosk: {e}")

@app.route('/')
def index():
    return render_template("index.html")

@sock.route('/ws')
def recognize(ws):
    print("📝 Đang chờ dữ liệu từ WebSocket...")
    audio_data = b""

    try:
        while True:
            data = ws.receive()
            if data:
                audio_data += data  # Thêm dữ liệu âm thanh vào biến audio_data
                if recognizer.AcceptWaveform(audio_data):
                    result = recognizer.Result()
                    ws.send(result)  # Gửi kết quả về client
                    audio_data = b""  # Xóa dữ liệu âm thanh sau khi nhận diện xong
    except Exception as e:
        print(f"❌ Lỗi khi xử lý WebSocket: {e}")
        ws.close()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

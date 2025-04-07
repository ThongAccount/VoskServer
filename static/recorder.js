let mediaRecorder;
let audioChunks = [];

function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    audioChunks = [];

    mediaRecorder.ondataavailable = e => {
      audioChunks.push(e.data);
    };

    alert("🔴 Đang ghi âm...");
  });
}

function stopRecording() {
  mediaRecorder.stop();

  mediaRecorder.onstop = () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });

    // Gửi dữ liệu
    const formData = new FormData();
    formData.append("audio_data", audioBlob, "record.wav");

    fetch("/transcribe", {
      method: "POST",
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById("result").innerText = data.text || "Không nhận diện được";
    });
  };
}

function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  if (!fileInput.files.length) {
    alert("Hãy chọn một file .wav trước");
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("audio_data", file);

  fetch("/transcribe", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("result").innerText = data.text || "Không nhận diện được";
    });
}


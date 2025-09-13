from flask import Flask, send_from_directory
from flask_socketio import SocketIO, join_room, emit
import base64, os
from pydub import AudioSegment
from pydub.utils import which

# Setup ffmpeg for pydub
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")

RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

@socketio.on("connect")
def handle_connect():
    print("✅ Client connected")

@socketio.on("join_session")
def handle_join(data):
    session_id = data.get("session_id", "default")
    join_room(session_id)
    print(f"📌 Client joined session {session_id}")

@socketio.on("audio_chunk")
def handle_audio_chunk(data):
    session_id = data.get("session_id", "default")
    chunk_b64 = data.get("chunk")
    if not chunk_b64:
        return
    webm_path = os.path.join(RECORDINGS_DIR, f"{session_id}.webm")
    audio_bytes = base64.b64decode(chunk_b64)
    with open(webm_path, "ab") as f:
        f.write(audio_bytes)
    emit("audio_chunk", {"chunk": chunk_b64}, room=session_id, include_self=False)

@socketio.on("stop_recording")
def handle_stop(data):
    session_id = data.get("session_id", "default")
    webm_path = os.path.join(RECORDINGS_DIR, f"{session_id}.webm")
    mp3_path = os.path.join(RECORDINGS_DIR, f"{session_id}.mp3")
    if os.path.exists(webm_path):
        sound = AudioSegment.from_file(webm_path, format="webm")
        sound.export(mp3_path, format="mp3", bitrate="64k")
        print(f"✅ Finalized recording: {mp3_path}")
        emit("recording_ready", {"file": f"/recordings/{session_id}.mp3"}, room=session_id)

@app.route("/recordings/<path:filename>")
def download_file(filename):
    return send_from_directory(RECORDINGS_DIR, filename, as_attachment=False)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
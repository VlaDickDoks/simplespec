# screen_server.py — один файл, зум работает в браузере
import configparser
from pathlib import Path

from flask import Flask, Response
import dxcam
import io, time
from PIL import Image
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

# --- Загрузка конфига ---
CONFIG_PATH = Path(__file__).with_name("config.ini")
cfg = configparser.ConfigParser()
if not cfg.read(CONFIG_PATH, encoding="utf-8"):
    raise SystemExit(f"Не найден файл конфигурации: {CONFIG_PATH}")

USERNAME      = cfg.get("auth", "username")
PASSWORD_HASH = cfg.get("auth", "password_hash")
FPS           = cfg.getint("stream", "fps")
QUALITY       = cfg.getint("stream", "quality")
HOST          = cfg.get("server", "host")
PORT          = cfg.getint("server", "port")
OUTPUT_COLOR  = cfg.get("capture", "output_color")
# ------------------------

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    if username == USERNAME and check_password_hash(PASSWORD_HASH, password):
        return username
    return None


camera = dxcam.create(output_color=OUTPUT_COLOR)


def gen_frames():
    buf = io.BytesIO()
    delay = 1.0 / FPS
    while True:
        t0 = time.perf_counter()
        frame = camera.grab()
        if frame is None:
            time.sleep(delay)
            continue
        im = Image.fromarray(frame)
        buf.seek(0)
        buf.truncate()
        im.save(buf, format="JPEG", quality=QUALITY)
        yield (
            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
            + buf.getvalue()
            + b"\r\n"
        )
        dt = time.perf_counter() - t0
        if dt < delay:
            time.sleep(delay - dt)


@app.route("/")
@auth.login_required
def index():
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  #wrap { overflow: hidden; cursor: grab; width: 100%; }
  #screen { display: block; width: 100%; transform-origin: 0 0; }
</style>
</head>
<body>
<div id="wrap">
  <img id="screen" src="/stream">
</div>
<script src="https://unpkg.com/@panzoom/panzoom@4.6.2/dist/panzoom.min.js"></script>
<script>
  const wrap = document.getElementById('wrap');
  const img = document.getElementById('screen');
  const pz = Panzoom(img, { maxScale: 5, minScale: 1, cursor: 'grab' });
  wrap.addEventListener('wheel', pz.zoomWithWheel, { passive: false });
</script>
</body>
</html>
"""


@app.route("/stream")
@auth.login_required
def stream():
    return Response(
        gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
# screen_server.py — один файл, зум работает в браузере
from flask import Flask, Response
import dxcam
import io, time
from PIL import Image

app = Flask(__name__)

FPS = 12
QUALITY = 100

# Камера создаётся один раз при старте
camera = dxcam.create()

def gen_frames():
    buf = io.BytesIO()
    delay = 1.0 / FPS
    while True:
        t0 = time.perf_counter()
        frame = camera.grab()
        if frame is None:
            time.sleep(delay)
            continue
        # dxcam отдаёт BGR — меняем на RGB
        rgb = frame[:, :, ::-1]
        im = Image.fromarray(rgb)
        buf.seek(0); buf.truncate()
        im.save(buf, format="JPEG", quality=QUALITY)
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
               + buf.getvalue() + b"\r\n")
        dt = time.perf_counter() - t0
        if dt < delay:
            time.sleep(delay - dt)

@app.route("/")
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
def stream():
    return Response(gen_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1488)

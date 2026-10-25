# screen_server.py — один файл, зум/пан работают в браузере без внешних библиотек
import configparser
import io
import threading
from pathlib import Path

from flask import Flask, Response
import dxcam
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


class Streamer:
    """Один захват и одно JPEG-кодирование на всех зрителей.

    Захват запускается, когда подключается первый зритель,
    и останавливается, когда отключается последний — без зрителей CPU/GPU не грузятся.
    Статичный экран тоже отдаётся сразу (video_mode дублирует последний кадр).
    """

    def __init__(self):
        self.cond = threading.Condition()
        self.cam_lock = threading.Lock()  # не даёт запустить камеру, пока старый поток её не остановил
        self.clients = 0
        self.frame = None
        self.seq = 0
        self.thread = None

    def _run(self):
        with self.cam_lock:
            camera.start(target_fps=FPS, video_mode=True)
            try:
                while True:
                    with self.cond:
                        if self.clients == 0:
                            self.thread = None
                            return
                    frame = camera.get_latest_frame()
                    if frame is None:
                        continue
                    buf = io.BytesIO()
                    Image.fromarray(frame).save(buf, format="JPEG", quality=QUALITY)
                    with self.cond:
                        self.frame = buf.getvalue()
                        self.seq += 1
                        self.cond.notify_all()
            finally:
                camera.stop()

    def subscribe(self):
        with self.cond:
            self.clients += 1
            if self.thread is None:
                self.thread = threading.Thread(target=self._run, daemon=True)
                self.thread.start()

    def unsubscribe(self):
        with self.cond:
            self.clients -= 1

    def frames(self):
        self.subscribe()
        last = 0
        try:
            while True:
                with self.cond:
                    self.cond.wait_for(lambda: self.seq != last, timeout=5)
                    if self.seq == last:
                        continue
                    data, last = self.frame, self.seq
                yield (
                    b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                    + str(len(data)).encode()
                    + b"\r\n\r\n"
                    + data
                    + b"\r\n"
                )
        finally:
            self.unsubscribe()


streamer = Streamer()

PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Экран</title>
<style>
  :root {
    --bg: #0b0d10;
    --panel: rgba(24, 28, 34, .82);
    --line: rgba(255, 255, 255, .12);
    --text: #e8ecf1;
    --muted: #8b95a3;
    --accent: #5ab0ff;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; height: 100%; background: var(--bg); color: var(--text);
    overflow: hidden; overscroll-behavior: none;
    font: 14px/1.4 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  #stage {
    position: fixed; inset: 0; overflow: hidden;
    display: flex; align-items: center; justify-content: center;
    cursor: grab; touch-action: none;
  }
  #stage.dragging { cursor: grabbing; }
  #screen {
    display: block; max-width: 100%; max-height: 100%;
    width: auto; height: auto;
    transform-origin: 50% 50%; will-change: transform;
    user-select: none; -webkit-user-drag: none;
  }
  #status {
    position: fixed; inset: 0; display: flex; align-items: center; justify-content: center;
    pointer-events: none; color: var(--muted); transition: opacity .3s;
  }
  #status.hidden { opacity: 0; }
  #bar {
    position: fixed; left: 50%; bottom: calc(16px + env(safe-area-inset-bottom, 0px));
    transform: translateX(-50%); display: flex; align-items: center; gap: 2px;
    padding: 4px; background: var(--panel); border: 1px solid var(--line);
    border-radius: 12px; backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
    transition: opacity .25s;
  }
  #bar.idle { opacity: 0; pointer-events: none; }
  #bar button {
    min-width: 38px; height: 38px; padding: 0 10px; border: 0; border-radius: 8px;
    background: transparent; color: var(--text); font: inherit; font-size: 18px; cursor: pointer;
  }
  #bar button:hover { background: rgba(255, 255, 255, .09); }
  #bar button:focus-visible { outline: 2px solid var(--accent); outline-offset: -2px; }
  #zoom {
    min-width: 58px; font-size: 13px !important; color: var(--muted) !important;
    font-variant-numeric: tabular-nums;
  }
  .sep { width: 1px; height: 22px; background: var(--line); margin: 0 4px; }
  #dot { width: 8px; height: 8px; margin: 0 10px; border-radius: 50%; background: #e5534b; }
  #dot.ok { background: #3fb950; }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>
<div id="stage">
  <img id="screen" alt="Экран" draggable="false">
</div>
<div id="status">Подключение…</div>
<div id="bar" role="toolbar" aria-label="Управление просмотром">
  <span id="dot" title="Соединение"></span>
  <button id="out" title="Уменьшить (−)" aria-label="Уменьшить">−</button>
  <button id="zoom" title="Сбросить масштаб (0)">100%</button>
  <button id="in" title="Увеличить (+)" aria-label="Увеличить">+</button>
  <span class="sep"></span>
  <button id="fs" title="Во весь экран (F)" aria-label="Во весь экран">⛶</button>
</div>
<script>
(() => {
  const stage = document.getElementById('stage');
  const img = document.getElementById('screen');
  const bar = document.getElementById('bar');
  const zoomBtn = document.getElementById('zoom');
  const status = document.getElementById('status');
  const dot = document.getElementById('dot');
  const MIN = 1, MAX = 8;
  let s = 1, x = 0, y = 0;

  // ---------- поток и переподключение ----------
  let lastLoad = 0, retry = 0;
  function connect() {
    img.src = '/stream?t=' + Date.now();
  }
  img.addEventListener('load', () => {
    lastLoad = Date.now(); retry = 0;
    status.classList.add('hidden'); dot.classList.add('ok');
    apply();
  });
  img.addEventListener('error', () => {
    dot.classList.remove('ok');
    status.textContent = 'Нет соединения. Повторяю…';
    status.classList.remove('hidden');
    retry = Math.min(retry + 1, 5);
    setTimeout(connect, retry * 1000);
  });
  connect();

  // ---------- масштаб и перемещение ----------
  function clamp() {
    const W = stage.clientWidth, H = stage.clientHeight;
    const iw = img.clientWidth * s, ih = img.clientHeight * s;
    const mx = Math.max(0, (iw - W) / 2), my = Math.max(0, (ih - H) / 2);
    x = Math.min(mx, Math.max(-mx, x));
    y = Math.min(my, Math.max(-my, y));
  }
  function apply() {
    clamp();
    img.style.transform = `translate(${x}px, ${y}px) scale(${s})`;
    zoomBtn.textContent = Math.round(s * 100) + '%';
  }
  // zoom к точке (cx, cy) в координатах окна
  function zoomAt(ns, cx, cy) {
    ns = Math.min(MAX, Math.max(MIN, ns));
    const r = stage.getBoundingClientRect();
    const px = cx - (r.left + r.width / 2), py = cy - (r.top + r.height / 2);
    const k = ns / s;
    x = px - (px - x) * k; y = py - (py - y) * k;
    s = ns; apply();
  }
  const center = () => { const r = stage.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; };
  function reset() { s = 1; x = 0; y = 0; apply(); }

  stage.addEventListener('wheel', e => {
    e.preventDefault();
    zoomAt(s * Math.exp(-e.deltaY * 0.0015), e.clientX, e.clientY);
  }, { passive: false });

  const ptrs = new Map();
  let pinch = null;
  stage.addEventListener('pointerdown', e => {
    stage.setPointerCapture(e.pointerId);
    ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
    stage.classList.add('dragging');
    if (ptrs.size === 2) {
      const [a, b] = [...ptrs.values()];
      pinch = { d: Math.hypot(a.x - b.x, a.y - b.y), s };
    }
  });
  stage.addEventListener('pointermove', e => {
    const p = ptrs.get(e.pointerId);
    if (!p) return;
    if (ptrs.size === 1) {
      x += e.clientX - p.x; y += e.clientY - p.y; apply();
    } else if (ptrs.size === 2 && pinch) {
      p.x = e.clientX; p.y = e.clientY;
      const [a, b] = [...ptrs.values()];
      const d = Math.hypot(a.x - b.x, a.y - b.y);
      zoomAt(pinch.s * d / pinch.d, (a.x + b.x) / 2, (a.y + b.y) / 2);
    }
    p.x = e.clientX; p.y = e.clientY;
  });
  const up = e => {
    ptrs.delete(e.pointerId); pinch = null;
    if (!ptrs.size) stage.classList.remove('dragging');
  };
  stage.addEventListener('pointerup', up);
  stage.addEventListener('pointercancel', up);
  stage.addEventListener('dblclick', e => {
    if (s > 1.01) reset(); else zoomAt(2.5, e.clientX, e.clientY);
  });

  // ---------- панель ----------
  document.getElementById('in').onclick  = () => zoomAt(s * 1.4, ...center());
  document.getElementById('out').onclick = () => zoomAt(s / 1.4, ...center());
  zoomBtn.onclick = reset;
  const fsBtn = document.getElementById('fs');
  function toggleFS() {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen?.();
  }
  fsBtn.onclick = toggleFS;
  if (!document.documentElement.requestFullscreen) fsBtn.hidden = true;

  window.addEventListener('keydown', e => {
    if (e.key === '+' || e.key === '=') zoomAt(s * 1.4, ...center());
    else if (e.key === '-') zoomAt(s / 1.4, ...center());
    else if (e.key === '0') reset();
    else if (e.key === 'f' || e.key === 'F') toggleFS();
  });
  window.addEventListener('resize', apply);

  // панель скрывается, когда мышь/палец неактивны
  let idleTimer;
  function wake() {
    bar.classList.remove('idle');
    clearTimeout(idleTimer);
    idleTimer = setTimeout(() => bar.classList.add('idle'), 3000);
  }
  ['pointermove', 'pointerdown', 'keydown', 'wheel'].forEach(t => window.addEventListener(t, wake, { passive: true }));
  bar.addEventListener('pointerdown', e => e.stopPropagation());
  bar.addEventListener('dblclick', e => e.stopPropagation());
  wake();
})();
</script>
</body>
</html>
"""


@app.route("/")
@auth.login_required
def index():
    resp = Response(PAGE, mimetype="text/html")
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.route("/stream")
@auth.login_required
def stream():
    resp = Response(
        streamer.frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["X-Accel-Buffering"] = "no"
    return resp


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, threaded=True)

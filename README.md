# simplespec

A simple screen streaming tool for your local network or over the internet. Runs in a web browser, no client software required. Includes authentication, zoom, and pan directly in the browser.

## Features

- Real-time screen capture via DXcam (low overhead)
- HTTP Basic Auth with hashed passwords (scrypt)
- Zoom and pan with the mouse wheel in the browser (Panzoom)
- LAN access without installing anything on the client
- HTTPS link for remote viewers via Cloudflare Tunnel (no port forwarding)
- Configurable via `config.ini` (FPS, quality, port, host)

## Installation

1. Install [Python](https://www.python.org/downloads/) and add it to `PATH`.
2. Run the dependency installer:

```bat
req\install_deps.bat
```

This creates a virtual environment at `req\.venv`, installs dependencies (Flask, Flask-HTTPAuth, DXcam, Pillow, NumPy, OpenCV), and downloads `cloudflared.exe` into `req`.

## Usage

### Local network

```bat
runsimplespec.bat
```

The console prints an address like `http://192.168.1.100:1488`. Open it in a browser on any device on the same Wi-Fi network.

### Over the internet

1. Start the server (see above).
2. In a separate window, run:

```bat
run_tunnel.bat
```

After a few seconds a link like `https://....trycloudflare.com` appears. Share it with the viewer. Keep the tunnel window open while they watch.

## Configuration

All settings live in `config.ini`:

```ini
[auth]
username = admin
password_hash = scrypt:...

[stream]
fps = 12
quality = 85

[server]
host = 0.0.0.0
port = 1488

[capture]
output_color = RGB
```

- **username / password_hash** — login and password hash.
- **fps** — frame rate.
- **quality** — JPEG quality (1–100; 100 is highest quality and largest frame size).
- **host / port** — server bind address and port.
- **output_color** — capture color format (`RGB` or `BGR`).

### Changing the password

Run:

```bat
generate_hash.bat
```

Enter the new password and the script prints a hash. Copy it into `config.ini` under `password_hash`.

Note: `generate_hash.bat` looks for `.venv` in the **project root**, while `install_deps.bat` creates it at **`req\.venv`**. If hash generation fails, either create a venv in the root (`python -m venv .venv`) or edit the path in the batch file to point at `req\.venv`.

## Updating

```bat
update_from_github.bat
```

Clones the repository if `.git` is missing, otherwise runs `git pull`. The virtual environment and caches are left untouched. If dependencies changed, re-run `req\install_deps.bat` afterward.

## Troubleshooting

- **A device can't connect (LAN)** — Windows Firewall is likely blocking it. Allow Python access to private networks or add port `1488` to the firewall exceptions.
- **Stream is lagging** — lower `fps` and `quality` in `config.ini`.
- **Tunnel won't start** — check that `req\cloudflared.exe` exists (re-run `install_deps.bat`).
- **Server crashed** — the `runsimplespec.bat` window stays open on error so you can read the message.

## Project layout

```
simplespec/
├── req/
│   ├── simplespec.py        # server
│   ├── config.ini           # settings
│   ├── install_deps.bat     # dependency installer
│   ├── cloudflared.exe      # tunnel binary (downloaded automatically)
│   └── .venv/               # virtual environment
├── runsimplespec.bat        # start the server
├── run_tunnel.bat           # start Cloudflare Tunnel
├── generate_hash.bat        # generate a password hash
└── update_from_github.bat   # update from GitHub
```

## Notes

Built with the help of DeepSeek.
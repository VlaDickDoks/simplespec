# simplespec

A simple script for streaming your screen over a local network. It runs in a web browser, so no client software is required.

## Installation

For Windows, use the provided batch scripts. Run:

```bat
req\install_deps.bat
```

This will create a virtual environment (`.venv`) and install the required dependencies.

## Usage

Start the server:

```bat
runsimplespec.bat
```

The console will output a local IP address (e.g., `http://192.168.1.100:1488`). Open this link in a browser on any device connected to the same Wi-Fi network.

## Configuration

Port, FPS, and image quality can be changed in `req/simplespec.py`.

- **Port**: the `port` parameter in `app.run(...)`
- **FPS**: the `FPS` variable
- **Quality**: the `QUALITY` variable (1 to 100, where 100 is the highest quality and largest frame size)

## Troubleshooting

If a device fails to connect, the Windows Firewall is likely blocking it. Allow Python access to private networks or add port 1488 to the firewall exceptions.

If the stream is lagging, try lowering the FPS and quality settings.

## Notes

Built with the help of DeepSeek.

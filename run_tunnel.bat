@echo off
setlocal
cd /d "%~dp0"

if not exist "req\config.ini" (
    echo [ERROR] req\config.ini not found in %~dp0
    pause
    exit /b 1
)
if not exist "req\.venv\Scripts\python.exe" (
    echo [ERROR] req\.venv\Scripts\python.exe not found in %~dp0
    pause
    exit /b 1
)
if not exist "req\cloudflared.exe" (
    echo [ERROR] req\cloudflared.exe not found in %~dp0
    pause
    exit /b 1
)
if not exist "req\modules\port.py" (
    echo [ERROR] req\modules\port.py not found in %~dp0
    pause
    exit /b 1
)

for /f "usebackq delims=" %%P in (`cmd /c ""req\.venv\Scripts\python.exe" "req\modules\port.py""`) do set "PORT=%%P"

if not defined PORT (
    echo [ERROR] Could not read server.port from req\config.ini
    pause
    exit /b 1
)

echo === Starting Cloudflare Tunnel ===
echo Port: %PORT%
echo Link will appear shortly. Do not close this window.
echo.

"req\cloudflared.exe" tunnel --loglevel info --protocol http2 --url http://127.0.0.1:%PORT%
pause
endlocal

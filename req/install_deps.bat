@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === Проверка Python ===
where python >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден в PATH. Установи Python и добавь его в PATH.
    pause
    exit /b 1
)

echo === Создание виртуального окружения .venv (внутри req) ===
if not exist ".venv" (
    python -m venv .venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать venv.
        pause
        exit /b 1
    )
) else (
    echo .venv уже существует, пропускаю создание.
)

echo === Активация .venv ===
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ОШИБКА] Не удалось активировать venv.
    pause
    exit /b 1
)

echo === Настройка pip на официальный PyPI (без Яндекс-зеркала) ===
python -m pip config set global.index-url https://pypi.org/simple
python -m pip config set global.trusted-host pypi.org

echo === Обновление pip ===
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ОШИБКА] Не удалось обновить pip.
    pause
    exit /b 1
)

echo === Установка зависимостей (по одному) ===
python -m pip install flask
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить flask.
    pause
    exit /b 1
)

python -m pip install flask-httpauth
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить flask-httpauth.
    pause
    exit /b 1
)

python -m pip install dxcam
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить dxcam.
    pause
    exit /b 1
)

python -m pip install pillow
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить pillow.
    pause
    exit /b 1
)

python -m pip install numpy
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить numpy.
    pause
    exit /b 1
)

python -m pip install opencv-python
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить opencv-python.
    pause
    exit /b 1
)

echo === Скачивание cloudflared.exe (рядом, в req) ===
if not exist "cloudflared.exe" (
    echo Скачиваю cloudflared...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось скачать cloudflared.exe
        pause
        exit /b 1
    )
    echo cloudflared.exe скачан.
) else (
    echo cloudflared.exe уже есть, пропускаю.
)

echo.
echo === Готово! ===
echo Дальше:
echo   1) ..\runsimplespec.bat  - запустить сервер экрана
echo   2) ..\run_tunnel.bat     - запустить HTTPS-ссылку для друга
pause
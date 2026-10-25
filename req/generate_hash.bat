@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv not found in:
    echo         %~dp0.venv
    echo.
    echo Create it with:
    echo     python -m venv .venv
    echo and install deps:
    echo     .venv\Scripts\pip install flask flask-httpauth werkzeug dxcam pillow
    echo.
    pause
    exit /b 1
)

set /p "PLAIN_PASSWORD=Enter password to hash: "
if "%PLAIN_PASSWORD%"=="" (
    echo [ERROR] Empty password.
    pause
    exit /b 1
)

echo.
echo Generating hash...
echo.

set "PLAIN_PASSWORD=%PLAIN_PASSWORD%"
".venv\Scripts\python.exe" -c "import os; from werkzeug.security import generate_password_hash; print(generate_password_hash(os.environ['PLAIN_PASSWORD']))"

echo.
echo Done. Copy the line above into config.ini -^> password_hash
pause
endlocal

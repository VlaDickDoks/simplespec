@echo off
chcp 65001 >nul
setlocal

REM ==== Переход в папку, где лежит этот .bat ====
cd /d "%~dp0"

REM ==== Проверка наличия .venv ====
if not exist ".venv\Scripts\python.exe" (
    echo [ОШИБКА] Не найдена среда .venv в корне проекта:
    echo          %~dp0.venv
    echo.
    echo Создайте её командой:
    echo     python -m venv .venv
    echo и установите зависимости:
    echo     .venv\Scripts\pip install flask flask-httpauth werkzeug dxcam pillow
    echo.
    pause
    exit /b 1
)

REM ==== Запрос пароля ====
set /p "PLAIN_PASSWORD=Введите пароль для хеширования: "
if "%PLAIN_PASSWORD%"=="" (
    echo [ОШИБКА] Пароль не введён.
    pause
    exit /b 1
)

echo.
echo Генерация хеша...
echo.

REM ==== Запуск Python из .venv ====
".venv\Scripts\python.exe" -c "import os; from werkzeug.security import generate_password_hash; print(generate_password_hash(os.environ['PLAIN_PASSWORD']))"

echo.
echo Готово. Скопируйте строку выше в config.ini -^> password_hash
pause
endlocal
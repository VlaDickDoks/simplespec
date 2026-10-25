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

echo === Создание виртуального окружения .venv ===
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

echo === Обновление pip ===
python -m pip install --upgrade pip

echo === Установка зависимостей ===
python -m pip install flask dxcam pillow numpy

if errorlevel 1 (
    echo [ОШИБКА] Установка зависимостей провалилась.
    pause
    exit /b 1
)

echo.
echo === Готово! ===
echo Теперь запускай сервер так:
echo    .venv\Scripts\activate
echo    python simplespec.py
echo Или просто запусти run_server.bat (создам ниже).
pause

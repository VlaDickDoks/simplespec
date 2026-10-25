@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === Проверка Python ===
where python >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден в PATH. 
    pause
    exit /b 1
)

echo === Проверка версии Python ===
python --version
if errorlevel 1 (
    echo [ОШИБКА] Команда python есть, но она не работает.
    pause
    exit /b 1
)

if exist ".venv" goto activate_venv

echo === Создание виртуального окружения .venv ===
python -m venv .venv
if errorlevel 1 (
    echo [ОШИБКА] Не удалось создать venv.
    pause
    exit /b 1
)
goto activate_venv

:activate_venv
echo .venv уже существует или успешно создано.
echo === Активация .venv ===
call ".venv\Scripts\activate.bat"

echo === Обновление pip ===
python -m pip install --upgrade pip

echo === Установка зависимостей ===
python -m pip install flask mss pillow

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
echo Или просто запусти run_server.bat
pause
